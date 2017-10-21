# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
import dtceverywhere

setup(
    name=dtceverywhere.__appname__,
    version=dtceverywhere.__version__,
    packages=find_packages(),
    author="rezemika",
    author_email="reze.mika@gmail.com",
    description="Un lecteur hors-ligne en CLI pour les citations de DansTonChat.",
    long_description=open('README.md').read(),
    install_requires=["bs4", "configobj", "humanfriendly", "peewee", "requests"],
    include_package_data=True,
    url='http://github.com/rezemika/danstonchat_everywhere',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment :: Fortune Cookies",
    ],
    entry_points = {
        "console_scripts": [
            "dtceverywhere = dtceverywhere.main:main",
        ],
    },
)
