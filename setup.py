#!/usr/bin/env python

from setuptools import setup

setup(
    name="custom_games",
    version='0.2.7',
    author='gradiuscypher',
    author_email='gradiuscypher@gmail.com',
    license='MIT',
    description="Libraries for managing LoL custom tournaments.",
    packages=['lol_customs'],
    install_requires=['requests', 'sqlalchemy']
)
