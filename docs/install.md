# Installation

---

## Code overview
The current implementation of MAPIT is largely a GUI-based tool that is based on a few key Python scripts:

* `MAPIT.py` - The main GUI file that ties everything together

* `ScenarioSelector.py` - Code associated with the included dataset exploration and interaction
* `IOWizardMat.py` - Script responsible for reading MATLAB `.mat` file extensions

* `IOWizard.py` - Script responsible for reading `.csv` file extensions

* `StatsPackage.py` - Script containing functions pertaining to error propagation and statistics tests

> :information_source: Currently MAPIT is only being distributed through this repository as a series of scripts. Internal testing has used [PyInstaller](https://www.pyinstaller.org/) to generate standalone executables. MAPIT may be (optionally) distributed as an executable in the future.

> :exclamation: This guide does not cover proxy and SSL certificate configuration, which may be in place due to organizational policies. If applicable, please find guidance for these topics before installing MAPIT.

---

## Install procedure

### Experienced Python users
1. Download the master code branch from github.

2. Ensure the list of [requirements](requirements.txt) are installed into your environment.
  * pip: `pip install -r /path/to/requirements.txt`
  * conda: `conda install -c conda-forge --file /path/to/requirements.txt`
        * conda-forge is a required install channel for the required Pyside2 version


3. Launch MAPIT by running the main MAPIT file, `MAPIT.py`

### New to Python?
Python is an object-oriented programming language that is often used for scripting and application deployment. "Python" generally refers to the language interpreter and standard library. A more detailed introduction to Python can be found [here](https://docs.python.org/3/tutorial/index.html).

MAPIT relies on a several Python packages, which are outlined defined in the [requirements](requirements.txt) file. These packages provide additional functionality that do not come with the Python standard library and must be installed.

We recommend using the included install scripts to make sure MAPIT requirements are installed correctly.



#### 1. Downloading MAPIT

Download MAPIT from the main [page](https://github.com/sandialabs/MAPIT) by clicking the green code box, and selecting download ZIP. Then, unzip the folder to a location of your choice.

#### 2. Installing Anaconda
We recommend installing [Anaconda](https://www.anaconda.com/) to streamline the installation of packages required for MAPIT. Anaconda is a easy and convenient way to manage environments. Environments contain collections of Python packages that are separate from other environments. This can be particularly useful if you need different versions of Python packages for compatibility purposes. More information on environments can be found [here](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html).



#### 3. Finishing steps
:exclamation: Anaconda is required when using the install scripts

We have included scripts for both Windows and UNIX systems to prepare an environment to run MAPIT and install MAPIT.

Install the environment for MAPIT by running the install script for your system:
* Windows: Double click the `install.bat` located in `\path\to\MAPIT\windows_scripts`
* Linux: Run `bash install.sh` located in `/path/to/MAPIT/unix_scripts`
    * Ensure you run your terminal in the `unix_setup` folder


## FAQ's


* Having trouble? Try removing MAPIT and trying again.
    * Windows: Double click the `remove_MAPIT.bat`
    * Linux: Run `bash remove_MAPIT.sh` in a terminal

* Getting an "unrecognized app" error on windows? (see below)

<p align="center">
<img src="./assets/codeAssets/error1.png" width="50%" height="50%">
</p>

* You can continue by pressing `more info` (shown in the red box) and pressing `run anyways`
    * :exclamation: :exclamation: Note that you Generally shouldn't run scripts from unknown sources. You can verify the actions of these scripts by looking at the raw code. These scripts create a conda environment with the requirements described in `requirements.yml`.
