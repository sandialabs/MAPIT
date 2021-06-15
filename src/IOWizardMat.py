"""
    Reads in external .mat files
"""


from PySide2 import QtCore, QtWidgets, QtGui
import time
import numpy as np
import os
import glob
import sys
from scipy.io import loadmat
from pathlib import Path


class IOWizardMainMat(QtWidgets.QWizard):
  """
        Base class for IOWizard (.mat)
  """

  def __init__(self, parent=None):
    super(IOWizardMainMat, self).__init__()
    self.addPage(IntroPage(self))
    self.addPage(InitPage(self))
    self.addPage(DirPage(self))

    self.setWindowTitle("Data IO Wizard")
    self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
    self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.SavePages)

    x = str(Path(os.getcwd()).parents[0])
    F = os.path.join(x, 'assets', 'codeAssets', 'SNL_Horizontal_Black.jpg')
    res = QtGui.QPixmap(F)
    res = res.scaledToWidth(500)
    self.setPixmap(QtWidgets.QWizard.BannerPixmap, res)

    geometry = qApp.desktop().availableGeometry(self)
    self.setFixedSize(500, geometry.height() * 0.5)

    #initalize some variables
    self.MatDir = {}
    self.EleVec_IN = {}
    self.TempVec_IN = {}
    self.InKMP = {}
    self.InvKMP = {}
    self.OutKMP = {}
    self.InKMP_names = {}
    self.InvKMP_names = {}
    self.OutKMP_names = {}
    self.TimeUnitVec = {}
    self.MassUnitVec = {}
    self.IsMatV = 1  #imported data is a .mat

  def SavePages(self):
    """
            Function that performs the handoff
            between this IOWizard and the
            main part of MAPIT
    """

    self.MatDir = self.page(2).MatDirDisp.text()

    self.EleVec_IN = self.page(1).EleVec.text()
    self.TempVec_IN = self.page(1).TimeUnitVec.text()

    #infer number of KMPs by loading a mat
    #assumes the inp, inv, out all track same # of elements

    Z = loadmat(self.MatDir)
    self.InKMP = np.shape(Z['in']['data'][0])[0]
    self.InvKMP = np.shape(Z['invn']['data'][0])[0]
    self.OutKMP = np.shape(Z['outn']['data'][0])[0]

    self.InKMP_names = self.page(1).InpLabels.text()
    self.InvKMP_names = self.page(1).InvLabels.text()
    self.OutKMP_names = self.page(1).OutLabels.text()

    self.TimeUnitVec = self.page(1).TimeUnitVec.text()
    self.MassUnitVec = self.page(1).MassUnitVec.text()


class IntroPage(QtWidgets.QWizardPage):
  """
        Introduction page that (briefly) describes
        to users the format expected for the .mat
        files
  """

  def __init__(self, parent=None):
    super(IntroPage, self).__init__()
    self.IntroTxt = QtWidgets.QLabel(
        "This is a special wizard for "
        " importing data stored in MATLAB .mat format. It also "
        " has some unique capabilities to handle non-uniform sampling "
        " and structured MATLAB outputs with varying sample times. "
        "Note that this tool expects that the inputs (in) "
        ", inventories (invn) and outputs (outn) are all in a single directory"
        "with a single .mat file")
    self.IntroTxt.setWordWrap(1)
    self.setSubTitle('   ')

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.IntroTxt)
    self.setLayout(layout)


class InitPage(QtWidgets.QWizardPage):
  """
        Creates the first page seen that collects
        some optional data that can help the plots
        and (future) exported data labels look
        better
  """

  def __init__(self, parent=None):
    super(InitPage, self).__init__()
    self.setSubTitle('    ')

    layout = QtWidgets.QVBoxLayout(self)

    ReqForms = QtWidgets.QGroupBox(self)
    OptForms = QtWidgets.QGroupBox(self)

    #unlike the .csv import the .mat import doesn't require
    #any inputs as the format that's required can be used
    #to infer all necessary parameters

    ReqForms.setTitle("Required Inputs")
    OptForms.setTitle("Optional Inputs")

    layoutR = QtWidgets.QGridLayout(ReqForms)
    layoutO = QtWidgets.QGridLayout(OptForms)

    layout.addWidget(ReqForms)
    layout.addWidget(OptForms)

    self.EleVec = QtWidgets.QLineEdit(self, "")
    layoutO.addWidget(self.EleVec, 0, 1)

    self.EleTxt = QtWidgets.QLabel("Enter the elemental ordering", self)
    layoutO.addWidget(self.EleTxt, 0, 0)

    self.TimeUnitVec = QtWidgets.QLineEdit(self, "")
    layoutO.addWidget(self.TimeUnitVec, 1, 1)

    self.MassUnitVec = QtWidgets.QLineEdit(self, "")
    layoutO.addWidget(self.MassUnitVec, 2, 1)

    self.TimeUnitTxt = QtWidgets.QLabel("Enter the temporal units", self)
    layoutO.addWidget(self.TimeUnitTxt, 1, 0)

    self.MassUnitTxt = QtWidgets.QLabel("Enter the mass units", self)
    layoutO.addWidget(self.MassUnitTxt, 2, 0)

    self.InpLabels = QtWidgets.QLineEdit(self, "")
    self.InpLabelsTxt = QtWidgets.QLabel("Enter input labels")

    layoutO.addWidget(self.InpLabels, 3, 1)
    layoutO.addWidget(self.InpLabelsTxt, 3, 0)

    self.InvLabels = QtWidgets.QLineEdit(self, "")
    self.InvLabelsTxt = QtWidgets.QLabel("Enter inventory labels")

    layoutO.addWidget(self.InvLabels, 5, 1)
    layoutO.addWidget(self.InvLabelsTxt, 5, 0)

    self.OutLabels = QtWidgets.QLineEdit(self, "")
    self.OutLabelTxt = QtWidgets.QLabel("Enter output labels")

    layoutO.addWidget(self.OutLabels, 7, 1)
    layoutO.addWidget(self.OutLabelTxt, 7, 0)

    self.setLayout(layout)


