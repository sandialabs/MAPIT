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

sys.path.append(str(Path(sys.argv[0]).resolve().parents[2]))





from PySide2 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import time

import MAPIT_internal.core.Preprocessing as Preprocessing

from MAPIT_internal.core import StatsTests as Tests
from MAPIT_internal.core import AuxFunctions as Aux

from MAPIT_internal.GUI.IOWizard import IOWizardMain 
#from MAPIT_internal.GUI.IOWizardMat import IOWizardMainMat
from MAPIT_internal.GUI import PlotOps, StyleOps, GeneralOps, DialogComponents, StatsPanelOps, ScenarioSelector, AnimationTools, ErrorPanelOps









class GUIopts:
  pass

class DataHolder:
  pass


class customExecp(Exception):
  pass
#https://stackoverflow.com/questions/19442443/busy-indication-with-pyqt-progress-bar


GUIparams = GUIopts()

#for now ignore the case
#of multiple species analysis

#UraniumData = DataHolder()
#PlutoniumData = DataHolder()
#GenericData = DataHolder()

AnalysisData = DataHolder()

class StatGUIInterface:
  def runAnalysisPipe(self):

    global AnalysisData
    global GUIparams

    if len(self.OBox.text()) > 0:
      AnalysisData.offset = int(self.OBox.text())
    else:
      AnalysisData.offset = 0

    mbaTime = int(self.MBPBox.text())
    IT = int(self.IterBox.text())

    #processed terms have been adjusted according to offset (if applicable)
    #AnalysisData should be loaded prior to this either from the scene select
    #or a csv/mat loader (not currently implemented)
    
    processedInput, processedInputTimes, \
    processedInventory, processedInventoryTimes, \
    processedOutput, processedOutputTimes, \
    GUIparams = Preprocessing.FormatInput(rawInput = AnalysisData.rawInput,
                                          rawInventory = AnalysisData.rawInventory,
                                          rawOutput = AnalysisData.rawOutput,
                                          rawInputTimes = AnalysisData.rawInputTimes,
                                          rawInventoryTimes = AnalysisData.rawInventoryTimes,
                                          rawOutputTimes = AnalysisData.rawOutputTimes,
                                          dataOffset = AnalysisData.offset,
                                          GUIObject = self,
                                          GUIparams = GUIparams)

    


    GLoc, GUIparams = StatsPanelOps.verifyGUIRequests(GUIObject = self, GUIparams = GUIparams)
    
    AnalysisData.ErrorMatrix = StatsPanelOps.getGUIErrorVals(self,
                                                            len(processedInput),
                                                            len(processedInventory),
                                                            len(processedOutput),
                                                            GLoc)   

    


    AnalysisData.inputAppliedError = Preprocessing.SimErrors(input = processedInput, 
                                                              ErrorMatrix =  AnalysisData.ErrorMatrix, 
                                                              iterations = IT,
                                                              GUIObject = self,
                                                              GUIDispString = 'input errors')

    AnalysisData.inventoryAppliedError = Preprocessing.SimErrors(input = processedInventory,
                                                                ErrorMatrix =  AnalysisData.ErrorMatrix, 
                                                                iterations = IT,
                                                                GUIObject = self,
                                                                GUIDispString = 'inventory errors')


    AnalysisData.outputAppliedError = Preprocessing.SimErrors(input = processedOutput, 
                                                              ErrorMatrix =  AnalysisData.ErrorMatrix, 
                                                              iterations = IT,
                                                              GUIObject = self,
                                                              GUIDispString = 'output errors')



    doMUF, doCUMUF, doSEID, doSITMUF, doPage = StatsPanelOps.getRequestedTests(GUIObject = self)

    if doMUF == 1:
      AnalysisData.MUF = Tests.MUF(inputAppliedError = AnalysisData.inputAppliedError,
                                  inventoryAppliedError= AnalysisData.inventoryAppliedError,
                                  outputAppliedError = AnalysisData.outputAppliedError,
                                  processedInputTimes = processedInputTimes,
                                  processedInventoryTimes = processedInventoryTimes,
                                  processedOutputTimes = processedOutputTimes,
                                  MBP = mbaTime,
                                  GUIObject = self,
                                  GUIparams = GUIparams)

    if doCUMUF == 1:
      AnalysisData.CUMUF = Tests.CUMUF(AnalysisData.MUF,
                                      GUIObject = self,
                                      GUIparams = GUIparams)
                 
    if doSEID == 1:
      AnalysisData.SEMUF, \
      AnalysisData.SEMUFContribR, \
      AnalysisData.SEMUFContribS, \
      AnalysisData.SEMUFContribI = Tests.SEMUF(inputAppliedError = AnalysisData.inputAppliedError,
                                              inventoryAppliedError= AnalysisData.inventoryAppliedError,
                                              outputAppliedError = AnalysisData.outputAppliedError,
                                              processedInputTimes = processedInputTimes,
                                              processedInventoryTimes = processedInventoryTimes,
                                              processedOutputTimes = processedOutputTimes,
                                              MBP = mbaTime,
                                              ErrorMatrix = AnalysisData.ErrorMatrix,
                                              GUIObject = self,
                                              GUIparams= GUIparams)

    if doSITMUF == 1:

      AnalysisData.SITMUF = Tests.SITMUF(inputAppliedError = AnalysisData.inputAppliedError,
                                                            inventoryAppliedError= AnalysisData.inventoryAppliedError,
                                                            outputAppliedError = AnalysisData.outputAppliedError,
                                                            processedInputTimes = processedInputTimes,
                                                            processedInventoryTimes = processedInventoryTimes,
                                                            processedOutputTimes = processedOutputTimes,
                                                            ErrorMatrix = AnalysisData.ErrorMatrix,
                                                            MBP = mbaTime,
                                                            MUF = AnalysisData.MUF,
                                                            GUIObject = self,
                                                            GUIparams= GUIparams)  

      MBPs = Aux.getMBPs(processedInputTimes,processedInventoryTimes,processedOutputTimes,mbaTime)
      AnalysisData.Page = Tests.PageTrendTest(AnalysisData.SITMUF,mbaTime,MBPs)


                                                                       


    StatsPanelOps.preparePlotterOptions(self, doMUF,doCUMUF,doSEID,doSITMUF,doPage,GUIparams)
    self.CalcThresh.PassLoc('CTB')
    self.CalcThresh._animation.start()
    self.CalcThresh.setEnabled(1)





