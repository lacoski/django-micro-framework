import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="djangomicroframework",
    version="0.0.1a3",
    license='MIT',
    author="thanhnb",
    author_email="bathanhtlu@gmail.com",
    install_requires=[
        'django',
        'djangorestframework',
        'pyjwt',
        'redis',
        'hiredis'
    ],
    python_requires='>=3.6,<3.7',
    description="Micro framework for Django",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/lacoski/django-micro-framework",
    packages=setuptools.find_packages(exclude=['tests', 'tests.*', 'requirements']),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
