"""
    Reads in external .csv files
"""


from PySide2 import QtCore, QtWidgets, QtGui
import time
import numpy as np
import os
import sys
from pathlib import Path


#temp
class IOWizardMain(QtWidgets.QWizard):
  """
        QWizard used for importing
        .csv, .mat, or .npz data for use with
        MAPIT
  """

  def __init__(self, parent=None):
    super(IOWizardMain, self).__init__()
    self.addPage(IntroPage(self))
    self.addPage(InitPage(self))
    self.addPage(DirPage(self))

    self.setWindowTitle("Data IO Wizard")
    self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
    self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.SavePages)

    #bring in the first page banner
    x = Path(sys.argv[0]).resolve().parents[1]
    F = os.path.join(x, 'docs_v2','source', 'assets', 'codeAssets', 'SNL_Horizontal_Black.jpg')
    res = QtGui.QPixmap(F)
    res = res.scaledToWidth(500)
    self.setPixmap(QtWidgets.QWizard.BannerPixmap, res)

    geometry = qApp.desktop().availableGeometry(self)
    self.setFixedSize(500, geometry.height() * 0.5)

    #initalize some variables
    self.InDir = {}
    self.InvDir = {}
    self.OutDir = {}
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

    #set a flag here to say that imported
    #data is NOT a mat file
    self.IsMatV = 0

  def SavePages(self):
    """
            Function used to hand off between
            the wizard and the main part of
            MAPIT.
    """

    self.InDir = self.page(2).InpDirDisp.text()
    self.InvDir = self.page(2).InvDirDisp.text()
    self.OutDir = self.page(2).OutDirDisp.text()


    self.TempVec_IN = self.page(1).TimeUnitVec.text()


    self.InKMP_names = self.page(1).InpLabels.text()
    self.InvKMP_names = self.page(1).InvLabels.text()
    self.OutKMP_names = self.page(1).OutLabels.text()

    self.TimeUnitVec = self.page(1).TimeUnitVec.text()
    self.MassUnitVec = self.page(1).MassUnitVec.text()

    self.dataType = self.page(1).inpFmt.currentText()


class IntroPage(QtWidgets.QWizardPage):

  def __init__(self, parent=None):
    super(IntroPage, self).__init__()
    self.IntroTxt = QtWidgets.QLabel(
      """This wizard will help you import the relevant data for use within MAPIT. It is assumed that your data is organized into folders reflecting different key measurement point types (e.g., inputs, inventories, and outputs). It is also assumed that each file will be of shape [2,n] or [n,2] where n is the total number of samples, and the 2 is the time and data respectively. It is important that the time be the first row or column in your dataset. See the input guide for  more information.
      """)
    self.IntroTxt.setWordWrap(1)
    self.setSubTitle('   ')

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.IntroTxt)
    self.setLayout(layout)


