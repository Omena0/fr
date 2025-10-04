from setuptools import setup, find_packages
import os

# Read version from environment variable (set by GitHub Actions)
version = os.environ.get('PACKAGE_VERSION', '0.0.0')

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='frscript',
    version=version,
    author='Omena0',
    description='Simple bytecode compiled C-style scripting language',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='PolyForm Noncommercial License 1.0.0',
    url='https://github.com/Omena0/fr',
    project_urls={
        'Bug Reports': 'https://github.com/Omena0/fr/issues',
        'Source': 'https://github.com/Omena0/fr',
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Interpreters',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'fr=src.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'src': ['*.c'],
    },
)
