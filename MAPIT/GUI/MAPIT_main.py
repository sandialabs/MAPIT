"""
Started 11/01/2019
Author: Nathan Shoman
Sandia National Laboratories

The purpose of this code is to perform
safeguards analysis on a generic set of
data. It performs error propagation and
includes several statistical tests used
by the IAEA.

This is the main component of MAPIT
"""
import os
import sys
from pathlib import Path
import time
import queue
import json
os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"]             = "1"

from PySide2 import QtCore, QtWidgets, QtGui
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import time






from MAPIT.GUI.IOWizard import IOWizardMain 
#from MAPIT.GUI.IOWizardMat import IOWizardMainMat
from MAPIT.GUI import PlotOps, StyleOps, GeneralOps, DialogComponents, StatsPanelOps, ScenarioSelector, AnimationTools, ErrorPanelOps, ThreadTools, GUIComponents





class GUIopts:
  def __init__(self, international, errorstyle):
    self.international = international
    self.errorstyle = errorstyle

class DataHolder:
  pass


class customExecp(Exception):
  pass
#https://stackoverflow.com/questions/19442443/busy-indication-with-pyqt-progress-bar


GUIparams = GUIopts(False, True)
GUIparams = GeneralOps.loadGUILabels(GUIparams, international = False)

AnalysisData = DataHolder()

class StatGUIInterface:
  def runAnalysisPipe(self):

    global AnalysisData
    global GUIparams

    #disable buttons during thread execution

    StyleOps.disable_ani_button(button_obj=self.ErrorS, guiobj=self)
    StyleOps.disable_ani_button(button_obj=self.RunStats, guiobj=self)
    StyleOps.disable_ani_button(button_obj=self.CalcThresh, guiobj=self)
    StyleOps.disable_ani_button(button_obj=self.PlotRunner, guiobj=self)


    


    if len(self.OBox.text()) > 0:
      AnalysisData.offset = int(self.OBox.text())
    else:
      AnalysisData.offset = 0

    mbaTime = int(self.MBPBox.text())

    if self.IterBox.text() == '':
      IT = 0
    else:
      IT = int(self.IterBox.text())

    doError, doMUF, doAI, doCUMUF, doSEID, doSEIDAI, doSITMUF, doPage = StatsPanelOps.getRequestedTests(GUIObject = self)

    GLoc, GUIparams = StatsPanelOps.verifyGUIRequests(GUIObject = self, GUIparams = GUIparams)

    inpdict = {'doError': doError, 'doMUF': doMUF, 'doAI': doAI, 'doCUMUF': doCUMUF,
               'doSEID': doSEID, 'doSEIDAI': doSEIDAI, 'doSITMUF': doSITMUF, 'doPage': doPage, 
               'GLoc': GLoc, 'GUIparams': GUIparams, 'AnalysisData':AnalysisData, 'MBP':mbaTime,
               'IT':IT}


    Q = queue.Queue()
    thread = ThreadTools.AnalysisThread(Q,self.handleAnalysisThread,parent=self)
    thread.start()
    Q.put(inpdict)                                                                   









class customExecp(Exception):
    pass





