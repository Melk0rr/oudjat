""" Setup module """
from os.path import abspath, dirname, join
from setuptools import find_packages, setup

from oudjat import __version__

this_dir = abspath(dirname(__file__))

with open(join(this_dir, 'README.md'), encoding='utf-8') as f:
  long_description = f.read()

with open(join(this_dir, 'requirements.txt'), encoding='utf-8') as f:
  reqs = f.read().splitlines()

setup(
    name='oudjat',
    version=__version__,
    description='Online CERT security news gathering',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Melk0rr/Oudjat',
    author='me1k0r',
    author_email='runner-me1k0r@proton.me',
    classifiers=['Intended Audience :: Developers',
                 'Topic :: Utilities',
                 'License :: Public Domain',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.10', ],
    keywords='cli',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[reqs],
    include_package_data=True,
    entry_points={'console_scripts': ['oudjat=oudjat.cli:main', ], },
)