class DirPage(QtWidgets.QWizardPage):
  """
        Page that allows users to pick the
        location of the .mat to be analyzed.
  """

  def __init__(self, parent=None):
    super(DirPage, self).__init__()
    self.setSubTitle('   ')

    layout = QtWidgets.QGridLayout(self)

    self.InputDirLabel = QtWidgets.QLabel("Select location of mat directory")

    self.MatDirButton = QtWidgets.QPushButton("Select Directory")

    self.MatDirDisp = QtWidgets.QLineEdit(self, "")

    self.MatDirDisp.setReadOnly(1)

    layout.addWidget(self.InputDirLabel, 0, 0)
    layout.addWidget(self.MatDirDisp, 1, 0)
    layout.addWidget(self.MatDirButton, 1, 1)

    self.MatDirButton.clicked.connect(self.GetInDirs)

    self.SaveLoadContainer = QtWidgets.QFrame(self)
    self.SaveLoadLayout = QtWidgets.QHBoxLayout(self.SaveLoadContainer)
    layout.addWidget(self.SaveLoadContainer, 6, 0, 8, 2)

    self.LoadConfig = QtWidgets.QPushButton("Load Config", self)
    self.SaveConfig = QtWidgets.QPushButton("Save Config", self)

    self.SaveLoadLayout.addWidget(self.LoadConfig)
    self.SaveLoadLayout.addWidget(self.SaveConfig)

    self.SaveConfig.clicked.connect(self.SaveCfg)
    self.LoadConfig.clicked.connect(self.LoadCfg)

  def GetInDirs(self):
    """
            Gets the directory selected by user
    """

    #there is some strange behavior in some Linux distros
    #when the native dialog is used, so we opt to use
    #the QT dialog rather than native dialog

    fname = QtWidgets.QFileDialog(
        self, options=QtWidgets.QFileDialog.DontUseNativeDialog)
    fname.setFileMode(QtWidgets.QFileDialog.ExistingFile)
    fname.setViewMode(QtWidgets.QFileDialog.List)
    fname.setNameFilter('MATLAB Container (*.mat)')

    if fname.exec_():
      fileNames = fname.selectedFiles()
      self.MatDirDisp.setText(fileNames[0])

  def LoadCfg(self):
    """
            If there's a pre-saved configuation
            to load then load it.
    """

    x = [None]
    i = 0
    outdir = os.path.join(os.getcwd(), 'IOsaveconfig.txt')
    with open(outdir, 'r') as f:
      x = f.read().splitlines()

    self.wizard().page(1).EleVec.setText(x[0]) if x[0] != 'null' else None
    self.wizard().page(1).TimeUnitVec.setText(x[1]) if x[1] != 'null' else None
    self.wizard().page(1).MassUnitVec.setText(x[2]) if x[2] != 'null' else None
    self.wizard().page(2).InpDirDisp.setText(x[6]) if x[6] != 'null' else None
    self.wizard().page(1).InpLabels.setText(x[9]) if x[9] != 'null' else None
    self.wizard().page(1).InvLabels.setText(x[10]) if x[10] != 'null' else None
    self.wizard().page(1).OutLabels.setText(x[11]) if x[11] != 'null' else None

  def SaveCfg(self):
    """
            Function to save the entered
            dataset parameters for later
            use.
    """

    x = [
        self.wizard().page(1).EleVec.text(),
        self.wizard().page(1).TimeUnitVec.text(),
        self.wizard().page(1).MassUnitVec.text(),
        self.wizard().page(1).InpVec.text(),
        self.MatDirDisp.text(),
        self.wizard().page(1).InpLabels.text(),
        self.wizard().page(1).InvLabels.text(),
        self.wizard().page(1).OutLabels.text()
    ]

    for i in range(0, 12):
      if x[i] == '':
        x[i] = 'null'

    outdir = os.path.join(os.getcwd(), 'IOsaveconfig.txt')

    with open(outdir, 'w') as f:
      for item in x:
        f.write("%s\n" % item)


if __name__ == '__main__':

  #launch the wizard!

  import sys
  app = QtWidgets.QApplication()
  wizard = IOWizardMainMat()
  wizard.show()
  sys.exit(app.exec_())
