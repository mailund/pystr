"""Package implementing various string algorithms in python."""

from setuptools import find_packages, setup

setup(
    name='pystr',
    version='0.0.1',
    url="http://github.com/mailund/pystr",
    author="Thomas Mailund",
    author_email="thomas@mailund.dk",
    packages=find_packages(),
    package_data={
        'pystr': ['py.typed'],
    },
    install_requires=[],
)
