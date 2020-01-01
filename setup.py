import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    # Replace with your own username
    name="djangomicroframework",
    # version 
    version="0.0.1",
    author="thanhnb",
    author_email="bathanhtlu@gmail.com",
    install_requires=[
        'django',
        'djangorestframework',
        'pyjwt',
    ],
    python_requires='==3.6',
    description="Micro framework for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lacoski",
    packages=setuptools.find_packages(exclude=['tests', 'tests.*', 'requirements']),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)