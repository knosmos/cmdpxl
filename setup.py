#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read()


setup(
    author="Jieruei Chang",
    author_email="jierueic@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="A totally practical command-line image editor",
    entry_points={
        "console_scripts": [
            "cmdpxl=cmdpxl.main:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords=["cmdpxl", "opencv", "image-editor", "terminal-based"],
    name="cmdpxl",
    packages=find_packages(include=["cmdpxl", "cmdpxl.*"]),
    url="https://github.com/knosmos/cmdpxl",
    version="0.1.1",
    zip_safe=False,
)
