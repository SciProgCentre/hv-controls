#!/usr/bin/python

import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mipt-npm-hv-controls",
    version="0.2.2",
    author="NPM Group",
    author_email="mihail.zelenyy@phystech.edu",
    url='https://npm.mipt.ru/',
    description="Simple GUI for HV controls",
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="hv",
    packages= setuptools.find_packages(),
    entry_points = {
      "gui_scripts" : [
          "hv-controls = hv.run:app"
      ]
    },
    package_data = {
        "hv" : ["data/*", "device_data/*"],
        "hv.ui" : ["resources/*", "resources/fonts/roboto/*"]
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    project_urls={
        "Bug Tracker": "https://github.com/mipt-npm/hv-controls",
        "Documentation": "https://github.com/mipt-npm/hv-controls",
        "Source Code": "https://github.com/mipt-npm/hv-controls",
    },
    install_requires=[
        "pyqt5",
        "pyftdi",
        # "ftd2xx",
        "matplotlib",
        "Jinja2"
    ],
    python_requires=">=3.7"
)
