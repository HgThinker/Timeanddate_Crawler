from setuptools import setup, find_packages
import sys

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

# with open('LICENSE', encoding='utf-8') as f:
#     license = f.read()

with open('requirements.txt', encoding='utf-8') as f:
    reqs = f.readlines()

setup(
    name = 'timeanddate_crawler',
    version='0.1.0',
    description='Timeanddate.com data crawler',
    long_description='readme',
    python_requires='>=3.9',
    package_dir={"": "src"},
    packages=find_packages(exclude=('data')),
    # install_requires=reqs.strip().split('\n'),
    install_requires=reqs,
)