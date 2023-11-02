from PySide2 import  QtCore
import matplotlib
import numpy as np
from MAPIT.GUI import PlotOps, StyleOps


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
      


      # store the current values
      currentMetric = GUIObject.metricBox.currentText()
      currentNum = GUIObject.NumToPlot.currentText()
      currentLoc = GUIObject.LocBox.currentText()
      currentType = GUIObject.NucIDBox.currentText()

      PlotOps.UpdatePlotOpts(GUIObject)

      if doMUF == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box12L"])
      if doAI == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box13L"])
      if doCUMUF:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box14L"])
      if doSEID == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box15L"])
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box46L"])
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box47L"])
      if doSEIDAI == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box16L"])
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box49L"])
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box50L"])
      if doSITMUF == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box17L"])
      if doPage == 1:
        UpdatePlotterLocs(GUIObject,GUIparams,GUIparams.labels["Box18L"])

      # restore previous location selection, if relevant and present
      if GUIObject.metricBox.findText(currentMetric) != -1:
          GUIObject.metricBox.setCurrentIndex(GUIObject.metricBox.findText(currentMetric))

      PlotOps.UpdateLocOpts(GUIObject,GUIparams)  #add locations to plot since default plot option is ground truth

      # restore previous selection if still present and relevant
      if GUIObject.NumToPlot.findText(currentNum) != -1:
          GUIObject.NumToPlot.setCurrentIndex(GUIObject.NumToPlot.findText(currentNum))

      if GUIObject.LocBox.findText(currentLoc) != -1:
          GUIObject.LocBox.setCurrentIndex(GUIObject.LocBox.findText(currentLoc))

      if GUIObject.NucIDBox.findText(currentType) != -1:
          GUIObject.NucIDBox.setCurrentIndex(GUIObject.NucIDBox.findText(currentType))

      GUIObject.mb1.setEnabled(1)
      GUIObject.mb1.setTitle(GUIparams.labels["Box31L"])
      GUIObject.mb1.ChangeActive(1)
      StyleOps.update_aniGBoxSmall_styleSheet(GUIObject.colordict,GUIObject.mb1,isactive=1)      

      StyleOps.update_aniGBoxLarge_styleSheet(GUIObject.colordict,GUIObject.SGSetContainer)
      StyleOps.update_aniGBoxLarge_styleSheet(GUIObject.colordict,GUIObject.AnalysisContainer)
      StyleOps.update_aniGBoxLarge_styleSheet(GUIObject.colordict,GUIObject.datasetContainer)


      #resets button animation and turns off after running, but
      #since the GUI supports new runs without restarting probably
      #better to leave them on
      #GUIObject.HasRunOnce=1

      GUIObject.threshContainer._animation.setLoopCount(3)
      GUIObject.threshContainer._animation.start()

      GUIObject.PlotControls._animation.setLoopCount(3)
      GUIObject.PlotControls._animation.start()

      GUIObject.PlotRunner.setEnabled(1)
      StyleOps.enable_ani_button(GUIObject,GUIObject.PlotRunner)
      GUIObject.PlotRunner._animation.setLoopCount(3)
      GUIObject.PlotRunner._animation.start()



      GUIObject.ExportDat.setEnabled(1)
      GUIObject.StatThresh.setEnabled(1)

      if GUIObject.CB_SMUF.isChecked() == 1:
        GUIObject.TabView.setEnabled(1)
        GUIObject.TabOpt.setToolTip('')

      if GUIObject.CB_SMUFAI.isChecked() == 1:
          GUIObject.TabView1.setEnabled(1)



      GUIObject.PB.setFormat('Execution finished')
      GUIObject.PB.setValue(100)

      QtCore.QCoreApplication.instance().processEvents()

      # need to reset rcparam defaults incase some were changed
      # during scene select

      matplotlib.rcParams.update(matplotlib.rcParamsDefault)


