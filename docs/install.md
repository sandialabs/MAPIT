# Installation

## Code overview
The current implementation of MAPIT is largely a GUI-based tool that is based on a few key Python scripts:

* `MAPIT.py` - The main GUI file that ties everything together

* `ScenarioSelector.py` - Code associated with the included dataset exploration and interaction
* `IOWizardMat.py` - Script responsible for reading MATLAB `.mat` file extensions

* `IOWizard.py` - Script responsible for reading `.csv` file extensions

* `StatsPackage.py` - Script containing functions pertaining to error propagation and statistics tests

Currently MAPIT is only being distributed through this repository as a series of scripts. Internal testing has used [PyInstaller](https://www.pyinstaller.org/) to generate standalone executables. However, given the level of development to take MAPIT out of beta this strategy is not currently being pursued.

## Install procedure

### New to Python?
If you are new to Python the easiest way to get started is using a [Python IDE](https://wiki.python.org/moin/IntegratedDevelopmentEnvironments) like [Pycharm](https://www.jetbrains.com/pycharm/) or [Spyder](https://www.spyder-ide.org/), although an IDE is not required.

Further documentation on getting started with Python can be found [here](https://www.python.org/about/gettingstarted/).

Note Currently Anaconda does not have the needed version of module PySide2 so a separate python version with a pip environment will be required. 
A python3 environment will be required to run this code here is some documents on setting up a specific environment on various systems:
Mac: https://medium.com/random-life-journal/set-up-python-environment-correctly-on-mac-db97e481dc5a#:~:text=Set%20up%20Python%20environment%20correctly%20on%20Mac%201,virtual%20environment%20for%20each%20project%20or%20repository.%20
Windows: https://www.freecodecamp.org/news/installing-multiple-python-versions-on-windows-using-virtualenv/#:~:text=Installing%20Multiple%20Python%20Versions%20on%20Windows%20Using%20Virtualenv.,create%20a%20virtualenv%2C%20open%20Command%20Prompt%20and%20
	tip: if you already have anaconda installed on windows, in your environment variables place the the path to your python3 folder above and your computer will by default load the python3 environment needed to run this code. 
Linux: https://medium.datadriveninvestor.com/how-to-install-and-manage-multiple-python-versions-on-linux-916990dabe4b

### Requirements install
MAPIT relies on a number of third party libraries that must be installed before use. We have generated a list of [requirements](requirements.txt). Install these requirements from inside your environment using `pip install -r /path/to/requirements.txt`.

That's it! Once the requirements are installed you should be able to open MAPIT using
 `python /path/to/script/MAPIT.py`
