from PySide2 import QtWidgets, QtCore, QtGui
from MAPIT_internal.core import AuxFunctions as Aux
from MAPIT_internal.GUI import IOWizard, GeneralOps
import os
import numpy as np
import time


def launchIOWindow(self, AnalysisData, GUIparams):

  Wizard = IOWizard.IOWizardMain(self)
  Wizard.setWindowModality(QtCore.Qt.ApplicationModal)
  Wizard.exec_()



  GUIparams = GeneralOps.loadGUILabels(GUIparams)
  GeneralOps.getExtData(self,AnalysisData,GUIparams,Wizard)




class ViewErrorTabs(QtWidgets.QDialog):
  """
        This function displays the contribution
        of various material balance terms
        to the uncertainty (i.e. sigma MUF)
  """

  def __init__(self, parent, AnalysisData, GUIparams):
    super(ViewErrorTabs, self).__init__()

    mbaTime = int(parent.MBPBox.text())
    IT = int(parent.IterBox.text())
    MBPs = int(AnalysisData.SEMUF.shape[1]/mbaTime)-1

    li_l = QtWidgets.QGridLayout(self)

    MatContainer = QtWidgets.QGroupBox(self)
    MCC = QtWidgets.QVBoxLayout(MatContainer)
    MatContainer.setTitle('Material')
    li_l.addWidget(MatContainer, 0, 0)


    ck2 = parent.CB_MUF.isChecked() + parent.CB_SMUF.isChecked(
    ) + parent.CB_SITMUF.isChecked() + parent.CB_PAGE.isChecked()

    #checking to see what was selected to
    #apply labels
    self.MatTyp = QtWidgets.QComboBox(self)
    if ck2 > 0:
      self.MatTyp.addItem('Generic')
    MCC.addWidget(self.MatTyp)

    MBPContainer = QtWidgets.QGroupBox(self)
    MBC = QtWidgets.QVBoxLayout(MBPContainer)
    MBPContainer.setTitle('MBP')
    li_l.addWidget(MBPContainer, 0, 1)

    self.MBPDisp = QtWidgets.QSpinBox(self)
    self.MBPDisp.setMaximum(MBPs)
    self.MBPDisp.setMinimum(1)
    MBC.addWidget(self.MBPDisp)
    self.EP2 = QtWidgets.QTableWidget()

    self.EP2.setRowCount(GUIparams.nTotalLocations+2) #+2 is for spacer rows
    self.EP2.setVerticalHeaderLabels(GUIparams.rowNames) #names
    self.EP2.setColumnCount(3)
    self.EP2.setHorizontalHeaderLabels(
        ['Observed Data (kg)', 'Random Contribution (kg)', 'Systematic Contribution (kg)'])
    
    header = self.EP2.horizontalHeader()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

    self.EP2.setColumnCount(3)
    self.EP2.setHorizontalHeaderLabels(
        ['Observed Data (kg)', 'Random Contribution(kg)', 'Systematic Contribution (kg)'])

    self.EP2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    self.parent = parent
    self.MBPDisp.valueChanged.connect(lambda: self.setItems(AnalysisData, GUIparams))

    self.setItems(AnalysisData, GUIparams)  #set the table items
    
    self.EP2.setVerticalHeaderLabels(GUIparams.rowNames)
    #print(GUIparams.rowNames)
    li_l.addWidget(self.EP2, 1, 0, 1, 2)
    self.parent = parent

  def setItems(self, AnalysisData, GUIparams):
    """
            Function to get and set
            the contribution to the
            uncertanity in MUF
            (i.e. sigma MUF) of various
            measurements.
    """

    TimeLoc = int(self.MBPDisp.value())
    mbaTime = int(self.parent.MBPBox.text())
    
    offset1 = 1
    offset2 = 1
    EleLoc = 0

    if hasattr(self.parent, 'Wizard'):  #if data was imported
      TotalLocs = int(self.parent.Wizard.InKMP) + int(
          self.parent.Wizard.InvKMP) + int(self.parent.Wizard.OutKMP)

      InLocs = int(self.parent.Wizard.InKMP)
      InvLocs = int(self.parent.Wizard.InvKMP)
      OutLocs = int(self.parent.Wizard.OutKMP)

    else:  #if data is from the scenario selector
      TotalLocs = GUIparams.nTotalLocations

      InLocs = GUIparams.nInputLocations
      InvLocs = GUIparams.nInventoryLocations
      OutLocs = GUIparams.nOutputLocations

    if self.MatTyp.currentText() == 'Pu':
      EleLoc = self.parent.PuLoc
    if self.MatTyp.currentText() == 'U':
      EleLoc = self.parent.ULoc
    if self.MatTyp.currentText() == 'Generic':
      EleLoc = self.parent.GLoc
    
    #the inventory at a specific time
    #changes based on if the sample time
    #was variable or constant
    #future TODO: change to have same structure
    #regardless of sample time
    for i in range(0, InLocs):
      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribI,i,TimeLoc,typ='inv'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i, 0, item) 

      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribR,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i, 1, item)

      item =  QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribS,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i, 2, item)

    for i in range(InLocs, InvLocs + InLocs):
      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribI,i,TimeLoc,typ='inv'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1, 0, item) 

      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribR,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1, 1, item)

      item =  QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribS,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1, 2, item)

    for i in range(InvLocs + InLocs, TotalLocs):
      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribI,i,TimeLoc,typ='inv'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1 + offset2, 0, item) 

      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribR,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1 + offset2, 1, item)

      item =  QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribS,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1 + offset2, 2, item)