class LaunchGUI(QtWidgets.QMainWindow):
  """
        Main MAPIT class (Main window widget)

        This class sets some variables needed
        for MAPIT and handles some theme related
        items.
  """

  def __init__(self):
    super(LaunchGUI, self).__init__()

    global GUIparams
    

    


    self.CBHolder = []  #this is just for some of the style stuff later on
    self.PuLoc = -1
    self.ULoc = -1
    self.GLoc = -1
    self.HasRunErrors = 0
    self.launch_master_window()

    self.RunStats.clicked.connect(lambda: StatGUIInterface.runAnalysisPipe(self))
    self.ErrorS.clicked.connect(self.InitErrors)
    self.PlotRunner.clicked.connect(lambda: PlotOps.ExecPlot(self,GUIparams,AnalysisData))
    self.PlotRunner.clicked.connect(self.RunPlotTresh)
    self.metricBox.activated.connect(lambda: PlotOps.UpdateLocOpts(self,GUIparams)) #TODO: CUMUF here  


    

    #

    x = str(Path(__file__).resolve().parents[1])
    F = os.path.join(x, 'docs_v2', 'codeAssets', 'mapit_logo.png')
    self.setWindowIcon(QtGui.QIcon(F))

    StatsPanelOps.update_data_opts(self,0) #call for initial layout setup

  def launchSamplePathDlg(self, setInitStyle=False):
    dlg  = DialogComponents.checkForSampleData(self, setInitStyle)
    dlg.setWindowTitle("Exemplar data")
    dlg.exec_()
    self.updateSamplePath()
    self.loadExemplarData()


  def updateDataUI(self):
    self.datopts.clear()
    self.mdlopts.clear()

    for item in GUIparams.availableDatas:
      self.datopts.addItem(GUIparams.availableDatas[item])

    for item in GUIparams.availableMdls:
      self.mdlopts.addItem(GUIparams.availableMdls[item])


  def updateSamplePath(self):
    global GUIparams
    settings = QtCore.QSettings("current", "mapit")
    GUIparams.exemplarDataPath = settings.value("dataPathDefault")


  def closeEvent(self,event):
    settings = QtCore.QSettings("current", "mapit")
    settings.setValue("geometry", self.saveGeometry())
    settings.setValue("fontsize",self.currentFontSize)
    if self.MakeDark.isChecked() == True:
      settings.setValue("theme","dark")
    else:
      settings.setValue("theme","light")
    QtWidgets.QMainWindow.closeEvent(self, event)

  def handleLoadThread(self, result):
    global GUIparams
    global AnalysisData

    AnalysisData, GUIparams  = result



  def handleAnalysisThread(self, result):
    global AnalysisData

    AnalysisData, doMUF, doAI, doCUMUF, doSEID, doSEIDAI, doSITMUF, doPage = result

    #reenable controls
    StyleOps.enable_ani_button(button_obj = self.ErrorS, guiobj = self, loc = 'EAB')
    StyleOps.enable_ani_button(button_obj = self.RunStats, guiobj = self, loc = 'RSB')

    StatsPanelOps.preparePlotterOptions(self, doMUF, doAI, doCUMUF,doSEID, doSEIDAI,doSITMUF,doPage,GUIparams,AnalysisData)
    self.CalcThresh._animation.start()
    self.CalcThresh.setEnabled(1)
    StyleOps.enable_ani_button(button_obj = self.CalcThresh, guiobj = self)

    self.PlotRunner._animation.start()
    self.PlotRunner.setEnabled(1)
    StyleOps.enable_ani_button(button_obj = self.PlotRunner, guiobj = self)



  def update_errorB_text(self):
    if self.CB_ErrorProp.isChecked() == 1:
      self.ErrorS.setText('Set Simulated Errors')
      self.IterBox.setEnabled(1)
    else:
      self.ErrorS.setText('Set Estimated Errors')
      self.IterBox.setEnabled(0)
      self.IterBox.setText("")



  def InitErrors(self):
    """
            This function creates the pop-up to select
            errors for imported or scenario data.
    """


    StyleOps.enable_ani_button(button_obj=self.RunStats, guiobj=self)

    self.RunStats.setEnabled(
        1)  #flag to show that the calc has run at least once

    ErrorBox = [
        '0.005', '0.01','0.05', '0.1', '0.5', '1.0', '3.0', '5.0', '10.0', '15.0', '20.0', '25.0', '50.0'
    ]
    ErrorBoxLabels = [x + ' %' for x in ErrorBox]

    dirname, _ = os.path.split(os.path.abspath(__file__))
    x = Path(dirname).resolve().parents[0]

    if self.HasRunErrors == 1 and GUIparams.errorstyle == True:  #if has run previously get those values
      pastEVals = np.zeros((self.EP.rowCount(), 2))
      for i in range(0, self.EP.rowCount()):
        for j in range(0, 1):
          if self.EP.item(i, j) is None and self.EP.item(i, j+1) is None:
            pastEVals[i, j] = 0
            pastEVals[i, j+1] = 0
          elif self.EP.item(i, j) is not None:

            if self.EP.item(i, j+1) is None:
              if self.EP.item(i, j).text().endswith('%'):
                pastEVals[i, j] = self.EP.item(i, j).text()[:-2]
                pastEVals[i, j+1] = '0.0'
              else:
                pastEVals[i, j] = self.EP.item(i, j).text()
                pastEVals[i, j+1] = '0.0'            
            else:
              if self.EP.item(i, j).text().endswith('%'):
                pastEVals[i, j] = self.EP.item(i, j).text()[:-2]
                pastEVals[i, j+1] = self.EP.item(i, j+1).text()[:-2]
              else:
                pastEVals[i, j] = self.EP.item(i, j).text()
                pastEVals[i, j+1] = self.EP.item(i, j+1).text()

    elif self.HasRunErrors == 1 and GUIparams.errorstyle == False: 
      pastEVals = np.zeros((self.EP.rowCount(), 2))
      for i in range(0, self.EP.rowCount()):
        for j in range(0, 1):
          if self.EP.item(i, j) is None:
            pastEVals[i, j] = 0
          else:
            if self.EP.item(i, j).text().endswith('%'):
                pastEVals[i, j] = self.EP.item(i, j).text()[:-2]
            else:
              pastEVals[i, j] = self.EP.item(i, j).text()



    self.ErrorPane = QtWidgets.QDialog()
    ep_L = QtWidgets.QVBoxLayout(self.ErrorPane)
    epat_L = QtWidgets.QGridLayout()

    if GUIparams.errorstyle == True:
      # errors for dropdown

      # pane for all errors, all ins, outs, invs
      # pane for all errors + table is a grid layout (0, 1) (all) and (0, 0) (table)
      # buttons to save, load error config, and press done appear below in a QVBoxLayout

      BContain = QtWidgets.QGroupBox(self.ErrorPane)
      bc_L = QtWidgets.QVBoxLayout(BContain)
      epat_L.addWidget(BContain, 0, 2)
      BContain.setTitle("Mass error control")
      # pane for all errors
      AllError = QtWidgets.QGroupBox(BContain)
      AE_L = QtWidgets.QGridLayout(AllError)
      AllError.setTitle("All errors")

      AllRandLabel = QtWidgets.QLabel("Random")
      AllSysLabel = QtWidgets.QLabel("Systematic")

      self.AllRand = QtWidgets.QComboBox(AllError)
      self.AllSys = QtWidgets.QComboBox(AllError)

      self.AllRand.addItems(ErrorBoxLabels)
      self.AllSys.addItems(ErrorBoxLabels)
      self.AllRand.setCurrentIndex(6)
      self.AllSys.setCurrentIndex(6)

      self.AllRand.activated.connect(lambda: ErrorPanelOps.MultiLocUpdate(self,GUIparams,'rand'))
      self.AllSys.activated.connect(lambda: ErrorPanelOps.MultiLocUpdate(self,GUIparams,'sys'))

      AE_L.addWidget(AllRandLabel, 0, 0)
      AE_L.addWidget(AllSysLabel, 0, 1)
      AE_L.addWidget(self.AllRand, 1, 0)
      AE_L.addWidget(self.AllSys, 1, 1)
      bc_L.addWidget(AllError)

      # Pane for Input
      InpError = QtWidgets.QGroupBox(BContain)
      IE_L = QtWidgets.QGridLayout(InpError)
      InpError.setTitle("Input Error")

      InpRandLabel = QtWidgets.QLabel("Random")
      InpSysLabel = QtWidgets.QLabel("Systematic")

      self.InpRand = QtWidgets.QComboBox(InpError)
      self.InpSys = QtWidgets.QComboBox(InpError)

      self.InpRand.addItems(ErrorBoxLabels)
      self.InpSys.addItems(ErrorBoxLabels)
      self.InpRand.setCurrentIndex(6)
      self.InpSys.setCurrentIndex(6)

      self.InpRand.activated.connect(lambda: ErrorPanelOps.SingleLocUpdate(self,GUIparams,'rand','inp'))
      self.InpSys.activated.connect(lambda: ErrorPanelOps.SingleLocUpdate(self,GUIparams,'sys','inp'))

      IE_L.addWidget(InpRandLabel, 0, 0)
      IE_L.addWidget(InpSysLabel, 0, 1)
      IE_L.addWidget(self.InpRand, 1, 0)
      IE_L.addWidget(self.InpSys, 1, 1)
      bc_L.addWidget(InpError)

      # Pane for Inventory

      InvError = QtWidgets.QGroupBox(BContain)
      IV_L = QtWidgets.QGridLayout(InvError)
      InvError.setTitle("Inventory Error")

      InvRandLabel = QtWidgets.QLabel("Random")
      InvSysLabel = QtWidgets.QLabel("Systematic")

      self.InvRand = QtWidgets.QComboBox(InvError)
      self.InvSys = QtWidgets.QComboBox(InvError)


      self.InvRand.addItems(ErrorBoxLabels)
      self.InvSys.addItems(ErrorBoxLabels)
      self.InvRand.setCurrentIndex(6)
      self.InvSys.setCurrentIndex(6)

      self.InvRand.activated.connect(lambda: ErrorPanelOps.SingleLocUpdate(self,GUIparams,'rand','inv'))
      self.InvSys.activated.connect(lambda: ErrorPanelOps.SingleLocUpdate(self,GUIparams,'sys','inv'))

      IV_L.addWidget(InvRandLabel, 0, 0)
      IV_L.addWidget(InvSysLabel, 0, 1)
      IV_L.addWidget(self.InvRand, 1, 0)
      IV_L.addWidget(self.InvSys, 1, 1)
      bc_L.addWidget(InvError)

      # Pane for Output

      OutError = QtWidgets.QGroupBox(BContain)
      OE_L = QtWidgets.QGridLayout(OutError)
      OutError.setTitle("Output Error")

      OutRandLabel = QtWidgets.QLabel("Random")
      OutSysLabel = QtWidgets.QLabel("Systematic")

      self.OutRand = QtWidgets.QComboBox(OutError)
      self.OutSys = QtWidgets.QComboBox(OutError)

      self.OutRand.addItems(ErrorBoxLabels)
      self.OutSys.addItems(ErrorBoxLabels)
      self.OutRand.setCurrentIndex(6)
      self.OutSys.setCurrentIndex(6)

      self.OutRand.activated.connect(lambda: ErrorPanelOps.SingleLocUpdate(self,GUIparams,'rand','out'))
      self.OutSys.activated.connect(lambda: ErrorPanelOps.SingleLocUpdate(self,GUIparams,'sys','out'))

      OE_L.addWidget(OutRandLabel, 0, 0)
      OE_L.addWidget(OutSysLabel, 0, 1)
      OE_L.addWidget(self.OutRand, 1, 0)
      OE_L.addWidget(self.OutSys, 1, 1)
      bc_L.addWidget(OutError)

      # table pane
      self.EP = QtWidgets.QTableWidget()

      TotalLocs = GUIparams.nTotalLocations
      self.EP.setColumnCount(2)
      self.EP.setHorizontalHeaderLabels(['Rand ', 'Sys'])
      #self.EP.setHorizontalHeaderLabels(GUIparams.rowNames)

      self.EP.setRowCount(TotalLocs + 2)

      epat_L.addWidget(self.EP, 0, 0)
      
      self.EP.setVerticalHeaderLabels(GUIparams.rowNames)
      self.PlotLocLabels = list(
          filter(len, GUIparams.rowNames)
      )  #remove spaces which don't serve a purpose in the plotter dropdown

      # set the initial table items
      # the 2 and 31 index are separator rows
      if self.HasRunErrors == 0:
        for i in range(0, self.EP.columnCount()):
          for j in range(0, TotalLocs + 2):
            if self.EP.verticalHeaderItem(j).text() != '' and self.EP.horizontalHeaderItem(i) is not None:
              self.EP.setItem(j, i, QtWidgets.QTableWidgetItem(str(3.0) + ' %'))

      if self.HasRunErrors == 1:
        for i in range(np.shape(pastEVals)[0]):
          for j in range(0, 1):
            if pastEVals[i, j] != 0:
              self.EP.setItem(i, j, QtWidgets.QTableWidgetItem(str(pastEVals[i, j])+' %'))
              self.EP.setItem(i, j+1, QtWidgets.QTableWidgetItem(str(pastEVals[i, j+1])+' %'))

      ep_L.addLayout(epat_L)
      self.EP.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
      self.EP.setMinimumWidth(self.EP.sizeHint().width()+self.EP.sizeHintForColumn(1)*3) #HACK: minwidth for both columns
      self.EP.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)

    else:

      BContain = QtWidgets.QGroupBox(self.ErrorPane)
      bc_L = QtWidgets.QVBoxLayout(BContain)
      epat_L.addWidget(BContain, 0, 2)
      BContain.setTitle("Mass error control")

      # pane for all errors
      AllError = QtWidgets.QGroupBox(BContain)
      AE_L = QtWidgets.QGridLayout(AllError)
      AllError.setTitle("All errors")

      AllLabel = QtWidgets.QLabel("Errors")

      self.All = QtWidgets.QComboBox(AllError)

      self.All.addItems(ErrorBoxLabels)
      self.All.setCurrentIndex(6)

      self.All.activated.connect(lambda: ErrorPanelOps.MultiLocUpdate(self,GUIparams,'rand'))

      AE_L.addWidget(AllLabel, 0, 0)
      AE_L.addWidget(self.All, 1, 0)
      bc_L.addWidget(AllError)

      # Pane for Input
      InpError = QtWidgets.QGroupBox(BContain)
      IE_L = QtWidgets.QGridLayout(InpError)
      InpError.setTitle("Input Error")

      InpLabel = QtWidgets.QLabel("Errors")

      self.Inp = QtWidgets.QComboBox(InpError)

      self.Inp.addItems(ErrorBoxLabels)
      self.Inp.setCurrentIndex(6)

      self.Inp.activated.connect(lambda: ErrorPanelOps.SingleLocUpdate(self,GUIparams,'rand','inp'))

      IE_L.addWidget(InpLabel, 0, 0)
      IE_L.addWidget(self.Inp, 1, 0)
      bc_L.addWidget(InpError)

      # Pane for Inventory

      InvError = QtWidgets.QGroupBox(BContain)
      IV_L = QtWidgets.QGridLayout(InvError)
      InvError.setTitle("Inventory Error")

      InvRandLabel = QtWidgets.QLabel("Random Errors")

      self.InvRand = QtWidgets.QComboBox(InvError)

      self.InvRand.addItems(ErrorBoxLabels)
      self.InvRand.setCurrentIndex(6)

      self.InvRand.activated.connect(lambda: ErrorPanelOps.SingleLocUpdate(self,GUIparams,'rand','inv'))

      IV_L.addWidget(InvRandLabel, 0, 0)
      IV_L.addWidget(self.InvRand, 1, 0)
      bc_L.addWidget(InvError)

      # Pane for Output

      OutError = QtWidgets.QGroupBox(BContain)
      OE_L = QtWidgets.QGridLayout(OutError)
      OutError.setTitle("Output Error")

      OutLabel = QtWidgets.QLabel("Random Errors")

      self.Out = QtWidgets.QComboBox(OutError)

      self.Out.addItems(ErrorBoxLabels)
      self.Out.setCurrentIndex(6)

      self.Out.activated.connect(lambda: ErrorPanelOps.SingleLocUpdate(self,GUIparams,'rand','out'))

      OE_L.addWidget(OutLabel, 0, 0)
      OE_L.addWidget(self.Out, 1, 0)
      bc_L.addWidget(OutError)

      # table pane
      self.EP = QtWidgets.QTableWidget()

      TotalLocs = GUIparams.nTotalLocations
      self.EP.setColumnCount(1)
      self.EP.setHorizontalHeaderLabels(['Error '])
      #self.EP.setHorizontalHeaderLabels(GUIparams.rowNames)

      self.EP.setRowCount(TotalLocs + 2)
      epat_L.addWidget(self.EP, 0, 0)
      
      self.EP.setVerticalHeaderLabels(GUIparams.rowNames)
      self.PlotLocLabels = list(
          filter(len, GUIparams.rowNames)
      )  #remove spaces which don't serve a purpose in the plotter dropdown

      # set the initial table items
      # the 2 and 31 index are separator rows

      if self.HasRunErrors == 0:
        for i in range(0, self.EP.columnCount()):
          for j in range(0, TotalLocs + 2):
            if self.EP.verticalHeaderItem(j).text() != '' and self.EP.horizontalHeaderItem(i) is not None:
              self.EP.setItem(j, i, QtWidgets.QTableWidgetItem(str(3.0) + ' %'))

      if self.HasRunErrors == 1:

        for j in range(0, self.EP.columnCount()):
          for i in range(0, GUIparams.nInputLocations):
            self.EP.setItem(i, j, QtWidgets.QTableWidgetItem(str(pastEVals[i, j])+' %'))
          for i in range(GUIparams.nInputLocations+1, GUIparams.nInventoryLocations+GUIparams.nInputLocations+1):
            self.EP.setItem(i, j, QtWidgets.QTableWidgetItem(str(pastEVals[i, j])+' %'))
          for i in range(GUIparams.nInventoryLocations+GUIparams.nInputLocations+2, GUIparams.nInventoryLocations+GUIparams.nInputLocations+GUIparams.nOutputLocations+2):
            self.EP.setItem(i, j, QtWidgets.QTableWidgetItem(str(pastEVals[i, j])+' %'))
        