class customExecp(Exception):
    pass

class SubBoxAni(QtWidgets.QGroupBox):
  """
        This class defines animated boxes
        within MAPIT. Specifically, the
        boxes that contain dropdown elements
        in the plot area.

        Animation functions largely control
        changing border colors to bring
        attention to certain areas of MAPIT.

        A second animation has the border react
        when the mouse enters the area.
  """

  def __init__(self, parent):
    super(SubBoxAni, self).__init__()

    #note there animation values (start,end)
    #are required to be floats for some reason

    self._animation = QtCore.QVariantAnimation()
    self._animation.setStartValue(0.0)
    self._animation.setEndValue(1.0)
    self._animation.setDuration(150)
    self._animation.setLoopCount(1)
    self._animation.valueChanged.connect(
        lambda: AnimationTools.runAnimation(self))

    self.IsActive = 0

  def PassLoc(self, loc):
    self.Loc = loc

  def enterEvent(self, event):
    #on enter make border lighter
    if self.IsActive == 1:
      self._animation.setDirection(QtCore.QAbstractAnimation.Forward)
      self._animation.start()
    super().enterEvent(event)

  def leaveEvent(self, event):
    #on leave make border darker
    if self.IsActive == 1:
      self._animation.setDirection(QtCore.QAbstractAnimation.Backward)
      self._animation.start()
    super().leaveEvent(event)

  def ChangeActive(self, newState):
    self.IsActive = newState


class AniButton(QtWidgets.QPushButton):
  """
        Class for animated buttons.

        These buttons animate when first active.

        They also have a linear gradient of color
        that changes once the mouse enters the area.
  """

  def __init__(self, parent):
    super(AniButton, self).__init__()

    self.IsDone = 0

    #set animation parameters
    self._animation = QtCore.QVariantAnimation()
    self._animation.setStartValue(0.0)
    self._animation.setEndValue(2.0)
    self._animation.setDuration(1000)
    self._animation.valueChanged.connect(
        lambda: AnimationTools.runDualAnimation(self))

    self._animation.finished.connect(self.UpdateIState)
    self._animation.setLoopCount(10)

    self._animation2 = QtCore.QVariantAnimation()
    self._animation2.setStartValue(0.0)
    self._animation2.setEndValue(1.0)
    self._animation2.setDuration(150)
    self._animation2.valueChanged.connect(
        lambda: AnimationTools.GradButtonChange(self))

  def UpdateIState(self):
    #check if the initial border animation
    #has finished
    self.IsDone = 1

  def enterEvent(self, event):
    self._animation2.setDirection(QtCore.QAbstractAnimation.Forward)
    self._animation2.start()

    super().enterEvent(event)

  def leaveEvent(self, event):

    self._animation2.setDirection(QtCore.QAbstractAnimation.Backward)
    self._animation2.start()

    super().enterEvent(event)

  def PassLoc(self, loc):
    self.Loc = loc