def getGUIErrorVals(GUIObject,GUIparams,lenInp,lenInv,lenOut,GLoc):

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

        if GUIparams.errorstyle == True:
            for j in range(ColLoc,ColLoc+2):

                for i in range(0,lenInp):
                    if GUIObject.EP.item(i,j) is not None:
                        if  GUIObject.EP.item(i, j).text().endswith('%'):
                            ErrorMatrix[i, j-ColLoc] = float(GUIObject.EP.item(i, j).text()[:-2]) / 100
                        else:
                            ErrorMatrix[i, j-ColLoc] = float(GUIObject.EP.item(i, j).text()) / 100
                for i in range(lenInp+1,lenInp+lenInv+1):
                    if GUIObject.EP.item(i,j) is not None:
                        if  GUIObject.EP.item(i, j).text().endswith('%'):
                            ErrorMatrix[i-1, j-ColLoc] = float(GUIObject.EP.item(i, j).text()[:-2]) / 100

                        else:
                            ErrorMatrix[i-1, j-ColLoc] = float(GUIObject.EP.item(i, j).text()) / 100

                for i in range(lenInp+lenInv+1,lenInp+lenInv+lenOut+2):
                    if GUIObject.EP.item(i,j) is not None:
                        if  GUIObject.EP.item(i, j).text().endswith('%'):
                            ErrorMatrix[i-2, j-ColLoc] = float(GUIObject.EP.item(i, j).text()[:-2]) / 100
                        else:
                            ErrorMatrix[i-2, j-ColLoc] = float(GUIObject.EP.item(i, j).text()) / 100
        else:
            for j in range(ColLoc,ColLoc+1):

                for i in range(0,lenInp):
                    if GUIObject.EP.item(i,j) is not None:
                        if  GUIObject.EP.item(i, j).text().endswith('%'):
                            ErrorMatrix[i, j-ColLoc] = float(GUIObject.EP.item(i, j).text()[:-2]) / 100
                            ErrorMatrix[i, j-ColLoc+1] = 0.0
                        else:
                            ErrorMatrix[i, j-ColLoc] = float(GUIObject.EP.item(i, j).text()) / 100
                            ErrorMatrix[i, j-ColLoc+1] = 0.0

                for i in range(lenInp+1,lenInp+lenInv+1):
                    if GUIObject.EP.item(i,j) is not None:
                        if  GUIObject.EP.item(i, j).text().endswith('%'):
                            ErrorMatrix[i-1, j-ColLoc] = float(GUIObject.EP.item(i, j).text()[:-2]) / 100
                            ErrorMatrix[i, j-ColLoc+1] = 0.0

                        else:
                            ErrorMatrix[i-1, j-ColLoc] = float(GUIObject.EP.item(i, j).text()) / 100
                            ErrorMatrix[i-1, j-ColLoc+1] = 0.0

                for i in range(lenInp+lenInv+1,lenInp+lenInv+lenOut+2):
                    if GUIObject.EP.item(i,j) is not None:
                        if  GUIObject.EP.item(i, j).text().endswith('%'):
                            ErrorMatrix[i-2, j-ColLoc] = float(GUIObject.EP.item(i, j).text()[:-2]) / 100
                            ErrorMatrix[i-2, j-ColLoc+1] = 0.0
                        else:
                            ErrorMatrix[i-2, j-ColLoc] = float(GUIObject.EP.item(i, j).text()) / 100
                            ErrorMatrix[i-2, j-ColLoc+1] = 0.0
        return ErrorMatrix


def update_data_opts(GUIObj,flag):

  if flag  == 1: #external data

    disable_setup_controls(GUIObj)
    GUIObj.sandDataContain.setChecked(False)
    GUIObj.extDataContain.setChecked(True)
    StyleOps.update_aniGBoxSmall_styleSheet(GUIObj.colordict,GUIObj.mdlbox,isactive=0)
    StyleOps.update_aniGBoxSmall_styleSheet(GUIObj.colordict,GUIObj.datBox,isactive=0)

    #disable animations
    GUIObj.mdlbox.ChangeActive(0)
    GUIObj.datBox.ChangeActive(0)

    

    GUIObj.PB.setFormat("Waiting for data import")

    
  else: #sand data

    enable_setup_controls(GUIObj)
    GUIObj.sandDataContain.setChecked(True)
    GUIObj.extDataContain.setChecked(False)
    StyleOps.update_aniGBoxSmall_styleSheet(GUIObj.colordict,GUIObj.mdlbox,isactive=1)
    StyleOps.update_aniGBoxSmall_styleSheet(GUIObj.colordict,GUIObj.datBox,isactive=1)

    GUIObj.mdlbox.ChangeActive(1)
    GUIObj.datBox.ChangeActive(1)


    GUIObj.CB_ErrorProp.setEnabled(0)
    GUIObj.CB_ErrorProp.setChecked(1)



    



    GUIObj.PB.setFormat("Waiting for problem setup")