#        for i in range(np.shape(pastEVals)[0]):
#          for j in range(np.shape(pastEVals)[1]):
#            if pastEVals[i, j] != 0:
#              self.EP.setItem(i, j, QtWidgets.QTableWidgetItem(str(pastEVals[i, j])+' %'))

      ep_L.addLayout(epat_L)



    # save/load buttons
    SLContain = QtWidgets.QFrame(self.ErrorPane)
    SL_L = QtWidgets.QGridLayout(SLContain)

    self.saveEConfig = QtWidgets.QPushButton("Save Error Config", SLContain)
    self.loadEConfig = QtWidgets.QPushButton("Load Error Config", SLContain)
    self.CloseEConfig = QtWidgets.QPushButton("Done", self.ErrorPane)

    # self.OutRand.currentTextChanged.connect(self.OutRandFcn)
    self.saveEConfig.clicked.connect(lambda: ErrorPanelOps.saveErrorToDisk(self))
    self.loadEConfig.clicked.connect(lambda: ErrorPanelOps.loadErrorFromDisk(self))
    self.CloseEConfig.clicked.connect(self.ErrorPane.accept)

    SL_L.addWidget(self.loadEConfig, 0, 0)
    SL_L.addWidget(self.saveEConfig, 0, 1)

    ep_L.addWidget(SLContain)
    ep_L.addWidget(self.CloseEConfig)

    self.ErrorPane.setWindowTitle("Error Selection")
    F = os.path.join(x, 'docs_v2', 'codeAssets', 'mapit_logo.png')
    self.ErrorPane.setWindowIcon(QtGui.QIcon(F))
    self.ErrorPane.setWindowModality(QtCore.Qt.ApplicationModal)
    self.ErrorPane.finished.connect(self.RunStats._animation.start)
    #self.ErrorPane.resize(1000, 800)
    self.ErrorPane.show()
    self.PB.setFormat("Ready to execute")
    self.HasRunErrors = 1
    

  def helpLaunch(self):
    """
            This function launches a small
            window with some general guidelines.
    """

    IContainer = QtWidgets.QMessageBox(self)
    IContainer.setStandardButtons(QtWidgets.QMessageBox.Ok)
    IContainer.setIcon(QtWidgets.QMessageBox.Information)
    IContainer.setTextFormat(QtCore.Qt.RichText)


    boxText = "Check out Github for tutorials and help at: " + \
    "<br> <a href='https://github.com/sandialabs/MAPIT'>https://github.com/sandialabs/MAPIT</a>"
    IContainer.setText(boxText)

    IContainer.exec_()

  def ContactLaunch(self):
    """
            Function to launch a window with
            contact information of authors.
    """
    CheckPrint = QtWidgets.QDialog(self)
    CPL = QtWidgets.QGridLayout(CheckPrint)
    label = QtWidgets.QLabel()

    dirname, _ = os.path.split(os.path.abspath(__file__))
    x = str(Path(__file__).resolve().parents[1])
    F = os.path.join(x, 'docs','assets', 'codeAssets', 'SNL_Horizontal_Black_Blue.jpg')
    banner = QtGui.QPixmap(F)

    banner = banner.scaled(banner.size() * 0.8)
    label.setPixmap(banner)
    CPL.addWidget(label, 0, 0, 1, 2)

    N1 = QtWidgets.QLineEdit()
    N1.setReadOnly(1)
    N1.setText('Nathan Shoman')

    N2 = QtWidgets.QLineEdit()
    N2.setReadOnly(1)
    N2.setText('nshoman@sandia.gov')
    N2.setMinimumWidth(190)
    CPL.addWidget(N1, 1, 0)
    CPL.addWidget(N2, 1, 1)

    P1 = QtWidgets.QLineEdit()
    P1.setReadOnly(1)
    P1.setText('Pat Moosir')

    P2 = QtWidgets.QLineEdit()
    P2.setReadOnly(1)
    P2.setText('mhiggin@sandia.gov')

    CPL.addWidget(P1, 2, 0)
    CPL.addWidget(P2, 2, 1)
 
    CheckPrint.show()

  def RunTable(self):
    """
            Function calling the error selection
            function.
    """
    dlg = DialogComponents.ViewErrorTabs(self, AnalysisData, GUIparams)
    dlg.setWindowTitle('SEID Contributions')
    x = str(Path(__file__).resolve().parents[1])
    F = os.path.join(x, 'docs_v2', 'codeAssets', 'mapit_logo.png')
    dlg.setWindowIcon(QtGui.QIcon(F))
    dlg.resize(1200,800)
    res = dlg.show()

  def RunTableAI(self):
    """
          Function calling the error tab for% AI
    """  

    dlg = DialogComponents.ViewErrorTabsAI(self, AnalysisData, GUIparams)
    dlg.setWindowTitle('SEID(AI) Contributions')
    x = str(Path(__file__).resolve().parents[1])
    F = os.path.join(x, 'docs_v2', 'codeAssets', 'mapit_logo.png')
    dlg.setWindowIcon(QtGui.QIcon(F))
    dlg.resize(1200, 800)
    res = dlg.exec_()

  def RunHPCDlg(self):
    dlg = DialogComponents.HPCWindow(self, AnalysisData)
    res = dlg.exec_()


  def launch_master_window(self):
    """
            Function responsible for handeling
            the setup of the main MAPIT frame

            Adds all the widgets to the QFrame.
            The main window (specified by LaunchGUI)
            holds the QFrame created by this class.
    """
    # create main container frame
    global GUIparams
    self.main_CF = QtWidgets.QFrame(self)




