import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='migvalidator',
    version='1.0',
    author='Gyojun An',
    author_email='sencom1028@gmail.com',
    description='Apache Hive and MariaDB(MySQL) conversion library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'impyla==0.17.0',
        'pandas==1.3.5',
        'numpy==1.21.4',
        'PyMySQL==1.0.2',
        'pandera==0.8.0',
        #'pyarrow==6.0.1',
    ],
    python_requires='>=3.0',
)