from PySide2 import  QtCore
import matplotlib
import numpy as np
from MAPIT.GUI import PlotOps
from MAPIT.GUI import DialogComponents


def verifyGUIRequests(GUIObject,GUIparams):
        

        #need to find the index to operate on if there's multiple elements
        #assumes we are only going to operate on one element, not multiple

        eleNames = GUIparams.eleList
        GLoc = GUIObject.GESelector.currentIndex()
        GUIparams.Loc = GUIObject.GESelector.currentIndex()

        indexQuery = []

        #if generic box was specified then assign that now


        #check the list of element names for U and Pu
        if len(eleNames) > 0:
            
            #if imported from the wizard need to split 
            #into a list

            try:
                eleNames = eleNames.split(",")
            except:
                None


        #need to create an empty vector for element names
        EleVecLabel = [None] * GUIparams.nInferredEles
        
        #set some default names
        for i in range(0, len(EleVecLabel)):
            EleVecLabel[i] = 'Element ' + str(i + 1)

        #if names were given, overwrite those
        if len(eleNames) > 0:
            for i in eleNames:
                EleVecLabel[int(eleNames.index(i))] = i



        GUIparams.EleVecLabel = EleVecLabel

        GUIparams.TestType = 'G'




        return GLoc, GUIparams


def UpdatePlotterLocs(GUIObject,GUIparams,addType):


        if GUIparams.EleVecLabel[GUIparams.Loc][:7] == 'Element':
            GUIObject.metricBox.addItem('Generic ' + addType)
        else:
            GUIObject.metricBox.addItem(GUIparams.EleVecLabel[GUIparams.Loc] + ' '+ addType)


def getRequestedTests(GUIObject):

        doError = 0
        doMUF = 0
        doAI = 0
        doCUMUF = 0
        doSEID = 0
        doSEIDAI = 0
        doSITMUF = 0
        doPage = 0

        if (GUIObject.CB_ErrorProp.isChecked()) > 0:
          doError = 1

        if (GUIObject.CB_MUF.isChecked()) > 0:
            doMUF = 1

        if (GUIObject.CB_AI.isChecked()) > 0:
            doAI = 1

        if (GUIObject.CB_CUMUF.isChecked()) > 0:
            doCUMUF = 1

        if (GUIObject.CB_SMUF.isChecked()) > 0:
            doSEID = 1

        if (GUIObject.CB_SMUFAI.isChecked()) > 0:
            doSEIDAI = 1

        if (GUIObject.CB_SITMUF.isChecked()) > 0:
            doSITMUF = 1
        
        if (GUIObject.CB_PAGE.isChecked()) > 0:
            doPage = 1

        return doError, doMUF, doAI, doCUMUF, doSEID, doSEIDAI, doSITMUF, doPage