#    geometry = QtGui.qApp.desktop().availableGeometry(self)

    geometry = QtWidgets.QApplication.primaryScreen().size()
    self.setCentralWidget(self.main_CF)
    self.main_CL = QtWidgets.QGridLayout(self.main_CF)
    #important to note the maxWidth parameter
    #of some items in column 0
    #dictate this scaling
    #items in column2 might also impact, but
    #labels in combobox require a minimumwidth also
    self.main_CL.setColumnStretch(0,0)
    self.main_CL.setColumnStretch(1,3)
    # self.main_CL.setColumnStretch(2,1)
    self.main_CL.setColumnMinimumWidth(1,geometry.width()*0.5) #HACK: this should not be hard coded, and needs to be strech instead
    # self.main_CL.resize(round(geometry.width()*0.65),round(geometry.height()*0.65))

    self.setWindowTitle(
        '(M)aterial (A)ccountancy (P)erformance (I)ndicator (T)oolkit')


    #self.statusBar().setSizeGripEnabled(True)
    self.statusBar().hide()
    self.PB = QtWidgets.QProgressBar(self)
    # helps shorten the progress bar
    #self.PB.setFixedWidth(self.PB.sizeHint().width() * 2)
    self.PB.setAlignment(QtCore.Qt.AlignCenter)
    #self.statusBar().addPermanentWidget(self.PB)
    self.PB.setValue(0)
    #self.PB.setMaximumWidth(250)
    

    # menubar
    menubar = self.menuBar()
    menu = QtWidgets.QMenu("File", self)
    accmenu = QtWidgets.QMenu("Accessibility",self)
    menubar.addMenu(menu)

    self.TabOpt = QtWidgets.QMenu("Tabular Data View", self)
    menubar.addMenu(self.TabOpt)

    self.TabView = QtWidgets.QAction("Error Contribution", self)
    self.TabView.triggered.connect(self.RunTable)
    
    self.TabOpt.addAction(self.TabView)
    self.TabView.setToolTip(GUIparams.labels["Box15L"] + ' calculation required')
    self.TabView.setEnabled(0)

    self.TabView1 = QtWidgets.QAction("Error Contribution (AI)", self)
    self.TabView1.triggered.connect(self.RunTableAI)

    self.TabOpt.addAction(self.TabView1)
    self.TabView1.setToolTip(GUIparams.labels["Box16L"] + ' calculation required')
    self.TabView1.setEnabled(0)

    themeOpt = QtWidgets.QMenu("Theme", self)
    menubar.addMenu(themeOpt)

    HelpLoader = QtWidgets.QMenu("Help", self)
    menubar.addMenu(HelpLoader)

    InstructAction = QtWidgets.QAction("Tool Instructions", self)
    InstructAction.triggered.connect(self.helpLaunch)
    HelpLoader.addAction(InstructAction)

    HelpAction = QtWidgets.QAction("Contact Information", self)
    HelpAction.triggered.connect(self.ContactLaunch)
    HelpLoader.addAction(HelpAction)

    

    TG = QtWidgets.QActionGroup(self, exclusive=True)
    self.MakeLight = TG.addAction(
        QtWidgets.QAction("Light", self, checkable=True))
    themeOpt.addAction(self.MakeLight)
    self.MakeDark = TG.addAction(QtWidgets.QAction("Dark", self, checkable=True))
    themeOpt.addAction(self.MakeDark)
    TG.triggered.connect(lambda: StyleOps.ChangeColor(self))
    StyleOps.setInitialStyle(self)
   


    self.ExportDat = QtWidgets.QAction("Save Data", self)
    menu.addAction(self.ExportDat)
    self.ExportDat.triggered.connect( lambda: GeneralOps.SaveStats(self,AnalysisData,GUIparams))
    self.ExportDat.setEnabled(0)

    self.HPC_opts = QtWidgets.QAction("High performance options",self)
    menu.addAction(self.HPC_opts)
    self.HPC_opts.triggered.connect(self.RunHPCDlg)
    self.HPC_opts.setEnabled(0)

    redoExempPath = QtWidgets.QAction("Load exemplar data",self)
    menu.addAction(redoExempPath)
    redoExempPath.triggered.connect(self.launchSamplePathDlg)

    menubar.addMenu(accmenu)

    upfont = QtWidgets.QAction("Increase font size",self)
    downfont = QtWidgets.QAction("Decrease font size",self)
    restorewin = QtWidgets.QAction("Restore defaults",self)
    errorsty = QtWidgets.QAction("Change error style", self)

    upfont.triggered.connect(lambda: StyleOps.IncreaseFont(self))
    downfont.triggered.connect(lambda: StyleOps.DecreaseFont(self))
    restorewin.triggered.connect(lambda: StyleOps.RestoreWindow(self))
    errorsty.triggered.connect(lambda: ErrorStyleChange())


    accmenu.addAction(upfont)
    accmenu.addAction(downfont)
    accmenu.addAction(restorewin)
    accmenu.addAction(errorsty)



    #self.StatDlg = MssgRunner(self)
    #self.StatDlg.setMaximumWidth(450)
    #self.StatDlg._animation.start()
    #self.StatDlg.UpdateDispText('Waiting for data import')
    #self.StatDlg.setEnabled(0)
    #self.statusBar().addWidget(self.StatDlg)
    #self.CBHolder.append(menu)

    
    add_plot_box(self)
    add_stats_box(self)

    




    
    # sysPalette = QtGui.QPalette()
    # #try to autodetect theme
    # if sum(sysPalette.base().color().getRgb()[0:3]) != 765:
    #   self.MakeLight.setChecked(0)
    #   self.MakeDark.setChecked(1)
    # else:
    #   self.MakeLight.setChecked(1)
    #   self.MakeDark.setChecked(0)

    # StyleOps.ChangeColor(self)

    #HACK: theme here
    #note: light is default and this is just a force
    #to dark because it's my preference
    #also, the navigation icons in the canvas
    #are handleded by the MPL backend and are
    #difficult to change, so we do the light theme
    #first, to ensure black icons, then change from there
    #as white icons (generated under dark theme if initially
    # selected) are difficult to see and change (they are
    # actually transpartent pngs that are filled with color)
    #self.MakeDark.setChecked(1)
    #StyleOps.ChangeColor(self)


    #initial loading
    # show the window if needed, 
    settings = QtCore.QSettings("current", "mapit")
    if settings.value("dataPathBypass") == False or settings.value("dataPathBypass") == None:
      self.launchSamplePathDlg(setInitStyle=True)
    else:
      self.updateSamplePath()

    self.loadExemplarData()
      
    
    


  def loadExemplarData(self):
    #initial loading
    GeneralOps.loadDatasetLabels(GUIparams)
    GeneralOps.removeUnavailableDatasets(GUIparams)
    self.updateDataUI()

    #only load data if some is available
    if len(GUIparams.availableMdls) > 0 and len(GUIparams.availableDatas):
      loadInternalData(self)


  def RunStatThresh(self):
    #call the function to update the threshold statistics
    dh, _ = PlotOps.getData(self,GUIparams,AnalysisData, ThresholdL = True)
    self.canvas.update_thresh(float(self.StatThresh.text()), dh[1])

  def RunPlotTresh(self):
    self.StatThreshDisp.setText("0.0")
    #determines if plot has been pressed and resets the % above threshold box"

  #################################################################################################
  ###########################################  Load & Settings  ###################################
  #################################################################################################