class ViewErrorTabsAI(QtWidgets.QDialog):
  """
        This function displays the contribution
        of various material balance terms
        to the uncertainty (i.e. sigma MUF)
  """

  def __init__(self, parent, AnalysisData, GUIparams):
    super(ViewErrorTabsAI, self).__init__()

    mbaTime = int(parent.MBPBox.text())
    IT = int(parent.IterBox.text())
    MBPs = int(AnalysisData.SEMUF.shape[1]/mbaTime)-1

    li_l = QtWidgets.QGridLayout(self)

    MatContainer = QtWidgets.QGroupBox(self)
    MCC = QtWidgets.QVBoxLayout(MatContainer)
    MatContainer.setTitle('Material')
    li_l.addWidget(MatContainer, 0, 0)


    ck2 = parent.CB_MUF.isChecked() + parent.CB_SMUF.isChecked(
    ) + parent.CB_SITMUF.isChecked() + parent.CB_PAGE.isChecked()

    #checking to see what was selected to
    #apply labels
    self.MatTyp = QtWidgets.QComboBox(self)
    if ck2 > 0:
      self.MatTyp.addItem('Generic')
    MCC.addWidget(self.MatTyp)

    MBPContainer = QtWidgets.QGroupBox(self)
    MBC = QtWidgets.QVBoxLayout(MBPContainer)
    MBPContainer.setTitle('MBP')
    li_l.addWidget(MBPContainer, 0, 1)

    self.MBPDisp = QtWidgets.QSpinBox(self)
    self.MBPDisp.setMaximum(MBPs)
    self.MBPDisp.setMinimum(1)
    MBC.addWidget(self.MBPDisp)
    self.EP2 = QtWidgets.QTableWidget()

    self.EP2.setRowCount(GUIparams.nTotalLocations+2) #+2 is for spacer rows
    self.EP2.setVerticalHeaderLabels(GUIparams.rowNames) #names
    self.EP2.setColumnCount(3)
    self.EP2.setHorizontalHeaderLabels(
        ['Observed Data (kg)', 'Random Contribution(% AI)', 'Systematic Contribution (% AI)'])
    
    header = self.EP2.horizontalHeader()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

    self.EP2.setColumnCount(3)
    self.EP2.setHorizontalHeaderLabels(
        ['Observed Data (kg)', 'Random Contribution(% AI)', 'Systematic Contribution (% AI)'])

    self.EP2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    self.parent = parent
    self.MBPDisp.valueChanged.connect(lambda: self.setItemsAI(AnalysisData, GUIparams))

    self.setItemsAI(AnalysisData, GUIparams)  #set the table items
    
    self.EP2.setVerticalHeaderLabels(GUIparams.rowNames)
    #print(GUIparams.rowNames)
    li_l.addWidget(self.EP2, 1, 0, 1, 2)
    self.parent = parent

  def setItemsAI(self, AnalysisData, GUIparams):
    """
            Function to get and set
            the contribution to the
            uncertanity in MUF
            (i.e. sigma MUF) of various
            measurements.
    """

    TimeLoc = int(self.MBPDisp.value())
    mbaTime = int(self.parent.MBPBox.text())
    
    offset1 = 1
    offset2 = 1
    EleLoc = 0

    if hasattr(self.parent, 'Wizard'):  #if data was imported
      TotalLocs = int(self.parent.Wizard.InKMP) + int(
          self.parent.Wizard.InvKMP) + int(self.parent.Wizard.OutKMP)

      InLocs = int(self.parent.Wizard.InKMP)
      InvLocs = int(self.parent.Wizard.InvKMP)
      OutLocs = int(self.parent.Wizard.OutKMP)

    else:  #if data is from the scenario selector
      TotalLocs = GUIparams.nTotalLocations

      InLocs = GUIparams.nInputLocations
      InvLocs = GUIparams.nInventoryLocations
      OutLocs = GUIparams.nOutputLocations

    if self.MatTyp.currentText() == 'Pu':
      EleLoc = self.parent.PuLoc
    if self.MatTyp.currentText() == 'U':
      EleLoc = self.parent.ULoc
    if self.MatTyp.currentText() == 'Generic':
      EleLoc = self.parent.GLoc
    
    #the inventory at a specific time
    #changes based on if the sample time
    #was variable or constant
    #future TODO: change to have same structure
    #regardless of sample time
    for i in range(0, InLocs):
      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribI,i,TimeLoc,typ='inv'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i, 0, item) 

      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFAIContribR,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i, 1, item)

      item =  QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFAIContribS,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i, 2, item)

    for i in range(InLocs, InvLocs + InLocs):
      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribI,i,TimeLoc,typ='inv'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1, 0, item) 

      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFAIContribR,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1, 1, item)

      item =  QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFAIContribS,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1, 2, item)

    for i in range(InvLocs + InLocs, TotalLocs):
      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribI,i,TimeLoc,typ='inv'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1 + offset2, 0, item) 

      item = QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFAIContribR,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1 + offset2, 1, item)

      item =  QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFAIContribS,i,TimeLoc,typ='error'),4)))
      item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
      self.EP2.setItem(i + offset1 + offset2, 2, item)
  
