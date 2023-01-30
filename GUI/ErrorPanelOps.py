import numpy as np
from PySide2 import QtWidgets
import os

def MultiLocUpdate(GUIObject,GUIparams,errorType):



        if hasattr(GUIObject, 'Wizard'):
            TotalLocs = int(GUIObject.Wizard.InKMP) + int(GUIObject.Wizard.InvKMP) + int(
            GUIObject.Wizard.OutKMP)
        else:
            TotalLocs = GUIparams.nTotalLocations

        #nColumns can be up to 6 for multiple element analyses, for example
        #if user chooses u, pu, and generic. But if they chose less, then item
        #will be none anyways

        if errorType == 'rand':
            nColumns = 5
            Column = 0
            updateStr = str(GUIObject.AllRand.currentText())
            CI = GUIObject.AllRand.currentIndex()

            #this sets the value of the individual dropdown boxes
            #to be the same as the overall random error box
            GUIObject.InpRand.setCurrentIndex(CI)
            GUIObject.InvRand.setCurrentIndex(CI)
            GUIObject.OutRand.setCurrentIndex(CI)


        else:
            nColumns = 6
            Column = 1
            updateStr = str(GUIObject.AllSys.currentText())
            CI = GUIObject.AllSys.currentIndex()
            
            #this sets the value of the individual dropdown boxes
            #to be the same as the overall random error box
            GUIObject.InpSys.setCurrentIndex(CI)
            GUIObject.InvSys.setCurrentIndex(CI)
            GUIObject.OutSys.setCurrentIndex(CI)




        #now set for the individual entries
        while Column < nColumns:
            for j in range(0, GUIObject.EP.rowCount()):
                if GUIObject.EP.item(j, Column) is not None:
                    GUIObject.EP.setItem(
                        j, Column, QtWidgets.QTableWidgetItem(updateStr))
            Column += 2



def SingleLocUpdate(GUIObject,GUIparams,errorType,location):




        if hasattr(GUIObject, 'Wizard'):
            TotalLocs = int(GUIObject.Wizard.InKMP) + int(GUIObject.Wizard.InvKMP) + int(
            GUIObject.Wizard.OutKMP)
        else:
            TotalLocs = GUIparams.nTotalLocations

        #nColumns can be up to 6 for multiple element analyses, for example
        #if user chooses u, pu, and generic. But if they chose less, then item
        #will be none anyways

        if errorType == 'rand':
            nColumns = 5
            Column = 0
        else:
            nColumns = 6
            Column = 1


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

            if errorType == 'rand':
                updateStr = str(GUIObject.InpRand.currentText())
            else:
                updateStr = str(GUIObject.InpSys.currentText())

        elif location == 'inv':
            low = inLocs + 1
            high = inLocs + invLocs + 1

            if errorType == 'rand':
                updateStr = str(GUIObject.InvRand.currentText())
            else:
                updateStr = str(GUIObject.InvSys.currentText())


        elif location == 'out':
            low = inLocs + invLocs + 2
            high = inLocs + invLocs + outLocs + 2

            if errorType == 'rand':
                updateStr = str(GUIObject.OutRand.currentText())
            else:
                updateStr = str(GUIObject.OutSys.currentText())


        while Column < nColumns:
            for j in range(low, high):
                if GUIObject.EP.item(j, Column) is not None:
                    GUIObject.EP.setItem(
                        j, Column, QtWidgets.QTableWidgetItem(updateStr))
            Column += 2





def loadErrorFromDisk(GUIObject):
        """
                This function loads previously
                configured error values
        """

        outdir = os.path.abspath(os.path.join(os.path.dirname(__file__),'errorConfig.csv'))
        try:
            x = np.loadtxt(outdir, delimiter=',')

            for i in range(np.shape(x)[0]):
                for j in range(np.shape(x)[1]):
                    if x[i, j] != 0:
                        GUIObject.EP.setItem(i, j, QtWidgets.QTableWidgetItem(str(x[i, j])))
        except:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setIcon(QtWidgets.QMessageBox.Warning)
            msgbox.setText("Error configuration not found on path: \n"+outdir)
            msgbox.exec_()


def saveErrorToDisk(GUIObject):
        """
                This function saves configured
                error values
        """

        outdir = os.path.abspath(os.path.join(os.path.dirname(__file__),'errorConfig.csv'))

        x = np.zeros((GUIObject.EP.rowCount(), 6))

        for i in range(0, GUIObject.EP.rowCount()):
            for j in range(0, 6):
                if GUIObject.EP.item(i, j) is None:
                    x[i, j] = 0
                else:
                    x[i, j] = GUIObject.EP.item(i, j).text()

        np.savetxt(outdir, x, delimiter=',')