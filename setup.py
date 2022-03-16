#!/usr/bin/env python3


from setuptools import find_packages, setup

setup(
    name="redirect",
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Pyramid",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Typing :: Typed",
    ],
    packages=find_packages(exclude=["tests.*"]),
    entry_points={
        "paste.app_factory": [
            "main = redirect:main",
        ],
    },
    package_data={"tilecloud_chain": ["py.typed"]},
)
