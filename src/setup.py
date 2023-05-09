#!/usr/bin/env python3

import setuptools

install_requires = [
    "docker",
    "click",
    "paramiko",
]

setuptools.setup(
    name="swarmify",
    version="1.1",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    entry_points={
        "console_scripts": ["swarmify = main:service"],
    },
    include_package_data=True,
)
