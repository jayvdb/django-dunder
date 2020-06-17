import io
import os
import re
import sys

from setuptools import setup, find_packages

PATH_BASE = os.path.dirname(__file__)
PACKAGE_NAME = 'django-dunder'
PACKAGE_DIR = 'django_dunder'

def read_file(fpath):
    """Reads a file within package directories."""
    with io.open(os.path.join(PATH_BASE, fpath)) as f:
        return f.read()


def get_version():
    """Returns version number, without module import (which can lead to
    ImportError if some dependencies are unavailable before install."""
    contents = read_file(os.path.join(PACKAGE_DIR, '__init__.py'))
    version = re.search('VERSION = \(([^)]+)\)', contents)
    version = version.group(1).replace(', ', '.').strip()
    return version


setup(
    name=PACKAGE_NAME,
    version=get_version(),
    url='http://github.com/jayvdb/' + PACKAGE_NAME,

    description='Reusable Django app to automate dunders `__repr__` and `__str__`',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',

    author='John Mark Vandenberg',
    author_email='jayvdb@gmail.com',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    test_suite=PACKAGE_DIR + '.tests',
    tests_require=[
        'pytest-djangoapp',
        'django-fake-model',
        'django-nine',
    ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
