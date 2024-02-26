from collections import namedtuple
from PySide2 import QtCore, QtWidgets, QtGui
import numpy as np
import json
from pathlib import Path
import os
import sys
from MAPIT.GUI import PlotOps

#NOTE: qcheckbox color doesn't change as it's an image unfortunately
# would require custom image

def get_palette(color,return_dict=False):

    if color == 'light':
        with open(os.path.join(str(Path(__file__).resolve().parents[1]),'GUI','stylesheets','light_colors'+'.json'),'r') as fp:
            colordict = json.load(fp)
    else:
        with open(os.path.join(str(Path(__file__).resolve().parents[1]),'GUI','stylesheets','dark_colors'+'.json'),'r') as fp:
            colordict = json.load(fp)

    palette = QtCore.QCoreApplication.instance().palette() #get light pallet from here
    
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(colordict['WindowBackground']))

    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(colordict['WindowText']))

    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(colordict['Base']))

    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(colordict['AlternateBaseBackground']))

    palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(colordict['TooltipBase']))

    palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(colordict['TooltipText']))

    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(colordict['Text']))

    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(colordict['ButtonBackground']))

    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(colordict['ButtonText']))

    palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(colordict['BrightText']))

    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(colordict['Link']))

    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(colordict['Highlight']))

    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(colordict['HighlightedText']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Window,QtGui.QColor(colordict['DisabledWindow']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText,QtGui.QColor(colordict['DisabledWindowText']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Base,QtGui.QColor(colordict['DisabledBase']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase,QtGui.QColor(colordict['DisabledAlternateBase']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase,QtGui.QColor(colordict['DisabledTooltip']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText,QtGui.QColor(colordict['DisabledTooltipText']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button,QtGui.QColor(colordict['DisabledButton']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText,QtGui.QColor(colordict['DisabledButtonText']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText,QtGui.QColor(colordict['DisabledBrightText']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Link,QtGui.QColor(colordict['DisabledLink']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight,QtGui.QColor(colordict['DisabledHighlight']))

    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText,QtGui.QColor(colordict['DisabledHighlightText']))

    if return_dict:
        return palette, colordict
    else:
        return palette

def getSysDefaultTheme():
    sysPalette = QtGui.QPalette()
    if sum(sysPalette.base().color().getRgb()[0:3]) != 765:
        theme = 'dark'
    else:
        theme= 'light'
    return theme

def getDlgColorDict(self,parent,setInitStyle):
    theme = ''
    if setInitStyle:
        settings = QtCore.QSettings("current", "mapit")
        theme = settings.value("theme")
        if theme is None:
            theme = "light"

    else:
        if parent.MakeDark.isChecked():
            theme="dark"
        else:
            theme="light"

    P, colordict = get_palette(theme,return_dict=True) 
    self.colordict = colordict

    if setInitStyle:
        QtCore.QCoreApplication.instance().setPalette(P)

def setInitialStyle(self):

    
    with open(os.path.join(str(Path(__file__).resolve().parents[1]),'GUI','stylesheets','dark_colors'+'.json'),'r') as fp:
      dark_color_dict = json.load(fp)



    # bigger font here
    F = QtCore.QCoreApplication.instance().font().pointSize()
    self.currentFontSize = F
    QtCore.QCoreApplication.instance().setFont(QtGui.QFont("Open Sans", F))
    QtCore.QCoreApplication.instance().setStyle('Fusion')
    QtCore.QCoreApplication.instance().setApplicationDisplayName('MAPIT')

    #

    P, colordict = get_palette('light',return_dict=True) 
    self.colordict = colordict
    
    QtCore.QCoreApplication.instance().setPalette(P)


def ChangeColor(self):

    if self.MakeLight.isChecked():
        palette, colordict = get_palette('light',return_dict=True)
    else:
        palette, colordict = get_palette('dark',return_dict=True)

    QtCore.QCoreApplication.instance().setPalette(palette)
    self.colordict = colordict

    self.canvas.fig.set_facecolor(colordict["WindowBackground"])
    self.canvas.axes.set_facecolor(colordict["plotBg"])
    self.canvas.setStyleSheet("background-color: "+colordict["WindowBackground"])



    self.canvas.axes.spines['bottom'].set_color(colordict["Text"])
    self.canvas.axes.spines['top'].set_color(colordict["Text"])
    self.canvas.axes.spines['right'].set_color(colordict["Text"])
    self.canvas.axes.spines['left'].set_color(colordict["Text"])

    self.canvas.axes.tick_params(axis='x', colors=colordict["Text"], which='both')
    self.canvas.axes.tick_params(axis='y', colors=colordict["Text"], which='both')

    self.canvas.axes.yaxis.label.set_color(colordict["Text"])
    self.canvas.axes.xaxis.label.set_color(colordict["Text"])
    self.canvas.axes.title.set_color(colordict["Text"])


    update_naviStyle(self.colordict,self.navi_toolbar)


    self.canvas.draw()

    for j in range(len(self.children())):
        try:
          self.children()[j].setPalette(palette)
        except:
          None

    update_aniGBoxSmall_styleSheet(self.colordict,self.mb1)
    update_aniGBoxSmall_styleSheet(self.colordict,self.mb2)
    update_aniGBoxSmall_styleSheet(self.colordict,self.mb3)
    update_aniGBoxSmall_styleSheet(self.colordict,self.mb4)
    update_aniGBoxSmall_styleSheet(self.colordict,self.mdlbox,isactive=1)
    update_aniGBoxSmall_styleSheet(self.colordict,self.datBox,isactive=1)

    update_aniGBoxLarge_styleSheet(self.colordict,self.AnalysisContainer,isactive=1 if (self.AnalysisContainer.colorBorder == 1) else 0, valueA=0 if (self.AnalysisContainer.colorBorder == 1) else None)
    update_aniGBoxLarge_styleSheet(self.colordict,self.SGSetContainer,isactive=1 if (self.SGSetContainer.colorBorder == 1) else 0, valueA=0 if (self.SGSetContainer.colorBorder == 1) else None)
    update_aniGBoxLarge_styleSheet(self.colordict,self.PlotControls,isactive=1 if (self.PlotControls.colorBorder == 1) else 0, valueA=0 if (self.PlotControls.colorBorder == 1) else None)
    update_aniGBoxLarge_styleSheet(self.colordict,self.threshContainer,isactive=1 if (self.threshContainer.colorBorder == 1) else 0, valueA=0 if (self.threshContainer.colorBorder == 1) else None)
    update_aniGBoxLarge_styleSheet(self.colordict,self.datasetContainer,isactive=1 if (self.datasetContainer.colorBorder == 1) else 0, valueA=0 if (self.datasetContainer.colorBorder == 1) else None)
    update_aniGBoxLarge_styleSheet(self.colordict,self.sandDataContain,isStatic=1)
    update_aniGBoxLarge_styleSheet(self.colordict,self.extDataContain,isStatic=1)


    update_aniButton_styleSheet(self.ErrorS,self.colordict,colorborder=self.ErrorS.isEnabled(),staticfill=1 if self.ErrorS.isEnabled() else 0)
    update_aniButton_styleSheet(self.RunStats,self.colordict,colorborder=self.RunStats.isEnabled(),staticfill=1 if self.RunStats.isEnabled() else 0)
    update_aniButton_styleSheet(self.PlotRunner,self.colordict,colorborder=self.PlotRunner.isEnabled(),staticfill=1 if self.PlotRunner.isEnabled() else 0, extraspace=13)
    update_aniButton_styleSheet(self.CalcThresh,self.colordict,colorborder=self.CalcThresh.isEnabled(),staticfill=1 if self.CalcThresh.isEnabled() else 0)
    update_aniButton_styleSheet(self.sceneExplorePush,self.colordict,colorborder=self.sceneExplorePush.isEnabled(),staticfill=1 if self.sceneExplorePush.isEnabled() else 0)
    update_aniButton_styleSheet(self.extDatBtn,self.colordict,colorborder=self.extDatBtn.isEnabled(),staticfill=1 if self.extDatBtn.isEnabled() else 0)

    update_scrollObjStype(self.scrollTests,self.scrollHolder,self.colordict)



    #self.StatDlg.setPalette(palette)
    #update_messageBox_styleSheet(self.StatDlg,self.colordict,valueA=0)
    update_pbarStyle(self.PB,self.colordict)


def update_naviStyle(cd,navibar):
    grad = "QToolBar{background-color: "+\
            cd["WindowBackground"] +\
            ";}"

    navibar.setStyleSheet(grad)

def get_ani_hex(colordict,valueA):

    h = colordict["Highlight"].lstrip('#') 
    rgb_bord_L = tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) #covert to RGB

    h = colordict["HighlightDark"].lstrip('#')  
    rgb_bord_D = tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) #covert to RGB

    c0 = rgb_bord_D[0] + (rgb_bord_L[0] - rgb_bord_D[0]) * valueA
    c1 = rgb_bord_D[1] + (rgb_bord_L[1] - rgb_bord_D[1]) * valueA
    c2 = rgb_bord_D[2] + (rgb_bord_L[2] - rgb_bord_D[2]) * valueA

    bord = "#{0:02x}{1:02x}{2:02x}".format(int(max(0,min(c0,255))), 
                                            int(max(0,min(c1,255))), 
                                            int(max(0,min(c2,255))))

    return bord

def update_aniGBoxSmall_styleSheet(colordict,gbox,isactive=0,valueA=None):

    #top, right, bot, left
    gradA = "QWidget#{VAL}"
    gradC = "QWidget#{VAL}"
    gradD = """::title {
                top: -10px;
                left: 10px;
            }"""

    if not isactive and valueA is None: 
        bc = colordict["AlternateBaseBackground"]
    elif isactive and valueA is None:
        bc = colordict["HighlightDark"]
    elif isactive and valueA is not None:
        bc = get_ani_hex(colordict,valueA)

    
    gradB = "{border-color: " + bc +";" +\
            "border-width: 2px;" +\
            "border-style: solid;" +\
            "padding: 0px;" +\
            "border-radius: 7px;" +\
            "margin-top: 15px;" +\
            "margin-right: 5px;" +\
            "margin-left: 5px;" +\
            "margin-bottom: 5px;" +\
            "background-color: "+ colordict["AlternateWindowBackground"] + ";}"


    gbox.setStyleSheet( gradA.format(VAL=gbox.objectName()) + gradB + gradC.format(VAL=gbox.objectName()) + gradD)

def update_aniGBoxLarge_styleSheet(colordict,gbox,isactive=0,valueA=None,isStatic=0):

    if isStatic==1:
        gradA = "QWidget#{VAL}"
        gradC = "QWidget#{VAL}"
        gradD = """::title {
                    top: -10px;
                    left: 10px;
                }"""
        bckg = colordict["AlternateWindowBackground"]

           
            
        gradB = "{border-color: " + colordict["AlternateBaseBackground"] +";" +\
                "border-width: 1px;" +\
                "border-style: solid;" +\
                "padding: 5px 0px 0px 0px;" +\
                "border-radius: 7px;" +\
                "margin-top: 10px;" ";}"           
            


        gbox.setStyleSheet( gradA.format(VAL=gbox.objectName()) + gradB )


    else:
        gradA = "QWidget#{VAL}"
        gradC = "QWidget#{VAL}"
        gradD = """::title {
                    top: -10px;
                    left: 10px;
                }"""
        bckg = colordict["AlternateWindowBackground"]

        if valueA is None and isactive == 0:
            bord = colordict["AlternateBaseBackground"]
            gbox.colorBorder = 0

        elif valueA is not None and isactive == 1:
            bord = get_ani_hex(colordict,valueA)        
            gbox.colorBorder = 1
            
            
        gradB = "{border-color: " + bord +";" +\
                "border-width: 2px;" +\
                "border-style: solid;" +\
                "padding: 0px;" +\
                "border-radius: 7px;" +\
                "margin-top: 10px;" +\
                "background-color: "+ bckg + ";}"           
            


        gbox.setStyleSheet( gradA.format(VAL=gbox.objectName()) + gradB + gradC.format(VAL=gbox.objectName()) + gradD)





def update_aniButton_styleSheet(btn,colordict,colorborder=0,isrunning=0,valueA=None, valueB=None, staticfill=0,extraspace=0):

    EST = 0
    ESB = 0

    if extraspace > 0:
        EST = extraspace
    elif extraspace < 0:
        ESB = -extraspace



    #default style, not active and not animated
    if not (isrunning and valueA and valueB):
        bc = colordict["AlternateBaseBackground"]
        bg = colordict["AlternateWindowBackground"]
    if isrunning and valueA is not None and valueB is None:
        bc = colordict["AlternateBaseBackground"]
        bg = "qlineargradient(spread:pad, x1:0, y1:0, x2:5, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1})".format(color1=colordict["HighlightDark"], color2=colordict["Base"], value=valueA)
    if isrunning and valueA is not None and valueB is not None:
        bc = get_ani_hex(colordict,valueB) 
        bg = "qlineargradient(spread:pad, x1:0, y1:0, x2:5, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1})".format(color1=colordict["HighlightDark"], color2=colordict["Base"], value=valueA)

    if colorborder and valueB is None:
        bc = colordict["HighlightDark"]

    if colorborder and staticfill:
        bc = colordict["HighlightDark"]
        bg = "qlineargradient(spread:pad, x1:0, y1:0, x2:5, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1})".format(color1=colordict["HighlightDark"], color2=colordict["Base"], value=0)

    
    grad = "QWidget{" +\
        "border-color: " + bc +";" +\
        "border-width: 2px;" +\
        "border-style: solid;" +\
        "padding: 6px;" +\
        "margin-bottom: "+str(3+ESB)+"px;" +\
        "margin-left: 3px;" +\
        "margin-right: 3px;" +\
        "margin-top: " + str(EST) + "px;" +\
        "border-radius: 7px;" +\
        "background-color: " + bg +";" +\
        "color: " + colordict["Text"] + ";}"

    grad2 = """QToolTip {
                        background-color: rgb(239,239,239);
                        border-width: 2px;
                        border-color: rgb(153,200,221);
                        border-style: solid;
                        border-radius: 7px;
                        color: black;
                        }"""


    btn.setStyleSheet(grad)

def update_messageBox_styleSheet(box,colordict,valueA=None,progress=None):
   
    qss = """
        :disabled{color: rgb(0,0,0);
    """
    
    bg = colordict["AlternateWindowBackground"]

    if valueA is None:
        bc = colordict["AlternateBaseBackground"]
    else:
        bc = get_ani_hex(colordict,valueA) 

    grad = "border-color: " + bc +";" +\
            "border-width: 2px;" +\
            "border-style: solid;" +\
            "padding: 6px;" +\
            "border-radius: 7px;" +\
            "background-color: " + bg +";" +\
            "color: " + colordict["Text"] + ";}"

    qss += grad
    box.setStyleSheet(qss)


def update_scrollObjStype(area,frame,colordict):

    bg = colordict["AlternateWindowBackground"]
    bc = colordict["AlternateBaseBackground"]

    #top, right, bot, left
    A="QScrollArea {"
    B="QFrame {"

    grad = "border-color: " + bc +";" +\
            "border-width: 0px;" +\
            "border-style: solid;" +\
            "padding: 0px 0px 0px 0px;" +\
            "border-radius: 7px;" +\
            "background-color: " + bc +";" +\
            "color: " + colordict["Text"] + ";}"
    
    area.setStyleSheet(A+grad)
    frame.setStyleSheet(B+grad)
    

def disable_ani_button(guiobj, button_obj):
    button_obj._animation.stop()
    button_obj.doGradientAni = 0
    button_obj.setEnabled(0)

    update_aniButton_styleSheet(button_obj,guiobj.colordict)

    

def enable_ani_button(guiobj, button_obj, loc=None):
    button_obj.doGradientAni = 1
    button_obj.setEnabled(1)
    button_obj.IsDone = 1
    update_aniButton_styleSheet(button_obj,guiobj.colordict,colorborder=1,staticfill=1)


def update_pbarStyle(pbarobj,colordict):
    if colordict["Base"] == "#ffffff": #if light, use light highlight instead
        bg = colordict["Highlight"]
    else:
        bg = colordict["HighlightDark"]
    pbarobj.setStyleSheet("QProgressBar" +\
                        "{" +\
                        "border-radius: 7px;"+
                         "padding: 6px" ";}" +\
                        "QProgressBar::chunk " +\
                        "{background-color: " +bg + ";" +\
                        "border-radius :7px;" +\
                        "}")




def IncreaseFont(self):
    changeFontSize(self,1)
    
def DecreaseFont(self):
    changeFontSize(self,-1)

def changeFontSize(self,increment):
    app = QtWidgets.QApplication.instance()
    self.currentFontSize += increment
    QtWidgets.QApplication.instance().setFont(QtGui.QFont("Open Sans",self.currentFontSize))
    #idk why these have to be set separate, but if not their font won't change properly
    QtWidgets.QApplication.instance().setFont(QtGui.QFont("Open Sans",self.currentFontSize),"QtWidget")
    QtWidgets.QApplication.instance().setFont(QtGui.QFont("Open Sans",self.currentFontSize),"QGroupBox")
    QtWidgets.QApplication.instance().setFont(QtGui.QFont("Open Sans",self.currentFontSize),"QLabel")
    QtWidgets.QApplication.instance().setFont(QtGui.QFont("Open Sans",self.currentFontSize),"QProgressBar")
    PlotOps.fontresize(self)

def RestoreWindow(self):
    center_point = QtWidgets.QApplication.primaryScreen().geometry().center()
    frameGM = self.frameGeometry()
    frameGM.moveCenter(center_point)
    self.move(frameGM.topLeft())
    QtWidgets.QApplication.instance().setFont(QtGui.QFont("Open Sans"))
    self.currentFontSize  =QtWidgets.QApplication.instance().font().pointSize()

