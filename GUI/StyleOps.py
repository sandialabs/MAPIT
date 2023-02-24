from collections import namedtuple
from PySide2 import QtCore, QtWidgets, QtGui
import numpy as np

def setInitialStyle(self):

    

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
                              QtGui.QColor(53, 53, 53))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.WindowText,
                              QtGui.QColor(53+40, 53+40, 53+40))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base,
                              QtGui.QColor(25, 25, 25))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.AlternateBase,
                              QtGui.QColor(53, 53, 53))

    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    self.Darkpalette.setColor(QtGui.QPalette.Disabled,
                              QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    self.Darkpalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text,
                              QtCore.Qt.white)
    self.Darkpalette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button,
                              QtGui.QColor(53, 53, 53))

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
                               border-radius: 7px;
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
                               border-radius: 7px;
                               color: white;
                               }""")