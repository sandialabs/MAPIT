from PySide6 import QtWidgets, QtCore, QtGui
from MAPIT.core import AuxFunctions as Aux
from MAPIT.GUI import IOWizard, GeneralOps, StyleOps, GUIComponents
import os
from platformdirs import user_config_dir, user_data_dir
import uuid


def launchIOWindow(self, AnalysisData, GUIparams):

  Wizard = IOWizard.IOWizardMain(self)
  Wizard.setWindowModality(QtCore.Qt.ApplicationModal)
  Wizard.exec_()



  

  if Wizard.gracefulExit:
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


class checkForSampleData(QtWidgets.QDialog):
  def __init__(self, parent, setInitStyle=False):
    super(checkForSampleData, self).__init__()


    StyleOps.getDlgColorDict(self,parent,setInitStyle)

    if QtCore.QSettings("current", "mapit").value("dataPathDefault") is not None:
      self.ex_data_path = QtCore.QSettings("current", "mapit").value("dataPathDefault")
    else:
      self.ex_data_path = os.path.join(os.path.join(user_data_dir('MAPIT',False),'input'))
    
   

    Mlayout = QtWidgets.QVBoxLayout(self)
    Mlayout.setSpacing(15)
    Mlayout2 = QtWidgets.QHBoxLayout()
    Mlayout3 = QtWidgets.QHBoxLayout()

    #dirdlg = QtWidgets.QFileDialog()
    #dirdlg.setDirectory(default_path)
    #Mlayout.addWidget(dirdlg)

    helptxt = QtWidgets.QLabel("(Optional): Select directory for MAPIT example data")

    self.dirtext = QtWidgets.QLabel()
    self.dirtext.setText(self.ex_data_path)

    label1 = QtWidgets.QLabel("Data directory: ")

    #selectBTN = QtWidgets.QPushButton("Select directory")
    #closeBTN = QtWidgets.QPushButton("Confirm")

    selectBTN = GUIComponents.AniButton(self)
    selectBTN.setObjectName('sb1')
    selectBTN.setText("Select directory")
    StyleOps.enable_ani_button(button_obj = selectBTN, guiobj = self, loc = 'sb1')

    closeBTN = GUIComponents.AniButton(self)
    closeBTN.setObjectName('sb2')
    closeBTN.setText("Confirm")
    StyleOps.enable_ani_button(button_obj = closeBTN, guiobj = self, loc = 'sb2')

    self.rememberBX = QtWidgets.QCheckBox("Remember selection and do not show again")
    self.rememberBX.setChecked(1)

    Mlayout3.addWidget(selectBTN)
    Mlayout3.addWidget(closeBTN)

    Mlayout.addWidget(helptxt)
    Mlayout2.addWidget(label1)
    Mlayout2.addWidget(self.dirtext)
    Mlayout.addLayout(Mlayout2)
    Mlayout.addWidget(self.rememberBX)
    Mlayout.addLayout(Mlayout3)

    closeBTN.clicked.connect(self.close)
    selectBTN.clicked.connect(lambda: self.pickDir(self.dirtext))

  def pickDir(self, dirlabel):
    self.ex_data_path = QtWidgets.QFileDialog.getExistingDirectory(
        self, options=QtWidgets.QFileDialog.DontUseNativeDialog)
    
    dirlabel.setText(self.ex_data_path)
  
  def closeEvent(self, event):
    settings = QtCore.QSettings("current", "mapit")
    if self.rememberBX.isChecked():
      settings.setValue("dataPathBypass",True)
    else:
      settings.setValue("dataPathBypass",False)
    
    settings.setValue("dataPathDefault",self.dirtext.text())
    
    
