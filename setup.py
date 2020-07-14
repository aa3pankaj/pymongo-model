import setuptools

with open('README.md') as file: 
    long_description = file.read() 

REQUIREMENTS = ['jsondiff','pymongo'] 

setuptools.setup(
    name="pymongo-model",
    version="1.0.6",
    author="Pankaj Singh",
    author_email="aa3pankaj@gmail.com",
    description="Simple model based usage of pymongo, also provides optional feature for tracking mongoDB document history",
    long_description=long_description,
    long_description_content_type='text/markdown',
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