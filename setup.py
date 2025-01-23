"""MAPIT: Material Accountancy Performance Indicator Toolkit.

See:
https://github.com/sandialabs/MAPIT
https://sandialabs.github.io/MAPIT/index.html
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="MAPIT",  # Required
    version="1.4.8-beta",  # Required
    author="Nathan Shoman",  # Optional
    author_email="nshoman@sandia.gov",  # Optional
    install_requires = ["matplotlib","numpy","Pillow","tqdm","scipy","pyside6","ray[default]"],
    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GPL3",
        "Programming Language :: Python :: 3.9"
    ],
    packages=find_packages(),  # Required
    include_package_data=True,
    python_requires=">3.8",
    project_urls={  # Optional
        "Data": "https://github.com/sandialabs/MAPIT-tools/",
        "Documents": "https://sandialabs.github.io/MAPIT/index.html",
        "Source": "https://github.com/sandialabs/MAPIT",
    },
    entry_points = {
        'console_scripts':[
            'MAPIT = MAPIT.GUI.MAPIT_main:launchMAPIT'
        ],
    },
)