class dataTypeSelector(QtWidgets.QWidget):
    def __init__(self, text, colordict):
        super().__init__()

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.gb = QtWidgets.QGroupBox(text)
        self.layout.addWidget(self.gb)
        self.gb_layout = QtWidgets.QVBoxLayout()
        self.gb.setLayout(self.gb_layout)
        self.gb.setObjectName(str(uuid.uuid4()))
        StyleOps.update_aniGBoxSmall_styleSheet(colordict, self.gb, isactive=1)

        self.rb_type_cont = QtWidgets.QRadioButton("Continuous")
        self.rb_type_disc = QtWidgets.QRadioButton("Discrete")
        self.rb_type_cont.setChecked(True)

        self.gb_layout.addWidget(self.rb_type_cont)
        self.gb_layout.addWidget(self.rb_type_disc)


    def get_type(self):
        if self.rb_type_cont.isChecked():
            return "continuous"
        else:
            return "discrete"

        
class getImportDataTypeDlg(QtWidgets.QDialog):
    def __init__(self, entries, colordict):
      super().__init__()

      self.entries = entries
      self.entry_widgets = []

      self.scroll_area = QtWidgets.QScrollArea()
      self.scroll_area.setWidgetResizable(True)

      

      self.container = QtWidgets.QFrame()
      self.scroll_area.setWidget(self.container)

      StyleOps.update_scrollObjStype(self.scroll_area, self.container, colordict)

      self.layout = QtWidgets.QVBoxLayout()
      self.container.setLayout(self.layout)

      for entry in self.entries:
          widget = dataTypeSelector(entry, colordict)          
          self.entry_widgets.append(widget)
          self.layout.addWidget(widget)

      #self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
      #self.button_box.accepted.connect(self.accept)
      #self.button_box.rejected.connect(self.reject)

      self.loadbtn = GUIComponents.AniButton(None)
      self.loadbtn.setText("Load")

      self.savebtn = GUIComponents.AniButton(None)
      self.savebtn.setText("Save")

      self.donebtn = GUIComponents.AniButton(None)
      self.donebtn.setText("Done")

      tlw = QtWidgets.QApplication.topLevelWidgets()
      for w in tlw:
        if hasattr(w,'colordict'):
          mw = w

      StyleOps.enable_ani_button(button_obj=self.loadbtn, guiobj=mw)
      StyleOps.enable_ani_button(button_obj=self.savebtn, guiobj=mw)
      StyleOps.enable_ani_button(button_obj=self.donebtn, guiobj=mw)


      self.main_layout = QtWidgets.QVBoxLayout()
      self.main_layout.addWidget(self.scroll_area)
      #self.main_layout.addWidget(self.button_box)

      self.subwidget = QtWidgets.QWidget()
      self.sublayout = QtWidgets.QGridLayout()
      self.subwidget.setLayout(self.sublayout)

      self.sublayout.addWidget(self.loadbtn, 0, 0)
      self.sublayout.addWidget(self.savebtn, 0, 1)
      self.sublayout.addWidget(self.donebtn, 1, 0, 1, 2)
      self.donebtn.clicked.connect(self.accept)
      self.loadbtn.clicked.connect(self.load_data)
      self.savebtn.clicked.connect(self.save_data)


      self.main_layout.addWidget(self.subwidget)

      self.setLayout(self.main_layout)


    def get_types(self):
        return [widget.get_type() for widget in self.entry_widgets]
    
    def set_option(self, options):
      for i, option in enumerate(options):
        if option == 'continuous':
          self.entry_widgets[i].rb_type_cont.setChecked(True)
        elif option == 'discrete':
          self.entry_widgets[i].rb_type_disc.setChecked(True)
        else:
          print("error")
    
    def save_data(self):
      dat = self.get_types()

      outdir = os.path.join(user_config_dir('MAPIT',False), 'DatTypeConfig.txt')

      with open(outdir, 'w') as f:
        for item in dat:
          f.write("%s\n" % item)

    
    def load_data(self):
      outdir = os.path.join(user_config_dir('MAPIT',False), 'DatTypeConfig.txt')

      with open(outdir, 'r') as f:
        x = f.read().splitlines()

      self.set_option(x)