def enable_setup_controls(GUIObj):
    #in case it was already running, stop
    GUIObj.SGSetContainer._animation.stop()
    GUIObj.datasetContainer._animation.stop()
    GUIObj.AnalysisContainer._animation.stop()

    GUIObj.SGSetContainer._animation.start()
    GUIObj.datasetContainer._animation.start()
    GUIObj.AnalysisContainer._animation.start()

    GUIObj.SGSetContainer.colorBorder = 1
    GUIObj.datasetContainer.colorBorder = 1
    GUIObj.AnalysisContainer.colorBorder = 1
    StyleOps.enable_ani_button(button_obj=GUIObj.ErrorS, guiobj=GUIObj)
    StyleOps.disable_ani_button(button_obj=GUIObj.RunStats, guiobj=GUIObj)
    GUIObj.ErrorS._animation.start()

    StyleOps.update_aniGBoxLarge_styleSheet(GUIObj.colordict,GUIObj.AnalysisContainer,isactive=1 if (GUIObj.AnalysisContainer.colorBorder == 1) else 0, valueA=0 if (GUIObj.AnalysisContainer.colorBorder == 1) else None)
    StyleOps.update_aniGBoxLarge_styleSheet(GUIObj.colordict,GUIObj.SGSetContainer,isactive=1 if (GUIObj.SGSetContainer.colorBorder == 1) else 0, valueA=0 if (GUIObj.SGSetContainer.colorBorder == 1) else None)
    StyleOps.update_aniGBoxLarge_styleSheet(GUIObj.colordict,GUIObj.datasetContainer,isactive=1 if (GUIObj.datasetContainer.colorBorder == 1) else 0, valueA=0 if (GUIObj.datasetContainer.colorBorder == 1) else None)
    StyleOps.update_scrollObjStype(GUIObj.scrollTests,GUIObj.scrollHolder,GUIObj.colordict)


    GUIObj.CB_ErrorProp.setEnabled(1)
    GUIObj.CB_MUF.setEnabled(1)
    GUIObj.CB_AI.setEnabled(1)
    GUIObj.CB_CUMUF.setEnabled(1)
    GUIObj.CB_SMUF.setEnabled(1)
    GUIObj.CB_SMUFAI.setEnabled(1)
    GUIObj.CB_SITMUF.setEnabled(1)
    GUIObj.CB_PAGE.setEnabled(1)

def disable_setup_controls(GUIObj):
    #TODO: disable styles
    GUIObj.SGSetContainer._animation.stop()
    GUIObj.datasetContainer._animation.stop()
    GUIObj.datasetContainer._animation.start()
    GUIObj.AnalysisContainer._animation.stop()

    GUIObj.SGSetContainer.colorBorder = 0
    GUIObj.AnalysisContainer.colorBorder = 0

    StyleOps.enable_ani_button(button_obj=GUIObj.ErrorS, guiobj=GUIObj)
    StyleOps.enable_ani_button(button_obj=GUIObj.RunStats, guiobj=GUIObj)
    #GUIObj.StatDlg.UpdateDispText('Waiting for data import',rebootAni=True)
    



    GUIObj.CB_ErrorProp.setChecked(0)
    GUIObj.IterBox.setEnabled(0)
    GUIObj.IterBox.setText("")
    GUIObj.CB_MUF.setEnabled(0)
    GUIObj.CB_AI.setEnabled(0)
    GUIObj.CB_CUMUF.setEnabled(0)
    GUIObj.CB_SMUF.setEnabled(0)
    GUIObj.CB_SMUFAI.setEnabled(0)
    GUIObj.CB_SITMUF.setEnabled(0)
    GUIObj.CB_PAGE.setEnabled(0)

    #SGSetContainer
    #AnalysisContainer
    #datasetContainer
    #scrollTests
    #scrollHolder
    #mdlBox
    #datBox

    StyleOps.update_aniGBoxLarge_styleSheet(GUIObj.colordict,GUIObj.AnalysisContainer,isactive=1 if (GUIObj.AnalysisContainer.colorBorder == 1) else 0, valueA=0 if (GUIObj.AnalysisContainer.colorBorder == 1) else None)
    StyleOps.update_aniGBoxLarge_styleSheet(GUIObj.colordict,GUIObj.SGSetContainer,isactive=1 if (GUIObj.SGSetContainer.colorBorder == 1) else 0, valueA=0 if (GUIObj.SGSetContainer.colorBorder == 1) else None)
    StyleOps.update_aniGBoxLarge_styleSheet(GUIObj.colordict,GUIObj.datasetContainer,isactive=1 if (GUIObj.datasetContainer.colorBorder == 1) else 0, valueA=0 if (GUIObj.datasetContainer.colorBorder == 1) else None)
    StyleOps.update_scrollObjStype(GUIObj.scrollTests,GUIObj.scrollHolder,GUIObj.colordict)
    StyleOps.update_aniGBoxSmall_styleSheet(GUIObj.colordict,GUIObj.mdlbox,isactive=0)
    StyleOps.update_aniGBoxSmall_styleSheet(GUIObj.colordict,GUIObj.datBox,isactive=0)

