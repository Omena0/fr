"""
Setup script for frscript with C runtime compilation
"""
import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from setuptools.command.develop import develop


class BuildCRuntime(build_ext):
    """Custom build command to compile the C runtime VM"""
    
    def run(self):
        """Build the C VM runtime"""
        # First run the standard build_ext
        super().run()
        
        # Determine the runtime directory
        runtime_dir = Path(__file__).parent / 'runtime'
        
        if not runtime_dir.exists():
            print("Warning: runtime directory not found, skipping C VM build")
            return
        
        vm_source = runtime_dir / 'vm.c'
        if not vm_source.exists():
            print("Warning: vm.c not found, skipping C VM build")
            return
        
        print("=" * 70)
        print("Building C VM runtime...")
        print("=" * 70)
        
        # First try using make if Makefile exists
        makefile = runtime_dir / 'Makefile'
        if makefile.exists():
            try:
                subprocess.run(['make', '--version'], capture_output=True, check=True)
                print("Using Makefile to build VM...")
                subprocess.run(['make'], cwd=str(runtime_dir), check=True)
                vm_output = runtime_dir / 'vm'
                if vm_output.exists():
                    print(f"✓ Successfully built C VM runtime using make: {vm_output}")
                    print("=" * 70)
                    return
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("Make failed or not found, falling back to manual compilation...")
        
        # Try to get Python config for embedding
        try:
            python_config = 'python3-config'
            cflags_result = subprocess.run(
                [python_config, '--cflags', '--embed'],
                capture_output=True,
                text=True
            )
            if cflags_result.returncode != 0:
                # Fall back to non-embed version
                cflags_result = subprocess.run(
                    [python_config, '--cflags'],
                    capture_output=True,
                    text=True,
                    check=True
                )
            python_cflags = cflags_result.stdout.strip()
            
            ldflags_result = subprocess.run(
                [python_config, '--ldflags', '--embed'],
                capture_output=True,
                text=True
            )
            if ldflags_result.returncode != 0:
                ldflags_result = subprocess.run(
                    [python_config, '--ldflags'],
                    capture_output=True,
                    text=True,
                    check=True
                )
            python_ldflags = ldflags_result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: python3-config not found, using minimal flags")
            python_cflags = f"-I{sys.prefix}/include/python{sys.version_info.major}.{sys.version_info.minor}"
            python_ldflags = f"-L{sys.prefix}/lib -lpython{sys.version_info.major}.{sys.version_info.minor}"
        
        # Compile the VM
        cc = os.environ.get('CC', 'gcc')
        vm_output = runtime_dir / 'vm'
        
        compile_cmd = [
            cc,
            '-Wall', '-Wextra', '-O3', '-std=c11',
            '-march=native', '-flto', '-ffast-math',
            '-funroll-loops', '-finline-functions',
            '-fomit-frame-pointer',
        ] + python_cflags.split() + [
            '-o', str(vm_output),
            str(vm_source),
            '-lm', '-lgmp', '-flto'
        ] + python_ldflags.split()
        
        print(f"Compiling: {' '.join(compile_cmd)}")
        
        try:
            subprocess.run(compile_cmd, check=True, cwd=str(runtime_dir))
            print(f"✓ Successfully built C VM runtime: {vm_output}")
            
            # Make sure the VM is executable
            import stat
            if vm_output.exists():
                vm_output.chmod(vm_output.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                print("✓ Set executable permissions on VM")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to build C VM runtime: {e}")
            print("The package will still install, but C VM features may not work.")
            print("You can build it manually later with: cd runtime && make")
        except FileNotFoundError:
            print(f"✗ Compiler '{cc}' not found")
            print("Please install a C compiler (gcc or clang)")
            print("The package will still install, but C VM features may not work.")
        
        print("=" * 70)


class CustomInstall(install):
    """Custom install to trigger C runtime build"""
    
    def run(self):
        # Build the C runtime
        self.run_command('build_ext')
        # Run standard install
        super().run()


class CustomDevelop(develop):
    """Custom develop install to trigger C runtime build"""
    
    def run(self):
        # Build the C runtime
        self.run_command('build_ext')
        # Run standard develop
        super().run()


# Run setup
if __name__ == '__main__':
    setup(
        cmdclass={
            'build_ext': BuildCRuntime,
            'install': CustomInstall,
            'develop': CustomDevelop,
        },
    )