def loadInternalData(self):
    global GUIparams
    global AnalysisData

    # the signal for the combobox for data and model can trigger
    # even when the combobox is being cleared, so if that happens,
    # don't load data
    if self.datopts.currentIndex() == -1:
      return
    
    inpdict = {'GUIparams': GUIparams, 'AnalysisData':AnalysisData}
    Q = queue.Queue()
    thread = ThreadTools.dataLoadThread(Q,self.handleLoadThread,parent=self)
    thread.start()
    Q.put(inpdict)  


def unloadInternalData(self):
    global GUIparams
    global AnalysisData

    GUIparams = GUIopts(False, True)
    AnalysisData = DataHolder()
    GUIparams = GeneralOps.loadGUILabels(GUIparams)



def ErrorStyleChange():
    global GUIparams
    GUIparams.errorstyle = not GUIparams.errorstyle


def dataSourceChanged(self, flag):
  
  StatsPanelOps.update_data_opts(self,flag)

  if not flag:
    loadInternalData(self)
    StyleOps.enable_ani_button(button_obj = self.sceneExplorePush, guiobj = self, loc = 'SEPB')
    self.sceneExplorePush._animation.start()

    StyleOps.enable_ani_button(button_obj = self.ErrorS, guiobj = self, loc = 'EAB')
    self.ErrorS._animation.start()

    StyleOps.disable_ani_button(button_obj=self.extDatBtn, guiobj=self)
  else:
    unloadInternalData(self)
    StyleOps.disable_ani_button(button_obj=self.sceneExplorePush, guiobj=self)
    StyleOps.disable_ani_button(button_obj=self.RunStats, guiobj=self)
    StyleOps.disable_ani_button(button_obj=self.ErrorS, guiobj=self)
    StyleOps.enable_ani_button(button_obj = self.extDatBtn, guiobj = self, loc = 'EXDB')
    self.extDatBtn._animation.start()

