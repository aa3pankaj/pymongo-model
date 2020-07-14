import setuptools

with open('README.md') as file: 
    long_description = file.read() 

REQUIREMENTS = ['jsondiff','pymongo'] 

setuptools.setup(
    name="pymongo-model",
    version="1.0.1",
    author="Pankaj Singh",
    author_email="aa3pankaj@gmail.com",
    description="Simple pymongo document model",
    long_description=long_description,
    url="https://github.com/aa3pankaj/pymongo-model",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS, 
    python_requires='>=3.6',
)