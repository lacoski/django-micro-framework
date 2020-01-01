import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

extras_require = {
    'test': [
        'cryptography',
        'pytest-cov',
        'pytest-django',
        'pytest-xdist',
        'pytest',
        'tox',
    ],
    'lint': [
        'flake8',
        'pep8',
        'isort',
    ],
    'doc': [
        'Sphinx>=1.6.5,<2',
        'sphinx_rtd_theme>=0.1.9',
    ],
    'dev': [
        'bumpversion>=0.5.3,<1',
        'pytest-watch',
        'wheel',
        'twine',
        'ipython',
    ],
    'python-jose': [
        'python-jose==3.0.0',
    ],
}

extras_require['dev'] = (
    extras_require['dev'] +  # noqa: W504
    extras_require['test'] +  # noqa: W504
    extras_require['lint'] +  # noqa: W504
    extras_require['doc'] +  # noqa: W504
    extras_require['python-jose']
)


setuptools.setup(
    # Replace with your own username
    name="djangomicroframework",
    # version 
    version="0.0.1",
    license='MIT',
    author="thanhnb",
    author_email="bathanhtlu@gmail.com",
    install_requires=[
        'django',
        'djangorestframework',
        'pyjwt',
    ],
    python_requires='>=3.6,<3.9',
    extras_require=extras_require,
    description="Micro framework for Django",
    long_description=long_description,
    url="https://github.com/lacoski",
    packages=setuptools.find_packages(exclude=['tests', 'tests.*', 'requirements']),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)