def add_stats_box(self):

  global GUIparams
  global AnalysisData

  statContainer = QtWidgets.QFrame(self.main_CF)
  statContainerL = QtWidgets.QVBoxLayout(statContainer)
  #statContainer.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
  self.main_CL.addWidget(statContainer, 0, 0)

  #################################################################################################
  ###########################################  Data Loading Box  ##################################
  #################################################################################################
  
  self.datasetContainer = GUIComponents.AniGBox(statContainer)
  self.datasetContainer.setTitle('Data')
  self.datasetContainer.setObjectName('PB9')
  datasetContainerL = QtWidgets.QVBoxLayout(self.datasetContainer)
  statContainerL.addWidget(self.datasetContainer)
  

  #scrollData = QtWidgets.QScrollArea(self.datasetContainer)
  #scrollHolderD = QtWidgets.QFrame()
  #scrollHolderDL = QtWidgets.QGridLayout(scrollHolderD)
  
  self.sandDataContain = GUIComponents.AniGBox()
  self.extDataContain = GUIComponents.AniGBox()

  self.sandDataContain.setObjectName('sdc')
  self.extDataContain.setObjectName('edc')

  sandDataContainL = QtWidgets.QVBoxLayout(self.sandDataContain)
  extDataContainL = QtWidgets.QVBoxLayout(self.extDataContain)

  self.sandDataContain.setTitle('Exemplar data')
  self.extDataContain.setTitle('External data')

  self.sandDataContain.setCheckable(True)
  self.extDataContain.setCheckable(True)


  self.mdlbox = GUIComponents.SubBoxAni(self)
  self.datBox = GUIComponents.SubBoxAni(self)

  self.mdlbox.setObjectName('PB10')
  self.datBox.setObjectName('PB11')

  mdlboxL = QtWidgets.QVBoxLayout(self.mdlbox)
  databoxL = QtWidgets.QVBoxLayout(self.datBox)
  
  self.mdlopts = QtWidgets.QComboBox()
  self.datopts = QtWidgets.QComboBox()

  mdlboxL.addWidget(self.mdlopts)
  databoxL.addWidget(self.datopts)

  self.mdlbox.setTitle('Model selection')
  self.datBox.setTitle('Scenario selection')


  self.sceneExplorePush = GUIComponents.AniButton(self)
  self.sceneExplorePush.setObjectName('SEPB')
  self.sceneExplorePush._animation.setLoopCount(3)
  StyleOps.enable_ani_button(button_obj = self.sceneExplorePush, guiobj = self, loc = 'SEPB')
  self.sceneExplorePush._animation.start()
  
  self.sceneExplorePush.setText('Scenario Explorer')
  self.sceneExplorePush.clicked.connect(lambda: launch_explorer(self.mdlopts.currentText(), self.datopts.currentText()))

  #when options changed, change dataset
  self.datopts.currentIndexChanged.connect(lambda: loadInternalData(self))
  self.mdlopts.currentIndexChanged.connect(lambda: loadInternalData(self))



  self.sandDataContain.clicked.connect(lambda: dataSourceChanged(self,0))
  self.extDataContain.clicked.connect(lambda: dataSourceChanged(self,1))




  self.extDatBtn = GUIComponents.AniButton(self)
  self.extDatBtn.setText('Load external data')
  self.extDatBtn.clicked.connect(lambda: DialogComponents.launchIOWindow(self, AnalysisData, GUIparams))
  self.extDatBtn._animation.setLoopCount(3)
  self.extDatBtn.setObjectName('EXDB')
  StyleOps.disable_ani_button(button_obj=self.extDatBtn, guiobj=self)

  sandDataContainL.addWidget(self.mdlbox)
  sandDataContainL.addWidget(self.datBox)
  sandDataContainL.addWidget(self.sceneExplorePush)
  sandDataContainL.setMargin(0)
  sandDataContainL.setContentsMargins(0,0,0,0)
  extDataContainL.addWidget(self.extDatBtn)


  datasetContainerL.addWidget(self.sandDataContain)
  datasetContainerL.addWidget(self.extDataContain)


  #################################################################################################
  ###################################  Statistical Test Block  ####################################
  #################################################################################################
  
  self.AnalysisContainer = GUIComponents.AniGBox(statContainer)
  self.AnalysisContainer.setTitle(GUIparams.labels['OuterL'])
  self.AnalysisContainer.setObjectName('PB7')
  AnalysisContainerL = QtWidgets.QVBoxLayout(self.AnalysisContainer)
  statContainerL.addWidget(self.AnalysisContainer)

  self.scrollTests = QtWidgets.QScrollArea(self.AnalysisContainer)
  self.scrollTests.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
  self.scrollTests.setWidgetResizable(True)
  #scrollTests.horizontalScrollBar().setEnabled(False)

  self.scrollHolder = QtWidgets.QFrame()
  scrollHolderH=QtWidgets.QVBoxLayout(self.scrollHolder)

  self.CB_ErrorProp = QtWidgets.QCheckBox(GUIparams.labels["Box11L"])
  self.CB_MUF = QtWidgets.QCheckBox(GUIparams.labels["Box12L"])
  self.CB_AI = QtWidgets.QCheckBox(GUIparams.labels["Box13L"])
  self.CB_CUMUF = QtWidgets.QCheckBox(GUIparams.labels["Box14L"])
  self.CB_SMUF = QtWidgets.QCheckBox(GUIparams.labels["Box15L"])
  self.CB_SMUFAI = QtWidgets.QCheckBox(GUIparams.labels["Box16L"])
  self.CB_SITMUF = QtWidgets.QCheckBox(GUIparams.labels["Box17L"])
  self.CB_PAGE = QtWidgets.QCheckBox(GUIparams.labels["Box18L"])

  self.CB_ErrorProp.clicked.connect(self.update_errorB_text)

  scrollHolderH.addWidget(self.CB_ErrorProp)
  scrollHolderH.addWidget(self.CB_MUF)
  scrollHolderH.addWidget(self.CB_AI)
  scrollHolderH.addWidget(self.CB_CUMUF)
  scrollHolderH.addWidget(self.CB_SMUF)
  scrollHolderH.addWidget(self.CB_SMUFAI)
  scrollHolderH.addWidget(self.CB_SITMUF)
  scrollHolderH.addWidget(self.CB_PAGE)

  self.scrollTests.setWidget(self.scrollHolder)
  self.scrollTests.horizontalScrollBar().setEnabled(False)
  self.scrollTests.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)


  AnalysisContainerL.addWidget(self.scrollTests)



  #################################################################################################
  ###########################################  MBP & Iterations  ##################################
  #################################################################################################
    
  #self.SGSetContainer = QtWidgets.QGroupBox(statContainer)
  self.SGSetContainer = GUIComponents.AniGBox(statContainer)
  self.SGSetContainer.setTitle(GUIparams.labels["Box2L"])
  self.SGSetContainer.setObjectName('PB6')
  statContainerL.addWidget(self.SGSetContainer)
  SGS_L = QtWidgets.QVBoxLayout(self.SGSetContainer)

  # creates a box for label and iterations
  LIContainer = QtWidgets.QFrame(self.SGSetContainer)
  SGS_L.addWidget(LIContainer)
  LIL = QtWidgets.QGridLayout(LIContainer)

  MBPLabel = QtWidgets.QLabel(GUIparams.labels["Box21L"], LIContainer)
  self.MBPBox = QtWidgets.QLineEdit("", LIContainer)
  self.MBPBox.setMaxLength(4)
  LIL.addWidget(MBPLabel, 0, 0)
  LIL.addWidget(self.MBPBox, 0, 1)
  self.CBHolder.append(MBPLabel)
  self.CBHolder.append(self.MBPBox)
  self.MBPBox.setMaximumWidth(75)
  MBPLabel.setToolTip('Duration between balances')

  # iteration label and edit box
  IterLabel = QtWidgets.QLabel(GUIparams.labels["Box22L"], LIContainer)
  LIL.addWidget(IterLabel, 1, 0)
  self.IterBox = QtWidgets.QLineEdit("", LIContainer)

  self.CBHolder.append(IterLabel)
  self.CBHolder.append(self.IterBox)
  IterLabel.setToolTip('Requested quantity of calculated realizations')

  self.IterBox.setMaxLength(4)
  self.IterBox.setMaximumWidth(75)
  #self.IterBox.setFixedWidth(45)
  LIL.addWidget(self.IterBox, 1, 1)

  # generic element index
  self.GESelector = QtWidgets.QComboBox()
  self.GESelector.setFrame(0)
  self.GESelector.setMaximumWidth(75)
  GELabel = QtWidgets.QLabel(GUIparams.labels["Box23L"], LIContainer)

 
  LIL.addWidget(GELabel, 2, 0)
  LIL.addWidget(self.GESelector, 2, 1)

  self.CBHolder.append(GELabel)
  self.CBHolder.append(self.GESelector)
  self.GESelector.setToolTip('*Optional* - Index (row) \n of element to be analyzed')

  #offset index (optional)
  OLabel = QtWidgets.QLabel(GUIparams.labels["Box24L"], LIContainer)
  self.OBox = QtWidgets.QLineEdit("", LIContainer)
  self.OBox.setMaxLength(4)
  LIL.addWidget(OLabel, 3, 0)
  LIL.addWidget(self.OBox, 3, 1)
  self.OBox.setMaximumWidth(75)
  self.CBHolder.append(OLabel)
  self.CBHolder.append(self.OBox)
  OLabel.setToolTip(
      '*Optional* Delay before \n first material balance is calculated')

  # error push button
  self.ErrorS = GUIComponents.AniButton(self)
  self.ErrorS.setText(GUIparams.labels["Box25L"])
  self.ErrorS.setObjectName('EAB')
  # self.ErrorS.setStyleSheet('border:2px solid rgb(255,170,255);')
  SGS_L.addWidget(self.ErrorS)
  SGS_L.setMargin(0)
  SGS_L.setContentsMargins(0,0,0,0)
  self.ErrorS.setToolTip('Measurement error specification')
  self.ErrorS._animation.setLoopCount(3)

  #sets the border now for a later animation
  #if not done causes elements to shift when animation
  #is activated

  #self.ErrorS.setStyleSheet(grad + grad2)
  StyleOps.enable_ani_button(button_obj = self.ErrorS, guiobj = self, loc = 'EAB')
  self.ErrorS._animation.start()

  # Run stats button
  self.RunStats = GUIComponents.AniButton(self)
  self.RunStats.setObjectName('RSB')
  self.RunStats._animation.setLoopCount(3)
  self.RunStats.setText(GUIparams.labels["Box26L"])
  SGS_L.addWidget(self.RunStats)
  self.RunStats.setEnabled(0)
  StyleOps.disable_ani_button(button_obj=self.RunStats, guiobj=self)

  # group box for metric and location
  #MLContainer = QtWidgets.QGroupBox()


  #statContainerL.addWidget(self.StatDlg)
  statContainerL.addWidget(self.PB)

  #################################################################################################
  ###########################################  Size Policy  #######################################
  #################################################################################################

  #self.main_CL, statContainerL
  #Minimum, MinimumExpanding
  #self.AnalysisContainer.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
  #self.scrollHolder.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)
  #self.scrollTests.setSizePolicy(QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)

  statContainerL.setStretch(0,0)
  statContainerL.setStretch(1,1)
  statContainerL.setStretch(2,0)
  statContainerL.setStretch(3,0)

  #AnalysisContainerL





