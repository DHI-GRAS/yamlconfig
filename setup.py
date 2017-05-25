from setuptools import setup, find_packages

setup(
    name='yamlconfig',
    version='2.0',
    description='YAML config file parsing',
    author='Jonas Solvsteen',
    author_email='josl@dhi-gras.com',
    packages=find_packages(),
    install_requires=['ruamel.yaml', 'click'])
