
from os.path import join, dirname
from setuptools import setup


setup(
    name='memspacespy',
    version='0.0.1',

    description='a python library for shared memory tuple spaces',
#    long_description=open(join(dirname(__file__), 'README.md')).read(),

    packages=[
        'memspaces',
    ],

    install_requires=[
        'posix_ipc',
    ],

    test_suite='tests',
    tests_require=[
        'pytest',
    ],

    setup_requires=['pytest_runner'],
)

