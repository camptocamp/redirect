#!/usr/bin/env python3


from setuptools import find_packages, setup

setup(
    name="redirect",
    packages=find_packages(exclude=["tests.*"]),
    entry_points={
        "paste.app_factory": [
            "main = redirect:main",
        ],
    },
)