class HPCWindow(QtWidgets.QDialog):
  """
        TBD
  """

  def __init__(self, parent, AnalysisData):
    super(HPCWindow, self).__init__()
    #self.parent = parent

    layout = QtWidgets.QVBoxLayout(self)
    enable_parCB = QtWidgets.QCheckBox("Enable parallel processing")
    layout.addWidget(enable_parCB)

    container = QtWidgets.QGroupBox()
    container.setTitle('CPU count')
    container_layout = QtWidgets.QHBoxLayout(container)


    CancelButton = QtWidgets.QPushButton("Cancel", self)
    AcceptButton = QtWidgets.QPushButton("Done", self)

    AcceptButton.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DialogOkButton))
    CancelButton.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton))

    hbox = QtWidgets.QHBoxLayout()
    hbox.addWidget(CancelButton)
    hbox.addWidget(AcceptButton)

    
    maxcore = os.cpu_count()

    self.coreslider = QtWidgets.QSlider(orientation=QtCore.Qt.Orientation(1))
    self.coreslider.setMinimum(0)
    self.coreslider.setMaximum(maxcore)
    self.coreslider.setValue(maxcore)

    self.corecount = QtWidgets.QLineEdit("")
    self.corecount.setMaxLength(4)

    

    self.corecount.setText(str(maxcore))

    hbox2 = QtWidgets.QHBoxLayout()
    hbox2.addWidget(self.coreslider,75)
    hbox2.addWidget(self.corecount,25)

    container_layout.addLayout(hbox2)
    

    layout.addWidget(container)
    layout.addLayout(hbox)

    self.coreslider.sliderMoved.connect(self.updatecpubox)
    self.corecount.textEdited.connect(self.updatecpuslider)
    AcceptButton.clicked.connect(self.yesHPC)
    CancelButton.clicked.connect(self.noHPC)
    vv = QtGui.QIntValidator()
    vv.setRange(1,maxcore)
    self.corecount.setValidator(vv)

  def yesHPC(self):
    self.accept()

  def noHPC(self):
    self.reject()

  def updatecpubox(self):
    self.corecount.setText(str(self.coreslider.value()))

  def updatecpuslider(self):
    self.coreslider.setValue(int(self.corecount.text()))