#################################################################################################
###########################################  Plot Column  #######################################
#################################################################################################
def add_plot_box(self):

  PlotContainer = QtWidgets.QFrame(self.main_CF)
  PlotContainerL = QtWidgets.QVBoxLayout(PlotContainer)
  self.main_CL.addWidget(PlotContainer, 0, 1)

  #################################################################################################
  ###########################################  Plot Controls  #####################################
  #################################################################################################
  
  self.PlotControls = GUIComponents.AniGBox(self)
  self.PlotControls.setTitle(GUIparams.labels["Box3L"])
  self.PlotControls.setMaximumHeight(200)
  self.PlotControls.setObjectName('PB5')
  PlotContainerL.addWidget(self.PlotControls)
  PlotControlL = QtWidgets.QHBoxLayout(self.PlotControls)

  self.mb1 = GUIComponents.SubBoxAni(self)
  self.mb1L = QtWidgets.QHBoxLayout(self.mb1)
  self.mb1.setObjectName('PB1')
  self.mb1.setEnabled(0)

  #self.mb1.setTitle(GUIparams.labels['Box31L'])


  self.metricBox = QtWidgets.QComboBox(self.mb1)
  self.metricBox.setMinimumWidth(50)

  #self.mb1L.setContentsMargins(10,15,10,15)
  self.mb1L.addWidget(self.metricBox)


  PlotControlL.addWidget(self.mb1)

  self.mb2 = GUIComponents.SubBoxAni(self)
  #self.mb2.setTitle(GUIparams.labels["Box32L"])
  self.mb2.setObjectName('PB2')
  self.mb2.setEnabled(0)


  self.mb2L = QtWidgets.QHBoxLayout(self.mb2)
  self.LocBox = QtWidgets.QComboBox(self.PlotControls)

  self.mb2L.addWidget(self.LocBox)
  #self.mb2L.setContentsMargins(10,15,10,15)
  PlotControlL.addWidget(self.mb2)
  self.LocBox.setMinimumWidth(50)

  self.mb3 = GUIComponents.SubBoxAni(self)
  self.mb3L = QtWidgets.QHBoxLayout(self.mb3)
  self.mb3.setObjectName('PB3')
  #self.mb3.setTitle(GUIparams.labels["Box33L"])
  self.NucIDBox = QtWidgets.QComboBox(self.PlotControls)
  self.mb3.setEnabled(0)

  self.mb3L.addWidget(self.NucIDBox)
  #self.mb3L.setContentsMargins(10,15,10,15)
  PlotControlL.addWidget(self.mb3)
  self.NucIDBox.setMinimumWidth(50)

  self.mb4 = GUIComponents.SubBoxAni(self)
  self.mb4L = QtWidgets.QHBoxLayout(self.mb4)
  #self.mb4L.setContentsMargins(10,15,10,15)
  self.mb4.setObjectName('PB4')
  #self.mb4.setTitle(GUIparams.labels["Box34L"])
  self.mb4.setEnabled(0)
  self.NumToPlot = QtWidgets.QComboBox(self.PlotControls)
  self.NumToPlot.setMinimumWidth(50)


  self.mb4L.addWidget(self.NumToPlot)

  PlotControlL.addWidget(self.mb4)

  self.PlotRunner = GUIComponents.AniButton(self)
  self.PlotRunner.setText('Plot')
  self.PlotRunner.setObjectName('PRB')
  PlotControlL.addWidget(self.PlotRunner)
  #PlotControlL.setVerticalSpacing(PlotControlL.verticalSpacing())
  self.PlotRunner.setEnabled(0)
  StyleOps.disable_ani_button(self,self.PlotRunner)

  #sets the border now for a later animation
  #if not done causes elements to shift when animation
  #is activated

  StyleOps.update_aniButton_styleSheet(self.PlotRunner,self.colordict,colorborder=0,isrunning=0,extraspace=13)

  #################################################################################################
  ###########################################  Plot Window  #######################################
  #################################################################################################
  


  self.canvas = PlotOps.MPLCanvas(self)
  self.navi_toolbar = NavigationToolbar(self.canvas, self)

  PlotContainerL.addWidget(self.canvas)
  PlotContainerL.addWidget(self.navi_toolbar, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
  #PlotContainerL.addWidget(QtWidgets.QPushButton(), alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
 
  #################################################################################################
  ###########################################  Threshold  #########################################
  #################################################################################################
  
  self.threshContainer = GUIComponents.AniGBox(self)
  self.threshContainer.setMaximumHeight(200)
  #self.threshContainer.setFixedWidth(self.PlotWindowSize)
  self.threshContainer.setTitle(GUIparams.labels["Box4L"])
  self.threshContainer.setObjectName('PB8')
  threshouterL = QtWidgets.QGridLayout(self.threshContainer)

  # set threshold

  self.StatThresh = QtWidgets.QLineEdit("", self.threshContainer)
  self.TL1 = QtWidgets.QLabel(GUIparams.labels["Box41L"])
  #self.TL1.setContentsMargins(5,15,5,15)
  self.StatThresh.setMaxLength(4)
  self.StatThresh.setMaximumWidth(75)
  threshouterL.addWidget(self.TL1, 0, 0)
  threshouterL.addWidget(self.StatThresh, 1, 0)
  self.TL1.setToolTip("Parameter to find data above this value")
  self.StatThresh.setEnabled(0)

  # set precision, more work to be done here in the future
  self.StatPrec = QtWidgets.QLineEdit("0.5", self.threshContainer)
  self.TL2 = QtWidgets.QLabel("Sensitivity") #HACK: PM: fix this please
  #self.TL2.setContentsMargins(10,15,10,15)
  self.StatPrec.setMaxLength(4)
  self.StatPrec.setMaximumWidth(75)
  threshouterL.addWidget(self.TL2, 0, 1)
  threshouterL.addWidget(self.StatPrec, 1, 1)
  self.StatPrec.setEnabled(0)
  self.TL2.setToolTip("Sensitivity helps calibrate Page's Trend Test")

  
  # threshold display
  self.TL3 = QtWidgets.QLabel(GUIparams.labels["Box42L"], self.threshContainer)
  #self.TL3.setContentsMargins(10,15,10,15)
  self.StatThreshDisp = QtWidgets.QLineEdit("0.00", self.threshContainer)
  self.StatThreshDisp.setAutoFillBackground(True)
  self.StatThreshDisp.setMaximumWidth(75)
  threshouterL.addWidget(self.TL3, 0, 2)
  threshouterL.addWidget(self.StatThreshDisp, 1, 2)
  self.StatThreshDisp.setEnabled(0)
  self.TL3.setToolTip("Displays % of data above threshold")

  # calculate button
  self.CalcThresh = GUIComponents.AniButton(self)
  #self.CalcThresh.setContentsMargins(50,65,50,65)
  self.CalcThresh.setMaximumWidth(200)
  self.CalcThresh.setText(GUIparams.labels["Box43L"])
  self.CalcThresh.setObjectName('CTB')
  self.CalcThresh.setEnabled(0)
  StyleOps.disable_ani_button(self,self.CalcThresh)
  self.CalcThresh.clicked.connect(self.RunStatThresh)  
  self.CalcThresh.setToolTip("Calculates data above inputted Threshold")
  threshouterL.addWidget(self.CalcThresh, 0, 3, 2, 1)


  PlotContainerL.addWidget(self.threshContainer) 
  PlotContainerL.setStretch(0,0)
  PlotContainerL.setStretch(1,1)
  PlotContainerL.setStretch(2,0)
  PlotContainerL.setStretch(3,0)






  
def launch_explorer(mdlname, datname):
  global GUIparams
  ss = ScenarioSelector.SceneExamine(mdlname, datname, GUIparams)
  ss.setWindowModality(QtCore.Qt.ApplicationModal)
  ss.exec_()


def launchMAPIT():
  app = QtWidgets.QApplication(sys.argv)
  #app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

  #splash
  x = str(Path(__file__).resolve().parents[1])
  F = os.path.join(x, 'docs_v2', 'codeAssets', 'splash3.png')
  splash_pix = QtGui.QPixmap(F)
  G = QtWidgets.QApplication.instance().devicePixelRatio()
  splash_pix.setDevicePixelRatio(G)
  geometry = QtWidgets.QApplication.primaryScreen().size()
  splash_pix = splash_pix.scaledToWidth(int(geometry.width()*0.35*G),QtCore.Qt.SmoothTransformation)  
  splash = QtWidgets.QSplashScreen(splash_pix)
  splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint
                        | QtCore.Qt.FramelessWindowHint)
  splash.setEnabled(False)
  


  F = os.path.join(x, 'docs_v2', 'codeAssets', 'SNL_Stacked_Black_Blue2.jpg')
  splash.setWindowIcon(QtGui.QIcon(F))

  progressBar = QtWidgets.QProgressBar(splash)
  # 378, 323
  # 1890, 1614

  # 125, 
  # 25, 288, 328, 25
  #x,y,w,h
  progressBar.setMaximum(100)
  progressBar.setGeometry(splash_pix.width()*0.10/G,
                          splash_pix.height()*0.90/G,
                          splash_pix.width()*0.80/G, splash_pix.height()*0.075/G)

  splash.show()

  barSty = """
    QProgressBar{
    border-radius: 5px;
    border-style: solid;
    border-color: rgb(211,211,211);
    background-color: rgb(200,200,200);
    border-width: 2px;
    text-align: center;
    color: black;
    }
    QProgressBar::chunk{
    background-color: #D9B36D;
    }
    """

  progressBar.setStyleSheet(barSty)
  t = 0

  while t < 3:
    progressBar.setValue(t / 3 * 100)
    app.processEvents()
    time.sleep(0.10)
    t += 0.10

  progressBar.setValue(100)


  splash.close()

  widget = LaunchGUI()

  try:
    settings = QtCore.QSettings("current", "mapit")
    widget.currentFontSize = int(settings.value("fontsize"))
    widget.restoreGeometry(settings.value("geometry"))
    StyleOps.changeFontSize(widget,0)
    if settings.value("theme") == "dark":
      widget.MakeDark.setChecked(1)
    else:
      widget.MakeLight.setChecked(1) 
    StyleOps.ChangeColor(widget)
  except:
    StyleOps.RestoreWindow(widget)

  widget.show()
  widget.activateWindow()

  sys.exit(app.exec_())

if __name__ == "__main__":
  launchMAPIT()
