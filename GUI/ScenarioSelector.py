"""
    Code responsible for the interactive scenario selection.
    Currently only includes simulated data representative of a
    generic fuel fabrication facility.
"""

import sys
from PySide2 import QtCore, QtWidgets, QtGui
import numpy as np
import os
import string
import copy
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage,
                                  AnnotationBbox, HPacker)

from matplotlib.patches import Rectangle
import matplotlib
import scipy.io
import matplotlib.animation as animation
from pathlib import Path
import re

class MPLCanvas(FigureCanvas):
  """
        Class containing the underlying
        matplotlib canvas used to display
        the various animations used in the
        scenario selector.
  """

  def __init__(self, parent=None, dpi=400):

    self.fig = Figure(dpi=dpi, frameon=True)
    self.fig.subplots_adjust(left=0.10, bottom=0.10, right=0.98, top=1.15)
    if parent.palette().background().color().getRgb()[0] < 100:
      self.fig.set_facecolor((53 / 256, 53 / 256, 53 / 256))
      rectColor = ((106 / 256, 106 / 256, 106 / 256))
    else:
      rectColor = ((255 / 255, 255 / 255, 255 / 255))

    self.axes = self.fig.add_subplot(111)
    self.axes_defColor = self.axes.get_facecolor()

    DB = 0

    #dynamically check for the MAPIT theme using background()
    if parent.palette().background().color().getRgb()[0] < 100:
      self.axes.spines['bottom'].set_color('white')
      self.axes.spines['top'].set_color('white')
      self.axes.spines['right'].set_color('white')
      self.axes.spines['left'].set_color('white')
      colorupdate = {
          'axes.facecolor': (106 / 256, 106 / 256, 106 / 256),
          'axes.edgecolor': (256 / 256, 256 / 256, 256 / 256),
          'xtick.color': 'white',
          'ytick.color': 'white',
          'text.color': 'white',
          'ytick.major.pad': 1,
          'ytick.labelsize': 4,
          'ytick.labelsize': 4,
          'xtick.labelbottom': 0,
          'xtick.major.bottom': 0,
          'axes.titlepad': 2,
          'axes.linewidth': 0.5
      }

      matplotlib.rcParams.update(colorupdate)

      DB = 0

    else:

      # incase swapped themes between loads - load defaults
      matplotlib.rcParams.update(matplotlib.rcParamsDefault)

      colorupdate = {
          'ytick.major.pad': 1,
          'ytick.labelsize': 4,
          'ytick.labelsize': 4,
          'xtick.labelbottom': 0,
          'xtick.major.bottom': 0,
          'axes.titlepad': 2,
          'axes.linewidth': 0.5
      }

      matplotlib.rcParams.update(colorupdate)

      DB = 0

    #load the background image
    dirname, _ = os.path.split(os.path.abspath(__file__))
    x = Path(dirname).resolve().parents[0]
    F = os.path.join(x, 'docs_v2', 'codeAssets', 'FuelFabBase.png')
    self.axes.imshow(Image.open(F), interpolation='catrom')

    self.axes.set_ylim(self.axes.get_ylim()[0], self.axes.get_ylim()[1] - 500)
    self.axes.axis('off')

    self.HasDrawnAniChild = 0

    DB = 0
    #next blocks of code place annotation boxes
    #which will point from the model to the plots

    # vaporization
    xy = [100, 200]
    xx = Rectangle(xy=(0, 0), width=30, height=30, color=rectColor)
    da = DrawingArea(30, 30, 0, 0)
    da.add_artist(xx)
    self.ab_Vap = AnnotationBbox(
        offsetbox=da,
        xy=xy,
        xybox=(-77., 10.),
        xycoords='data',
        boxcoords="offset points",
        pad=0.001,
        frameon=True,
        arrowprops=dict(
            arrowstyle="->, head_width=0.025, head_length=0.05", lw=0.5))

    self.axes.add_artist(self.ab_Vap)

    #calcine + reduction
    xy = [890, 269]
    xx = Rectangle(xy=(0, 0), width=30, height=30, color=rectColor)
    da = DrawingArea(30, 30, 0, 0)
    da.add_artist(xx)
    self.ab_CR = AnnotationBbox(
        offsetbox=da,
        xy=xy,
        xybox=(80., 10.),
        xycoords='data',
        boxcoords="offset points",
        pad=0.001,
        frameon=True,
        arrowprops=dict(
            arrowstyle="->, head_width=0.025, head_length=0.05", lw=0.5))

    self.axes.add_artist(self.ab_CR)

    xy = [99, 510]
    xx = Rectangle(xy=(0, 0), width=30, height=30, color=rectColor)
    da = DrawingArea(30, 30, 0, 0)
    da.add_artist(xx)
    self.ab_MX1 = AnnotationBbox(
        offsetbox=da,
        xy=xy,
        xybox=(-30., 0.),
        xycoords='data',
        boxcoords="offset points",
        pad=0.001,
        frameon=True,
        arrowprops=dict(
            arrowstyle="->, head_width=0.025, head_length=0.05", lw=0.5))

    self.axes.add_artist(self.ab_MX1)

    # tube filling
    xy = [1265, 550]
    xx = Rectangle(xy=(0, 0), width=30, height=30, color=rectColor)
    da = DrawingArea(30, 30, 0, 0)
    da.add_artist(xx)
    self.ab_TF = AnnotationBbox(
        offsetbox=da,
        xy=xy,
        xybox=(50., -10.),
        xycoords='data',
        boxcoords="offset points",
        pad=0.001,
        frameon=True,
        arrowprops=dict(
            arrowstyle="->, head_width=0.025, head_length=0.05", lw=0.5))

    self.axes.add_artist(self.ab_TF)

    # pellet storage
    xy = [950, 542]
    xx = Rectangle(xy=(0, 0), width=30, height=30, color=rectColor)
    da = DrawingArea(30, 30, 0, 0)
    da.add_artist(xx)
    self.ab_PS = AnnotationBbox(
        offsetbox=da,
        xy=xy,
        xybox=(-154., -19.),
        xycoords='data',
        boxcoords="offset points",
        pad=0.001,
        frameon=True,
        arrowprops=dict(
            arrowstyle="->, head_width=0.025, head_length=0.05",
            lw=0.5,
            connectionstyle="angle,angleA=0,angleB=90,rad=10"))

    self.axes.add_artist(self.ab_PS)

    # sum of scrap storage
    xy = [207, 912]
    xx = Rectangle(xy=(0, 0), width=30, height=30, color=rectColor)
    da = DrawingArea(30, 30, 0, 0)
    da.add_artist(xx)
    self.ab_SS = AnnotationBbox(
        offsetbox=da,
        xy=xy,
        xybox=(-43., -12.),
        xycoords='data',
        boxcoords="offset points",
        pad=0.001,
        frameon=True,
        arrowprops=dict(
            arrowstyle="->, head_width=0.025, head_length=0.05", lw=0.5))

    self.axes.add_artist(self.ab_SS)

    self.compute_initial_figure()

    FigureCanvas.__init__(self, self.fig)
    self.setParent(parent)

    FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)

  def compute_initial_figure(self):
    pass

  def update_figure(self, data):
    """
            Function for updating
            scene plots
  """

    self.axes.cla()
    self.axes.plot(data)
    self.draw()

  def update_figure_title(self, data):
    self.axes.set_title(data[0])
    self.axes.title.set_color(self.axes.yaxis.label.get_color())
    self.axes.set_xlabel(data[1])
    self.axes.set_ylabel(data[2])
    self.draw()