def preparePlotterOptions(GUIObject,doMUF,doAI,doCUMUF,doSEID,doSEIDAI,doSITMUF,doPage,GUIparams,AnalysisData):
      PlotOps.UpdatePlotOpts(GUIObject)

      #update style on some dropdown boxes
      #to show that the error prop has run
      #and that those options are available
      gradA = "QWidget#{VAL}"
      gradB = "{" + "border-color: rgb({value},{value2},{value3});".format(value=153,value2=200,value3=221) +\
        "border-width: 2px;" +\
        "border-style: solid;" +\
        "padding: 0px;" +\
        "border-radius: 7px;" +\
        "margin-top: 20px;" +\
        "background-color: rgb(239,239,239);" +\
          "}"
      gradC = "QWidget#{VAL}"
      gradD = ":"

      if GUIObject.window().MakeLight.isChecked() == 0:
        gradB = gradB.replace('rgb(239,239,239)', 'rgb(51,51,51)')
        gradB = gradB.replace('rgb(153,200,221)', 'rgb(0,83,118)')

      GUIObject.mb1.ChangeActive(1)
      GUIObject.mb1.setStyleSheet(
          gradA.format(VAL='PB1') + gradB + gradC.format(VAL='PB1') + gradD)


      PlotOps.UpdateLocOpts(GUIObject,GUIparams)  #add locations to plot since default plot option is ground truth

      grad2 = "border-color: rgb({value},{value2},{value3});".format(value=211,value2=211,value3=211) +\
      "border-width: 5px;" +\
      "border-style: solid;" +\
      "padding: 6px;" +\
      "border-radius: 7px;}"

      if GUIObject.window().MakeLight.isChecked() == 0:
        grad2 = grad2.replace('rgb(211,211,211)', 'rgb(66,66,66)')

      GUIObject.SGSetContainer.setStyleSheet(
          "QWidget#{VAL}".format(VAL=GUIObject.SGSetContainer.Loc) + "{" + grad2 +
          "QWidget#{VAL}".format(VAL=GUIObject.SGSetContainer.Loc) )
      GUIObject.AnalysisContainer.setStyleSheet(
          "QWidget#{VAL}".format(VAL=GUIObject.AnalysisContainer.Loc) + "{" + grad2 +
          "QWidget#{VAL}".format(VAL=GUIObject.AnalysisContainer.Loc))

      #resets button animation and turns off after running, but
      #since the GUI supports new runs without restarting probably
      #better to leave them on
      #GUIObject.HasRunOnce=1

      GUIObject.threshContainer.PassLoc('PB8')
      GUIObject.threshContainer._animation.setLoopCount(3)
      GUIObject.threshContainer._animation.start()

      GUIObject.PlotControls.PassLoc('PB5')
      GUIObject.PlotControls._animation.setLoopCount(3)
      GUIObject.PlotControls._animation.start()

      GUIObject.PlotRunner.setEnabled(1)
      GUIObject.PlotRunner.PassLoc('PRB')
      GUIObject.PlotRunner._animation.setLoopCount(3)
      GUIObject.PlotRunner._animation.start()



      GUIObject.ExportDat.setEnabled(1)

      if GUIObject.CB_SMUF.isChecked() == 1:
        GUIObject.TabView.setEnabled(1)
        GUIObject.TabOpt.setToolTip('')




    #   if GUIObject.decompStatus == 0:
    #       GUIObject.StatDlg.UpdateDispText('Decomposition error, restart calculation')
    #       GUIObject.PB.setValue(0)
    #   else:

      GUIObject.StatDlg.UpdateDispText('Execution Finished')
      GUIObject.PB.setValue(100)

      QtCore.QCoreApplication.instance().processEvents()

      # need to reset rcparam defaults incase some were changed
      # during scene select

      matplotlib.rcParams.update(matplotlib.rcParamsDefault)

      if doMUF == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box12L"])
      if doAI == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box13L"])
      if doCUMUF:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box14L"])
      if doSEID == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box15L"])
      if doSEIDAI == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box16L"])
      if doSITMUF == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box17L"])
      if doPage == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box18L"])


def importDataUpdateUI(GUIObject,GUIparams):

      GUIObject.StatDlg.UpdateDispText('Importing data...')
      QtCore.QCoreApplication.instance().processEvents()

      GUIObject.PB.setMaximum(0)
      GUIObject.PB.setMinimum(0)
      


      if GUIObject.CB_PAGE.isChecked():
        GUIObject.CB_SITMUF.setChecked(1)
        GUIObject.CB_MUF.setChecked(1)

      if GUIObject.CB_SITMUF.isChecked():
        GUIObject.CB_MUF.setChecked(1)


      QtCore.QCoreApplication.instance().processEvents()
      

    #   if hasattr(GUIparams,'sceneName'):
    #     liH = ['U'] #the fuel fab only has U, other scenarios not yet included
    #     GUIparams.nInferredEles = 1






def getGUIErrorVals(GUIObject,lenInp,lenInv,lenOut,GLoc):

        if hasattr(GUIObject, 'Wizard'):  #if data was imported
            TotalLocs = int(GUIObject.Wizard.InKMP) + int(GUIObject.Wizard.InvKMP) + int(
            GUIObject.Wizard.OutKMP)

        else:  #otherwise (scene selection)
            TotalLocs = lenInp + lenInv + lenOut

        ErrorMatrix = np.zeros((TotalLocs, 2))

        # setup error table using
        # previously described errors

        #this ensures that the right items are placed correctly within the error matrix
        #as sometimes the GUI can have missing columns, added rows, etc for aesthetic purposes

        mapDict = {'Rand':0, 'Sys':1}
        # create a dictionary to map between the location
        # and the error matrix

        ColLoc = 0


        if GLoc != -1:
            ColLoc = 0


        for j in range(ColLoc,ColLoc+2):
            P = 0
            
            for i in range(0,GUIObject.EP.rowCount()):
                if GUIObject.EP.item(i,j) is not None:
                    uncert_str = GUIObject.EP.item(i, j).text()[:-2]
                    ErrorMatrix[P, j-ColLoc] = float(uncert_str) / 100
                    P+= 1



        
        # for i in range(0, GUIObject.EP.rowCount()):
        #     for j in range(ColLoc, ColLoc+2):
        #         if GUIObject.EP.item(i, j) is not None:




        return ErrorMatrix