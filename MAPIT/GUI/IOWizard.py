"""
    Reads in external .csv files
"""


from PySide6 import QtCore, QtWidgets, QtGui
import os
import sys
from pathlib import Path
from MAPIT.GUI import GUIComponents, StyleOps
import site
from platformdirs import user_config_dir


#temp
class IOWizardMain(QtWidgets.QWizard):
  """
        QWizard used for importing
        .csv, .mat, or .npz data for use with
        MAPIT
  """

  def __init__(self, parent=None):
    super(IOWizardMain, self).__init__()
    self.colordict = parent.colordict
    self.addPage(IntroPage(self))
    self.addPage(DirPage(self))
    self.addPage(OptPage(self))
    self.gracefulExit = 0
    

    self.setWindowTitle("Data IO Wizard")
    self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
    
    
    self.backbutton = GUIComponents.AniButton(self)
    self.backbutton.setText('< Back')
    StyleOps.enable_ani_button(button_obj=self.backbutton, guiobj=self)

    self.nextbutton = GUIComponents.AniButton(self)
    self.nextbutton.setText('> Next')
    StyleOps.enable_ani_button(button_obj=self.nextbutton, guiobj=self)

    self.cancelbutton = GUIComponents.AniButton(self)
    self.cancelbutton.setText('Cancel')
    StyleOps.enable_ani_button(button_obj=self.cancelbutton, guiobj=self)

    self.finishbutton = GUIComponents.AniButton(self)
    self.finishbutton.setText('Finish')
    StyleOps.enable_ani_button(button_obj=self.finishbutton, guiobj=self)

    self.setButton(QtWidgets.QWizard.BackButton,self.backbutton)
    self.setButton(QtWidgets.QWizard.NextButton,self.nextbutton)
    self.setButton(QtWidgets.QWizard.CancelButton,self.cancelbutton)
    self.setButton(QtWidgets.QWizard.FinishButton,self.finishbutton)

    #TODO: behavior for finish/cancel button
    self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.SavePages)



    #bring in the first page banner
    dirname = site.getsitepackages()[-1] + '/MAPIT/'
    x = Path(dirname).resolve().parents[0]
    F = os.path.join(site.getsitepackages()[-1], 'MAPIT', 'docs_v2', 'codeAssets', 'SNL_Horizontal_Black.jpg')
    res = QtGui.QPixmap(F)
    geometry = qApp.desktop().availableGeometry(self)
    res = res.scaledToWidth(geometry.width()*0.25)
    self.setPixmap(QtWidgets.QWizard.BannerPixmap, res)

    
    self.resize(geometry.width()*0.25, geometry.height() * 0.5)

    #initalize some variables
    self.InDir = {}
    self.InvDir = {}
    self.OutDir = {}
    self.EleVec_IN = {}
    self.TempVec_IN = {}
    self.InKMP = {}
    self.InvKMP = {}
    self.OutKMP = {}
    self.InKMP_names = []
    self.InvKMP_names = []
    self.OutKMP_names = []
    self.TimeUnitVec = {}
    self.MassUnitVec = {}
    self.EleIsoName = ""

    #set a flag here to say that imported
    #data is NOT a mat file
    self.IsMatV = 0

  def IncompleteFinish(self):
    self.gracefulExit = 0

  def SavePages(self):
    """
            Function used to hand off between
            the wizard and the main part of
            MAPIT.
    """

    #disable animations before the delete call otherwise
    #there will be some errors when the animation
    #tries to be updated for a deleted object
    StyleOps.disable_ani_button(button_obj=self.backbutton, guiobj=self)
    StyleOps.disable_ani_button(button_obj=self.cancelbutton, guiobj=self)
    StyleOps.disable_ani_button(button_obj=self.nextbutton, guiobj=self)
    StyleOps.disable_ani_button(button_obj=self.finishbutton, guiobj=self)




    self.InDir = self.page(1).InpDirDisp.text()
    self.InvDir = self.page(1).InvDirDisp.text()
    self.OutDir = self.page(1).OutDirDisp.text()


    self.TempVec_IN = self.page(2).TimeUnitVec.text()

    if len(self.page(2).InpLabels.text()) > 0:
      self.InKMP_names = [loc.strip() for loc in self.page(2).InpLabels.text().split(",")]

    if len(self.page(2).InvLabels.text()) > 0:      
      self.InvKMP_names = [loc.strip() for loc in self.page(2).InvLabels.text().split(",")]

    if len(self.page(2).OutLabels.text()) > 0:
      self.OutKMP_names = [loc.strip() for loc in self.page(2).OutLabels.text().split(",")]
      

    self.TimeUnitVec = self.page(2).TimeUnitVec.text()
    self.MassUnitVec = self.page(2).MassUnitVec.text()

    self.dataType = self.page(1).inpFmt.currentText()

    self.EleIsoName = self.page(2).EleIsoText.text()

    self.gracefulExit = 1


  def LoadCfg(self):
    """
            Function to load a previously
            recorded configuration of input
            information.
    """

    x = [None]
    outdir = os.path.join(user_config_dir('MAPIT',False), 'IOsaveconfig.txt')
    with open(outdir, 'r') as f:
      x = f.read().splitlines()

    self.page(1).inpFmt.setCurrentIndex(int(x[0])) if x[0] != 'null' else None
    self.page(2).TimeUnitVec.setText(x[1]) if x[1] != 'null' else None
    self.page(2).MassUnitVec.setText(x[2]) if x[2] != 'null' else None
    self.page(2).EleIsoText.setText(x[3]) if x[3] != 'null' else None
    self.page(1).InpDirDisp.setText(x[4]) if x[4] != 'null' else None
    self.page(1).InvDirDisp.setText(x[5]) if x[5] != 'null' else None
    self.page(1).OutDirDisp.setText(x[6]) if x[6] != 'null' else None
    self.page(2).InpLabels.setText(x[7]) if x[7] != 'null' else None
    self.page(2).InvLabels.setText(x[8]) if x[8] != 'null' else None
    self.page(2).OutLabels.setText(x[9]) if x[9] != 'null' else None

  def SaveCfg(self):
    """
            Function to save a specified
            configuration of input information.
    """
    p = Path(sys.argv[0]).resolve().parents[1]


    x = [
        self.page(1).inpFmt.currentIndex(),
        self.page(2).TimeUnitVec.text(),
        self.page(2).MassUnitVec.text(),
        self.page(2).EleIsoText.text(),
        self.page(1).InpDirDisp.text(),
        self.page(1).InvDirDisp.text(),
        self.page(1).OutDirDisp.text(),
        self.page(2).InpLabels.text(),
        self.page(2).InvLabels.text(),
        self.page(2).OutLabels.text()
    ]

    for i in range(len(x)):
      if x[i] == '':
        x[i] = 'null'

    outdir = os.path.join(user_config_dir('MAPIT',False), 'IOsaveconfig.txt')

    with open(outdir, 'w') as f:
      for item in x:
        f.write("%s\n" % item)


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