class AniGBox(QtWidgets.QGroupBox):
  """
        Box containing multiple items that
        animates to bring attention. These
        are the larger 'containers' like
        the area that says 'plot controls'
  """

  def __init__(self, parent=None):
    super().__init__(parent)

    self._animation = QtCore.QVariantAnimation()
    self._animation.setStartValue(0.0)
    self._animation.setEndValue(2.0)
    self._animation.setDuration(1000)
    self._animation.valueChanged.connect(
        lambda: AnimationTools.runAnimationSB(self))

    self._animation.setLoopCount(10)

    self.Loc = 0

  def PassLoc(self, loc):
    """
            In QT widgets can be identified by an object name.
            This function gives some finer control over setting
            widget border colors.
    """

    self.Loc = loc

    if self.Loc != 0:

      grad2 = "border-color: rgb({value},{value2},{value3});".format(value=211,value2=211,value3=211) +\
     "border-width: 5px;" +\
    "border-style: solid;" +\
    "padding: 6px;" +\
    "color: black;" +\
    "border-radius: 3px;}"

      if self.window().MakeLight.isChecked() == 0:
        grad2 = grad2.replace('rgb(211,211,211)', 'rgb(66,66,66)')

      self.setStyleSheet(
          "QWidget#{VAL}".format(VAL=self.Loc) + "{" + grad2 +
          "QWidget#{VAL}".format(VAL=self.Loc) +
          ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")


class MssgRunner(QtWidgets.QLineEdit):
  """
        The class for the message bar
        at the bottom of MAPIT.

        Contains an animation that runs
        at startup to notify user that
        importing data is required.
  """

  def __init__(self, parent=None):
    super().__init__(parent)

    self.color1 = QtGui.QColor(0, 50, 0)
    self.color2 = QtGui.QColor(0, 150, 0)

    self._animation = QtCore.QVariantAnimation()
    self._animation.setStartValue(0.0)
    self._animation.setEndValue(2.0)
    self._animation.setDuration(1000)
    self._animation.valueChanged.connect(
        lambda: AnimationTools.runMsgAnimation(self))

    self._animation.setLoopCount(10)

  def UpdateDispText(self, txt):

    if self.window().MakeLight.isChecked() == 1:
      R = 211
    else:
      R = 66

    self.setText(txt)

    qss = """
                :disabled{color: rgb(0,0,0);
    """
    grad = "border-color: rgb({value},{value2},{value3});".format(value=R,value2=R,value3=R) +\
           "border-width: 5px;" +\
          "border-style: solid;" +\
          "padding: 6px;" +\
          "border-radius: 3px;"

    qss += grad

    if self.window().MakeLight.isChecked() == 1:
      qss += 'background-color: rgb(239,239,239);color: black;}'
    else:
      qss += 'background-color: rgb(52,52,52);color: white;}'

    self.setStyleSheet(qss)









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
    global AnalysisData


    self.CBHolder = []  #this is just for some of the style stuff later on
    self.hasRunIO = 0
    self.PuLoc = -1
    self.ULoc = -1
    self.GLoc = -1
    self.HasRunOnce = 0
    self.HasRunErrors = 0
    self.launch_master_window()



    self.RunStats.clicked.connect(lambda: StatGUIInterface.runAnalysisPipe(self))
    self.ErrorS.clicked.connect(self.InitErrors)
    self.PlotRunner.clicked.connect(lambda: PlotOps.ExecPlot(self,GUIparams,AnalysisData))
    self.metricBox.activated.connect(lambda: PlotOps.UpdateLocOpts(self,GUIparams)) #TODO: CUMUF here


    


    

    #
    x = Path(sys.argv[0]).resolve().parents[1]
    F = os.path.join(x, 'docs_v2','source', 'assets', 'codeAssets', 'SNL_Stacked_Black_Blue2.jpg')
    self.setWindowIcon(QtGui.QIcon(F))

    loadDlgBox = QtWidgets.QMessageBox()
    loadDlgBox.setWindowIcon(QtGui.QIcon(F))
    loadDlgBox.setIcon(QtWidgets.QMessageBox.Question)
    loadDlgBox.setText('Select data for analysis \n')
    loadDlgBox.setInformativeText('You may select your own data (.csv, .mat, .npz supported) or from included SNL generated datasets')
    CD = loadDlgBox.addButton('Own data',QtWidgets.QMessageBox.ResetRole) #this is arbitrary, but if accept and reject roles aren't present then the red X to close the dialog wont work
    #MD = loadDlgBox.addButton('.mat dataset',QtWidgets.QMessageBox.ApplyRole)
    SC = loadDlgBox.addButton('SNL curated dataset',QtWidgets.QMessageBox.RejectRole)
    QC = loadDlgBox.addButton('Quit', QtWidgets.QMessageBox.NoRole)

    loadDlgBox.exec()

    DoRun = 1

    if loadDlgBox.clickedButton() == CD:
        self.IOWindow()
    # elif loadDlgBox.clickedButton() == MD:
    #     self.IOWindowM()
    elif loadDlgBox.clickedButton() == SC:
        self.ScenarioSelector()
    else:
        sys.exit()


    if DoRun == 1:
        self.show()
    else:
        raise customExcep("No dataset selected, please rerun MAPIT")




    # required or changing borders causes expansion
    #self.mb4.setFixedWidth(self.mb4.sizeHint().width() * 2)



  def force_muf_enabled(self):
    if (self.CB_CUMUF.isChecked() or 
      self.CB_SITMUF.isChecked()):
        self.CB_MUF.setChecked(1)
        self.CB_MUF.setEnabled(0)
    else:
      self.CB_MUF.setEnabled(1)

  def force_page_reqs(self):
    if self.CB_PAGE.isChecked():
      self.CB_MUF.setChecked(1)
      self.CB_SITMUF.setChecked(1)
      self.CB_MUF.setEnabled(0)
      self.CB_SITMUF.setEnabled(0)
    else:
      self.CB_MUF.setEnabled(1)
      self.CB_SITMUF.setEnabled(1)


  def InitErrors(self):
    """
            Function to select
            errors for imported or
            scenario data.
    """

    global GUIparams


    self.RunStats.setEnabled(
        1)  #flag to show that the calc has run at least once


    if self.HasRunErrors == 1:  #if has run previously get those values
      pastEVals = np.zeros((self.EP.rowCount(), 2))
      for i in range(0, self.EP.rowCount()):
        for j in range(0, 2):
          if self.EP.item(i, j) is None:
            pastEVals[i, j] = 0
          else:
            pastEVals[i, j] = self.EP.item(i, j).text()


    #stop animation if running
    if (self.SGSetContainer._animation.currentLoopTime()
        == self.SGSetContainer._animation.duration()) and (
            self.SGSetContainer._animation.currentLoop() >=
            self.SGSetContainer._animation.loopCount() - 1):
      None
    else:
      self.SGSetContainer._animation.setLoopCount(1)
      self.AnalysisContainer._animation.setLoopCount(1)
      self.ErrorS._animation.setLoopCount(1)

    self.ErrorPane = QtWidgets.QDialog()

    ep_L = QtWidgets.QVBoxLayout(self.ErrorPane)

    # errors for dropdown
    ErrorBox = [
        '0.5', '1.0', '3.0', '5.0', '10.0', '15.0', '20.0', '25.0', '50.0'
    ]

    # pane for all errors, all ins, outs, invs
    BContain = QtWidgets.QGroupBox(self.ErrorPane)
    bc_L = QtWidgets.QVBoxLayout(BContain)
    ep_L.addWidget(BContain)
    BContain.setTitle("Mass error control")

    # pane for all errors
    AllError = QtWidgets.QGroupBox(BContain)
    AE_L = QtWidgets.QGridLayout(AllError)
    AllError.setTitle("All errors")

    AllRandLabel = QtWidgets.QLabel("Random Errors")
    AllSysLabel = QtWidgets.QLabel("Systematic Errors")

    self.AllRand = QtWidgets.QComboBox(AllError)
    self.AllSys = QtWidgets.QComboBox(AllError)

    self.AllRand.addItems(ErrorBox)
    self.AllSys.addItems(ErrorBox)
  
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

    InpRandLabel = QtWidgets.QLabel("Random Errors")
    InpSysLabel = QtWidgets.QLabel("Systematic Errors")

    self.InpRand = QtWidgets.QComboBox(InpError)
    self.InpSys = QtWidgets.QComboBox(InpError)

    self.InpRand.addItems(ErrorBox)
    self.InpSys.addItems(ErrorBox)

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

    InvRandLabel = QtWidgets.QLabel("Random Errors")
    InvSysLabel = QtWidgets.QLabel("Systematic Errors")

    self.InvRand = QtWidgets.QComboBox(InvError)
    self.InvSys = QtWidgets.QComboBox(InvError)

    self.InvRand.addItems(ErrorBox)
    self.InvSys.addItems(ErrorBox)

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

    OutRandLabel = QtWidgets.QLabel("Random Errors")
    OutSysLabel = QtWidgets.QLabel("Systematic Errors")

    self.OutRand = QtWidgets.QComboBox(OutError)
    self.OutSys = QtWidgets.QComboBox(OutError)

    self.OutRand.addItems(ErrorBox)
    self.OutSys.addItems(ErrorBox)

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
    x = Path(sys.argv[0]).resolve().parents[1]
    self.EP.setColumnCount(2)
    self.EP.setHorizontalHeaderLabels(['Rand ', 'Sys'])
    #self.EP.setHorizontalHeaderLabels(GUIparams.rowNames)



    self.EP.setRowCount(TotalLocs + 2)
    ep_L.addWidget(self.EP)

    x = Path(sys.argv[0]).resolve().parents[1]

    self.EP.setVerticalHeaderLabels(GUIparams.rowNames)
    self.PlotLocLabels = list(
        filter(len, GUIparams.rowNames)
    )  #remove spaces which don't serve a purpose in the plotter dropdown

    # set the initial table items
    # the 2 and 31 index are separator rows
    if self.HasRunErrors == 0:
      for i in range(0, self.EP.rowCount()):
        for j in range(0, TotalLocs + 2):
          if self.EP.verticalHeaderItem(j).text() != '' and self.EP.horizontalHeaderItem(i) is not None:
            self.EP.setItem(j, i, QtWidgets.QTableWidgetItem(str(0.5)))

    if self.HasRunErrors == 1:
      for i in range(np.shape(pastEVals)[0]):
        for j in range(np.shape(pastEVals)[1]):
          if pastEVals[i, j] != 0:
            self.EP.setItem(i, j, QtWidgets.QTableWidgetItem(str(pastEVals[i, j])))

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
    self.ErrorPane.setWindowModality(QtCore.Qt.ApplicationModal)
    self.ErrorPane.finished.connect(self.RunStats._animation.start)
    self.ErrorPane.resize(700, 750)
    self.ErrorPane.show()
    self.StatDlg.UpdateDispText('Ready to execute')
    self.HasRunErrors = 1
    

  def ScenarioSelector(self):
    """
            This function launches the
            scenario selector and sets
            some GUI elements.
    """


    global AnalysisData
    global GUIparams


    self.ErrorS.setEnabled(1)
    QtCore.QCoreApplication.instance().processEvents()
    SS = ScenarioSelector.SceneSelect(self)
    SS.setWindowModality(QtCore.Qt.ApplicationModal)
    SS.exec_()
    self.StatDlg._animation.stop()
    self.StatDlg._animation.updateCurrentValue(2)
    self.StatDlg.UpdateDispText('Waiting for calculation setup...')

    AnalysisData.rawInventory = SS.Inventories
    AnalysisData.rawInput = SS.Inputs
    AnalysisData.rawOutput = SS.Outputs

    AnalysisData.rawInventoryTimes = SS.InventoriesT
    AnalysisData.rawInputTimes = SS.InputsT
    AnalysisData.rawOutputTimes = SS.OutputsT

    GUIparams.sceneName = SS.sceneName
    GUIparams.nInputLocations = np.shape(AnalysisData.rawInput)[0]
    GUIparams.nInventoryLocations =  np.shape(AnalysisData.rawInventory)[0]
    GUIparams.nOutputLocations = np.shape(AnalysisData.rawOutput)[0]
    GUIparams.nTotalLocations = np.shape(AnalysisData.rawInput)[0] + np.shape(AnalysisData.rawInventory)[0] + np.shape(AnalysisData.rawOutput)[0]

    F = os.path.join(x, 'data', 'fuel_fab', GUIparams.sceneName, 'auxData.npz')
    A = np.load(F)
    GUIparams.rowNames = A['arr2']
    self.GESelector.addItem("U")
    #self.liH = ['U'] 
    GUIparams.eleList = ['U']
    GUIparams.nInferredEles = 1






    #disable some checkboxes for fuel fab scenario
    #fuel fab only has uranium and some other
    #non actinide materials



    #PassLoc is used to setup for the animation of
    #individual elements. Not specifying the name
    #can cause children elements to inherit the style
    #leading to undesireable behavior
    self.SGSetContainer.PassLoc('PB6')
    self.SGSetContainer._animation.start()

    self.AnalysisContainer.PassLoc('PB7')
    self.AnalysisContainer._animation.start()

    self.ErrorS.PassLoc('EAB')
    self.ErrorS._animation.start()

  def IOWindow(self):
    """
            This function launches the IOWindow
            for .csv input (IOWizard.py)
    """

    global AnalysisData
    global GUIparams

    self.statusBar().setStyleSheet('')

    QtCore.QCoreApplication.instance().processEvents()

    self.ErrorS.setEnabled(1)
    Wizard = IOWizardMain(self)

    # blocks input to main GUI while IO is active
    Wizard.setWindowModality(QtCore.Qt.ApplicationModal)
    Wizard.exec_()

    w = QtWidgets.QProgressDialog("Importing data, please wait...","Abort",0,0,self)
    w.setWindowModality(QtCore.Qt.ApplicationModal)

    w.show()
    time.sleep(0.10)
    QtCore.QCoreApplication.instance().processEvents()
    AnalysisData.rawInput, AnalysisData.rawInputTimes, \
    AnalysisData.rawInventory, AnalysisData.rawInventoryTimes, \
    AnalysisData.rawOutput, AnalysisData.rawOutputTimes = GeneralOps.processWizardData(Wizard)
    w.close()

    GUIparams.nInputLocations, GUIparams.nInventoryLocations, \
    GUIparams.nOutputLocations, GUIparams.nTotalLocations, \
    GUIparams.rowNames = GeneralOps.processWizardGUI(AnalysisData,Wizard)

    eleNames = []
    eleMax = 1
    if len(AnalysisData.rawInput[0].shape) > 1:
      eleMax = len(AnalysisData.rawInput[0].shape[1])

    if len(Wizard.EleVec_IN) != eleMax:
      for G in range(eleMax):
        self.GESelector.addItem(str(G))
        eleNames.append('Element '+str(G))
    else:
      for G in range(eleMax):
        self.GESelector.addItem(Wizard.EleVec_IN[G])
        eleNames.append(Wizard.EleVec_IN[G])

    GUIparams.nInferredEles = eleMax
    GUIparams.eleList = eleNames


    self.StatDlg._animation.stop()
    self.StatDlg._animation.updateCurrentValue(2)

    self.SGSetContainer.PassLoc('PB6')
    self.SGSetContainer._animation.start()

    self.AnalysisContainer.PassLoc('PB7')
    self.AnalysisContainer._animation.start()

    self.ErrorS.PassLoc('EAB')

    self.ErrorS._animation.start()


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

    x = Path(sys.argv[0]).resolve().parents[1]
    F = os.path.join(x, 'docs','assets', 'codeAssets', 'SNL_Horizontal_Black_Blue.jpg')
    banner = QtGui.QPixmap(F)

    banner = banner.scaled(banner.size() * 0.6)
    label.setPixmap(banner)
    CPL.addWidget(label, 0, 0, 1, 2)

    N1 = QtWidgets.QLineEdit()
    N1.setReadOnly(1)
    N1.setText('Nathan Shoman')

    N2 = QtWidgets.QLineEdit()
    N2.setReadOnly(1)
    N2.setText('nshoman@sandia.gov')

    CPL.addWidget(N1, 1, 0)
    CPL.addWidget(N2, 1, 1)

    B1 = QtWidgets.QLineEdit()
    B1.setReadOnly(1)
    B1.setText('Benjamin Cipiti')

    B2 = QtWidgets.QLineEdit()
    B2.setReadOnly(1)
    B2.setText('bbcipit@sandia.gov')

    CPL.addWidget(B1, 2, 0)
    CPL.addWidget(B2, 2, 1)

    CheckPrint.show()





  def RunTable(self):
    """
            Function calling the error selection
            function.
    """
    dlg = DialogComponents.ViewErrorTabs(self, AnalysisData, GUIparams)
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
    self.main_CF = QtWidgets.QFrame(self)




#    geometry = QtGui.qApp.desktop().availableGeometry(self)

    geometry = QtWidgets.QApplication.primaryScreen().size()
    self.resize(round(geometry.width()*0.65),round(geometry.height()*0.65))
    # self.resize(
    #     1400, 900
    # )  #the app is set as fixed with due to some scaling issues, this might cause problems
    #with smaller screens and require changing in the future
    self.setCentralWidget(self.main_CF)
    self.main_CL = QtWidgets.QGridLayout(self.main_CF)
    #self.main_CL.setColumnMinimumWidth(0, geometry.width() * 0.50)
    self.main_CL.setColumnStretch(0,7)
    self.main_CL.setColumnStretch(1,4)

    self.setWindowTitle(
        '(M)aterial (A)ccountancy (P)erformance (I)ndicator (T)oolkit')

    QtCore.QCoreApplication.instance().processEvents()

    self.statusBar().setSizeGripEnabled(True)
    self.PB = QtWidgets.QProgressBar(self)
    # helps shorten the progress bar
    #self.PB.setFixedWidth(self.PB.sizeHint().width() * 2)
    self.PB.setAlignment(QtCore.Qt.AlignCenter)
    self.statusBar().addPermanentWidget(self.PB)
    self.PB.setValue(0)
    self.PB.setMaximumWidth(250)

    # menubar
    menubar = self.menuBar()
    menu = QtWidgets.QMenu("File", self)
    menubar.addMenu(menu)

    self.TabOpt = QtWidgets.QMenu("Tabular Data View", self)
    menubar.addMenu(self.TabOpt)

    self.TabView = QtWidgets.QAction("Error Contribution", self)
    self.TabView.triggered.connect(self.RunTable)
    
    self.TabOpt.addAction(self.TabView)
    self.TabOpt.setToolTip('Sigma MUF calculation required')
    self.TabView.setEnabled(0)

    themeOpt = QtWidgets.QMenu("Theme", self)
    menubar.addMenu(themeOpt)

    # SceneOpt = QtWidgets.QMenu("Select Scenario", self)
    # menubar.addMenu(SceneOpt)

    # SceneAction = QtWidgets.QAction("Load", self)
    # SceneAction.triggered.connect(self.ScenarioSelector)
    # SceneOpt.addAction(SceneAction)

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
    self.MakeLight.setChecked(1)
    TG.triggered.connect(lambda: StyleOps.ChangeColor(self))

    # IOAction = QtWidgets.QAction("Load Data (.csv)", self)
    # IOAction.setStatusTip("Select .csv data to load for analysis")
    # IOAction.triggered.connect(self.IOWindow)
    # menu.addAction(IOAction)
    #
    # IOAction2 = QtWidgets.QAction("Load Data (.mat)", self)
    # IOAction2.setStatusTip("Select .mat data to load for analysis")
    # IOAction2.triggered.connect(self.IOWindowM)
    # menu.addAction(IOAction2)

    self.ExportDat = QtWidgets.QAction("Save Data", self)
    menu.addAction(self.ExportDat)
    self.ExportDat.triggered.connect( lambda: GeneralOps.SaveStats(self,AnalysisData,GUIparams))
    self.ExportDat.setEnabled(0)



    add_stats_box(self)
    add_plot_box(self)

    self.StatDlg = MssgRunner(self)
    self.StatDlg.setMaximumWidth(450)
    self.StatDlg._animation.start()
    self.StatDlg.UpdateDispText('Waiting for data import')
    self.StatDlg.setEnabled(0)
    self.statusBar().addWidget(self.StatDlg)
    #self.CBHolder.append(menu)


    StyleOps.setInitialStyle(self)
    sysPalette = QtGui.QPalette()
    if sum(sysPalette.base().color().getRgb()[0:3]) != 765:
      self.MakeLight.setChecked(0)
      self.MakeDark.setChecked(1)
      StyleOps.ChangeColor(self)

  def RunStatThresh(self):
    #call the function to update the threshold statistics
    dh, _ = PlotOps.getData(self,GUIparams,AnalysisData)
    self.canvas.update_thresh(float(self.StatThresh.text()), dh[1])


def add_stats_box(self):
  """
        This function places some of the
        main MAPIT GUI elements.
    """

  statContainer = QtWidgets.QGroupBox(self.main_CF)
  statContainer.setTitle('Safeguards Analysis')
  self.CBHolder.append(statContainer)
  self.main_CL.addWidget(statContainer, 0, 1)
  statContainerL = QtWidgets.QGridLayout(statContainer)

  # iterations and so on
  #self.SGSetContainer = QtWidgets.QGroupBox(statContainer)
  self.SGSetContainer = AniGBox(statContainer)
  self.SGSetContainer.setTitle('Statistics')
  self.SGSetContainer.setObjectName('PB6')
  self.SGSetContainer.PassLoc('PB6')
  statContainerL.addWidget(self.SGSetContainer, 1, 0, 1, 1)
  SGS_L = QtWidgets.QVBoxLayout(self.SGSetContainer)

  # creates a box for label and iterations
  LIContainer = QtWidgets.QFrame(self.SGSetContainer)
  SGS_L.addWidget(LIContainer)
  LIL = QtWidgets.QGridLayout(LIContainer)

  # iteration label and edit box
  IterLabel = QtWidgets.QLabel("Iterations", LIContainer)
  LIL.addWidget(IterLabel, 1, 0)
  self.IterBox = QtWidgets.QLineEdit("", LIContainer)
  self.IterBox.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  self.CBHolder.append(IterLabel)
  self.CBHolder.append(self.IterBox)
  IterLabel.setToolTip('Requested quantity of calculated realizations')

  self.IterBox.setMaxLength(4)
  self.IterBox.setMinimumWidth(75)
  #self.IterBox.setFixedWidth(45)
  LIL.addWidget(self.IterBox, 1, 1)

  MBPLabel = QtWidgets.QLabel("MBP", LIContainer)
  self.MBPBox = QtWidgets.QLineEdit("", LIContainer)
  self.MBPBox.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  self.MBPBox.setMaxLength(4)
  #self.MBPBox.setFixedWidth(45)
  LIL.addWidget(MBPLabel, 0, 0)
  LIL.addWidget(self.MBPBox, 0, 1)
  self.CBHolder.append(MBPLabel)
  self.CBHolder.append(self.MBPBox)
  self.MBPBox.setMinimumWidth(75)
  MBPLabel.setToolTip('Duration between balances')

  # generic element index
  self.GESelector = QtWidgets.QComboBox()
  self.GESelector.setFrame(0)
  GELabel = QtWidgets.QLabel("Analysis Element/Index", LIContainer)
  #self.GESelector.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
 
  LIL.addWidget(GELabel, 2, 0)
  LIL.addWidget(self.GESelector, 2, 1)
  self.CBHolder.append(GELabel)
  self.CBHolder.append(self.GESelector)
  self.GESelector.setToolTip('*Optional* - Index (row) \n of element to be analyzed')

  #offset index (optional)
  OLabel = QtWidgets.QLabel("Temporal Offset", LIContainer)
  self.OBox = QtWidgets.QLineEdit("", LIContainer)
  self.OBox.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  self.OBox.setMaxLength(4)
  #self.OBox.setFixedWidth(45)
  LIL.addWidget(OLabel, 3, 0)
  LIL.addWidget(self.OBox, 3, 1)
  self.OBox.setMinimumWidth(75)
  self.CBHolder.append(OLabel)
  self.CBHolder.append(self.OBox)
  OLabel.setToolTip(
      '*Optional* Delay before \n first material balance is calculated')

  # error push button
  self.ErrorS = AniButton(self)
  self.ErrorS.setText('Select Errors')
  self.ErrorS.setObjectName('EAB')
  # self.ErrorS.setStyleSheet('border:2px solid rgb(255,170,255);')
  SGS_L.addWidget(self.ErrorS)
  self.ErrorS.setEnabled(0)
  self.ErrorS.setToolTip('Measurement error specification')

  #sets the border now for a later animation
  #if not done causes elements to shift when animation
  #is activated
  if self.window().MakeLight.isChecked() == 0:
    R1 = 66
    R2 = 66
    R3 = 66
  else:
    R1 = 211
    R2 = 211
    R3 = 211

  grad = "QWidget{" +\
         "border-color: rgb({value},{value2},{value3});".format(value=R1,value2=R2,value3=R3) +\
         "border-width: 2px;" +\
         "border-style: solid;" +\
         "padding: 6px;" +\
         "border-radius: 3px;" +\
         "color: black;}"

  grad2 = """QToolTip {
                          background-color: rgb(239,239,239);
                          border-width: 3px;
                          border-color: rgb(153,200,221);
                          border-style: solid;
                          border-radius: 3px;
                          color: black;
                          }"""

  self.ErrorS.setStyleSheet(grad + grad2)

  # Run stats button
  self.RunStats = AniButton(self)
  self.RunStats.setObjectName('RSB')
  self.RunStats.PassLoc('RSB')
  self.RunStats._animation.setLoopCount(3)
  self.RunStats.setText('Run')
  SGS_L.addWidget(self.RunStats)
  self.RunStats.setEnabled(0)
  self.RunStats.setStyleSheet(grad)

  # group box for metric and location
  MLContainer = QtWidgets.QGroupBox()

  # Tests to run
  self.AnalysisContainer = AniGBox(statContainer)
  self.AnalysisContainer.setTitle('Tests')
  self.AnalysisContainer.setObjectName('PB7')
  self.AnalysisContainer.PassLoc('PB7')
  statContainerL.addWidget(self.AnalysisContainer, 0, 0, 1, 1)
  self.AnalysisContainerL = QtWidgets.QVBoxLayout(self.AnalysisContainer)
  # self.AnalysisContainerL = QtWidgets.QFormLayout(self.AnalysisContainer)

  # PUContain = QtWidgets.QGroupBox(self.AnalysisContainer)
  # PUContain.setTitle("Plutonium")
  # pulay = QtWidgets.QVBoxLayout(PUContain)

  #UContain = QtWidgets.QGroupBox(self.AnalysisContainer)
  #UContain.setTitle("Uranium")
  #ulay = QtWidgets.QVBoxLayout(UContain)

  # GEContain = QtWidgets.QGroupBox(self.AnalysisContainer)
  # GEContain.setTitle("Generic Element")
  # glay = QtWidgets.QVBoxLayout(GEContain)

  self.CB_MUF = QtWidgets.QCheckBox("MUF", self.AnalysisContainer)
  self.CB_CUMUF = QtWidgets.QCheckBox("CUMUF",self.AnalysisContainer)
  self.CB_SMUF = QtWidgets.QCheckBox("Sigma MUF", self.AnalysisContainer)
  self.CB_SITMUF = QtWidgets.QCheckBox("SITMUF", self.AnalysisContainer)
  self.CB_PAGE = QtWidgets.QCheckBox("Page's test SITMUF",
                                       self.AnalysisContainer)

  self.CB_CUMUF.clicked.connect(self.force_muf_enabled)
  self.CB_SITMUF.clicked.connect(self.force_muf_enabled)
  self.CB_PAGE.clicked.connect(self.force_page_reqs)
#  self.CBHolder.append(self.CB_MUF)
#  self.CBHolder.append(self.CB_SMUF)
#  self.CBHolder.append(self.CB_SITMUF)
#  self.CBHolder.append(self.CB_PAGE)

  #self.AnalysisContainerL.addWidget(PUContain)
  #self.AnalysisContainerL.addWidget(UContain)
  #self.AnalysisContainerL.addWidget(GEContain)

  self.AnalysisContainerL.addWidget(self.CB_MUF)
  self.AnalysisContainerL.addWidget(self.CB_CUMUF)
  self.AnalysisContainerL.addWidget(self.CB_SMUF)
  self.AnalysisContainerL.addWidget(self.CB_SITMUF)
  self.AnalysisContainerL.addWidget(self.CB_PAGE)

#  ulay.addWidget(self.CB_MUF)
#  ulay.addWidget(self.CB_SMUF)
#  ulay.addWidget(self.CB_SITMUF)
#  ulay.addWidget(self.CB_PAGE)




  # Add plot location locs
  self.PlotControls = AniGBox(self)
  self.PlotControls.setTitle("Plot Controls")
  self.PlotControls.setObjectName('PB5')
  self.PlotControls.PassLoc('PB5')

  statContainerL.addWidget(self.PlotControls, 0, 1, 1, 1)
  PlotControlL = QtWidgets.QGridLayout(self.PlotControls)

  f = QtCore.QCoreApplication.instance().font()

  # add dropdowns
  # qgroupbox
  self.mb1 = SubBoxAni(self)
  self.mb1L = QtWidgets.QHBoxLayout(self.mb1)
  self.mb1.setObjectName('PB1')
  self.mb1.PassLoc('PB1')
  self.mb1.setTitle('Plot Data Type')


  gradA = "QWidget#{VAL}"
  gradB = "{border-color: rgb(211,211,211);" +\
         "border-width: 2px;" +\
         "border-style: solid;" +\
         "padding: 0px;" +\
         "border-radius: 3px;" +\
         "margin-top: 10px;" +\
         "background-color: rgb(239,239,239);}"
  gradC = "QWidget#{VAL}"
  gradD = ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}"

  if self.window().MakeLight.isChecked() == 0:
    gradB = gradB.replace('rgb(239,239,239)', 'rgb(52,52,52)')

  self.mb1.setStyleSheet(
      gradA.format(VAL='PB1') + gradB + gradC.format(VAL='PB1') + gradD)
  self.metricBox = QtWidgets.QComboBox(self.mb1)
  self.metricBox.setMinimumWidth(50)


  self.mb1L.setContentsMargins(10,15,10,15)
  self.mb1L.addWidget(self.metricBox)


  PlotControlL.addWidget(self.mb1, 1, 1)

  self.mb2 = SubBoxAni(self)
  self.mb2.setTitle('Plot Data Location')
  self.mb2.setObjectName('PB2')
  self.mb2.PassLoc('PB2')

  self.mb2.setStyleSheet(
      gradA.format(VAL='PB2') + gradB + gradC.format(VAL='PB2') + gradD)
  self.mb2L = QtWidgets.QHBoxLayout(self.mb2)
  self.LocBox = QtWidgets.QComboBox(self.PlotControls)

  self.mb2L.addWidget(self.LocBox)
  self.mb2L.setContentsMargins(10,15,10,15)
  PlotControlL.addWidget(self.mb2, 2, 1)
  self.LocBox.setMinimumWidth(50)

  self.mb3 = SubBoxAni(self)
  self.mb3L = QtWidgets.QHBoxLayout(self.mb3)
  self.mb3.setObjectName('PB3')
  self.mb3.PassLoc('PB3')
  self.mb3.setTitle('Plot Data Nuclide')
  self.mb3.setStyleSheet(
      gradA.format(VAL='PB3') + gradB + gradC.format(VAL='PB3') + gradD)
  self.NucIDBox = QtWidgets.QComboBox(self.PlotControls)

  self.mb3L.addWidget(self.NucIDBox)
  self.mb3L.setContentsMargins(10,15,10,15)
  PlotControlL.addWidget(self.mb3, 3, 1)
  self.NucIDBox.setMinimumWidth(50)

  self.mb4 = SubBoxAni(self)
  self.mb4L = QtWidgets.QHBoxLayout(self.mb4)
  self.mb4L.setContentsMargins(10,15,10,15)
  self.mb4.setObjectName('PB4')
  self.mb4.PassLoc('PB4')
  self.mb4.setTitle('Iterations to Plot')
  self.mb4.setStyleSheet(
      gradA.format(VAL='PB4') + gradB + gradC.format(VAL='PB4') + gradD)
  self.NumToPlot = QtWidgets.QComboBox(self.PlotControls)
  self.NumToPlot.setMinimumWidth(50)


  self.mb4L.addWidget(self.NumToPlot)

  PlotControlL.addWidget(self.mb4, 4, 1)

  self.PlotRunner = AniButton(self)
  self.PlotRunner.setText('Plot')
  self.PlotRunner.setObjectName('PRB')
  PlotControlL.addWidget(self.PlotRunner, 5, 1)
  #PlotControlL.setVerticalSpacing(PlotControlL.verticalSpacing())
  self.PlotRunner.setEnabled(0)

  #sets the border now for a later animation
  #if not done causes elements to shift when animation
  #is activated
  if self.window().MakeLight.isChecked() == 0:
    R1 = 66
    R2 = 66
    R3 = 66
  else:
    R1 = 211
    R2 = 211
    R3 = 211

  grad = "border-color: rgb({value},{value2},{value3});".format(value=R1,value2=R2,value3=R3) +\
         "border-width: 2px;" +\
         "border-style: solid;" +\
         "padding: 6px;" +\
         "border-radius: 3px;" +\
         "color: black;"

  self.PlotRunner.setStyleSheet(grad)

  # add threshold box
  self.threshContainer = AniGBox(self)
  statContainerL.addWidget(self.threshContainer, 1, 1, 1, 1)
  self.threshContainer.setTitle("Statistical Thresholds")
  self.threshContainer.setObjectName('PB8')
  self.threshContainer.PassLoc('PB8')
  threshContainerL = QtWidgets.QGridLayout(self.threshContainer)

  # threshold box contents
  # set threshold
  self.StatThresh = QtWidgets.QLineEdit("", self.threshContainer)
  self.StatThresh.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  threshContainerL.addWidget(self.StatThresh, 2, 1)
  self.STL = QtWidgets.QLabel("Enter Threshold", self.threshContainer)
  threshContainerL.addWidget(self.STL, 2, 0)
  self.StatThresh.setMaxLength(4)
  self.StatThresh.setMinimumWidth(75)


  # threshold display
  self.STL2 = QtWidgets.QLabel("% Above Threshold", self.threshContainer)
  threshContainerL.addWidget(self.STL2, 3, 0)
  self.StatThreshDisp = QtWidgets.QLineEdit("0.00", self.threshContainer)
  self.StatThreshDisp.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  threshContainerL.addWidget(self.StatThreshDisp, 3, 1)
  self.StatThreshDisp.setMaxLength(6)
  self.StatThreshDisp.setMinimumWidth(75)


  # calculate button
  self.CalcThresh = AniButton(self)
  self.CalcThresh.setText('Calculate')
  self.CalcThresh.setObjectName('CTB')
  threshContainerL.addWidget(self.CalcThresh, 4, 0, 4, 2)
  threshContainerL.setVerticalSpacing(threshContainerL.verticalSpacing() * 14)
  self.CalcThresh.setEnabled(0)
  self.CalcThresh.clicked.connect(self.RunStatThresh)

  self.StatThreshDisp.setReadOnly(1)
  #statContainerL.setColumnMinimumWidth(1,
                                       #statContainer.sizeHint().width() * 0.40)

  #sets the border now for a later animation
  #if not done causes elements to shift when animation
  #is activated
  if self.window().MakeLight.isChecked() == 0:
    R1 = 66
    R2 = 66
    R3 = 66
  else:
    R1 = 211
    R2 = 211
    R3 = 211

  grad = "border-color: rgb({value},{value2},{value3});".format(value=R1,value2=R2,value3=R3) +\
         "border-width: 2px;" +\
         "border-style: solid;" +\
         "padding: 6px;" +\
         "border-radius: 3px;" +\
         "color: black;"

  self.CalcThresh.setStyleSheet(grad)


