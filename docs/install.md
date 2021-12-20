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

---

## Install procedure

### New to Python?
If you are new to Python the easiest way to get started is using a [Python IDE](https://wiki.python.org/moin/IntegratedDevelopmentEnvironments) like [Pycharm](https://www.jetbrains.com/pycharm/) or [Spyder](https://www.spyder-ide.org/), although an IDE is not required.

Further documentation on getting started with Python can be found [here](https://www.python.org/about/gettingstarted/).


### Requirements install
MAPIT relies on a number of third party libraries that must be installed before use. We have generated a list of [requirements](requirements.txt).

#### Pip
`pip install -r /path/to/requirements.txt`

#### Conda
`conda install -c conda-forge --file /path/to/requirements.txt`

> Pyside2 isn't available on the main conda channel, hence the use of conda-forge

---

That's it! Once the requirements are installed you should be able to open MAPIT using
 `python /path/to/script/MAPIT.py` (or alternatively launching through your IDE).
