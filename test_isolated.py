#!/usr/bin/env python3
"""
Isolated test runner - runs each test in a separate subprocess
"""
import sys
import subprocess
import os
import glob

def run_test_isolated(filename, content):
    """Run a single test in a subprocess"""
    script = f'''
import sys, os, tempfile, subprocess
from io import StringIO
sys.path.insert(0, 'src')
sys.argv.append('-d')

from parser import parse
from compiler import compile_ast_to_bytecode  
from runtime import run

content = """{content.replace('"', '\\"')}"""
expect, case = content.split("\\n", 1)
expect = expect.replace("//", "").strip()
case = "\\n" + case

is_output = expect.startswith("!")
if is_output:
    expect = expect[1:].strip().replace("\\\\n", "\\n")

try:
    ast = parse(case)
except Exception as e:
    print("PARSE_ERROR")
    sys.exit(0)

# Python
old_stdout = sys.stdout
sio = StringIO()
sys.stdout = sio
try:
    run(ast)
    py_out = sio.getvalue().strip()
finally:
    sys.stdout = old_stdout

# C VM
bc = compile_ast_to_bytecode(ast)
with tempfile.NamedTemporaryFile(mode='w', suffix='.bc', delete=False) as f:
    bcf = f.name
    f.write(bc)
result = subprocess.run(['runtime/vm', bcf], capture_output=True, text=True, timeout=5)
os.unlink(bcf)
vm_out = result.stdout.strip() if result.returncode == 0 else "None"

print(f"PY:{{py_out}}")
print(f"VM:{{vm_out}}")
print(f"EX:{{expect}}")
'''
    
    result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True, timeout=10, cwd='/home/runner/work/fr/fr')
    lines = result.stdout.strip().split('\n')
    
    py_out = vm_out = expect = ""
    for line in lines:
        if line.startswith("PY:"):
            py_out = line[3:]
        elif line.startswith("VM:"):
            vm_out = line[3:]
        elif line.startswith("EX:"):
            expect = line[3:]
    
    return {
        'file': filename,
        'py_ok': py_out == expect,
        'vm_ok': vm_out == expect,
        'py_out': py_out,
        'vm_out': vm_out,
        'expect': expect
    }

if __name__ == '__main__':
    os.chdir('/home/runner/work/fr/fr')
    
    tests = {}
    for path in sorted(glob.glob('cases/*.fr')):
        name = os.path.basename(path)
        with open(path) as f:
            tests[name] = f.read()
    
    print(f"Running {len(tests)} tests with isolation...")
    
    results = []
    for name, content in tests.items():
        results.append(run_test_isolated(name, content))
    
    py_pass = sum(1 for r in results if r['py_ok'])
    vm_pass = sum(1 for r in results if r['vm_ok'])
    
    for r in results:
        if not r['vm_ok']:
            print(f"❌ {r['file']} [C VM]: {repr(r['vm_out'])} != {repr(r['expect'])}")
    
    print(f"\nPython: {py_pass}/{len(tests)}")
    print(f"C VM: {vm_pass}/{len(tests)}")
    
    sys.exit(0 if vm_pass == len(tests) else 1)
