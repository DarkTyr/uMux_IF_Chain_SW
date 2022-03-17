from setuptools import setup, find_packages

setup(
    name='uMux_IF_Chain_SW',
    version='0.0.0',
    packages=find_packages(),
    install_requires=[
        'pyserial',
    ],
)