class OptPage(QtWidgets.QWizardPage):
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
    super(OptPage, self).__init__()
    self.setSubTitle('    ')

    layout = QtWidgets.QVBoxLayout(self)
    F3 = QtWidgets.QGroupBox()
    L3 = QtWidgets.QHBoxLayout(F3)

    #ReqForms = QtWidgets.QGroupBox(self)
    OptForms = QtWidgets.QGroupBox(self)

    #ReqForms.setTitle("Required Inputs")
    OptForms.setTitle("Optional Inputs")

    #layoutR = QtWidgets.QGridLayout(ReqForms)
    layoutO = QtWidgets.QGridLayout(OptForms)

    #layout.addWidget(ReqForms)
    layout.addWidget(OptForms)


    self.TimeUnitVec = QtWidgets.QLineEdit(self, "")
    layoutO.addWidget(self.TimeUnitVec, 1, 1)

    self.MassUnitVec = QtWidgets.QLineEdit(self, "")
    layoutO.addWidget(self.MassUnitVec, 2, 1)

    self.TimeUnitTxt = QtWidgets.QLabel("Enter the temporal units", self)
    layoutO.addWidget(self.TimeUnitTxt, 1, 0)

    self.MassUnitTxt = QtWidgets.QLabel("Enter the mass units", self)
    layoutO.addWidget(self.MassUnitTxt, 2, 0)

    self.EleIsoText = QtWidgets.QLineEdit(self, "")
    self.EleIsoLabel = QtWidgets.QLabel("Enter element/isotope name")

    layoutO.addWidget(self.EleIsoText, 3, 1)
    layoutO.addWidget(self.EleIsoLabel, 3, 0)

    #layoutR.addWidget(self.inpFmt, 2, 1)
    #layoutR.addWidget(self.InpVecTxt, 2, 0)

    self.InpLabels = QtWidgets.QLineEdit(self, "")
    self.InpLabelsTxt = QtWidgets.QLabel("Enter input labels")

    layoutO.addWidget(self.InpLabels, 4, 1)
    layoutO.addWidget(self.InpLabelsTxt, 4, 0)




    self.InvLabels = QtWidgets.QLineEdit(self, "")
    self.InvLabelsTxt = QtWidgets.QLabel("Enter inventory labels")

    layoutO.addWidget(self.InvLabels, 5, 1)
    layoutO.addWidget(self.InvLabelsTxt, 5, 0)



    self.OutLabels = QtWidgets.QLineEdit(self, "")
    self.OutLabelTxt = QtWidgets.QLabel("Enter output labels")

    layoutO.addWidget(self.OutLabels, 6, 1)
    layoutO.addWidget(self.OutLabelTxt, 6, 0)

    self.LoadConfigOpt = GUIComponents.AniButton(self)
    self.LoadConfigOpt.setText("Load")
    StyleOps.enable_ani_button(button_obj=self.LoadConfigOpt, guiobj=parent)

    self.SaveConfigOpt = GUIComponents.AniButton(self)
    self.SaveConfigOpt.setText("Save")
    StyleOps.enable_ani_button(button_obj=self.SaveConfigOpt, guiobj=parent)

    self.SaveConfigOpt.clicked.connect(parent.SaveCfg)
    self.SaveConfigOpt.clicked.connect(parent.LoadCfg)

    L3.addWidget(self.LoadConfigOpt)
    L3.addWidget(self.SaveConfigOpt)

    layout.addWidget(F3)

    F3.setTitle("Configuration")

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

    layout = QtWidgets.QVBoxLayout(self)

    F1 = QtWidgets.QGroupBox()
    F2 = QtWidgets.QGroupBox()
    F3 = QtWidgets.QGroupBox()

    L1 = QtWidgets.QHBoxLayout(F1)
    L2 = QtWidgets.QVBoxLayout(F2)
    L3 = QtWidgets.QHBoxLayout(F3)

    self.inpFmt = QtWidgets.QComboBox()
    self.inpFmt.addItem('.csv')
    self.inpFmt.addItem('.mat')
    self.inpFmt.addItem('.npz')

    
    L1.addWidget(self.inpFmt)
    F1.setTitle("Data format")
    F2.setTitle("Data location")

    G1 = QtWidgets.QGroupBox()
    G2 = QtWidgets.QGroupBox()
    G3 = QtWidgets.QGroupBox()

    G1.setTitle("Inputs")
    G2.setTitle("Inventories")
    G3.setTitle("Outputs")

    GL1 = QtWidgets.QGridLayout(G1)
    GL2 = QtWidgets.QGridLayout(G2)
    GL3 = QtWidgets.QGridLayout(G3)

    layout.addWidget(F1)

    self.InputDirLabel = QtWidgets.QLabel("Select location of input directory")
    self.InvDirLabel = QtWidgets.QLabel(
        "Select location of inventory directory")
    self.OutDirLabel = QtWidgets.QLabel("Select location of output directory")

    #self.InDirButton = QtWidgets.QPushButton("Select Directory")
    self.InDirButton = GUIComponents.AniButton(self)
    self.InDirButton.setText("Select Directory")
    StyleOps.enable_ani_button(button_obj=self.InDirButton, guiobj=parent)

    self.InvDirButton = GUIComponents.AniButton(self)
    self.InvDirButton.setText("Select Directory")
    StyleOps.enable_ani_button(button_obj=self.InvDirButton, guiobj=parent)

    self.OutDirButton = GUIComponents.AniButton(self)
    self.OutDirButton.setText("Select Directory")
    StyleOps.enable_ani_button(button_obj=self.OutDirButton, guiobj=parent)

    self.InpDirDisp = QtWidgets.QLineEdit(self, "")
    self.InvDirDisp = QtWidgets.QLineEdit(self, "")
    self.OutDirDisp = QtWidgets.QLineEdit(self, "")

    self.InpDirDisp.setReadOnly(1)
    self.InvDirDisp.setReadOnly(1)
    self.OutDirDisp.setReadOnly(1)

    GL1.addWidget(self.InpDirDisp,0,0)
    GL2.addWidget(self.InvDirDisp,0,0)
    GL3.addWidget(self.OutDirDisp,0,0)

    GL1.addWidget(self.InDirButton,0,1)
    GL2.addWidget(self.InvDirButton,0,1)
    GL3.addWidget(self.OutDirButton,0,1)

    L2.addWidget(G1)
    L2.addWidget(G2)
    L2.addWidget(G3)



    layout.addWidget(F2)

    self.LoadConfig = GUIComponents.AniButton(self)
    self.LoadConfig.setText("Load")
    StyleOps.enable_ani_button(button_obj=self.LoadConfig, guiobj=parent)

    self.SaveConfig = GUIComponents.AniButton(self)
    self.SaveConfig.setText("Save")
    StyleOps.enable_ani_button(button_obj=self.SaveConfig, guiobj=parent)

    self.SaveConfig.clicked.connect(parent.SaveCfg)
    self.LoadConfig.clicked.connect(parent.LoadCfg)

    L3.addWidget(self.LoadConfig)
    L3.addWidget(self.SaveConfig)

    layout.addWidget(F3)

    F3.setTitle("Configuration")



    # layout.addWidget(self.inpFmt, 0, 0)

    # layout.addWidget(self.InputDirLabel, 1, 0)
    # layout.addWidget(self.InpDirDisp, 2, 0)
    # layout.addWidget(self.InDirButton, 2, 1)

    # layout.addWidget(self.InvDirLabel, 3, 0)
    # layout.addWidget(self.InvDirDisp, 4, 0)
    # layout.addWidget(self.InvDirButton, 4, 1)

    # layout.addWidget(self.OutDirLabel, 5, 0)
    # layout.addWidget(self.OutDirDisp, 5, 0)
    # layout.addWidget(self.OutDirButton, 6, 1)

    self.InDirButton.clicked.connect(self.GetInDirs)
    self.InvDirButton.clicked.connect(self.GetInvDirs)
    self.OutDirButton.clicked.connect(self.GetOutDirs)

    # self.SaveLoadContainer = QtWidgets.QFrame(self)
    # self.SaveLoadLayout = QtWidgets.QHBoxLayout(self.SaveLoadContainer)
    # layout.addWidget(self.SaveLoadContainer, 7, 0, 8, 2)



    # self.SaveLoadLayout.addWidget(self.LoadConfig)
    # self.SaveLoadLayout.addWidget(self.SaveConfig)

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




if __name__ == '__main__':

  #run the wizard
  import sys
  app = QtWidgets.QApplication()
  wizard = IOWizardMain()
  wizard.show()
  sys.exit(app.exec_())
