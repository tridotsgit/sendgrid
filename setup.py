# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='sendgrid_integration',
    version=version,
    description='Later',
    author='Semilimes Ltd.',
    author_email='alexander.melkoff@semilimes.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
