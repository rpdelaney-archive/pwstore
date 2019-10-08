# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pwstore",
    description="a command-line password manager",
    long_description=long_description,
    version="0.15",
    url="https://github.com/rpdelaney/pwstore",
    author="Ryan Delaney",
    author_email="ryan.delaney@gmail.com",
    license="GPL3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",  # noqa E501
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="security",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=[
        "python-gnupg",
        "dulwich",
        "Click",
        "appdirs",
        "PyQRCode",
        "Pillow",
        "pypng",
        "pyperclip",
        "PyAutoGUI",
    ],
    extras_require={"test": ["pytest", "pytest-mock", "pytest-cov"]},
    entry_points={"console_scripts": ["pwstore=pwstore.__init__:main"]},
)
