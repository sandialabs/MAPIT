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

import sys
from PySide2 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
from IOWizard import IOWizardMain
from IOWizardMat import IOWizardMainMat
from ScenarioSelector import SceneSelect
import os
import string
import copy
import matplotlib.pyplot as plt
import time
import matplotlib
from scipy.io import loadmat
from itertools import chain
from collections import namedtuple
import StatsPackage
import datetime
import bisect
from pathlib import Path
import AnimationTools




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

  def __init__(self, parent):
    super(ViewErrorTabs, self).__init__()
    li_l = QtWidgets.QGridLayout(self)

    if isinstance(parent.inpFrame,list):
      timeSteps = np.shape(parent.inpFrame[0])[0]
    else:
      timeSteps = np.shape(parent.inpFrame)[1]
    mbaTime = int(parent.MBPBox.text())
    MBPs = np.shape(parent.SEMUFContribR)[2] - 1  #1 to total MBPs


    MatContainer = QtWidgets.QGroupBox(self)
    MCC = QtWidgets.QVBoxLayout(MatContainer)
    MatContainer.setTitle('Material')
    li_l.addWidget(MatContainer, 0, 0)

    ck0 = parent.CB_PuMUF.isChecked() + parent.CB_PuSMUF.isChecked(
    ) + parent.CB_PuSITMUF.isChecked() + parent.CB_PuSPage.isChecked()
    ck1 = parent.CB_UMUF.isChecked() + parent.CB_USMUF.isChecked(
    ) + parent.CB_USITMUF.isChecked() + parent.CB_USPage.isChecked()
    ck2 = parent.CB_GMUF.isChecked() + parent.CB_GSMUF.isChecked(
    ) + parent.CB_GSITMUF.isChecked() + parent.CB_GSPage.isChecked()

    #checking to see what was selected to
    #apply labels
    self.MatTyp = QtWidgets.QComboBox(self)
    if ck0 > 0:
      self.MatTyp.addItem('Pu')
    if ck1 > 0:
      self.MatTyp.addItem('U')
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

    if hasattr(parent, 'Wizard'):  #if imported data
      TotalLocs = int(parent.Wizard.InKMP) + int(parent.Wizard.InvKMP) + int(
          parent.Wizard.OutKMP)
      InLocs = int(parent.Wizard.InKMP)
      InvLocs = int(parent.Wizard.InvKMP)
      OutLocs = int(parent.Wizard.OutKMP)
      self.EP2.setRowCount(TotalLocs + 2)  #+2 is for spacer rows
      self.EP2.setVerticalHeaderLabels(parent.Wizard.InKMP_names +
                                       parent.Wizard.InvKMP_names +
                                       parent.Wizard.OutKMP_names)

      offset1 = 1
      offset2 = 1

    else:  #if scenario (included) data
      TotalLocs = np.shape(parent.SS.Inputs)[0] + np.shape(parent.SS.Inventories)[0] + \
                  np.shape(parent.SS.Outputs)[0]
      InLocs = np.shape(parent.SS.Inputs)[0]
      InvLocs = np.shape(parent.SS.Inventories)[0]
      OutLocs = np.shape(parent.SS.Outputs)[0]

      offset1 = 1
      offset2 = 1

      self.EP2.setRowCount(TotalLocs + 2)

    self.EP2.setColumnCount(3)
    self.EP2.setHorizontalHeaderLabels(
        ['Inventory', 'Random Contribution', 'Systematic Contribution'])

    header = self.EP2.horizontalHeader()
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

    #fixed width widget
    #self.setFixedWidth(self.EP2.sizeHint().width() * 3.1)
    #self.EP2.setFixedWidth(self.EP2.sizeHint().width() * 3)

    self.EP2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    self.MBPDisp.valueChanged.connect(self.setItems)


    self.parent = parent
    ViewErrorTabs.setItems(self)  #set the table items

    if hasattr(parent, 'Wizard'):  #if imported
      # grab the row names

      # split convert string into list
      #check to see if names were specified
      if parent.Wizard.InKMP_names != '':
        parent.Wizard.InKMP_names = parent.Wizard.InKMP_names.split(',')

      else:
        None

      if parent.Wizard.InvKMP_names != '':
        parent.Wizard.InvKMP_names = parent.Wizard.InvKMP_names.split(',')

      else:
        None

      if parent.Wizard.OutKMP_names != '':
        parent.Wizard.OutKMP_names = parent.Wizard.OutKMP_names.split(',')

      else:
        None

      rowNames = [None] * (TotalLocs + 2)  #2 extra rows for spacers

      #if locations weren't given then provide
      #some generic labels
      for i in range(0, int(parent.Wizard.InKMP)):
        if parent.Wizard.InKMP_names == '':
          rowNames[i] = 'input' + str(i + 1)

        elif i >= len(parent.Wizard.InKMP_names):
          rowNames[i] = 'input' + str(i + 1)

        else:
          rowNames[i] = parent.Wizard.InKMP_names[i]

      rowNames[int(parent.Wizard.InKMP)] = ''

      for i in range(0, int(parent.Wizard.InvKMP)):
        if parent.Wizard.InvKMP_names == '':
          rowNames[i + int(parent.Wizard.InKMP) + 1] = 'inventory' + str(i + 1)

        elif i >= len(parent.Wizard.InvKMP_names):
          rowNames[i + int(parent.Wizard.InKMP) + 1] = 'inventory' + str(i + 1)

        else:
          rowNames[i + int(parent.Wizard.InKMP)] = parent.Wizard.InvKMP_names[i]

      rowNames[int(parent.Wizard.InKMP) + int(parent.Wizard.InvKMP) + 1] = ''

      for i in range(0, int(parent.Wizard.OutKMP)):
        if parent.Wizard.OutKMP_names == '':
          rowNames[i + int(parent.Wizard.InKMP) + int(parent.Wizard.InvKMP) +
                   2] = 'output' + str(i + 1)

        elif i >= len(parent.Wizard.OutKMP_names):
          rowNames[i + int(parent.Wizard.InKMP) + int(parent.Wizard.InvKMP) +
                   2] = 'output' + str(i + 1)

        else:
          rowNames[i + int(parent.Wizard.InKMP) +
                   int(parent.Wizard.InvKMP)] = parent.Wizard.OutKMP_names[i]

    else:  #if pulled from the fuel fab scenario use this labels
      F = os.path.join(x, 'data', 'fuel_fab', self.parent.SS.sceneName, 'auxData.npz')
      A = np.load(F)
      rowNames = A['arr2']

    self.EP2.setVerticalHeaderLabels(rowNames)
    li_l.addWidget(self.EP2, 1, 0, 1, 2)
    self.parent = parent

  def setItems(self):
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
      TotalLocs = np.shape(self.parent.SS.Inputs)[0] + np.shape(self.parent.SS.Inventories)[0] + \
                  np.shape(self.parent.SS.Outputs)[0]

      InLocs = np.shape(self.parent.SS.Inputs)[0]
      InvLocs = np.shape(self.parent.SS.Inventories)[0]
      OutLocs = np.shape(self.parent.SS.Outputs)[0]

    if self.MatTyp.currentText() == 'Pu':
      EleLoc = self.parent.PuLoc
    if self.MatTyp.currentText() == 'U':
      EleLoc = self.parent.ULoc
    if self.MatTyp.currentText() == 'Generic':
      EleLoc = self.parent.GLoc

    if isinstance(self.parent.inpEFrame, list):
      SEFrame = None
    else:
      SEFrame = np.concatenate(
          (self.parent.inpEFrame, self.parent.invEFrame, self.parent.outEFrame),
          axis=1,
          dtype=object)

    #the inventory at a specific time
    #changes based on if the sample time
    #was variable or constant
    #future TODO: change to have same structure
    #regardless of sample time
    for i in range(0, InLocs):
      if SEFrame is None:
        self.EP2.setItem(
            i, 0,
            QtWidgets.QTableWidgetItem(
                str(
                    round(
                        np.mean(
                            self.parent.SEMUFContribI[:, i, TimeLoc], axis=0),
                        4))))

      else:
        self.EP2.setItem(
            i, 0,
            QtWidgets.QTableWidgetItem(
                str(
                    round(
                        np.mean(
                            np.sum(
                                SEFrame[:, i, (TimeLoc - 1) * mbaTime:TimeLoc *
                                        mbaTime, EleLoc],
                                axis=1)), 4))))

      self.EP2.setItem(
          i, 1,
          QtWidgets.QTableWidgetItem(
              str(
                  round(
                      np.sqrt(
                          np.mean(
                              self.parent.SEMUFContribR[:, i, TimeLoc],
                              axis=0)), 4))))

      self.EP2.setItem(
          i, 2,
          QtWidgets.QTableWidgetItem(
              str(
                  round(
                      np.sqrt(
                          np.mean(
                              self.parent.SEMUFContribS[:, i, TimeLoc],
                              axis=0)), 4))))

    for i in range(InLocs, InvLocs + InLocs):
      if SEFrame is None:
        self.EP2.setItem(
            i + offset1, 0,
            QtWidgets.QTableWidgetItem(
                str(
                    round(
                        np.mean(
                            self.parent.SEMUFContribI[:, i, TimeLoc], axis=0),
                        4))))

      else:
        self.EP2.setItem(
            i + offset1, 0,
            QtWidgets.QTableWidgetItem(
                str(
                    round(np.mean(SEFrame[:, i, TimeLoc * mbaTime, EleLoc]),
                          4))))

      self.EP2.setItem(
          i + offset1, 1,
          QtWidgets.QTableWidgetItem(
              str(
                  round(
                      np.sqrt(
                          np.mean(
                              self.parent.SEMUFContribR[:, i, TimeLoc],
                              axis=0)), 4))))

      self.EP2.setItem(
          i + offset1, 2,
          QtWidgets.QTableWidgetItem(
              str(
                  round(
                      np.sqrt(
                          np.mean(
                              self.parent.SEMUFContribS[:, i, TimeLoc],
                              axis=0)), 4))))

    for i in range(InvLocs + InLocs, TotalLocs):
      if SEFrame is None:
        self.EP2.setItem(
            i + offset1 + offset2, 0,
            QtWidgets.QTableWidgetItem(
                str(
                    round(
                        np.mean(
                            self.parent.SEMUFContribI[:, i, TimeLoc], axis=0),
                        4))))

      else:
        self.EP2.setItem(
            i + offset1 + offset2, 0,
            QtWidgets.QTableWidgetItem(
                str(
                    round(
                        np.mean(
                            np.sum(
                                SEFrame[:, i, (TimeLoc - 1) * mbaTime:TimeLoc *
                                        mbaTime, EleLoc],
                                axis=1)), 4))))

      self.EP2.setItem(
          i + offset1 + offset2, 1,
          QtWidgets.QTableWidgetItem(
              str(
                  round(
                      np.sqrt(
                          np.mean(
                              self.parent.SEMUFContribR[:, i, TimeLoc],
                              axis=0)), 4))))

      self.EP2.setItem(
          i + offset1 + offset2, 2,
          QtWidgets.QTableWidgetItem(
              str(
                  round(
                      np.sqrt(
                          np.mean(
                              self.parent.SEMUFContribS[:, i, TimeLoc],
                              axis=0)), 4))))


