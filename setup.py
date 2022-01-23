from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='CSCI6461Computer',
    version='0.1.0',
    description='Computer simulator for CSCI6461',
    long_description=readme,
    author='Ruojia Zhang, Changjia Yang, Yi Zheng, Guanyu Zuo',
    author_email='roger_zhang@gwu.edu',
    url='https://github.com/GWU-CS2021/CSCI6461',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)