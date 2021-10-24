import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="migvalidator",
    version="0.0.1",
    author="Gyojun An",
    author_email="sencom1028@gmail.com",
    description="database migration validator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Altera520/migvalidator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)