class MPLCanvas(FigureCanvas):
  """
        Class with functions to control
        the plot in MAPIT
  """

  def __init__(self, parent=None, dpi=100):

    self.fig = Figure(dpi=dpi, frameon=True)
    self.fig.subplots_adjust(left=0.10, bottom=0.10, right=0.98, top=0.95)
    self.axes = self.fig.add_subplot(111)
    self.axes_defColor = self.axes.get_facecolor()

    self.compute_initial_figure()

    FigureCanvas.__init__(self, self.fig)
    self.setParent(parent)

    FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
    self.Thresh = []

  def compute_initial_figure(self):
    pass

  def update_figure(self, data, isVariableFlag=0):
    #change the default color cycle
    #dark and light colors provided

    if self.window().MakeLight.isChecked() == 0:
      matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=[
          self.window().colorsD.lb,
          self.window().colorsD.t,
          self.window().colorsD.a,
          self.window().colorsD.p,
          self.window().colorsD.y,
          self.window().colorsD.r,
          self.window().colorsD.g,
          self.window().colorsD.la,
          self.window().colorsD.o
      ])
    else:
      matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=[
          self.window().colors.lb,
          self.window().colors.t,
          self.window().colors.a,
          self.window().colors.p,
          self.window().colors.y,
          self.window().colors.r,
          self.window().colors.g,
          self.window().colors.la,
          self.window().colors.o
      ])

    self.axes.cla()

    if isVariableFlag == 1:
      self.axes.plot(data[:, 0], data[:, 1])
    elif isVariableFlag == 2:
      self.axes.plot(data[0], data[1])
    else:
      self.axes.plot(data)

    self.draw()

  def update_figure_title(self, data):
    self.axes.set_title(data[0])
    self.axes.title.set_color(self.axes.yaxis.label.get_color())
    self.axes.set_xlabel(data[1])
    self.axes.set_ylabel(data[2])
    self.draw()

  def update_thresh(self, data,
                    data2):  #draw the threshold from the threshold calculator
    if hasattr(self.Thresh, '__len__'):
      TH = np.ones((int(self.axes.get_lines()[0]._x.max()),)) * data
      self.Thresh, = self.axes.plot(TH, 'k')
      self.draw()
    else:
      TH = np.ones((int(self.axes.get_lines()[0]._x.max()),)) * data
      self.Thresh.remove()
      self.Thresh, = self.axes.plot(TH, 'k')
      self.draw()

    TotOver = 0
    if len(np.shape(data2)) == 2:
      TotOver = np.sum(np.max(data2, axis=1) > data) / np.shape(data2)[0] * 100
    else:
      TotOver = (np.max(data2) > data) / np.shape(data2)[0] * 100

    # prob a better way/method to do this
    # future TODO: fix this abomination of a code line
    self.parent().parent().parent().StatThreshDisp.setText(
        str(round(TotOver, 2)))