class SceneExamine(QtWidgets.QDialog):
  """
        Underlying class for the scenario
        selection. It is actually one large
        dialog window with a bunch of added
        elements.

        On initialization the precalculated
        scenario data is loaded.
  """

  def __init__(self, mdlname, dataname, parent=None):
    super(SceneExamine, self).__init__()
    SS = QtWidgets.QHBoxLayout(self)

    setnames = {
            "Normal": "Normal",
            "Abrupt Loss": "Abrupt",
            "Protracted Loss":"Protract"
          }

    mdl_names = {
              "Fuel Fab":"fuel_fab"
          }

    #load the data
    dirname, _ = os.path.split(os.path.abspath(__file__))
    x = Path(dirname).resolve().parents[0]
    F = os.path.join(x, 'data', mdl_names[mdlname], setnames[dataname], 'data.mat')
    x1 = scipy.io.loadmat(F,squeeze_me=True)


    self.Inventories = x1['invn']['data']
    self.InventoriesT = x1['invn']['time']

    self.Inputs = x1['in']['data']
    self.InputsT = x1['in']['time']

    self.Outputs = x1['outn']['data']
    self.OutputsT = x1['outn']['time']

    self.sceneName = 'Normal'

    F = os.path.join(x, 'docs_v2','codeAssets', 'SNL_Stacked_Black_Blue2.jpg')
    self.setWindowIcon(QtGui.QIcon(F))


    #setup the animation control buttons
    self.XX = np.linspace(0, 249, 250)
    if self.palette().background().color().getRgb()[0] > 100:
      self.ThemePlotColor = '#00add0'
      pName = 'playDark.png'
      ppName = 'pauseDark.png'
    else:
      self.ThemePlotColor = '#66adcb'
      pName = 'play.png'
      ppName = 'pause.png'

    #setup main area
    MainWindow = QtWidgets.QGroupBox(self)
    MWL = QtWidgets.QGridLayout(MainWindow)
    SS.addWidget(MainWindow)

    SceneTabs = QtWidgets.QTabWidget()

    self.canvas = MPLCanvas(self)

    #TabA = QtWidgets.QFrame()
    #TabAL = QtWidgets.QGridLayout(TabA)
    MWL.addWidget(self.canvas, 1, 0, 1, 7)

    ICBContainer = QtWidgets.QGroupBox()
    ICBContainer.setTitle('Animation Controls')
    ICBL = QtWidgets.QGridLayout(ICBContainer)

    dirname, _ = os.path.split(os.path.abspath(__file__))
    x = Path(dirname).resolve().parents[0]
    F = os.path.join(x, 'docs_v2','codeAssets', pName)
    IC = QtGui.QPixmap(F)

    ICB = QtWidgets.QPushButton()
    ICB.setIcon(IC)
    ICBL.addWidget(ICB, 3, 0)
    ICB.clicked.connect(self.PlayButton)

    SCB = QtWidgets.QPushButton()
    F = os.path.join(x, 'docs_v2', 'codeAssets', ppName)
    SCBL = QtGui.QPixmap(F)

    SCB.setIcon(SCBL)
    ICBL.addWidget(SCB, 3, 1)
    SCB.clicked.connect(self.StopButton)

    MWL.addWidget(ICBContainer, 0, 4, 1, 6)

    StartHolder = QtWidgets.QGroupBox(self)
    StartHolderL = QtWidgets.QGridLayout(StartHolder)

    EndHolder = QtWidgets.QGroupBox(self)
    EndHolderL = QtWidgets.QGridLayout(EndHolder)

    #setup the slider for animation start/end time
    self.TAS = QtWidgets.QSlider(orientation=QtCore.Qt.Orientation(1))
    self.TAS.setMinimum(0)
    self.TAS.setMaximum(6480)
    self.TAS.sliderMoved.connect(self.SMU)

    self.TimeBox = QtWidgets.QLineEdit("")
    TBV = QtGui.QIntValidator()
    self.TimeBox.setValidator(TBV)
    TBV.setRange(0, 6480)
    self.TimeBox.setMaxLength(4)

    self.EAS = QtWidgets.QSlider(orientation=QtCore.Qt.Orientation(1))
    self.EAS.setMinimum(0)
    self.EAS.setMaximum(6480)
    self.EAS.setValue(250)
    self.EAS.actionTriggered.connect(self.TMU)

    self.EndBox = QtWidgets.QLineEdit("")
    self.EndBox.setMaxLength(4)
    self.EndBox.setText('250')

    StartHolderL.addWidget(self.TimeBox)
    StartHolderL.addWidget(self.TAS)

    EndHolderL.addWidget(self.EndBox)
    EndHolderL.addWidget(self.EAS)

    StartHolder.setTitle('Start Time')
    EndHolder.setTitle('End Time')

    ICBL.addWidget(StartHolder, 1, 0)

    ICBL.addWidget(EndHolder, 1, 1)

    #Some predetermined elements of interest
    #might change later if other datasets
    #are added

    self.AniEleSelect = QtWidgets.QComboBox()
    ICBL.addWidget(self.AniEleSelect, 0, 0, 1, 2)
    self.AniEleSelect.addItem('Uranium (kg)')

    #these aren't included at the moment
    #self.AniEleSelect.addItem('Plutonium (kg)')
    #self.AniEleSelect.addItem('Cesium (kg)')
    #self.AniEleSelect.addItem('Xenon (kg)')
    #self.AniEleSelect.addItem('Europium (kg)')

    self.TimeBox.setText(str(self.TAS.value()))
    self.TimeBox.textEdited.connect(self.TBU)
    self.EndBox.editingFinished.connect(self.EBU)

    DetailsBox = QtWidgets.QGroupBox()
    DBL = QtWidgets.QVBoxLayout(DetailsBox)
    self.DetailsText = QtWidgets.QTextEdit()
    self.DetailsText.insertPlainText(
        'Synthetic dataset based on generic fuel fab' +\
        ' facility (see IAEA-STR150). This facility produces' +\
        ' about 300 MT UO2 per year with a final assembly with' +\
        ' 3.0% weight percent U-235. ')

    self.DetailsText.setReadOnly(1)
    DBL.addWidget(self.DetailsText)
    DetailsBox.setTitle('Scenario Description')
    MWL.addWidget(DetailsBox, 0, 0, 1, 4)




    geometry = qApp.desktop().availableGeometry(self)
    self.resize(1920, 1040)

    self.SceneDict = {
        0:
            '''
            Normal operation for one year (270 operating days - 6480 hours). MBP time should be 416
            ''',
        1:
            '''
              Normal operation for one year (270 operating days - 6480 hours).
              An abrupt loss from the tube filling occurs. MBP time should be 416.
            ''',
        2:
            '''
              Normal operation for one year (270 operating days - 6480 hours).
              A protracted loss from the tube filling occurs. MBP time should be 416.
            '''
    }

    self.SceneDictShort = {0:'Normal',1:'Abrupt',2:'Protract'}



  def TMU(self):
    """
            Function to update
            the end time on the
            animation controls.

            Triggered if slider is used.
  """

    try:
      self.canvas.ani.event_source.stop()
    except:
      None

    if self.EAS.value() <= self.TAS.value():
      self.EAS.setRange(int(self.TimeBox.text()) + 1, 6480)
      self.EndBox.setText(str(self.EAS.value()))
    else:

      self.EndBox.setText(str(self.EAS.value()))

  def SMU(self):
    """
            Function to update
            the end time range on
            the animation controls.

            Triggered if slider is used.
  """

    # optional stop animation
    try:
      self.canvas.ani.event_source.stop()
    except:
      None

    self.TimeBox.setText(str(self.TAS.value()))

    if int(self.TimeBox.text()) > 6480 - 250:
      R = 6480 - int(self.TimeBox.text())
      self.EndBox.setText(str(self.TAS.value() + R))
      self.EAS.setValue(self.TAS.value() + R)
    else:
      self.EndBox.setText(str(self.TAS.value() + 250))
      self.EAS.setValue(self.TAS.value() + 250)

    self.EAS.setRange(int(self.TimeBox.text()) + 1, 6480)

  def TBU(self):
    """
            Function to update
            the end time on the
            animation controls.

            Triggered if text box is
            directly edited.
  """

    # optional stop animation
    try:
      self.canvas.ani.event_source.stop()
    except:
      None
    try:
      self.TAS.setValue(int(self.TimeBox.text()))
    except:
      None
      # occurs when box is empty
    if self.TimeBox.text() != '':
      if int(self.TimeBox.text()) > 6480:
        self.TimeBox.setText(str(6480))

    if self.TimeBox.text() != '':
      if int(self.TimeBox.text()) > 6480 - 250:
        R = 6480 - int(self.TimeBox.text())
        self.EndBox.setText(str(int(self.TimeBox.text()) + R))
        self.EAS.setValue(int(self.TimeBox.text()) + R)
      else:
        self.EndBox.setText(str(int(self.TimeBox.text()) + 250))
        self.EAS.setValue(int(self.TimeBox.text()) + 250)
      self.EAS.setRange(int(self.TimeBox.text()) + 1, 6480)

  def EBU(self):
    """
            Function to update
            the end time range
            on the animation controls.

            Triggered if text box is
            directly edited.
  """
    try:
      self.canvas.ani.event_source.stop()
    except:
      None

    try:
      self.EAS.setValue(int(self.EndBox.text()))

    except:
      None

    if self.EndBox.text() != '':
      if int(self.EndBox.text()) <= int(self.TimeBox.text()):
        if int(self.TimeBox.text()) > 6480 - 250:
          self.EndBox.setText(str(int(self.TimeBox.text()) + 250))
        else:
          R = 6480 - int(self.TimeBox.text())
          self.EndBox.setText(str(int(self.TimeBox.text()) + R))
      if int(self.EndBox.text()) > 6480:
        self.EndBox.setText(str(int(6480)))

  def initF(self):
    """
            This function is run when the animation
            is run the first time. Initalizes some
            plots and other parameters.
  """

    IDXS = [0,4,6,11,10]
    IDXS2 = np.linspace(12,17,5,dtype=int)
    ispresent = np.zeros((len(IDXS)+1,))
    AniLen = int(self.EndBox.text()) - int(self.TimeBox.text())

    x = [np.nan] * AniLen
    x = np.asarray(x)


    logicalslice = [] #find the relevant slices
    for i in range(len(IDXS)):
      logicalslice.append(np.logical_and(self.InventoriesT[IDXS[i]] >= int(self.TimeBox.text()),self.InventoriesT[IDXS[i]] <= int(self.EndBox.text())).reshape((-1)))

      if np.sum(logicalslice[-1]>0):
        ispresent[i] = 1

    for i in range(len(IDXS2)):
      if i == 0:
        MS = np.logical_and(self.InventoriesT[IDXS2[i]] >= int(self.TimeBox.text()),self.InventoriesT[IDXS2[i]] <= int(self.EndBox.text()))

      else:
        MS2 = np.logical_and(self.InventoriesT[IDXS2[i]] >= int(self.TimeBox.text()),self.InventoriesT[IDXS2[i]] <= int(self.EndBox.text()))

        MS = np.logical_and(MS,MS2)

    if np.sum(logicalslice[-1]>0):
      ispresent[-1] = 1

    logicalslice.append(MS.reshape((-1)))


    #AniLen = int(self.EndBox.text()) - int(self.TimeBox.text())

    #x = [np.nan] * AniLen
    #x = np.asarray(x)

    # so here we are going to predraw the figure to get
    # the ticks/limits
    #i = AniLen
    #CurrentWindow = int(self.TimeBox.text())

    ELEI = self.AniEleSelect.currentIndex()

    self.canvas.subax_V.cla()
    self.canvas.subax_CR.cla()
    self.canvas.subax_MX1.cla()
    self.canvas.subax_TF.cla()
    self.canvas.subax_PS.cla()
    self.canvas.subax_SS.cla()

    self.timeslice = []
    self.dataslice = []
    for i in range(len(ispresent)-1):
      if ispresent[i] == 1:
        self.dataslice.append(self.Inventories[IDXS[i]])
        self.timeslice.append(self.InventoriesT[IDXS[i]])
      else:
        self.dataslice.append(np.zeros((250,)))
        self.timeslice.append(np.zeros((250,)))

    if ispresent[-1] == 1:
      for i in range(len(IDXS2)):
        if i == 0:
          Z = self.Inventories[IDXS2[i]]
        else:
          Z += self.Inventories[IDXS2[i]]
          
      self.dataslice.append(Z)
      self.timeslice.append(self.InventoriesT[IDXS2[0]]) #index doesnt matter since all have same time


    self.canvas.subax_V.plot(self.timeslice[0],self.dataslice[0],color=self.ThemePlotColor)
    self.canvas.subax_CR.plot(self.timeslice[1],self.dataslice[1],color=self.ThemePlotColor)
    self.canvas.subax_MX1.plot(self.timeslice[2],self.dataslice[2],color=self.ThemePlotColor)
    self.canvas.subax_TF.plot(self.timeslice[3],self.dataslice[3],color=self.ThemePlotColor)
    self.canvas.subax_PS.plot(self.timeslice[4],self.dataslice[4],color=self.ThemePlotColor)
    self.canvas.subax_SS.plot(self.timeslice[5],self.dataslice[5],color=self.ThemePlotColor)


    VL = self.canvas.subax_V.get_ylim()
    CRL = self.canvas.subax_CR.get_ylim()
    MX1L = self.canvas.subax_MX1.get_ylim()
    TFL = self.canvas.subax_TF.get_ylim()
    PSL = self.canvas.subax_PS.get_ylim()
    SSL = self.canvas.subax_SS.get_ylim()

    self.canvas.subax_V.cla()
    self.canvas.subax_CR.cla()
    self.canvas.subax_MX1.cla()
    self.canvas.subax_TF.cla()
    self.canvas.subax_PS.cla()
    self.canvas.subax_SS.cla()

    fontdict = {'axes.titlesize': 4}
    matplotlib.rcParams.update(fontdict)

    self.canvas.subax_V.set_title('Vaporization')
    self.canvas.subax_CR.set_title('Calcination/Reduction')
    self.canvas.subax_MX1.set_title('Mixing Tank 1')
    self.canvas.subax_TF.set_title('Tube Filling')
    self.canvas.subax_PS.set_title('Pellet Storage')
    self.canvas.subax_SS.set_title('Sum of Scrap Storage')

    self.canvas.subax_TF.yaxis.set_label_position("right")
    self.canvas.subax_TF.yaxis.tick_right()

    self.canvas.subax_CR.yaxis.set_label_position("right")
    self.canvas.subax_CR.yaxis.tick_right()


    self.canvas.R1[0].set_ydata(x)
    self.canvas.R1[1].set_ydata(x)
    self.canvas.R1[2].set_ydata(x)
    self.canvas.R1[3].set_ydata(x)
    self.canvas.R1[4].set_ydata(x)
    self.canvas.R1[5].set_ydata(x)

    self.canvas.subax_V.set_xlim((0, AniLen))
    self.canvas.subax_V.set_ylim(VL)
    self.canvas.subax_V.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_CR.set_xlim((0, AniLen))
    self.canvas.subax_CR.set_ylim(CRL)
    self.canvas.subax_CR.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_MX1.set_xlim((0, AniLen))
    self.canvas.subax_MX1.set_ylim(MX1L)
    self.canvas.subax_MX1.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_TF.set_xlim((0, AniLen))
    self.canvas.subax_TF.set_ylim(TFL)
    self.canvas.subax_TF.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_PS.set_xlim((0, AniLen))
    self.canvas.subax_PS.set_ylim(PSL)
    self.canvas.subax_PS.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_SS.set_xlim((0, AniLen))
    self.canvas.subax_SS.set_ylim(SSL)
    self.canvas.subax_SS.yaxis.set_major_locator(plt.MaxNLocator(4))

    return self.canvas.R1

  def animate(self, AC):

    """
            Function that controls
            the actual animations of
            the various datasets shown
            in the scenario selector.
  """

    type = self.AniEleSelect.currentIndex()
    AniLen = int(self.EndBox.text()) - int(self.TimeBox.text())
    # locations are Vaporization, Calcination/Reduction, Mixing Tank 1, Tube Filling,
    # pellet sintering, sum of scrap storage
    # these are locs:
    # 0,4,6,11,8,12-17
    CurrentWindow = int(self.TimeBox.text())
    startt = int(self.TAS.value())
    entt = int(startt + AC)
    et = int(self.EAS.value())

    #empty entries to keep same segment length
    #regardless of where we are in the animation
    R = np.asarray([np.nan] * (AniLen - AC))

    for Q in range(len(self.canvas.R1)):
      self.canvas.R1[Q].set_ydata(np.concatenate((self.dataslice[Q][startt:entt], R)))



    return self.canvas.R1





  def StopButton(self):
    AniLen = int(self.EndBox.text()) - int(self.TimeBox.text())
    i = AniLen
    self.canvas.ani.event_source.stop()

    VL = self.canvas.subax_V.get_ylim()
    CRL = self.canvas.subax_CR.get_ylim()
    MX1L = self.canvas.subax_MX1.get_ylim()
    TFL = self.canvas.subax_TF.get_ylim()
    PSL = self.canvas.subax_PS.get_ylim()
    SSL = self.canvas.subax_SS.get_ylim()

    self.canvas.subax_V.cla()
    self.canvas.subax_CR.cla()
    self.canvas.subax_MX1.cla()
    self.canvas.subax_TF.cla()
    self.canvas.subax_PS.cla()
    self.canvas.subax_SS.cla()

    ts = self.TAS.value()
    te = self.EAS.value()





    #subtracting minimum relevant time to rebase axis to [0,250]

    self.canvas.subax_V.plot(self.timeslice[0][ts:te],self.dataslice[0][ts:te],color=self.ThemePlotColor,linewidth=0.5)

    self.canvas.subax_CR.plot(self.timeslice[1][ts:te],self.dataslice[1][ts:te],color=self.ThemePlotColor,linewidth=0.5)

    self.canvas.subax_MX1.plot(self.timeslice[2][ts:te],self.dataslice[2][ts:te],color=self.ThemePlotColor,linewidth=0.5)

    self.canvas.subax_TF.plot(self.timeslice[3][ts:te],self.dataslice[3][ts:te],color=self.ThemePlotColor,linewidth=0.5)

    self.canvas.subax_PS.plot(self.timeslice[4][ts:te],self.dataslice[4][ts:te],color=self.ThemePlotColor,linewidth=0.5)

    self.canvas.subax_SS.plot(self.timeslice[5][ts:te],self.dataslice[5][ts:te],color=self.ThemePlotColor,linewidth=0.5)

    
    
    
    
    
    

    self.canvas.subax_V.set_xlim((ts, te))
    self.canvas.subax_V.set_ylim(VL)
    self.canvas.subax_V.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_CR.set_xlim((ts, te))
    self.canvas.subax_CR.set_ylim(CRL)
    self.canvas.subax_CR.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_MX1.set_xlim((ts, te))
    self.canvas.subax_MX1.set_ylim(MX1L)
    self.canvas.subax_MX1.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_TF.set_xlim((ts, te))
    self.canvas.subax_TF.set_ylim(TFL)
    self.canvas.subax_TF.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_PS.set_xlim((ts, te))
    self.canvas.subax_PS.set_ylim(PSL)
    self.canvas.subax_PS.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_SS.set_xlim((ts, te))
    self.canvas.subax_SS.set_ylim(SSL)
    self.canvas.subax_SS.yaxis.set_major_locator(plt.MaxNLocator(4))

    self.canvas.subax_TF.yaxis.set_label_position("right")
    self.canvas.subax_TF.yaxis.tick_right()

    self.canvas.subax_CR.yaxis.set_label_position("right")
    self.canvas.subax_CR.yaxis.tick_right()

    self.canvas.subax_V.set_title('Vaporization')
    self.canvas.subax_CR.set_title('Calcination/Reduction')
    self.canvas.subax_MX1.set_title('Mixing Tank 1')
    self.canvas.subax_TF.set_title('Tube Filling')
    self.canvas.subax_PS.set_title('Pellet Storage')
    self.canvas.subax_SS.set_title('Sum of Scrap Storage')

    self.canvas.draw()

  def PlayButton(self):
    # have to adjust the plots after drawn
    if self.canvas.HasDrawnAniChild == 0:
      self.canvas.HasDrawnAniChild = 1

      self.canvas.ab_Vap.patch.set_visible(False)
      self.canvas.ab_CR.patch.set_visible(False)
      self.canvas.ab_MX1.patch.set_visible(False)
      self.canvas.ab_TF.patch.set_visible(False)
      self.canvas.ab_PS.patch.set_visible(False)
      self.canvas.ab_SS.patch.set_visible(False)

      # Vap
      TotSize = self.canvas.fig.get_size_inches() * 400  # 400 is the dpi

      X = self.canvas.ab_Vap.patch.get_extents().min[0]
      Y = self.canvas.ab_Vap.patch.get_extents().min[1]
      W = self.canvas.ab_Vap.patch.get_width() / TotSize[0]
      H = self.canvas.ab_Vap.patch.get_height() / TotSize[1]
      R = self.canvas.ab_Vap.offsetbox.get_transform()
      XY = R.transform((0, 0))
      self.canvas.subax_V = self.canvas.fig.add_axes(
          [XY[0] / TotSize[0], XY[1] / TotSize[1], W, H])
      self.canvas.subax_V.axis('off')

      #calcine + reduction
      X = self.canvas.ab_CR.patch.get_extents().min[0]
      Y = self.canvas.ab_CR.patch.get_extents().min[1]
      W = self.canvas.ab_CR.patch.get_width() / TotSize[0]
      H = self.canvas.ab_CR.patch.get_height() / TotSize[1]
      R = self.canvas.ab_CR.offsetbox.get_transform()
      XY = R.transform((0, 0))
      self.canvas.subax_CR = self.canvas.fig.add_axes(
          [XY[0] / TotSize[0], XY[1] / TotSize[1], W, H])
      self.canvas.subax_CR.axis('off')

      # MX1
      X = self.canvas.ab_MX1.patch.get_extents().min[0]
      Y = self.canvas.ab_MX1.patch.get_extents().min[1]
      W = self.canvas.ab_MX1.patch.get_width() / TotSize[0]
      H = self.canvas.ab_MX1.patch.get_height() / TotSize[1]
      R = self.canvas.ab_MX1.offsetbox.get_transform()
      XY = R.transform((0, 0))
      self.canvas.subax_MX1 = self.canvas.fig.add_axes(
          [XY[0] / TotSize[0], XY[1] / TotSize[1], W, H])
      self.canvas.subax_MX1.axis('off')

      # TubeFill
      X = self.canvas.ab_TF.patch.get_extents().min[0]
      Y = self.canvas.ab_TF.patch.get_extents().min[1]
      W = self.canvas.ab_TF.patch.get_width() / TotSize[0]
      H = self.canvas.ab_TF.patch.get_height() / TotSize[1]
      R = self.canvas.ab_TF.offsetbox.get_transform()
      XY = R.transform((0, 0))
      self.canvas.subax_TF = self.canvas.fig.add_axes(
          [XY[0] / TotSize[0], XY[1] / TotSize[1], W, H])
      self.canvas.subax_TF.axis('off')

      # Pellet Storage
      X = self.canvas.ab_PS.patch.get_extents().min[0]
      Y = self.canvas.ab_PS.patch.get_extents().min[1]
      W = self.canvas.ab_PS.patch.get_width() / TotSize[0]
      H = self.canvas.ab_PS.patch.get_height() / TotSize[1]
      R = self.canvas.ab_PS.offsetbox.get_transform()
      XY = R.transform((0, 0))
      self.canvas.subax_PS = self.canvas.fig.add_axes(
          [XY[0] / TotSize[0], XY[1] / TotSize[1], W, H])
      self.canvas.subax_PS.axis('off')

      # sum of scrap storage
      X = self.canvas.ab_SS.patch.get_extents().min[0]
      Y = self.canvas.ab_SS.patch.get_extents().min[1]
      W = self.canvas.ab_SS.patch.get_width() / TotSize[0]
      H = self.canvas.ab_SS.patch.get_height() / TotSize[1]
      R = self.canvas.ab_SS.offsetbox.get_transform()
      XY = R.transform((0, 0))
      self.canvas.subax_SS = self.canvas.fig.add_axes(
          [XY[0] / TotSize[0], XY[1] / TotSize[1], W, H])
      self.canvas.subax_SS.axis('off')

      self.canvas.draw()

    else:
      None

    # kill existing animation
    try:
      self.canvas.ani.event_source.stop()
    except:
      None

    AniLen = int(self.EndBox.text()) - int(self.TimeBox.text())

    # start animation
    self.canvas.R1 = [[]] * 6
    self.canvas.R1[0], = self.canvas.subax_V.plot(
        np.zeros((AniLen,)), linewidth=0.5, color=self.ThemePlotColor)
    self.canvas.R1[1], = self.canvas.subax_CR.plot(
        np.zeros((AniLen,)), linewidth=0.5, color=self.ThemePlotColor)
    self.canvas.R1[2], = self.canvas.subax_MX1.plot(
        np.zeros((AniLen,)), linewidth=0.5, color=self.ThemePlotColor)
    self.canvas.R1[3], = self.canvas.subax_TF.plot(
        np.zeros((AniLen,)), linewidth=0.5, color=self.ThemePlotColor)
    self.canvas.R1[4], = self.canvas.subax_PS.plot(
        np.zeros((AniLen,)), linewidth=0.5, color=self.ThemePlotColor)
    self.canvas.R1[5], = self.canvas.subax_SS.plot(
        np.zeros((AniLen,)), linewidth=0.5, color=self.ThemePlotColor)

    self.canvas.ani = animation.FuncAnimation(
        self.canvas.fig,
        self.animate,
        init_func=self.initF,
        frames=np.arange(1, AniLen),
        interval=50,
        blit=True,
        repeat=True)
    self.canvas.draw()
    # plt.show()

  def closeEvent(self, event):
    # on close kill all animations
    try:
      self.canvas.ani.event_source.stop()
    except:
      None
    event.accept()
