#!/usr/bin/env python3
"""
Parallel SSA pipeline test runner.
Compiles all test cases through the SSA native pipeline and compares output
against the expected output from the test file headers.

Uses ProcessPoolExecutor for parallelism - each test compiles and runs
in a separate process.
"""
import sys
import os
import glob
import json
import subprocess
import tempfile
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# Setup paths
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / 'src'))

RUNTIME_DIR = REPO_ROOT / 'runtime'
RUNTIME_SRC = RUNTIME_DIR / 'runtime_lib.c'
RUNTIME_HDR = RUNTIME_DIR / 'runtime_lib.h'
RUNTIME_OBJ = Path(tempfile.gettempdir()) / 'frscript_ssa_runtime_lib.o'


def ensure_runtime_object():
    """Compile runtime_lib.c once and cache it."""
    src_mtime = RUNTIME_SRC.stat().st_mtime
    hdr_mtime = RUNTIME_HDR.stat().st_mtime if RUNTIME_HDR.exists() else 0
    newest = max(src_mtime, hdr_mtime)

    if RUNTIME_OBJ.exists():
        try:
            if RUNTIME_OBJ.stat().st_mtime >= newest:
                return str(RUNTIME_OBJ)
        except OSError:
            pass

    tmp_obj = RUNTIME_OBJ.with_suffix('.o.tmp')
    result = subprocess.run(
        ['gcc', '-c', '-O3', '-march=native', '-mtune=native',
         '-ffunction-sections', '-fdata-sections',
         '-I', str(RUNTIME_DIR),
         '-o', str(tmp_obj), str(RUNTIME_SRC)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        try:
            tmp_obj.unlink()
        except OSError:
            pass
        raise RuntimeError(f'Failed to compile runtime_lib.c:\n{result.stderr}')

    tmp_obj.replace(RUNTIME_OBJ)
    return str(RUNTIME_OBJ)


def parse_test_file(path):
    """Extract expected output and code from a test file."""
    with open(path) as f:
        content = f.read()

    lines = content.split('\n')
    expect_lines = []
    code_start_idx = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#pragma'):
            code_start_idx = i + 1
            continue
        if stripped.startswith('//'):
            comment = stripped[2:].strip()
            if not expect_lines:
                expect_lines.append(comment)
                code_start_idx = i + 1
            elif comment.startswith('!') or comment.startswith('?') or comment.startswith('@'):
                if comment.startswith('!'):
                    comment = comment[1:]
                expect_lines.append(comment)
                code_start_idx = i + 1
            else:
                break
        elif stripped == '':
            if expect_lines:
                break
            code_start_idx = i + 1
        else:
            break

    if not expect_lines:
        return None, None, None, 'no_expect'

    expect_str = '\n'.join(expect_lines)

    # Check for runtime markers
    if '@python-only' in expect_str or '@python' in expect_str:
        return None, None, None, 'python_only'

    is_output = expect_str.startswith('!')
    if is_output:
        expect = expect_str[1:].strip().replace('\\n', '\n')
    else:
        expect = expect_str.strip()

    # Handle alternatives
    alternatives = None
    if '||' in expect:
        alternatives = [e.strip().replace('\\n', '\n') for e in expect.split('||')]
        if alternatives[0].startswith('!'):
            alternatives = [a[1:] if a.startswith('!') else a for a in alternatives]
        expect = alternatives[0]

    # "none" means parse-only test, no output expected
    if expect.lower() == 'none' and not is_output:
        return None, None, None, 'none_test'

    # Error tests (starts with ?) - we're only testing output correctness
    if not is_output:
        return None, None, None, 'error_test'

    code = '\n' * code_start_idx + '\n'.join(lines[code_start_idx:])
    return code, expect, alternatives, 'output'


def run_single_ssa_test(test_path, runtime_obj_path):
    """Run a single test through the SSA pipeline. Returns (test_path, status, detail)."""
    try:
        code, expect, alternatives, kind = parse_test_file(test_path)
        if kind != 'output':
            return (test_path, 'skip', kind)

        # Compile source to bytecode
        from parser import parse as fr_parse
        from compiler import compile_ast_to_bytecode

        ast = fr_parse(code, file=test_path)
        bytecode, _ = compile_ast_to_bytecode(ast)

        # Run through SSA pipeline
        from optimizer import compile_native_ssa
        try:
            asm = compile_native_ssa(bytecode, opt_level=2)
        except Exception as e:
            return (test_path, 'ssa_fail', str(e)[:200])

        # Write asm, assemble, link, run
        with tempfile.TemporaryDirectory() as tmpdir:
            asm_path = os.path.join(tmpdir, 'test.s')
            bin_path = os.path.join(tmpdir, 'test')

            with open(asm_path, 'w') as f:
                f.write(asm)

            # Assemble and link
            link_cmd = [
                'gcc', '-no-pie', '-o', bin_path, asm_path, runtime_obj_path,
                '-lm', '-lgmp',
                '-Wl,--gc-sections'
            ]
            result = subprocess.run(link_cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return (test_path, 'link_fail', result.stderr[:300])

            # Run
            result = subprocess.run(
                [bin_path], capture_output=True, text=True, timeout=5
            )
            actual = result.stdout.strip()

            # Compare
            expected_list = alternatives if alternatives else [expect]
            if any(actual == e.strip() for e in expected_list):
                return (test_path, 'pass', None)
            else:
                return (test_path, 'wrong', f'expected={repr(expect)}, got={repr(actual)}')

    except subprocess.TimeoutExpired:
        return (test_path, 'timeout', None)
    except Exception as e:
        return (test_path, 'error', f'{type(e).__name__}: {str(e)[:200]}')


def load_native_ignore_list():
    """Load tests that are known to not work on native from config.json."""
    config_path = REPO_ROOT / 'cases' / 'config.json'
    if not config_path.exists():
        return set()
    with open(config_path) as f:
        config = json.load(f)
    native_cfg = config.get('native', {})
    return set(native_cfg.get('ignore', []))


def main():
    import fnmatch

    # Ensure runtime is compiled
    print("Compiling runtime_lib.c...", flush=True)
    runtime_obj = ensure_runtime_object()

    # Collect tests
    test_files = sorted(glob.glob(str(REPO_ROOT / 'cases' / '**' / '*.fr'), recursive=True))
    print(f"Found {len(test_files)} test files", flush=True)

    # Load native ignore list
    ignore_patterns = load_native_ignore_list()

    # Filter out ignored tests
    filtered = []
    for t in test_files:
        rel = os.path.relpath(t, REPO_ROOT)
        # Extract category (first subdir under cases/)
        parts = rel.replace('cases/', '').split('/')
        category = parts[0] if len(parts) > 1 else ''
        skip = False
        for pattern in ignore_patterns:
            if category == pattern or fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(rel.replace('cases/', ''), pattern):
                skip = True
                break
        if not skip:
            filtered.append(t)

    print(f"Running {len(filtered)} tests (after native ignore filter)", flush=True)

    # Run in parallel
    workers = min(os.cpu_count() or 4, 16)
    results = {'pass': [], 'skip': [], 'wrong': [], 'ssa_fail': [], 'link_fail': [],
               'timeout': [], 'error': []}

    start = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_single_ssa_test, t, runtime_obj): t for t in filtered}
        done_count = 0
        total = len(futures)
        for future in as_completed(futures):
            done_count += 1
            test_path, status, detail = future.result()
            results[status].append((test_path, detail))
            if done_count % 20 == 0 or done_count == total:
                passed = len(results['pass'])
                failed = len(results['wrong']) + len(results['ssa_fail']) + len(results['link_fail']) + len(results['error'])
                print(f"\r[{done_count}/{total}] pass={passed} fail={failed} skip={len(results['skip'])}",
                      end='', flush=True)

    elapsed = time.time() - start
    print(f"\n\n{'='*60}")
    print(f"SSA Pipeline Test Results ({elapsed:.1f}s)")
    print(f"{'='*60}")

    total_run = len(results['pass']) + len(results['wrong']) + len(results['ssa_fail']) + \
                len(results['link_fail']) + len(results['timeout']) + len(results['error'])

    print(f"  Passed:      {len(results['pass'])}/{total_run}")
    print(f"  Wrong output: {len(results['wrong'])}")
    print(f"  SSA failure:  {len(results['ssa_fail'])}")
    print(f"  Link failure: {len(results['link_fail'])}")
    print(f"  Timeout:      {len(results['timeout'])}")
    print(f"  Error:        {len(results['error'])}")
    print(f"  Skipped:      {len(results['skip'])}")

    # Show failures grouped by category
    for category, label in [('wrong', 'WRONG OUTPUT'), ('ssa_fail', 'SSA COMPILE FAIL'),
                             ('link_fail', 'LINK FAIL'), ('error', 'ERROR'), ('timeout', 'TIMEOUT')]:
        items = results[category]
        if items:
            print(f"\n--- {label} ({len(items)}) ---")
            for path, detail in sorted(items)[:30]:
                rel = os.path.relpath(path, REPO_ROOT)
                if detail:
                    print(f"  {rel}: {detail[:120]}")
                else:
                    print(f"  {rel}")
            if len(items) > 30:
                print(f"  ... and {len(items) - 30} more")

    return 0 if not (results['wrong'] or results['ssa_fail'] or results['link_fail'] or results['error']) else 1


if __name__ == '__main__':
    sys.exit(main())