class LaunchGUI(QtWidgets.QMainWindow):
  """
        Main MAPIT class (Main window widget)

        This class sets some variables needed
        for MAPIT and handles some theme related
        items.
  """

  def __init__(self):
    super(LaunchGUI, self).__init__()
    self.CBHolder = []  #this is just for some of the style stuff later on
    self.hasRunIO = 0
    self.PuLoc = -1
    self.ULoc = -1
    self.GLoc = -1
    self.HasRunOnce = 0
    self.HasRunErrors = 0
    self.launch_master_window()
    self.RunStats.clicked.connect(lambda: StatsPackage.ErrorHandle.ExecIO(self))
    self.ErrorS.clicked.connect(self.InitErrors)
    self.PlotRunner.clicked.connect(self.ExecPlot)
    self.metricBox.activated.connect(self.UpdateLocOpts)

    Colors = namedtuple('Colors', [
        'db', 'mb', 'lb', 'b', 't', 'p', 'la', 'g', 'c', 'r', 'ro', 'o', 'a',
        'y', 'gr', 'wgr', 'bgr'
    ])
    ColorsD = namedtuple('ColorsD', [
        'db', 'mb', 'lb', 'b', 't', 'p', 'la', 'g', 'c', 'r', 'ro', 'o', 'a',
        'y', 'gr', 'wgr', 'bgr'
    ])

    #save some colors to be used later
    #these need to be better integrated
    #in the animations (future TODO)
    self.colors = Colors(
        '#003359', '#0076a9', '#00add0',
        '#0066cc', '#008e74', '#5a3cbf',
        '#b312b1', '#6cb312',
        '#822433', '#cc0000', '#f23f00',
        '#fd5947', '#ff8800', '#ffc200',
        '#999999', '#82786f',
        '#7d8ea0')

    self.colorsD = ColorsD(
        '#002541', '#00587e', '#00839d',
        '#004c99', '#006b57', '#442d8e',
        '#880d86', '#53880d',
        '#631b27', '#990000', '#b43000',
        '#d53220', '#bf6600', '#bf9300',
        '#737373', '#615953',
        '#5a6b7c')


    # bigger font here
    f = QtCore.QCoreApplication.instance().font()
    QtCore.QCoreApplication.instance().setFont(QtGui.QFont("Open Sans", 12))
    QtCore.QCoreApplication.instance().setStyle('Fusion')
    QtCore.QCoreApplication.instance().setApplicationDisplayName('MAPIT')
    #
    self.Lightpallette = QtCore.QCoreApplication.instance().palette()

    #setting up color palettes
    self.Darkpalette = QtGui.QPalette()
    self.Darkpalette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    self.Darkpalette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    self.Darkpalette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    self.Darkpalette.setColor(QtGui.QPalette.AlternateBase,
                              QtGui.QColor(53, 53, 53))

    self.Darkpalette.setColor(QtGui.QPalette.ToolTipBase,
                              QtGui.QColor(66, 66, 66))

    self.Darkpalette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    self.Darkpalette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    self.Darkpalette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    self.Darkpalette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    self.Darkpalette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    self.Darkpalette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    self.Darkpalette.setColor(QtGui.QPalette.Highlight,
                              QtGui.QColor(42, 130, 218))

    self.Darkpalette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)

    # inactive colors
    self.Darkpalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Window,
                              QtGui.QColor(53 + 20, 53 + 20, 53 + 20))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.WindowText,
                              QtGui.QColor(53, 53, 53))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base,
                              QtGui.QColor(25, 25, 25))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.AlternateBase,
                              QtGui.QColor(53 + 20, 53 + 20, 53 + 20))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    self.Darkpalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text,
                              QtCore.Qt.white)
    self.Darkpalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button,
                              QtGui.QColor(53 + 20, 53 + 20, 53 + 20))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.ButtonText,
                              QtGui.QColor(53, 53, 53))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.BrightText, QtCore.Qt.red)
    self.Darkpalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Link,
                              QtGui.QColor(42, 130, 218))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight,
                              QtGui.QColor(42, 130, 218))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    QtCore.QCoreApplication.instance().setPalette(self.Lightpallette)
    # in launch main window:
    # self.setStyleSheet('background-color: rgba(50, 50, 50, 1);')

    self.setStyleSheet("""QToolTip {
                           background-color: rgb(239,239,239);
                           border-width: 3px;
                           border-color: rgb(153,200,221);
                           border-style: solid;
                           border-radius: 3px;
                           color: black;
                           }""")

    #
    x = Path(sys.argv[0]).resolve().parents[1]
    F = os.path.join(x, 'assets', 'codeAssets', 'SNL_Horizontal_Black2.jpg')
    self.setWindowIcon(QtGui.QIcon(F))

    loadDlgBox = QtWidgets.QMessageBox()
    loadDlgBox.setIcon(QtWidgets.QMessageBox.Question)
    loadDlgBox.setText('Select data for analysis \n')
    loadDlgBox.setInformativeText('You may select your own data (.csv or .mat) or from included SNL generated datasets')
    CD = loadDlgBox.addButton('.csv dataset',QtWidgets.QMessageBox.ResetRole) #this is arbitrary, but if accept and reject roles aren't present then the red X to close the dialog wont work
    MD = loadDlgBox.addButton('.mat dataset',QtWidgets.QMessageBox.ApplyRole)
    SC = loadDlgBox.addButton('SNL curated dataset',QtWidgets.QMessageBox.RejectRole)
    QC = loadDlgBox.addButton('Quit', QtWidgets.QMessageBox.NoRole)

    loadDlgBox.exec()

    DoRun = 1

    if loadDlgBox.clickedButton() == CD:
        self.IOWindow()
    elif loadDlgBox.clickedButton() == MD:
        self.IOWindowM()
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

  def UpdateLocOpts(self):
    """
            Function to control
            GUI options once a GUI
            change has been detected
    """



    grad = "border-color: rgb({value},{value2},{value3});".format(value=153,value2=200,value3=221) +\
   "border-width: 2px;" +\
   "border-style: solid;" +\
   "padding: 0px;" +\
   "border-radius: 3px;" +\
   "margin-top: 10px;" +\
   "background-color: rgb(239,239,239);" +\
    "}"

    grad2 = "border-color: rgb({value},{value2},{value3});".format(value=211,value2=211,value3=211) +\
   "border-width: 2px;" +\
   "border-style: solid;" +\
   "padding: 0px;" +\
   "border-radius: 3px;" +\
   "margin-top: 10px;" +\
   "background-color: rgb(239,239,239);" +\
    "}"

    if self.window().MakeLight.isChecked() == 0:
      grad = grad.replace('rgb(239,239,239)', 'rgb(52,52,52)')
      grad = grad.replace('rgb(153,200,221)', 'rgb(0,83,118)')
      grad2 = grad2.replace('rgb(239,239,239)', 'rgb(52,52,52)')
      grad2 = grad2.replace('rgb(211,211,211)', 'rgb(66,66,66)')

    #not all combinations of plot options should have the same options
    #for example, ground truth shouldn't have iterations available
    #and MUF shouldn't have locations available

    # GT remove iterations
    if self.metricBox.currentText() == 'Ground Truth Data':
      for i in range(0, self.NumToPlot.count()):
        self.NumToPlot.removeItem(0)
      self.NumToPlot.setEnabled(0)
      self.mb4.ChangeActive(0)
      self.mb4.setStyleSheet(
          "QWidget#{VAL}".format(VAL=self.mb4.Loc) + "{" + grad2 +
          "QWidget#{VAL}".format(VAL=self.mb4.Loc) +
          ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")
    # OD add iterations
    elif self.metricBox.currentText() == 'Observed Data':
      if int(self.IterBox.text()) <= 100:
        if self.NumToPlot.count() > 0:
          for i in range(0, self.NumToPlot.count()):
            self.NumToPlot.removeItem(0)
        self.NumToPlot.addItem('1 Random Iteration')
        self.NumToPlot.addItem('Average of All Iterations')
        self.NumToPlot.addItem('All Iterations (' + self.IterBox.text() + ')')

      else:
        #if there's more than 100 iterations set a max of 15
        #to plot at once (keeps MPL backend from imploding)
        for i in range(0, self.NumToPlot.count()):
          self.NumToPlot.removeItem(0)

        self.NumToPlot.addItem('1 Random Iteration')
        self.NumToPlot.addItem('15 Random Iterations')
        self.NumToPlot.addItem('Average of All Iterations')
      self.NumToPlot.setEnabled(1)
      self.mb4.ChangeActive(1)
      self.mb4.setStyleSheet(
          "QWidget#{VAL}".format(VAL=self.mb4.Loc) + "{" + grad +
          "QWidget#{VAL}".format(VAL=self.mb4.Loc) +
          ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")
    else:
      None

    # GT/OD data - add ele and locs
    if self.metricBox.currentText(
    ) == 'Ground Truth Data' or self.metricBox.currentText() == 'Observed Data':
      if self.LocBox.count() == 0:
        for i in self.PlotLocLabels:
          if i != '':
            self.LocBox.addItem(i)
        for i in self.EleVecLabel:
          self.NucIDBox.addItem(i)
        self.LocBox.setEnabled(1)
        self.mb2.ChangeActive(1)
        self.mb2.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) + "{" + grad +
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) +
            ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")

        self.NucIDBox.setEnabled(1)
        self.mb3.ChangeActive(1)
        self.mb3.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) + "{" + grad +
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) +
            ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")

      else:
        None
    else:
      self.mb2.setStyleSheet('QGroupBox:title {' 'padding-right: 10px}')
      self.mb3.setStyleSheet('QGroupBox:title {' 'padding-right: 10px}')
      if self.LocBox.count(
      ) != 0:  # statistical test boxes - add iterations and remove location / ele ID
        for i in range(0, int(self.LocBox.count())):
          self.LocBox.removeItem(0)
        for i in range(0, int(self.NucIDBox.count())):
          self.NucIDBox.removeItem(0)

        self.LocBox.setEnabled(0)
        self.mb2.ChangeActive(0)
        self.mb2.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) + "{" + grad2 +
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) +
            ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")

        self.NucIDBox.setEnabled(0)
        self.mb3.ChangeActive(0)
        self.mb3.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) + "{" + grad2 +
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) +
            ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")

        if int(self.IterBox.text()) <= 100:  #check options for iterations
          if self.NumToPlot.count() > 0:
            for i in range(0, self.NumToPlot.count()):
              self.NumToPlot.removeItem(0)
          self.NumToPlot.addItem('1 Random Iteration')
          self.NumToPlot.addItem('Average of All Iterations')
          self.NumToPlot.addItem('All Iterations (' + self.IterBox.text() + ')')
        else:
          for i in range(0, self.NumToPlot.count()):
            self.NumToPlot.removeItem(0)
          self.NumToPlot.addItem('1 Random Iteration')
          self.NumToPlot.addItem('15 Random Iterations')
          self.NumToPlot.addItem('Average of All Iterations')
        self.NumToPlot.setEnabled(1)
        self.mb4.ChangeActive(1)
        self.mb4.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb4.Loc) + "{" + grad +
            "QWidget#{VAL}".format(VAL=self.mb4.Loc) +
            ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")
      else:
        #if not included then style will look weird when no changes
        #are made to the options, due to the style sheet change
        #at the top of this if block
        self.mb2.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) + "{" + grad2 +
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) +
            ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")
        self.mb3.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) + "{" + grad2 +
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) +
            ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")

  def UpdatePlotOpts(self):
    """
            Function to add GT and observed
            data options after error propogation
            has run. Also accounts for if
            this function is called after
            an initial calculation has been
            run.
    """

    # some logic in here to reset boxes as well
    if self.metricBox.count() > 0:
      for i in range(0, self.metricBox.count()):
        self.metricBox.removeItem(0)
      self.metricBox.addItem('Ground Truth Data')
      self.metricBox.addItem('Observed Data')
    else:
      self.metricBox.addItem('Ground Truth Data')
      self.metricBox.addItem('Observed Data')

    if self.NumToPlot.count() < 0:
      for i in range(0, self.NumToPlot.count()):
        self.NumToPlot.removeItem(i)
    else:
      None

  def ExecPlot(self):
    """
            This function is responsible for plotting
            data selected by a user
    """

    # determine how many to plot
    NumToPlot = 0
    if self.NumToPlot.currentText() == '1 Random Iteration':
      NumToPlot = 1
    elif self.NumToPlot.currentText() == 'Average of All Iterations':
      NumToPlot = -1
    elif self.NumToPlot.currentText(
    ) == 'All Iterations (' + self.IterBox.text() + ')':
      NumToPlot = -2
    elif self.NumToPlot.currentText() == '15 Random Iterations':
      NumToPlot = 15
    else:
      None

    # --------------- common plot variables ---------------------

    P = [self.NucIDBox.currentText()]
    if len(P[0]) > 5:
      NucIndex = int(P[0][8:len(P[0])]
                    ) - 1  # elements in GUI start at 1, python data starts at 0
    elif self.NucIDBox.currentText() != '':
      NucIndex = self.EleVecLabel.index(self.NucIDBox.currentText())
    else:
      None
    PlotIndex = int(self.LocBox.currentIndex())

    CanvasLabels = []
    # title, x, y
    if self.metricBox.currentText(
    ) == 'Ground Truth Data' or self.metricBox.currentText() == 'Observed Data':
      CanvasLabels.append(self.NucIDBox.currentText() + ' ' +
                          self.metricBox.currentText() + ' at ' +
                          self.LocBox.currentText())
    else:
      CanvasLabels.append(self.NucIDBox.currentText() + ' ' +
                          self.metricBox.currentText())

    if hasattr(self, 'Wizard'):
      CanvasLabels.append('Time (' + self.Wizard.TimeUnitVec + ')')
      CanvasLabels.append('Mass (' + self.Wizard.MassUnitVec + ')')
    else:
      CanvasLabels.append('Time (hr)')
      CanvasLabels.append('Mass (kg)')

    #this section is figuring out
    #what tests for what element
    #are available.

    #admitedly this section is a bit
    #convoluted so needs future TODO
    #code cleanup
    MUFIter = np.ones((3,)) * -1
    if self.CB_PuMUF.isChecked() == 1:
      MUFIter[0] = np.sum(MUFIter > -1)
    if self.CB_UMUF.isChecked() == 1:
      MUFIter[1] = np.sum(MUFIter > -1)
    if self.CB_GMUF.isChecked() == 1:
      MUFIter[2] = np.sum(MUFIter > -1)

    SEIDIter = np.ones((3,)) * -1
    if self.CB_PuSMUF.isChecked() == 1:
      SEIDIter[0] = np.sum(SEIDIter > -1)
    if self.CB_USMUF.isChecked() == 1:
      SEIDIter[1] = np.sum(SEIDIter > -1)
    if self.CB_GSMUF.isChecked() == 1:
      SEIDIter[2] = np.sum(SEIDIter > -1)

    SITMUFIter = np.ones((3,)) * -1
    if self.CB_PuSITMUF.isChecked() == 1:
      SITMUFIter[0] = np.sum(SITMUFIter > -1)
    if self.CB_USITMUF.isChecked() == 1:
      SITMUFIter[1] = np.sum(SITMUFIter > -1)
    if self.CB_GSITMUF.isChecked() == 1:
      SITMUFIter[2] = np.sum(SITMUFIter > -1)

    PageIter = np.ones((3,)) * -1
    if self.CB_PuSPage.isChecked() == 1:
      PageIter[0] = np.sum(PageIter > -1)
    if self.CB_USPage.isChecked() == 1:
      PageIter[1] = np.sum(PageIter > -1)
    if self.CB_GSPage.isChecked() == 1:
      PageIter[2] = np.sum(PageIter > -1)

    MUFIter = MUFIter.astype('int')
    SEIDIter = SEIDIter.astype('int')
    SITMUFIter = SITMUFIter.astype('int')
    PageIter = PageIter.astype('int')
    TP = -1
    TP2 = -1
    TP3 = -1
    TP4 = -1

    # ---------------------------------------------------------------

    if self.metricBox.currentText() == 'Ground Truth Data':

      if isinstance(self.inpFrame, list) == 0 and isinstance(self.invFrame, list) == 0 and isinstance(self.outFrame, list) == 0:
        PlotDat = np.concatenate((self.inpFrame, self.invFrame, self.outFrame),
                                 axis=0,
                                 dtype=object)
        self.canvas.update_figure(PlotDat[PlotIndex, :, NucIndex])
        self.canvas.update_figure_title(CanvasLabels)
        self.ThreshData = PlotDat[PlotIndex, :, NucIndex]

      else:
        #okay here is where we deal with variable
        #length arrays (i.e. non-constant sampling)

        #first find out what the plotindex belongs to
        #shape(list) is depreciated
        if isinstance(self.inpFrame, list):
          A1 = len(self.inpFrame)
        else:
          A1 = np.shape(self.inpFrame)[0]

        if isinstance(self.invFrame, list):
          A2 = len(self.invFrame)
        else:
          A2 = np.shape(self.invFrame)[0]

        if isinstance(self.outFrame, list):
          A3 = len(self.outFrame)
        else:
          A3 = np.shape(self.outFrame)[0]

        intervals = np.array([A1, A1 + A2, A1 + A2 + A3]) - 1
        plttyp = bisect.bisect_left(intervals, PlotIndex)

        localIndex = PlotIndex - (A1 * (plttyp >= 1) + A2 * (plttyp == 2))

        if plttyp == 0:
          #could be a list
          #could just do asarray(list) here later
          if isinstance(self.inpFrame, list):
            PDD = self.inpFrame[localIndex][:, NucIndex]
            PDD2 = self.inpTimeFrame[localIndex][:,NucIndex]
            EE = np.where(np.diff(PDD2) > 1)

            #list mode data is sometimes dense, but still represents pulses
            #for nicer plotting, add some zeros to make pulses more rounded
            for i in range(len(EE[0])): #len(EE[0])-1
                d = np.array([0])
                if i == 0:
                    RI = int(np.max(np.where(PDD[0:EE[0][0]]>0)))
                    xnew = np.concatenate(([np.array([PDD2[0]-1e-5]),PDD2[0:EE[0][0]][:RI],np.array([PDD2[:EE[0][0]][RI]+1e-5])]))
                    ynew = np.concatenate((d,PDD[0:EE[0][0]][:RI],d))
                else:
                    RI = int(np.max(np.where(PDD[EE[0][i-1]+1:EE[0][i]]>0)))
                    xnew = np.concatenate((xnew,np.array([PDD2[EE[0][i-1]+1]-1e-5]),PDD2[EE[0][i-1]+1:EE[0][i]][:RI],np.array([PDD2[EE[0][i-1]+1:EE[0][i]][RI]+1e-5])))
                    ynew = np.concatenate((ynew,d,PDD[EE[0][i-1]+1:EE[0][i]][:RI],d))

            if len(EE[0]) > 1:
              PDD2 = xnew
              PDD = ynew

          else:
            PDD = self.inpFrame[localIndex, :, NucIndex]
            PDD2 = self.inpTimeFrame[localIndex, :, NucIndex]

          self.canvas.update_figure(
              np.concatenate(
                  (PDD2.reshape((-1,1)), PDD.reshape((-1, 1))),axis=1), 1)
          self.canvas.update_figure_title(CanvasLabels)
          self.ThreshData = PDD

        elif plttyp == 1:
          if isinstance(self.invFrame, list):
            PDD = self.invFrame[localIndex][:, NucIndex]
            PDD2 = self.invTimeFrame[localIndex][:,NucIndex]
          else:
            PDD = self.invFrame[localIndex, :, NucIndex]
            PDD2 = self.invTimeFrame[localIndex, :, NucIndex]

          self.canvas.update_figure(

              np.concatenate(
                  (PDD2.reshape((-1,1)), PDD.reshape((-1, 1))),axis=1), 1)
          self.canvas.update_figure_title(CanvasLabels)
          self.ThreshData = PDD

        else:
          if isinstance(self.outFrame, list):
            PDD = self.outFrame[localIndex][:, NucIndex]
            PDD2 = self.outTimeFrame[localIndex][:,NucIndex]
            EE = np.where(np.diff(PDD2) > 1)

            for i in range(len(EE[0])): #len(EE[0])-1
                d = np.array([0])
                if i == 0:
                    RI = int(np.max(np.where(PDD[0:EE[0][0]]>0)))
                    xnew = np.concatenate(([np.array([PDD2[0]-1e-5]),PDD2[0:EE[0][0]][:RI],np.array([PDD2[:EE[0][0]][RI]+1e-5])]))
                    ynew = np.concatenate((d,PDD[0:EE[0][0]][:RI],d))
                else:
                    RI = int(np.max(np.where(PDD[EE[0][i-1]+1:EE[0][i]]>0)))
                    xnew = np.concatenate((xnew,np.array([PDD2[EE[0][i-1]+1]-1e-5]),PDD2[EE[0][i-1]+1:EE[0][i]][:RI],np.array([PDD2[EE[0][i-1]+1:EE[0][i]][RI]+1e-5])))
                    ynew = np.concatenate((ynew,d,PDD[EE[0][i-1]+1:EE[0][i]][:RI],d))
            if len(EE[0]) > 1:
              PDD2 = xnew
              PDD = ynew

          else:
            PDD = self.outFrame[localIndex, :, NucIndex]
            PDD2 = self.outTimeFrame[localIndex, :, NucIndex]

          self.canvas.update_figure(
              np.concatenate(
                  (PDD2.reshape((-1,1)), PDD.reshape((-1, 1))),axis=1,dtype=object), 1)
          self.canvas.update_figure_title(CanvasLabels)
          self.ThreshData = PDD

    elif self.metricBox.currentText() == 'Observed Data':

      # iter, location, timestep, element

      if isinstance(self.invEFrame,list) == False:  #is this uniformly sampled (if so concatenate will succeed)

        PlotDat = np.concatenate(
            (self.inpEFrame, self.invEFrame, self.outEFrame),
            axis=1,
            dtype=object)

        if NumToPlot == 1:  #1
          IterIndex = np.random.randint(
              low=0, high=int(self.IterBox.text()) - 1)
          self.canvas.update_figure(PlotDat[IterIndex, PlotIndex, :, NucIndex])
          self.ThreshData = PlotDat[IterIndex, PlotIndex, :, NucIndex]

        elif NumToPlot == -1:  #average
          self.canvas.update_figure(
              np.mean(PlotDat[:, PlotIndex, :, NucIndex], axis=0))
          self.ThreshData = np.mean(PlotDat[:, PlotIndex, :, NucIndex], axis=0)

        elif NumToPlot == -2:  #all
          self.canvas.update_figure(PlotDat[:, PlotIndex, :, NucIndex].T)
          self.ThreshData = PlotDat[:, PlotIndex, :, NucIndex].T

        elif NumToPlot == 15:  #random 15
          indexes = np.zeros((15,))
          for i in range(0, 15):
            indexes[i] = np.random.randint(
                low=0, high=int(self.IterBox.text()) - 1)

          self.canvas.update_figure(PlotDat[indexes.astype('int'), PlotIndex, :,
                                            NucIndex].T)
          self.ThreshData = PlotDat[indexes.astype('int'), PlotIndex, :,
                                    NucIndex].T

        else:
          None

        self.canvas.update_figure_title(CanvasLabels)

      else:  #this is not uniformily sampled

        #which terms are not uniformly sampled
        if isinstance(self.inpEFrame, list):
          A1 = len(self.inpEFrame)
        else:
          A1 = np.shape(self.inpEFrame)[0]

        if isinstance(self.invEFrame, list):
          A2 = len(self.invEFrame)
        else:
          A2 = np.shape(self.invEFrame)[0]

        if isinstance(self.outEFrame, list):
          A3 = len(self.outEFrame)
        else:
          A3 = np.shape(self.outEFrame)[0]

        #breakdown the indicies into intervals
        intervals = np.array([A1, A1 + A2, A1 + A2 + A3]) - 1
        plttyp = bisect.bisect_left(
            intervals, PlotIndex
        )  #plotIndex is where in the array the requested quantity is, question is is it inp, inv, or out?

        localIndex = PlotIndex - (
            A1 * (plttyp >= 1) + A2 * (plttyp == 2)
        )  #what is the index in the specific quantity type (i.e. what's the index in the inventory array)

        PH = []
        if plttyp == 0:
          #could be a list
          #could just do asarray(list) here later
          if isinstance(self.inpEFrame, list):
            PDD = self.inpEFrame[localIndex][:, :,
                                             NucIndex]  #get the measured data
            PDD2 = self.inpTimeFrame[
                localIndex][:, NucIndex]  #get the corresponding time

          else:
            PDD = self.inpEFrame[localIndex, :, :, NucIndex]
            PDD2 = self.inpTimeFrame[localIndex, :, :, NucIndex]

          PH.append(PDD2)
          PH.append(PDD)

        elif plttyp == 1:
          if isinstance(self.invEFrame, list):
            PDD = self.invEFrame[localIndex][:, :, NucIndex]
            PDD2 = self.invTimeFrame[localIndex][:, NucIndex]
          else:
            PDD = self.invEFrame[localIndex, :, :, NucIndex]
            PDD2 = self.invTimeFrame[localIndex, :, :, NucIndex]

          PH.append(PDD2)
          PH.append(PDD)

        else:
          if isinstance(self.outEFrame, list):
            PDD = self.outEFrame[localIndex][:, :, NucIndex]
            PDD2 = self.outTimeFrame[localIndex][:, NucIndex]
          else:
            PDD = self.outEFrame[localIndex, :, :, NucIndex]
            PDD2 = self.outTimeFrame[localIndex, :, :, NucIndex]

          PH.append(PDD2)
          PH.append(PDD)

        #FH = np.zeros(np.shape(PH[1]))
        #improved plotting visuals for pulses
        #note this won't show noise for zero values
        #as usually only dense, non-zero data is recorded
        #so no noise can be added to zeros (as they are unrecorded)
        #this is just an improved visual
        if len(np.where(np.diff(PH[0]) > 1)[0]) > 0:
          for J in range(np.shape(PH[1])[0]):
            PDD = PH[1][J,:]
            PDD2 = PH[0]
            EE = np.where(np.diff(PDD2) > 1)


            for i in range(len(EE[0])): #len(EE[0])-1
                d = np.array([0])
                if i == 0:
                    RI = int(np.max(np.where(PDD[0:EE[0][0]]>0)))
                    xnew = np.concatenate(([np.array([PDD2[0]-1e-5]),PDD2[0:EE[0][0]][:RI],np.array([PDD2[:EE[0][0]][RI]+1e-5])]))
                    ynew = np.concatenate((d,PDD[0:EE[0][0]][:RI],d))
                else:
                    RI = int(np.max(np.where(PDD[EE[0][i-1]+1:EE[0][i]]>0)))
                    xnew = np.concatenate((xnew,np.array([PDD2[EE[0][i-1]+1]-1e-5]),PDD2[EE[0][i-1]+1:EE[0][i]][:RI],np.array([PDD2[EE[0][i-1]+1:EE[0][i]][RI]+1e-5])))
                    ynew = np.concatenate((ynew,d,PDD[EE[0][i-1]+1:EE[0][i]][:RI],d))

            if len(EE[0]) > 1:
              PDD2 = xnew
              PDD = ynew
            if J == 0:
              FH = np.zeros((np.shape(PH[1])[0],np.shape(ynew)[0]))
            FH[J,:] = ynew

          PH[1] = FH
          PH[0] = PDD2
          del FH #garbage cleanup

        #how many to plot?
        if NumToPlot == 1:  #1
          IterIndex = np.random.randint(
              low=0, high=int(self.IterBox.text()) - 1)
          PH[1] = PH[1][IterIndex, :].reshape((-1,))
          self.canvas.update_figure(
              PH, 2
          )  #the 2 flag indicates theres X and Y data (as it is not unformly sampled)
          self.ThreshData = PH[1]

        elif NumToPlot == -1:  #average
          PH[1] = np.mean(PH[1], axis=0)
          self.canvas.update_figure(PH, 2)
          self.ThreshData = PH[1]

        elif NumToPlot == -2:  #all

          PH[1] = PH[1].T
          self.canvas.update_figure(PH, 2)
          self.ThreshData = PH[1].T

        elif NumToPlot == 15:  #random 15
          indexes = np.zeros((15,))
          for i in range(0, 15):
            indexes[i] = np.random.randint(
                low=0, high=int(self.IterBox.text()) - 1)

          PH[1] = PH[1][indexes.astype('int'), :]
          if PH[1].shape[0] < PH[1].shape[1]:
            PH[1] = PH[1].T
          self.canvas.update_figure(PH, 2)
          self.ThreshData = PH[1]

        else:
          None

        self.canvas.update_figure_title(CanvasLabels)

    elif self.metricBox.currentText() == 'Pu MUF':
      TP = MUFIter[0]
    elif self.metricBox.currentText() == 'Pu SEID':
      TP2 = SEIDIter[0]
    elif self.metricBox.currentText() == 'Pu SITMUF':
      TP3 = SITMUFIter[0]
    elif self.metricBox.currentText() == 'Page Pu SITMUF':
      TP4 = PageIter[0]
    elif self.metricBox.currentText() == 'U MUF':
      TP = MUFIter[1]
    elif self.metricBox.currentText() == 'U SEID':
      TP2 = SEIDIter[1]
    elif self.metricBox.currentText() == 'U SITMUF':
      TP3 = SITMUFIter[1]
    elif self.metricBox.currentText() == 'Page U SITMUF':
      TP4 = PageIter[1]
    elif self.metricBox.currentText() == 'Generic MUF':
      TP = MUFIter[2]
    elif self.metricBox.currentText() == 'Generic SEID':
      TP2 = SEIDIter[2]
    elif self.metricBox.currentText() == 'Generic SITMUF':
      TP3 = SITMUFIter[2]
    elif self.metricBox.currentText() == 'Generic Page SITMUF':
      TP4 = PageIter[2]
    else:
      None

    # if plot MUF
    if TP > -1:
      PlotDat = self.MUFCalcs

      if NumToPlot == 1:
        IterIndex = np.random.randint(
            low=0, high=int(self.IterBox.text()) - 1)  #get a random iteration
        self.canvas.update_figure(PlotDat[IterIndex, TP, :])

      elif NumToPlot == -1:
        self.canvas.update_figure(np.mean(PlotDat[:, TP, :],
                                          axis=0))  #plot the mean

      elif NumToPlot == -2:
        self.canvas.update_figure(PlotDat[:, MUFIter[2], :].T)  #plot them all

      elif NumToPlot == 15:
        indexes = np.zeros((15,))
        for i in range(0, 15):
          indexes[i] = np.random.randint(
              low=0, high=int(self.IterBox.text()) - 1)

        self.canvas.update_figure(PlotDat[indexes.astype('int'),
                                          TP, :].T)  #plot 15 iterations

      else:
        None

      #setup the plot label
      if hasattr(self, 'Wizard'):
        CanvasLabels[2] = ('MUF (' + self.Wizard.MassUnitVec + ')')

      else:
        CanvasLabels[2] = ('MUF (kg)')

      self.canvas.update_figure_title(CanvasLabels)
      self.ThreshData = PlotDat[:, TP, :]

    # if plot SEID
    #code largely mimics the plot
    #code for MUF above
    if TP2 > -1:
      PlotDat = self.SEMUFCalcs

      if NumToPlot == 1:
        IterIndex = np.random.randint(low=0, high=int(self.IterBox.text()) - 1)
        self.canvas.update_figure(PlotDat[IterIndex, TP2, :])

      elif NumToPlot == -1:
        self.canvas.update_figure(np.mean(PlotDat[:, TP2, :], axis=0))

      elif NumToPlot == -2:
        self.canvas.update_figure(PlotDat[:, TP2, :].T)

      elif NumToPlot == 15:
        indexes = np.zeros((15,))
        for i in range(0, 15):
          indexes[i] = np.random.randint(
              low=0, high=int(self.IterBox.text()) - 1)

        self.canvas.update_figure(PlotDat[indexes.astype('int'), TP2, :].T)

      else:
        None

      if hasattr(self, 'Wizard'):
        CanvasLabels[2] = ('SEID (' + self.Wizard.MassUnitVec + ')')

      else:
        CanvasLabels[2] = ('SEID (kg)')

      self.canvas.update_figure_title(CanvasLabels)
      self.ThreshData = PlotDat[:, TP2, :]

    # if plot SITMUF
    if TP3 > -1:
      PlotDat = self.SITMUFCalcs

      if NumToPlot == 1:
        IterIndex = np.random.randint(low=0, high=int(self.IterBox.text()) - 1)
        self.canvas.update_figure(PlotDat[IterIndex, TP3, :])

      elif NumToPlot == -1:
        self.canvas.update_figure(np.mean(PlotDat[:, TP3, :], axis=0))

      elif NumToPlot == -2:
        self.canvas.update_figure(PlotDat[:, TP3, :].T)

      elif NumToPlot == 15:
        indexes = np.zeros((15,))
        for i in range(0, 15):
          indexes[i] = np.random.randint(
              low=0, high=int(self.IterBox.text()) - 1)

        self.canvas.update_figure(PlotDat[indexes.astype('int'), TP3, :].T)

      else:
        None

      if hasattr(self, 'Wizard'):
        CanvasLabels[2] = ('SITMUF (' + self.Wizard.MassUnitVec + ')')

      else:
        CanvasLabels[2] = ('SITMUF (kg)')
      self.canvas.update_figure_title(CanvasLabels)
      self.ThreshData = PlotDat[:, TP3, :]

    # if plot page
    if TP4 > -1:
      PlotDat = self.PageCalcs

      if NumToPlot == 1:
        IterIndex = np.random.randint(low=0, high=int(self.IterBox.text()) - 1)
        self.canvas.update_figure(PlotDat[IterIndex, TP4, :])

      elif NumToPlot == -1:
        self.canvas.update_figure(np.mean(PlotDat[:, TP4, :], axis=0))

      elif NumToPlot == -2:
        self.canvas.update_figure(PlotDat[:, TP4, :].T)

      elif NumToPlot == 15:
        indexes = np.zeros((15,))
        for i in range(0, 15):
          indexes[i] = np.random.randint(
              low=0, high=int(self.IterBox.text()) - 1)

        self.canvas.update_figure(PlotDat[indexes.astype('int'), TP4, :].T)
      else:
        None

      # print("A")
      CanvasLabels[2] = 'Page Score'
      self.canvas.update_figure_title(CanvasLabels)
      self.ThreshData = PlotDat[:, TP4, :]

    if self.CalcThresh.isEnabled() == 0:
      self.CalcThresh.setEnabled(1)
      self.CalcThresh.PassLoc('CTB')
      self.CalcThresh._animation.start()

  def InitErrors(self):
    """
            Function to select
            errors for imported or
            scenario data.
    """
    self.RunStats.setEnabled(
        1)  #flag to show that the calc has run at least once


    if self.HasRunErrors == 1:  #if has run previously get those values
      pastEVals = np.zeros((self.EP.rowCount(), 6))
      for i in range(0, self.EP.rowCount()):
        for j in range(0, 6):
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

    self.AllRand.activated.connect(self.RandBoxChanged)
    self.AllSys.activated.connect(self.SysBoxChanged)

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

    self.InpRand.activated.connect(self.InpRandFcn)
    self.InpSys.activated.connect(self.InpSysFcn)

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

    self.InvRand.activated.connect(self.InvRandFcn)
    self.InvSys.activated.connect(self.InvSysFcn)

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

    self.OutRand.activated.connect(self.OutRandFcn)
    self.OutSys.activated.connect(self.OutSysFcn)

    OE_L.addWidget(OutRandLabel, 0, 0)
    OE_L.addWidget(OutSysLabel, 0, 1)
    OE_L.addWidget(self.OutRand, 1, 0)
    OE_L.addWidget(self.OutSys, 1, 1)
    bc_L.addWidget(OutError)

    # table pane
    self.EP = QtWidgets.QTableWidget()

    if hasattr(self, 'Wizard'):
      TotalLocs = int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + int(
          self.Wizard.OutKMP)

      self.EP.setColumnCount(6)
      self.EP.setHorizontalHeaderLabels([
        'U Rand ', 'U Sys', 'Pu Rand', 'Pu Sys', 'Generic Rand', 'Generic Sys'
    ])
    else:
      TotalLocs = len(self.SS.Inputs) + len(self.SS.Inventories) + len(self.SS.Outputs)
      x = Path(sys.argv[0]).resolve().parents[1]
      F = os.path.join(x, 'data', 'fuel_fab', self.SS.sceneName, 'auxData.npz')
      A = np.load(F)
      A = A['arr1']
      self.EP.setColumnCount(2)
      self.EP.setHorizontalHeaderLabels(['U Rand ', 'U Sys'])
      self.EP.setHorizontalHeaderLabels(A)



    self.EP.setRowCount(TotalLocs + 2)
    ep_L.addWidget(self.EP)

    if hasattr(self, 'Wizard'):  #if data is imported
      # attempt to grab the row names

      # split convert string into list
      if self.Wizard.InKMP_names != '':
        self.Wizard.InKMP_names = self.Wizard.InKMP_names.split(',')
      else:
        None

      if self.Wizard.InvKMP_names != '':
        self.Wizard.InvKMP_names = self.Wizard.InvKMP_names.split(',')
      else:
        None

      if self.Wizard.OutKMP_names != '':
        self.Wizard.OutKMP_names = self.Wizard.OutKMP_names.split(',')
      else:
        None

      rowNames = [None] * (TotalLocs + 2)  #2 extra rows for spacers

      for i in range(0, int(
          self.Wizard.InKMP)):  #if no names provided, add some generic ones
        if self.Wizard.InKMP_names == '':
          rowNames[i] = 'input' + str(i + 1)

        elif i >= len(self.Wizard.InKMP_names):
          rowNames[i] = 'input' + str(i + 1)

        else:
          rowNames[i] = self.Wizard.InKMP_names[i]

      rowNames[int(self.Wizard.InKMP)] = ''

      for i in range(0, int(self.Wizard.InvKMP)):
        if self.Wizard.InvKMP_names == '':
          rowNames[i + int(self.Wizard.InKMP) + 1] = 'inventory' + str(i + 1)

        elif i >= len(self.Wizard.InvKMP_names):
          rowNames[i + int(self.Wizard.InKMP) + 1] = 'inventory' + str(i + 1)

        else:
          rowNames[i + int(self.Wizard.InKMP)] = self.Wizard.InvKMP_names[i]

      rowNames[int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + 1] = ''

      for i in range(0, int(self.Wizard.OutKMP)):
        if self.Wizard.OutKMP_names == '':
          rowNames[i + int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) +
                   2] = 'output' + str(i + 1)

        elif i >= len(self.Wizard.OutKMP_names):
          rowNames[i + int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) +
                   2] = 'output' + str(i + 1)

        else:
          rowNames[i + int(self.Wizard.InKMP) +
                   int(self.Wizard.InvKMP)] = self.Wizard.OutKMP_names[i]

      self.EP.setVerticalHeaderLabels(rowNames)
      self.PlotLocLabels = list(
          filter(len, rowNames)
      )  #removes spaces which don't serve an asthetic purpose in the plot list

      if self.HasRunErrors == 0:
        for i in range(0, self.EP.rowCount()):
          for j in range(0, TotalLocs + 2):
            if self.EP.verticalHeaderItem(j).text() != '' and self.EP.horizontalHeaderItem(i) is not None:
              self.EP.setItem(j, i, QtWidgets.QTableWidgetItem(str(0.5)))

    else:  #predetermined labels for fuel fab scenario
      x = Path(sys.argv[0]).resolve().parents[1]
      F = os.path.join(x, 'data', 'fuel_fab', self.SS.sceneName, 'auxData.npz')
      A = np.load(F)

      self.EP.setVerticalHeaderLabels(A['arr2'])
      self.PlotLocLabels = list(
          filter(len, A['arr2'])
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
    self.saveEConfig.clicked.connect(self.SaveEfcn)
    self.loadEConfig.clicked.connect(self.LoadEfcn)
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
    #

  def RandBoxChanged(self):
    """
            Function for when random (all locations)
            error box has been changed
    """

    #this sets the value of the individual dropdown boxes
    #to be the same as the overall random error box
    self.InpRand.setCurrentIndex(self.AllRand.currentIndex())
    self.InvRand.setCurrentIndex(self.AllRand.currentIndex())
    self.OutRand.setCurrentIndex(self.AllRand.currentIndex())

    if hasattr(self, 'Wizard'):
      TotalLocs = int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + int(
          self.Wizard.OutKMP)
    else:
      TotalLocs = len(self.SS.Inputs) + len(self.SS.Inventories) + len(self.SS.Outputs.shape)
    RC = self.EP.columnCount()


    i = 0
    while i < 5:
      for j in range(0, self.EP.rowCount()):
        if self.EP.item(j, i) is not None:
          self.EP.setItem(
              j, i, QtWidgets.QTableWidgetItem(str(self.AllRand.currentText())))
      i += 2
    # change all the rows

  def SysBoxChanged(self):
    """
            Function for when systematic (all locations)
            error box has been changed
    """

    #this sets the value of the individual dropdown boxes
    #to be the same as the overall systematic error box
    self.InpSys.setCurrentIndex(self.AllSys.currentIndex())
    self.InvSys.setCurrentIndex(self.AllSys.currentIndex())
    self.OutSys.setCurrentIndex(self.AllSys.currentIndex())

    if hasattr(self, 'Wizard'):
      TotalLocs = int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + int(
          self.Wizard.OutKMP)
    else:
      TotalLocs = len(self.SS.Inputs) + len(self.SS.Inventories) + len(self.SS.Outputs.shape)


    i = 1
    while i < 6:
      for j in range(0, self.EP.rowCount()):
        if self.EP.item(j, i) is not None:
          self.EP.setItem(
              j, i, QtWidgets.QTableWidgetItem(str(self.AllSys.currentText())))
      i += 2

  def InpRandFcn(self):
    """
            Function changes all the random
            input errors
    """

    if hasattr(self, 'Wizard'):
      TD = int(self.Wizard.InKMP)
      TD2 = int(self.Wizard.InvKMP)
      TD3 = int(self.Wizard.OutKMP)
    else:
      TD = len(self.SS.Inputs)
      TD2 = len(self.SS.Inventories)
      TD3 = len(self.SS.Outputs.shape)


    i = 0
    while i < 5:
      for j in range(0, int(TD)):
        if self.EP.item(j, i) is not None:
          self.EP.setItem(
              j, i, QtWidgets.QTableWidgetItem(str(self.InpRand.currentText())))
      i += 2

  def InpSysFcn(self):
    """
            Function changes all the systematic
            input errors
    """

    if hasattr(self, 'Wizard'):
      TD = int(self.Wizard.InKMP)
      TD2 = int(self.Wizard.InvKMP)
      TD3 = int(self.Wizard.OutKMP)
    else:
      TD = len(self.SS.Inputs)
      TD2 = len(self.SS.Inventories)
      TD3 = len(self.SS.Outputs.shape)


    i = 1
    while i < 6:
      for j in range(0, int(TD)):
        if self.EP.item(j, i) is not None:
          self.EP.setItem(
              j, i, QtWidgets.QTableWidgetItem(str(self.InpSys.currentText())))
      i += 2

  def InvRandFcn(self):
    """
            Function changes all the random
            inventory errors
    """

    if hasattr(self, 'Wizard'):
      TD = int(self.Wizard.InKMP)
      TD2 = int(self.Wizard.InvKMP)
      TD3 = int(self.Wizard.OutKMP)
    else:
      TD = len(self.SS.Inputs)
      TD2 = len(self.SS.Inventories) +1
      TD3 = len(self.SS.Outputs.shape) +1


    i = 0
    while i < 5:
      for j in range(int(TD) + 1, int(TD + TD2) + 1):
        if self.EP.item(j, i) is not None:
          self.EP.setItem(
              j, i, QtWidgets.QTableWidgetItem(str(self.InvRand.currentText())))
      i += 2

  def InvSysFcn(self):
    """
            Function changes all the systematic
            inventory errors
    """

    if hasattr(self, 'Wizard'):
      TD = int(self.Wizard.InKMP)
      TD2 = int(self.Wizard.InvKMP)
      TD3 = int(self.Wizard.OutKMP)
    else:
      TD = len(self.SS.Inputs)
      TD2 = len(self.SS.Inventories) +1
      TD3 = len(self.SS.Outputs.shape) +1


    i = 1
    while i < 6:
      for j in range(
          int(TD) + 1,
          int(TD + TD2) + 1
      ):  #the +1 (and +2 for outputs) adjusts for spacer rows being present
        if self.EP.item(j, i) is not None:
          self.EP.setItem(
              j, i, QtWidgets.QTableWidgetItem(str(self.InvSys.currentText())))
      i += 2

  def OutRandFcn(self):
    """
            Function changes all the random
            output errors
    """

    if hasattr(self, 'Wizard'):
      TD = int(self.Wizard.InKMP)
      TD2 = int(self.Wizard.InvKMP)
      TD3 = int(self.Wizard.OutKMP)
    else:
      TD = len(self.SS.Inputs)
      TD2 = len(self.SS.Inventories) +1
      TD3 = len(self.SS.Outputs.shape) +1


    i = 0
    while i < 5:
      for j in range(int(TD + TD2) + 2, int(TD + TD2 + TD3) + 2):
        if self.EP.item(j, i) is not None:
          self.EP.setItem(
              j, i, QtWidgets.QTableWidgetItem(str(self.OutRand.currentText())))
      i += 2

  def OutSysFcn(self):
    """
            Function changes all the systematic
            output errors
    """

    if hasattr(self, 'Wizard'):
      TD = int(self.Wizard.InKMP)
      TD2 = int(self.Wizard.InvKMP)
      TD3 = int(self.Wizard.OutKMP)
    else:
      TD = len(self.SS.Inputs)
      TD2 = len(self.SS.Inventories) +1
      TD3 = len(self.SS.Outputs.shape) +1


    i = 1
    while i < 6:
      for j in range(int(TD + TD2) + 2, int(TD + TD2 + TD3) + 2):
        if self.EP.item(j, i) is not None:
          self.EP.setItem(
              j, i, QtWidgets.QTableWidgetItem(str(self.OutSys.currentText())))
      i += 2

  def LoadEfcn(self):
    """
            This function loads previously
            configured error values
    """

    outdir = os.path.join(os.getcwd(), 'errorConfig.csv')
    x = np.loadtxt(outdir, delimiter=',')

    for i in range(np.shape(x)[0]):
      for j in range(np.shape(x)[1]):
        if x[i, j] != 0:
          self.EP.setItem(i, j, QtWidgets.QTableWidgetItem(str(x[i, j])))

  def SaveEfcn(self):
    """
            This function saves configured
            error values
    """

    outdir = os.path.join(os.getcwd(), 'errorConfig.csv')

    x = np.zeros((self.EP.rowCount(), 6))

    for i in range(0, self.EP.rowCount()):
      for j in range(0, 6):
        if self.EP.item(i, j) is None:
          x[i, j] = 0
        else:
          x[i, j] = self.EP.item(i, j).text()

    np.savetxt(outdir, x, delimiter=',')

  def ScenarioSelector(self):
    """
            This function launches the
            scenario selector and sets
            some GUI elements.
    """

    self.ErrorS.setEnabled(1)
    QtCore.QCoreApplication.instance().processEvents()
    self.SS = SceneSelect(self)
    self.SS.setWindowModality(QtCore.Qt.ApplicationModal)
    self.SS.exec_()
    self.StatDlg._animation.stop()
    self.StatDlg._animation.updateCurrentValue(2)
    self.StatDlg.UpdateDispText('Waiting for calculation setup...')

    #disable some checkboxes for fuel fab scenario
    #fuel fab only has uranium and some other
    #non actinide materials

    self.CB_PuMUF.setEnabled(0)
    self.CB_PuSMUF.setEnabled(0)
    self.CB_PuSITMUF.setEnabled(0)
    self.CB_PuSPage.setEnabled(0)

    self.CB_GMUF.setEnabled(0)
    self.CB_GSMUF.setEnabled(0)
    self.CB_GSITMUF.setEnabled(0)
    self.CB_GSPage.setEnabled(0)

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

    self.statusBar().setStyleSheet('')

    QtCore.QCoreApplication.instance().processEvents()

    self.ErrorS.setEnabled(1)
    self.Wizard = IOWizardMain(self)

    # blocks input to main GUI while IO is active
    self.Wizard.setWindowModality(QtCore.Qt.ApplicationModal)
    self.Wizard.exec_()
    self.StatDlg._animation.stop()
    self.StatDlg._animation.updateCurrentValue(2)

    self.SGSetContainer.PassLoc('PB6')
    self.SGSetContainer._animation.start()

    self.AnalysisContainer.PassLoc('PB7')
    self.AnalysisContainer._animation.start()

    self.ErrorS.PassLoc('EAB')
    self.ErrorS._animation.start()

  def IOWindowM(self):
    """
            This function launches the IOWindow
            for .mat input (IOWizard.py)
    """

    self.statusBar().setStyleSheet('')

    QtCore.QCoreApplication.instance().processEvents()

    self.ErrorS.setEnabled(1)
    self.Wizard = IOWizardMainMat(self)

    # blocks input to main GUI while IO is active
    self.Wizard.setWindowModality(QtCore.Qt.ApplicationModal)
    self.Wizard.exec_()
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
    F = os.path.join(x, 'assets', 'codeAssets', 'SNL_Horizontal_Black_Blue.jpg')
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

  def SaveFig(self):
    """
            Function to save figures generated by MAPIT.
            Will be depreciated in a future release.
    """

    outdir = os.path.join(os.getcwd(), 'MAPIT_out.png')
    self.canvas.fig.savefig(outdir, facecolor=self.canvas.axes.get_facecolor())

  def SaveFigLargeFont(self):
    """
            Function to save (larger font) figures
            generated by MAPIT. Will be depreciated
            in a future release.
    """

    defFont = plt.rcParams['font.size']
    plt.rcParams.update({'font.size': 15})

    # have to redraw everything
    T1 = self.canvas.axes.get_title()
    T2 = self.canvas.axes.get_ylabel()
    T3 = self.canvas.axes.get_xlabel()

    PlotData = []
    for i in range(0, len(self.canvas.axes.get_lines())):
      PlotData.append(self.canvas.axes.get_lines()[i].get_xydata())

    self.canvas.axes.cla()

    for i in range(0, len(PlotData)):
      self.canvas.axes.plot(PlotData[i][:, 1], linewidth=2)

    self.canvas.axes.set_title(T1, fontsize=15)
    self.canvas.axes.set_ylabel(T2, fontsize=15)
    self.canvas.axes.set_xlabel(T3, fontsize=15)
    self.canvas.axes.title.set_color(self.canvas.axes.yaxis.label.get_color())

    self.canvas.draw()
    outdir = os.path.join(os.getcwd(), 'MAPIT_out.png')
    self.canvas.fig.savefig(outdir, facecolor=self.canvas.axes.get_facecolor())

    # fix font back
    plt.rcParams.update({'font.size': defFont})
    PlotData = []
    for i in range(0, len(self.canvas.axes.get_lines())):
      PlotData.append(self.canvas.axes.get_lines()[i].get_xydata())

    self.canvas.axes.cla()

    for i in range(0, len(PlotData)):
      self.canvas.axes.plot(PlotData[i][:, 1], linewidth=2)

    self.canvas.axes.set_title(T1, fontsize=12)
    self.canvas.axes.set_ylabel(T2, fontsize=defFont)
    self.canvas.axes.set_xlabel(T3, fontsize=defFont)
    self.canvas.axes.title.set_color(self.canvas.axes.yaxis.label.get_color())

    self.canvas.draw()

  def RunTable(self):
    """
            Function calling the error selection
            function.
    """

    dlg = ViewErrorTabs(self)
    res = dlg.exec_()

  def SaveStats(self):
    """
            This function exports
            results generated by MAPIT
            to (potentially multiple)
            .csv files.
    """

    #create a directory for output if doesnt exist
    outdir = os.path.join(Path(os.getcwd()).parents[0], 'MAPIT_Output')
    if not os.path.isdir(outdir):
      os.makedirs(outdir)

    self.PB.setMaximum(0)
    self.PB.setMinimum(0)
    self.StatDlg.UpdateDispText('Saving Data')
    QtCore.QCoreApplication.instance().processEvents()

    #determine what needs to be exported
    ck0 = []
    if self.CB_PuMUF.isChecked() == 1:
      ck0.append(self.PuLoc)
    else:
      None

    if self.CB_UMUF.isChecked() == 1:
      ck0.append(self.ULoc)
    else:
      None

    if self.CB_GMUF.isChecked() == 1:
      ck0.append(self.GLoc)
    else:
      None

    ck1 = []
    if self.CB_PuSMUF.isChecked() == 1:
      ck1.append(self.PuLoc)
    else:
      None

    if self.CB_USMUF.isChecked() == 1:
      ck1.append(self.ULoc)
    else:
      None

    if self.CB_GSMUF.isChecked() == 1:
      ck1.append(self.GLoc)
    else:
      None

    ck2 = []
    if self.CB_PuSITMUF.isChecked() == 1:
      ck2.append(self.PuLoc)
    else:
      None

    if self.CB_USITMUF.isChecked() == 1:
      ck2.append(self.ULoc)
    else:
      None

    if self.CB_GSITMUF.isChecked() == 1:
      ck2.append(self.GLoc)
    else:
      None

    ck3 = []
    if self.CB_PuSPage.isChecked() == 1:
      ck3.append(self.PuLoc)
    else:
      None

    if self.CB_USPage.isChecked() == 1:
      ck3.append(self.ULoc)
    else:
      None

    if self.CB_GSPage.isChecked() == 1:
      ck3.append(self.GLoc)
    else:
      None

    QtCore.QCoreApplication.instance().processEvents(
    )  #makes sure the GUI doesnt look frozen

    #MUF calcs
    if len(ck0) > 0:
      for i in range(0, len(ck0)):
        PR = 0
        if ck0[i] == self.ULoc:
          PR = 'U'
        elif ck0[i] == self.PuLoc:
          PR = 'Pu'
        else:
          PR = 'Generic'
        np.savetxt(
            os.path.join(outdir, PR + ' MUF.csv'),
            self.MUFCalcs[:, ck0[i], :].T,
            delimiter=',')
    else:
      None

    #sigma MUF
    QtCore.QCoreApplication.instance().processEvents()
    if len(ck1) > 0:
      for i in range(0, len(ck1)):
        PR = 0
        if ck1[i] == self.ULoc:
          PR = 'U'
        elif ck1[i] == self.PuLoc:
          PR = 'Pu'
        else:
          PR = 'Generic'
        np.savetxt(
            os.path.join(outdir, PR + ' SigmaMUF.csv'),
            self.MUFCalcs[:, ck0[i], :].T,
            delimiter=',')
    else:
      None

    #SITMUF calcs
    QtCore.QCoreApplication.instance().processEvents()
    if len(ck2) > 0:
      for i in range(0, len(ck2)):
        PR = 0
        if ck2[i] == self.ULoc:
          PR = 'U'
        elif ck2[i] == self.PuLoc:
          PR = 'Pu'
        else:
          PR = 'Generic'
        np.savetxt(
            os.path.join(outdir, PR + ' SITMUF.csv'),
            self.MUFCalcs[:, ck0[i], :].T,
            delimiter=',')
    else:
      None

    #Page's trend test on SITMUF
    QtCore.QCoreApplication.instance().processEvents()
    if len(ck3) > 0:
      for i in range(0, len(ck3)):
        PR = 0
        if ck3[i] == self.ULoc:
          PR = 'U'
        elif ck3[i] == self.PuLoc:
          PR = 'Pu'
        else:
          PR = 'Generic'
        np.savetxt(
            os.path.join(outdir, PR + ' PageTest.csv'),
            self.MUFCalcs[:, ck0[i], :].T,
            delimiter=',')
    else:
      None

    # print observed data
    #future TODO
    #will require some extra thought for
    #how to handle non-uniformly sampled data
    #save to .xlsx? separate .csv for time?
    CheckPrint = QtWidgets.QMessageBox(self)
    CheckPrint.setText('Save observed data?')
    CheckPrint.setInformativeText(
        'Observed data is the user supplied ground truth with applied specified errors'
    )
    CheckPrint.setStandardButtons(QtWidgets.QMessageBox.Yes
                                  | QtWidgets.QMessageBox.No)
    CPE = CheckPrint.exec_()

    ck0 = self.CB_PuMUF.isChecked() + self.CB_PuSMUF.isChecked(
    ) + self.CB_PuSITMUF.isChecked() + self.CB_PuSPage.isChecked()

    ck1 = self.CB_UMUF.isChecked() + self.CB_USMUF.isChecked(
    ) + self.CB_USITMUF.isChecked() + self.CB_USPage.isChecked()

    ck2 = self.CB_GMUF.isChecked() + self.CB_GSMUF.isChecked(
    ) + self.CB_GSITMUF.isChecked() + self.CB_GSPage.isChecked()


    # [iter, location, timestep, element]
    #if labels exist use them to help
    #write the name of the output files
    if QtWidgets.QMessageBox.Yes == CPE:

      OutDat = np.concatenate((self.inpEFrame, self.invEFrame, self.outEFrame),
                              axis=1)
      if ck0 > 0:
        for i in range(0, np.shape(OutDat)[1]):
          QtCore.QCoreApplication.instance().processEvents()
          np.savetxt(
              os.path.join(outdir,
                           self.PlotLocLabels[i].strip(' ') + '_PuOut.csv'),
              OutDat[:, i, :, self.PuLoc].T,
              delimiter=',')

      else:
        None

      if ck1 > 0:
        for i in range(0, np.shape(OutDat)[1]):
          QtCore.QCoreApplication.instance().processEvents()
          np.savetxt(
              os.path.join(outdir,
                           self.PlotLocLabels[i].strip(' ') + '_UOut.csv'),
              OutDat[:, i, :, self.ULoc].T,
              delimiter=',')
      else:
        None

      if ck2 > 0:
        for i in range(0, np.shape(OutDat)[1]):
          QtCore.QCoreApplication.instance().processEvents()
          np.savetxt(
              os.path.join(outdir, self.PlotLocLabels[i].strip(' ') +
                           '_GenericOut.csv'),
              OutDat[:, i, :, self.GLoc].T,
              delimiter=',')
      else:
        None

    self.PB.setMaximum(100)
    self.PB.setValue(100)
    self.StatDlg.UpdateDispText('Execution Finished')
    QtCore.QCoreApplication.instance().processEvents()

  def ChangeColor(self):
    """
            This function makes stylistic changes
            to the GUI when a change between light
            and dark themes is made.
    """

    if self.MakeLight.isChecked() == 1:  #change to light theme
      QtCore.QCoreApplication.instance().setPalette(self.Lightpallette)
      self.canvas.fig.set_facecolor(
          np.asarray(
              QtGui.QColor.getRgb(
                  self.Lightpallette.color(QtGui.QPalette.Window))[0:3]) / 255)
      self.canvas.axes.set_facecolor(self.canvas.axes_defColor)

      self.canvas.axes.spines['bottom'].set_color('black')
      self.canvas.axes.spines['top'].set_color('black')
      self.canvas.axes.spines['right'].set_color('black')
      self.canvas.axes.spines['left'].set_color('black')

      self.canvas.axes.tick_params(axis='x', colors='black', which='both')
      self.canvas.axes.tick_params(axis='y', colors='black', which='both')

      self.canvas.axes.yaxis.label.set_color('black')
      self.canvas.axes.xaxis.label.set_color('black')
      self.canvas.axes.title.set_color('black')

      for j in range(len(self.children())):
        try:
          self.children()[j].setPalette(self.Darkpalette)
        except:
          None

      #stuff for the linear gradient
      color2L = QtGui.QColor(247, 247, 247)
      color1L = QtGui.QColor(153, 200, 221)
      color2D = QtGui.QColor(66, 66, 66)
      color1D = QtGui.QColor(51, 145, 186)

      #init stuff for animated panes
      #have to change some of the animated panels background
      ChangeDic={'rgb(52,52,52)': 'rgb(239,239,239)','rgb(66,66,66)': 'rgb(211,211,211)','white': 'black','rgb(0,83,118)': 'rgb(153,200,221)', \
                 color1D.name() : color1L.name(), color2D.name(): color2L.name()}
      #self.CB_GMUF.setStyleSheet()

      for i, j in ChangeDic.items():
        self.mb1.setStyleSheet(self.mb1.styleSheet().replace(i, j))
        self.mb2.setStyleSheet(self.mb2.styleSheet().replace(i, j))
        self.mb3.setStyleSheet(self.mb3.styleSheet().replace(i, j))
        self.mb4.setStyleSheet(self.mb4.styleSheet().replace(i, j))

        self.AnalysisContainer.setStyleSheet(
            self.AnalysisContainer.styleSheet().replace(i, j))

        self.SGSetContainer.setStyleSheet(
            self.SGSetContainer.styleSheet().replace(i, j))

        self.PlotControls.setStyleSheet(self.PlotControls.styleSheet().replace(
            i, j))

        self.threshContainer.setStyleSheet(
            self.threshContainer.styleSheet().replace(i, j))

        self.StatDlg.setStyleSheet(self.StatDlg.styleSheet().replace(i, j))

        self.ErrorS.setStyleSheet(self.ErrorS.styleSheet().replace(i, j))
        self.RunStats.setStyleSheet(self.RunStats.styleSheet().replace(i, j))

        self.PlotRunner.setStyleSheet(self.PlotRunner.styleSheet().replace(
            i, j))

        self.CalcThresh.setStyleSheet(self.CalcThresh.styleSheet().replace(
            i, j))


      self.canvas.draw()
      for i in range(len(self.CBHolder)):
        self.CBHolder[i].setStyleSheet(self.AnalysisContainer.styleSheet())
      self.PB.setStyleSheet(self.AnalysisContainer.styleSheet())
      self.menuBar().setStyleSheet("""QMenuBar {
             background-color: rgb(239,239,239);
             color: black;
            }""")

      self.setStyleSheet("""QToolTip {
                               background-color: rgb(239,239,239);
                               border-width: 3px;
                               border-color: rgb(153,200,221);
                               border-style: solid;
                               border-radius: 3px;
                               color: black;
                               }""")

    else:  #change to dark theme
      QtCore.QCoreApplication.instance().setPalette(self.Darkpalette)
      self.canvas.fig.set_facecolor((53 / 256, 53 / 256, 53 / 256))
      self.canvas.axes.set_facecolor((106 / 256, 106 / 256, 106 / 256))

      self.canvas.axes.spines['bottom'].set_color('white')
      self.canvas.axes.spines['top'].set_color('white')
      self.canvas.axes.spines['right'].set_color('white')
      self.canvas.axes.spines['left'].set_color('white')

      self.canvas.axes.tick_params(axis='x', colors='white', which='both')
      self.canvas.axes.tick_params(axis='y', colors='white', which='both')

      self.canvas.axes.yaxis.label.set_color('white')
      self.canvas.axes.xaxis.label.set_color('white')
      self.canvas.axes.title.set_color('white')

      for j in range(len(self.children())):
        try:
          self.children()[j].setPalette(self.Darkpalette)
        except:
          None

      #stuff for the linear gradient
      color2L = QtGui.QColor(247, 247, 247)
      color1L = QtGui.QColor(153, 200, 221)
      color2D = QtGui.QColor(66, 66, 66)
      color1D = QtGui.QColor(51, 145, 186)

      #have to change some of the animated panels background
      ChangeDic={'rgb(239,239,239)': 'rgb(52,52,52)','rgb(211,211,211)': 'rgb(66,66,66)','black': 'white', 'rgb(153,200,221)': 'rgb(0,83,118)' , \
                 color1L.name() : color1D.name(), color2L.name(): color2D.name()}

      for i, j in ChangeDic.items():
        self.mb1.setStyleSheet(self.mb1.styleSheet().replace(i, j))
        self.mb2.setStyleSheet(self.mb2.styleSheet().replace(i, j))
        self.mb3.setStyleSheet(self.mb3.styleSheet().replace(i, j))
        self.mb4.setStyleSheet(self.mb4.styleSheet().replace(i, j))

        self.AnalysisContainer.setStyleSheet(
            self.AnalysisContainer.styleSheet().replace(i, j))

        self.SGSetContainer.setStyleSheet(
            self.SGSetContainer.styleSheet().replace(i, j))

        self.PlotControls.setStyleSheet(self.PlotControls.styleSheet().replace(
            i, j))

        self.threshContainer.setStyleSheet(
            self.threshContainer.styleSheet().replace(i, j))

        self.StatDlg.setStyleSheet(self.StatDlg.styleSheet().replace(i, j))

        self.ErrorS.setStyleSheet(self.ErrorS.styleSheet().replace(i, j))
        self.RunStats.setStyleSheet(self.RunStats.styleSheet().replace(i, j))

        self.PlotRunner.setStyleSheet(self.PlotRunner.styleSheet().replace(
            i, j))

        self.CalcThresh.setStyleSheet(self.CalcThresh.styleSheet().replace(
            i, j))

      self.canvas.draw()
      for i in range(len(self.CBHolder)):
        self.CBHolder[i].setStyleSheet(self.AnalysisContainer.styleSheet())

      self.PB.setStyleSheet(self.AnalysisContainer.styleSheet())
      self.menuBar().setStyleSheet("""QMenuBar {
             background-color: rgb(52,53,53);
             color: white;
            }""")

      self.setStyleSheet("""QToolTip {
                               background-color: rgb(52,52,52);
                               border-width: 3px;
                               border-color: rgb(0,83,118);
                               border-style: solid;
                               border-radius: 3px;
                               color: white;
                               }""")

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

    geometry = qApp.desktop().availableGeometry(self)
    self.resize(
        1400, 900
    )  #the app is set as fixed with due to some scaling issues, this might cause problems
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

    FigureS = QtWidgets.QMenu("Figure Options", self)
    menubar.addMenu(FigureS)

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
    MakeDark = TG.addAction(QtWidgets.QAction("Dark", self, checkable=True))
    themeOpt.addAction(MakeDark)
    self.MakeLight.setChecked(1)
    TG.triggered.connect(self.ChangeColor)

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
    self.ExportDat.triggered.connect(self.SaveStats)
    self.ExportDat.setEnabled(0)

    self.ExportFig = QtWidgets.QAction("Save Figure", self)
    FigureS.addAction(self.ExportFig)
    self.ExportFig.triggered.connect(self.SaveFig)
    self.ExportFig.setEnabled(0)

    self.ExportFigL = QtWidgets.QAction("Save Figure (Large Font)", self)
    FigureS.addAction(self.ExportFigL)
    self.ExportFigL.triggered.connect(self.SaveFigLargeFont)
    self.ExportFigL.setEnabled(0)

    add_stats_box(self)
    add_plot_box(self)

    self.StatDlg = MssgRunner(self)
    self.StatDlg.setMaximumWidth(450)
    self.StatDlg._animation.start()
    self.StatDlg.UpdateDispText('Waiting for data import')
    self.StatDlg.setEnabled(0)
    self.statusBar().addWidget(self.StatDlg)
    #self.CBHolder.append(menu)

  def RunStatThresh(self):
    #call the function to update the threshold statistics
    self.canvas.update_thresh(float(self.StatThresh.text()), self.ThreshData)


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
  statContainerL.addWidget(self.SGSetContainer, 1, 0)
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
  MBPLabel.setToolTip('Duration between balances')

  # generic element index
  GELabel = QtWidgets.QLabel("Generic Element Index", LIContainer)
  self.GEBox = QtWidgets.QLineEdit("", LIContainer)
  self.GEBox.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  self.GEBox.setMaxLength(4)
  #self.GEBox.setFixedWidth(45)
  LIL.addWidget(GELabel, 2, 0)
  LIL.addWidget(self.GEBox, 2, 1)
  self.CBHolder.append(GELabel)
  self.CBHolder.append(self.GEBox)
  GELabel.setToolTip('*Optional* - Index (row) \n of element to be analyzed')

  #offset index (optional)
  OLabel = QtWidgets.QLabel("Temporal Offset", LIContainer)
  self.OBox = QtWidgets.QLineEdit("", LIContainer)
  self.OBox.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  self.OBox.setMaxLength(4)
  #self.OBox.setFixedWidth(45)
  LIL.addWidget(OLabel, 3, 0)
  LIL.addWidget(self.OBox, 3, 1)
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
  statContainerL.addWidget(self.AnalysisContainer, 0, 0)
  self.AnalysisContainerL = QtWidgets.QVBoxLayout(self.AnalysisContainer)

  PUContain = QtWidgets.QGroupBox(self.AnalysisContainer)
  PUContain.setTitle("Plutonium")
  pulay = QtWidgets.QVBoxLayout(PUContain)

  UContain = QtWidgets.QGroupBox(self.AnalysisContainer)
  UContain.setTitle("Uranium")
  ulay = QtWidgets.QVBoxLayout(UContain)

  GEContain = QtWidgets.QGroupBox(self.AnalysisContainer)
  GEContain.setTitle("Generic Element")
  glay = QtWidgets.QVBoxLayout(GEContain)

  self.CB_PuMUF = QtWidgets.QCheckBox("Pu MUF", self.AnalysisContainer)
  self.CB_PuSMUF = QtWidgets.QCheckBox("Pu Sigma MUF", self.AnalysisContainer)
  self.CB_PuSITMUF = QtWidgets.QCheckBox("Pu SITMUF", self.AnalysisContainer)
  self.CB_PuSPage = QtWidgets.QCheckBox("Page's Test Pu SITMUF",
                                        self.AnalysisContainer)

  self.CB_UMUF = QtWidgets.QCheckBox("U MUF", self.AnalysisContainer)
  self.CB_USMUF = QtWidgets.QCheckBox("U Sigma MUF", self.AnalysisContainer)
  self.CB_USITMUF = QtWidgets.QCheckBox("U SITMUF", self.AnalysisContainer)
  self.CB_USPage = QtWidgets.QCheckBox("Page's test U SITMUF",
                                       self.AnalysisContainer)

  self.CB_GMUF = QtWidgets.QCheckBox("Generic MUF", self.AnalysisContainer)
  self.CB_GSMUF = QtWidgets.QCheckBox("Generic Sigma MUF",
                                      self.AnalysisContainer)
  self.CB_GSITMUF = QtWidgets.QCheckBox("Generic SITMUF",
                                        self.AnalysisContainer)
  self.CB_GSPage = QtWidgets.QCheckBox("Page's test Generic SITMUF",
                                       self.AnalysisContainer)

  self.CBHolder.append(self.CB_PuMUF)
  self.CBHolder.append(self.CB_PuSMUF)
  self.CBHolder.append(self.CB_PuSITMUF)
  self.CBHolder.append(self.CB_PuSPage)

  self.CBHolder.append(self.CB_UMUF)
  self.CBHolder.append(self.CB_USMUF)
  self.CBHolder.append(self.CB_USITMUF)
  self.CBHolder.append(self.CB_USPage)

  self.CBHolder.append(self.CB_GMUF)
  self.CBHolder.append(self.CB_GSMUF)
  self.CBHolder.append(self.CB_GSITMUF)
  self.CBHolder.append(self.CB_GSPage)

  self.AnalysisContainerL.addWidget(PUContain)
  self.AnalysisContainerL.addWidget(UContain)
  self.AnalysisContainerL.addWidget(GEContain)

  pulay.addWidget(self.CB_PuMUF)
  pulay.addWidget(self.CB_PuSMUF)
  pulay.addWidget(self.CB_PuSITMUF)
  pulay.addWidget(self.CB_PuSPage)
  ulay.addWidget(self.CB_UMUF)
  ulay.addWidget(self.CB_USMUF)
  ulay.addWidget(self.CB_USITMUF)
  ulay.addWidget(self.CB_USPage)
  glay.addWidget(self.CB_GMUF)
  glay.addWidget(self.CB_GSMUF)
  glay.addWidget(self.CB_GSITMUF)
  glay.addWidget(self.CB_GSPage)

  #prevents text clipping
  #self.CB_UMUF.setMinimumHeight(25)
  #self.CB_USMUF.setMinimumHeight(25)
  #self.CB_USITMUF.setMinimumHeight(25)
  #self.CB_USPage.setMinimumHeight(25)

  #self.CB_PuMUF.setMinimumHeight(25)
  #self.CB_PuSMUF.setMinimumHeight(25)
  #self.CB_PuSITMUF.setMinimumHeight(25)
  #self.CB_PuSPage.setMinimumHeight(25)

  #self.CB_GMUF.setMinimumHeight(25)
  #self.CB_GSMUF.setMinimumHeight(25)
  #self.CB_GSITMUF.setMinimumHeight(25)
  #self.CB_GSPage.setMinimumHeight(25)

  # Add plot location locs
  self.PlotControls = AniGBox(self)
  self.PlotControls.setTitle("Plot Controls")
  self.PlotControls.setObjectName('PB5')
  self.PlotControls.PassLoc('PB5')

  statContainerL.addWidget(self.PlotControls, 0, 1)
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
  self.metricBox.setMinimumWidth(200)
  self.metricBox.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)


  self.mb1L.addWidget(self.metricBox)
  self.mb1L.addStretch()

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
  self.mb2L.addStretch()
  PlotControlL.addWidget(self.mb2, 2, 1)
  self.LocBox.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  self.LocBox.setMinimumWidth(200)

  self.mb3 = SubBoxAni(self)
  self.mb3L = QtWidgets.QHBoxLayout(self.mb3)
  self.mb3.setObjectName('PB3')
  self.mb3.PassLoc('PB3')
  self.mb3.setTitle('Plot Data Nuclide')
  self.mb3.setStyleSheet(
      gradA.format(VAL='PB3') + gradB + gradC.format(VAL='PB3') + gradD)
  self.NucIDBox = QtWidgets.QComboBox(self.PlotControls)

  self.mb3L.addWidget(self.NucIDBox)
  self.mb3L.addStretch()
  PlotControlL.addWidget(self.mb3, 3, 1)
  self.NucIDBox.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  self.NucIDBox.setMinimumWidth(200)

  self.mb4 = SubBoxAni(self)
  self.mb4L = QtWidgets.QHBoxLayout(self.mb4)
  self.mb4.setObjectName('PB4')
  self.mb4.PassLoc('PB4')
  self.mb4.setTitle('Iterations to Plot')
  self.mb4.setStyleSheet(
      gradA.format(VAL='PB4') + gradB + gradC.format(VAL='PB4') + gradD)
  self.NumToPlot = QtWidgets.QComboBox(self.PlotControls)
  self.NumToPlot.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  self.NumToPlot.setMinimumWidth(200)


  self.mb4L.addWidget(self.NumToPlot)
  self.mb4L.addStretch()

  PlotControlL.addWidget(self.mb4, 4, 1)

  self.PlotRunner = AniButton(self)
  self.PlotRunner.setText('Plot')
  self.PlotRunner.setObjectName('PRB')
  PlotControlL.addWidget(self.PlotRunner, 5, 1)
  PlotControlL.setVerticalSpacing(PlotControlL.verticalSpacing() * 5)
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
  statContainerL.addWidget(self.threshContainer, 1, 1)
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
  self.StatThresh.setMinimumWidth(50)

  # threshold display
  self.STL2 = QtWidgets.QLabel("% Above Threshold", self.threshContainer)
  threshContainerL.addWidget(self.STL2, 3, 0)
  self.StatThreshDisp = QtWidgets.QLineEdit("0.00", self.threshContainer)
  self.StatThreshDisp.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)
  threshContainerL.addWidget(self.StatThreshDisp, 3, 1)
  self.StatThreshDisp.setMaxLength(6)


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

  self.canvas = MPLCanvas(plotContainer)
  self.navi_toolbar = NavigationToolbar(self.canvas, self)
  plotContainerL.addWidget(self.canvas, 0, 0)
  plotContainerL.addWidget(self.navi_toolbar)
  self.canvas.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,QtWidgets.QSizePolicy.MinimumExpanding)


if __name__ == "__main__":
  app = QtWidgets.QApplication([])

  #splash
  x = Path(sys.argv[0]).resolve().parents[1]
  F = os.path.join(x, 'assets', 'codeAssets', 'splashV2.png')
  splash_pix = QtGui.QPixmap(F)
  splash = QtWidgets.QSplashScreen(splash_pix)
  splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint
                        | QtCore.Qt.FramelessWindowHint)
  splash.setEnabled(False)

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