# add plot box
def add_plot_box(self):
  plotContainer = QtWidgets.QGroupBox(self.main_CF)

  plotContainer.setTitle('See help tab for detailed instructions')
  plotContainer.setStyleSheet('QGroupBox:title{color:rgb(0,173,208)}')
  plotContainer.setAlignment(4)
  F = QtGui.QFont()
  F.setBold(True)
  plotContainer.setFont(F)

  plotContainerL = QtWidgets.QGridLayout(plotContainer)
  self.main_CL.addWidget(plotContainer, 0, 0)

  self.canvas = PlotOps.MPLCanvas(plotContainer)
  self.navi_toolbar = NavigationToolbar(self.canvas, self)
  plotContainerL.addWidget(self.canvas, 0, 0)
  plotContainerL.addWidget(self.navi_toolbar)
  self.canvas.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.MinimumExpanding)



if __name__ == "__main__":
  app = QtWidgets.QApplication([])

  #splash
  x = Path(sys.argv[0]).resolve().parents[1]
  F = os.path.join(x, 'docs_v2','source', 'assets', 'codeAssets', 'splashV2.png')
  splash_pix = QtGui.QPixmap(F)
  splash = QtWidgets.QSplashScreen(splash_pix)
  splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint
                        | QtCore.Qt.FramelessWindowHint)
  splash.setEnabled(False)


  F = os.path.join(x, 'docs_v2','source', 'assets', 'codeAssets', 'SNL_Stacked_Black_Blue2.jpg')
  splash.setWindowIcon(QtGui.QIcon(F))

  progressBar = QtWidgets.QProgressBar(splash)
  progressBar.setMaximum(100)
  progressBar.setGeometry(25,
                          splash_pix.height() - 35,
                          splash_pix.width() - 50, 25)
  splash.show()

  barSty = """
    QProgressBar{
    border-radius: 5px;
    border-style: solid;
    border-color: rgb(211,211,211);
    border-width: 3px;
    text-align: center;
    color: black
    }
    QProgressBar::chunk{
    background-color: rgb(0,173,208);
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

  widget.show()
  widget.activateWindow()
  sys.exit(app.exec_())
