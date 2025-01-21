import numpy as np
from PySide6 import QtWidgets,QtCore
import os
import sys
from platformdirs import user_config_dir, user_data_dir

def MultiLocUpdate(GUIObject,GUIparams,errorType):


        if errorType == 'rand':
            Column = 0
            if GUIparams.errorstyle == True:
                updateStr = str(GUIObject.AllRand.currentText())
                CI = GUIObject.AllRand.currentIndex()
                GUIObject.InpRand.setCurrentIndex(CI)
                GUIObject.InvRand.setCurrentIndex(CI)
                GUIObject.OutRand.setCurrentIndex(CI)
            else:
                updateStr = str(GUIObject.All.currentText())
                CI = GUIObject.All.currentIndex()
                GUIObject.Inp.setCurrentIndex(CI)
                GUIObject.Inv.setCurrentIndex(CI)
                GUIObject.Out.setCurrentIndex(CI)

            #this sets the value of the individual dropdown boxes
            #to be the same as the overall random error box


        elif errorType == 'sys':
            Column = 1
            updateStr = str(GUIObject.AllSys.currentText())
            CI = GUIObject.AllSys.currentIndex()
            
            #this sets the value of the individual dropdown boxes
            #to be the same as the overall random error box
            GUIObject.InpSys.setCurrentIndex(CI)
            GUIObject.InvSys.setCurrentIndex(CI)
            GUIObject.OutSys.setCurrentIndex(CI)

        elif errorType == 'freq':
            Column = 2
            updateStr = str(GUIObject.allCalib.currentText())
            CI = GUIObject.allCalib.currentIndex()
            
            #this sets the value of the individual dropdown boxes
            #to be the same as the overall random error box
            GUIObject.InpCalib.setCurrentIndex(CI)
            GUIObject.InvCalib.setCurrentIndex(CI)
            GUIObject.OutCalib.setCurrentIndex(CI)


        #now set for the individual entries
        for j in range(0, GUIObject.EP.rowCount()):
            if GUIObject.EP.item(j, Column).text().strip(' ') != '': #and len(str(GUIObject.EP.item(j, Column).flags()))==110:
                GUIObject.EP.setItem(
                    j, Column, QtWidgets.QTableWidgetItem(updateStr))

def SingleLocUpdate(GUIObject,GUIparams,errorType,location):

    if errorType == 'rand':
        Column = 0
    elif errorType == 'sys':
        Column = 1
    elif errorType == 'freq':
        Column = 2


    if hasattr(GUIObject, 'Wizard'):
        inLocs = int(GUIObject.Wizard.InKMP)
        invLocs = int(GUIObject.Wizard.InvKMP)
        outLocs = int(GUIObject.Wizard.OutKMP)
    else:
        inLocs = GUIparams.nInputLocations
        invLocs = GUIparams.nInventoryLocations
        outLocs = GUIparams.nOutputLocations

    if location == 'inp':
        low = 0
        high = inLocs

        if errorType == 'rand' and GUIparams.errorstyle == True:
            updateStr = str(GUIObject.InpRand.currentText())
        elif errorType == 'rand' and GUIparams.errorstyle == False:
            updateStr = str(GUIObject.Inp.currentText())
        elif errorType == 'sys' and GUIparams.errorstyle == True:
            updateStr = str(GUIObject.InpSys.currentText())
        elif errorType == 'freq' and GUIparams.errorstyle == True:
            updateStr = str(GUIObject.InpCalib.currentText())

    elif location == 'inv':
        low = inLocs + 1
        high = inLocs + invLocs + 1

        if errorType == 'rand' and GUIparams.errorstyle == True:
            updateStr = str(GUIObject.InvRand.currentText())
        elif errorType == 'rand' and GUIparams.errorstyle == False:
            updateStr = str(GUIObject.Inv.currentText())
        elif errorType == 'sys' and GUIparams.errorstyle == True:
            updateStr = str(GUIObject.InvSys.currentText())
        elif errorType == 'freq' and GUIparams.errorstyle == True:
            updateStr = str(GUIObject.InvCalib.currentText())


    elif location == 'out':
        low = inLocs + invLocs + 2
        high = inLocs + invLocs + outLocs + 2

        if errorType == 'rand' and GUIparams.errorstyle == True:
            updateStr = str(GUIObject.OutRand.currentText())
        elif errorType == 'rand' and GUIparams.errorstyle == False:
            updateStr = str(GUIObject.Out.currentText())
        elif errorType == 'sys' and GUIparams.errorstyle == True:
            updateStr = str(GUIObject.OutSys.currentText())
        elif errorType == 'freq' and GUIparams.errorstyle == True:
            updateStr = str(GUIObject.OutCalib.currentText())



    for j in range(low, high):
        if GUIObject.EP.item(j, Column) is not None:
            GUIObject.EP.setItem(
                j, Column, QtWidgets.QTableWidgetItem(updateStr))

def loadErrorFromDisk(GUIObject):
    """
            This function loads previously
            configured error values
    """
    
    outdir = os.path.join(user_config_dir('MAPIT',False),'errorConfig.csv')

    try:
        x = np.genfromtxt(outdir,delimiter=',',missing_values='nan')
    except:
        msgbox = QtWidgets.QMessageBox()
        msgbox.setIcon(QtWidgets.QMessageBox.Warning)
        msgbox.setText("Error configuration not found on path: \n"+outdir)
        msgbox.exec()

    for i in range(np.shape(x)[0]):
        for j in range(np.shape(x)[1]):
            if np.isnan(x[i,j]):
                    GUIObject.EP.setItem(i, j,  QtWidgets.QTableWidgetItem(str('')))
            elif x[i, j] == -1:
                    GUIObject.EP.setItem(i, j,  QtWidgets.QTableWidgetItem(str('None')))
            else:
                if j == 0 or j == 1:
                    GUIObject.EP.setItem(i, j, QtWidgets.QTableWidgetItem(str(x[i, j])+' %'))
                else:
                    GUIObject.EP.setItem(i, j, QtWidgets.QTableWidgetItem(str(x[i, j])))                        

def saveErrorToDisk(GUIObject):
    """
        This function saves configured
        error values
    """

    outdir = os.path.join(user_config_dir('MAPIT',False),'errorConfig.csv')

    x = np.zeros((GUIObject.EP.rowCount(), GUIObject.EP.columnCount()))

    for i in range(0, GUIObject.EP.rowCount()):
        for j in range(0, GUIObject.EP.columnCount()):
            if GUIObject.EP.item(i, j) is None or GUIObject.EP.item(i,j).text().strip(' ') == '':
                x[i, j] = np.nan
            elif GUIObject.EP.item(i,j).text() == 'None':
                x[i, j] = -1
            else:
                x[i, j] = float(GUIObject.EP.item(i, j).text().strip(' %'))

    np.savetxt(outdir, x, delimiter=',')