class InitPage(QtWidgets.QWizardPage):
  """
        This page takes in the main
        data needed by MAPIT. Some
        information is required to
        help correctly setup the
        material balance later on.
        Other data is just for cosmetic
        purposes for use with plots.
  """

  def __init__(self, parent=None):
    super(InitPage, self).__init__()
    self.setSubTitle('    ')

    layout = QtWidgets.QVBoxLayout(self)

    ReqForms = QtWidgets.QGroupBox(self)
    OptForms = QtWidgets.QGroupBox(self)

    ReqForms.setTitle("Required Inputs")
    OptForms.setTitle("Optional Inputs")

    layoutR = QtWidgets.QGridLayout(ReqForms)
    layoutO = QtWidgets.QGridLayout(OptForms)

    layout.addWidget(ReqForms)
    layout.addWidget(OptForms)

    self.inpFmt = QtWidgets.QComboBox()
    self.inpFmt.addItem('.csv')
    self.inpFmt.addItem('.mat')
    self.inpFmt.addItem('.npz')
    self.InpVecTxt = QtWidgets.QLabel(
        "Select data format")


    self.TimeUnitVec = QtWidgets.QLineEdit(self, "")
    layoutO.addWidget(self.TimeUnitVec, 1, 1)

    self.MassUnitVec = QtWidgets.QLineEdit(self, "")
    layoutO.addWidget(self.MassUnitVec, 2, 1)

    self.TimeUnitTxt = QtWidgets.QLabel("Enter the temporal units", self)
    layoutO.addWidget(self.TimeUnitTxt, 1, 0)

    self.MassUnitTxt = QtWidgets.QLabel("Enter the mass units", self)
    layoutO.addWidget(self.MassUnitTxt, 2, 0)



    layoutR.addWidget(self.inpFmt, 2, 1)
    layoutR.addWidget(self.InpVecTxt, 2, 0)

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
        Page responsible for getting directories of .csv data.
        Since .csv is two dimensional there  will need to be
        multiple files to describe data that is potentially
        four dimensional (time, location, and element). It's
        assumed that there will be a different .csv for each location.
        Specifying each directory as it relates to the material balance
        (i.e. folders of inputs, inventories and outputs) is done using
        this page.
  """

  def __init__(self, parent=None):
    super(DirPage, self).__init__()
    self.setSubTitle('   ')

    layout = QtWidgets.QGridLayout(self)

    self.InputDirLabel = QtWidgets.QLabel("Select location of input directory")
    self.InvDirLabel = QtWidgets.QLabel(
        "Select location of inventory directory")
    self.OutDirLabel = QtWidgets.QLabel("Select location of output directory")

    self.InDirButton = QtWidgets.QPushButton("Select Directory")
    self.InvDirButton = QtWidgets.QPushButton("Select Directory")
    self.OutDirButton = QtWidgets.QPushButton("Select Directory")

    self.InpDirDisp = QtWidgets.QLineEdit(self, "")
    self.InvDirDisp = QtWidgets.QLineEdit(self, "")
    self.OutDirDisp = QtWidgets.QLineEdit(self, "")

    self.InpDirDisp.setReadOnly(1)
    self.InvDirDisp.setReadOnly(1)
    self.OutDirDisp.setReadOnly(1)

    layout.addWidget(self.InputDirLabel, 0, 0)
    layout.addWidget(self.InpDirDisp, 1, 0)
    layout.addWidget(self.InDirButton, 1, 1)

    layout.addWidget(self.InvDirLabel, 2, 0)
    layout.addWidget(self.InvDirDisp, 3, 0)
    layout.addWidget(self.InvDirButton, 3, 1)

    layout.addWidget(self.OutDirLabel, 4, 0)
    layout.addWidget(self.OutDirDisp, 5, 0)
    layout.addWidget(self.OutDirButton, 5, 1)

    self.InDirButton.clicked.connect(self.GetInDirs)
    self.InvDirButton.clicked.connect(self.GetInvDirs)
    self.OutDirButton.clicked.connect(self.GetOutDirs)

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
            Displays the selected (input) directory
            in a GUI element.
    """

    #There's some strange behavior on UNIX where
    #this will only allow file selection
    #and not folder selection
    #so the non-native dialog needs to be forced to
    #ensure correct behavior
    fname = QtWidgets.QFileDialog.getExistingDirectory(
        self, options=QtWidgets.QFileDialog.DontUseNativeDialog)

    self.InpDirDisp.setText(fname)

  def GetInvDirs(self):
    """
            Displays the selected (inventory) directory
            in a GUI element.
    """

    fname = QtWidgets.QFileDialog.getExistingDirectory(
        self, options=QtWidgets.QFileDialog.DontUseNativeDialog)

    self.InvDirDisp.setText(fname)

  def GetOutDirs(self):
    """
            Displays the selected (output) directory
            in a GUI element.
    """

    fname = QtWidgets.QFileDialog.getExistingDirectory(
        self, options=QtWidgets.QFileDialog.DontUseNativeDialog)

    self.OutDirDisp.setText(fname)

  def LoadCfg(self):
    """
            Function to load a previously
            recorded configuration of input
            information.
    """

    x = [None]
    p = Path(sys.argv[0]).resolve().parents[1]
    outdir = os.path.join(p, 'IOsaveconfig.txt')
    with open(outdir, 'r') as f:
      x = f.read().splitlines()

    self.wizard().page(1).inpFmt.setCurrentIndex(int(x[0])) if x[0] != 'null' else None
    self.wizard().page(1).TimeUnitVec.setText(x[1]) if x[1] != 'null' else None
    self.wizard().page(1).MassUnitVec.setText(x[2]) if x[2] != 'null' else None
    self.wizard().page(2).InpDirDisp.setText(x[3]) if x[3] != 'null' else None
    self.wizard().page(2).InvDirDisp.setText(x[4]) if x[4] != 'null' else None
    self.wizard().page(2).OutDirDisp.setText(x[5]) if x[5] != 'null' else None
    self.wizard().page(1).InpLabels.setText(x[6]) if x[6] != 'null' else None
    self.wizard().page(1).InvLabels.setText(x[7]) if x[7] != 'null' else None
    self.wizard().page(1).OutLabels.setText(x[8]) if x[8] != 'null' else None

  def SaveCfg(self):
    """
            Function to save a specified
            configuration of input information.
    """
    p = Path(sys.argv[0]).resolve().parents[1]


    x = [
        self.wizard().page(1).inpFmt.currentIndex(),
        self.wizard().page(1).TimeUnitVec.text(),
        self.wizard().page(1).MassUnitVec.text(),
        self.InpDirDisp.text(),
        self.InvDirDisp.text(),
        self.OutDirDisp.text(),
        self.wizard().page(1).InpLabels.text(),
        self.wizard().page(1).InvLabels.text(),
        self.wizard().page(1).OutLabels.text()
    ]

    for i in range(len(x)):
      if x[i] == '':
        x[i] = 'null'

    outdir = os.path.join(p, 'IOsaveconfig.txt')

    with open(outdir, 'w') as f:
      for item in x:
        f.write("%s\n" % item)


if __name__ == '__main__':

  #run the wizard
  import sys
  app = QtWidgets.QApplication()
  wizard = IOWizardMain()
  wizard.show()
  sys.exit(app.exec_())
