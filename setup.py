#!/usr/bin/python

import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hv-controls",
    version="0.0.1",
    author="NPM Group",
    author_email="mihail.zelenyy@phystech.edu",
    url='http://npm.mipt.ru/',
    description="Simple GUI for HV controls",
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="hv",
    packages=setuptools.find_packages(),
    entry_points = {
      "console_scripts" : [
          "hv-controls-cmd = hv.run:hv_controls_cmd",
          "hv-controls-qt = hv.run:hv_controls_qt",
      ]
    },
    package_data = { "hv" : ["data/*", "device_data/*"]},
    include_package_data = True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    # project_urls={
    #     "Bug Tracker": "",
    #     "Documentation": "",
    #     "Source Code": "",
    # },
    install_requires=[
        "pyqt5",
        "pyftdi",
        "ftd2xx"
    ]
)
