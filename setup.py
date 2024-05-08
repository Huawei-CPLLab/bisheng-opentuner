#!/usr/bin/python
try:
    from setuptools import setup
except ImportError:
    try:
        from setuptools.core import setup
    except ImportError:
        from distutils.core import setup

try:
    from pypandoc import convert_file

    read_md = lambda f: convert_file(f, 'rest')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

import os
from importlib.util import cache_from_source
from setuptools.command.build_py import build_py


class BuildPyCommand(build_py):
    """ Extend build_py and ask it to generate .pyc files. """

    def run(self):
        self.compile = True
        build_py.run(self)
        # Replace original .py files with the corresponding .pyc files.
        # This should be the same as calling compileall.compiledir in
        # legacy mode.
        files = build_py.get_outputs(self)
        for pyfile in files:
            if pyfile[-3:] == '.py':
                cfile = cache_from_source(pyfile)
                print("Moving {!s} to {!s}".format(cfile, pyfile + "c"))
                os.rename(cfile, pyfile + "c")
                print("Deleting {!s}".format(pyfile))
                os.remove(pyfile)


required = open('requirements.txt').read().splitlines()
required = [l.strip() for l in required
            if l.strip() and not l.strip().startswith('#')]


setup(
    name='bisheng-opentuner',
    version='0.8.8.1',
    url='https://github.com/Huawei-CPLLab/bisheng-opentuner',
    license='MIT',
    author='Jason Ansel',
    author_email='jansel@jansel.net',
    description='An extensible framework for program autotuning',
    long_description=read_md('README.md'),
    packages=['opentuner', 'opentuner.resultsdb', 'opentuner.utils',
              'opentuner.measurement', 'opentuner.search'],
    install_requires=required,
    cmdclass = {
        'build_py' : BuildPyCommand,
    },
)
