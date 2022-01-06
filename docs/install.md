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

#### Downloading MAPIT

Download MAPIT from the main [page](https://github.com/sandialabs/MAPIT) by clicking the green code box, and selecting download ZIP. Then, unzip the folder to a location of your choice.

#### Installing Anaconda
We recommend installing [Anaconda](https://www.anaconda.com/) to streamline the installation of packages required for MAPIT. Anaconda is a easy and convenient way to manage environments. Environments contain collections of Python packages that are separate from other environments. This can be particularly useful if you need different versions of Python packages for compatibility purposes. More information on environments can be found [here](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html).

:pushpin: Start by installing Anaconda, which can be found [here](https://www.anaconda.com/products/individual). Most platforms have graphical installers which will guide you through the installation.



**After installing Anaconda**, continue with the instructions below. If you're comfortable with command-line interface, skip to the next section titled "Command line instructions".

##### Graphical User Interface instructions
This guide uses the Anaconda Navigator. Further details and information can be found on [Anaconda's page](https://docs.anaconda.com/anaconda/navigator/overview/).


1. Start by opening Anaconda Navigator. The image should look similar to what is shown below.
  * This may or may not be listed in your computer's installed applications
  * If not listed in applications, then start by opening a terminal (Mac/Linux) or command prompt (Windows).
    * Run the command `conda anaconda-navigator`

![](https://docs.anaconda.com/_images/nav-defaults1.png)


2. Create a new environment and install the required packages.
  * Click the `Environments` tab on the left side
  * Click the `Import` button near the bottom
  * Select the `requirements.yml` file from the downloaded MAPIT folder
        * The new environment will automatically be named `MAPIT_env`, which can be changed if desired
  * Click `Import`
  * Allow time for packages to be installed



3. Install a graphical environment
  * Navigate home by clicking on the `Home` button located on the left side
  * Find the application named `Spyder` and install

> :tada: Everything needed to run MAPIT is installed


4. Launch Spyder from the home tab.

> :exclamation: It's important that Spyder is launched from the correct environment. This can be checked at the top of Anaconda Navigator where it says `Applications on` and the correct environment from step 2 should be selected.

###### Opening MAPIT

5. Open `MAPIT.py` in Spyder.
  * This can be done using File > Open or by dragging and dropping the file


6. Run MAPIT by pressing the green triangle on the command bar or pressing F5.
  * A one time prompt (run settings) will show.
  * Make sure the first set of options labeled `Console` has `Execute in an external system terminal` is selected.
        * MAPIT cannot be executed in an IPython console, the default option
  * If you need to see this prompt again after closing, navigate to Run > Configuration per file (alternatively, press Ctrl+F6).

MAPIT should successfully start.

##### Command line instructions

1. Start by accessing conda:
  * **Windows**: Open the program called `Anaconda Prompt`.
  * **Mac/Linux**: Open a terminal.





2. Start by creating a new environment by running the command `conda create --name myenv`
  * Replace `myenv` in the command with a name you prefer. For example `conda create --name MAPIT_run`


3. Activate the new environment by running the command `conda activate myenv` where `myenv` is the name you used in step 1.
  * Your prompt should now have (myenv) in front of the current line.


4. Install the requirements included in the MAPIT, `requirements.txt` using the command `conda install -c conda-forge --file /path/to/requirements.txt`
  * The `/path/to/requirements.txt` changes based on where your MAPIT folder is.
  * For example, one possible location might be `/home/User/Documents/MAPIT/requirements.txt`


5. Follow the on screen prompts to install packages.


> :tada: All of the requirements are now installed.

###### Running MAPIT
6. Ensure the correct environment is activated (step 3).


7. Run MAPIT by entering the command `python /path/to/MAPIT.py`
  * The path will change based where your MAPIT folder is
  * One possible location might be `/home/User/Documents/MAPIT/src/MAPIT.py`



> :exclamation: Opening a new terminal/prompt will cause conda to start in the base environment. You will need to change to the relevant MAPIT environment using `conda activate myenv` where `myenv` is the environment name.
