# Installation

## Code overview
The current implementation of MAPIT is largely a GUI-based tool that is based on a few key Python scripts:

> `MAPIT.py` - The main GUI file that ties everything together
> <br>
> `ScenarioSelector.py` - Code associated with the included dataset exploration and interaction
> <br>
> `IOWizardMat.py` - Script responsible for reading MATLAB `.mat` file extensions
> <br>
> `IOWizard.py` - Script responsible for reading `.csv` file extensions
> <br>
> `StatsPackage.py` - Script containing functions pertaining to error propagation and statistics tests

Currently MAPIT is only being distributed through this repository as a series of scripts. Internal testing has used [PyInstaller](https://www.pyinstaller.org/) to generate standalone executables. However, given the level of development to take MAPIT out of beta this strategy is not currently being pursued.

## Install procedure

### New to Python?
If you are new to Python the easiest way to get started is using a [Python IDE](https://wiki.python.org/moin/IntegratedDevelopmentEnvironments) like [Pycharm](https://www.jetbrains.com/pycharm/) or [Spyder](https://www.spyder-ide.org/), although an IDE is not required.

Further documentation on getting started with Python can be found [here](https://www.python.org/about/gettingstarted/).


### Requirements install
MAPIT relies on a number of third party libraries that must be installed before use. We have generated a list of [requirements](requirements.txt). Install these requirements from inside your environment using `pip install -r /path/to/requirements.txt`.

That's it! Once the requirements are installed you should be able to open MAPIT using
 `python /path/to/script/MAPIT.py`
