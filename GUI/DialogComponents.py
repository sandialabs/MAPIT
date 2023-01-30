from PySide2 import QtWidgets
from MAPIT_internal.core import AuxFunctions as Aux

class MissingIndex(QtWidgets.QDialog):
  """
        An array axis to operate on is required for
        MAPIT. If location of interest is not
        provided for imported data then this
        dialog requests it.
  """

  def __init__(self, parent):
    super(MissingIndex, self).__init__()
    li_l = QtWidgets.QGridLayout(self)
    smptxt = QtWidgets.QLabel("We can't find the index of "
                              "some of the elemental species "
                              "for requested statistical tests. "
                              "Please enter the required indicies")
    li_l.addWidget(smptxt, 0, 0, 2, 1)

    smptxt.setWordWrap(1)

    self.PuBox = QtWidgets.QLineEdit(self)
    self.UBox = QtWidgets.QLineEdit(self)
    self.GBox = QtWidgets.QLineEdit(self)

    PuBoxTxt = QtWidgets.QLabel("Enter the Pu Index")
    UBoxTxt = QtWidgets.QLabel("Enter the U Index")
    GBoxTxt = QtWidgets.QLabel("Enter the generic element Index")

    self.PuBox.setEnabled(0)
    self.UBox.setEnabled(0)
    self.GBox.setEnabled(0)

    li_l.addWidget(PuBoxTxt, 3, 0)
    li_l.addWidget(UBoxTxt, 4, 0)
    li_l.addWidget(GBoxTxt, 5, 0)

    li_l.addWidget(self.PuBox, 3, 1)
    li_l.addWidget(self.UBox, 4, 1)
    li_l.addWidget(self.GBox, 5, 1)

    EndBtn = QtWidgets.QPushButton("Done", self)
    li_l.addWidget(EndBtn, 6, 0, 7, 2)
    EndBtn.clicked.connect(self.SaveInxs)

    self.PuBox.setMaxLength(4)
    #self.PuBox.setFixedWidth(35)

    self.UBox.setMaxLength(4)
    #self.UBox.setFixedWidth(35)

    self.GBox.setMaxLength(4)
    #self.GBox.setFixedWidth(35)

    #self.setFixedSize(300, 400)

    #this part of code basically looks
    #to see if SOME indicies were given
    #even if they were not requested.
    #ex: user gives location for U but
    #requests Pu statistical tests.
    #this fills in those indices
    #and disables inputs for non-requested
    #elements
    for i in range(0, 3):
      try:
        parent.pmpt.index(i)
        if i == 0:
          self.PuBox.setEnabled(1)
        elif i == 1:
          self.UBox.setEnabled(1)
        else:
          self.GBox.setEnabled(1)
      except:
        if i == 0 and int(parent.PuLoc) != -1:
          self.PuBox.setText(str(parent.PuLoc))
        elif i == 1 and int(parent.ULoc) != -1:
          self.UBox.setText(str(parent.ULoc))
        elif int(parent.GLoc) != -1:
          self.GBox.setText(str(parent.GLoc))
        else:
          None

  def SaveInxs(self):

    # save the index and close
    x = self.parent()
    if self.PuBox.text() == "":
      self.PuLoc = -1
    else:
      self.PuLoc = int(self.PuBox.text())

    if self.UBox.text() == "":
      self.ULoc = -1
    else:
      self.ULoc = int(self.UBox.text())

    if self.GBox.text() == "":
      self.GLoc = -1
    else:
      self.GLoc = int(self.GBox.text())

    self.accept()
    pass

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
        ['Inventory', 'Random Contribution', 'Systematic Contribution'])
    
    header = self.EP2.horizontalHeader()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

    self.EP2.setColumnCount(3)
    self.EP2.setHorizontalHeaderLabels(
        ['Inventory', 'Random Contribution', 'Systematic Contribution'])

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
      self.EP2.setItem(i, 0,
          QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribI,i,TimeLoc,typ='inv'),4))))


      self.EP2.setItem(i, 1,
          QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribR,i,TimeLoc,typ='error'),4))))

      self.EP2.setItem(i, 2,
          QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribS,i,TimeLoc,typ='error'),4))))

    for i in range(InLocs, InvLocs + InLocs):
      self.EP2.setItem(i + offset1, 0,
          QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribI,i,TimeLoc,typ='inv'),4))))

      self.EP2.setItem(i + offset1, 1,
          QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribR,i,TimeLoc,typ='error'),4))))

      self.EP2.setItem(i + offset1, 2,
          QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribS,i,TimeLoc,typ='error'),4))))

    for i in range(InvLocs + InLocs, TotalLocs):
      self.EP2.setItem(i + offset1 + offset2, 0,
          QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribI,i,TimeLoc,typ='inv'),4))))

      self.EP2.setItem(i + offset1 + offset2, 1,
          QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribR,i,TimeLoc,typ='error'),4))))

      self.EP2.setItem(i + offset1 + offset2, 2,
          QtWidgets.QTableWidgetItem(str(round(Aux.SEIDcontrib(AnalysisData.SEMUFContribS,i,TimeLoc,typ='error'),4))))



  
