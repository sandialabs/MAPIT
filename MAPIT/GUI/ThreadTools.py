from PySide6 import QtCore
import time
import MAPIT.core.Preprocessing as Preprocessing
from MAPIT.GUI import StatsPanelOps, GeneralOps
import numpy as np
import glob
from scipy.io import loadmat
from MAPIT.core.StatsProcessor import MBArea



class AnalysisThread(QtCore.QThread):

    finished = QtCore.Signal(dict) #pass back dict of results
    progress = QtCore.Signal(float) #pass float describing progress
    pbartext = QtCore.Signal(str) #progress bar text
    resultsReady = QtCore.Signal(tuple) # results

    def __init__(self, queue, resultsReady_cb, parent=None):
        QtCore.QThread.__init__(self,parent)
        self.resultsReady.connect(resultsReady_cb)
        self.progress.connect(self.progress_cb)
        self.pbartext.connect(self.pbartext_callback)
        self.queue = queue
        self.parent = parent



    def run(self):
        argz = self.queue.get()

        if argz is None:
            return

        AnalysisData = argz['AnalysisData']
        GUIparams = argz['GUIparams']
        IT = argz['IT']

        nInputs = len(AnalysisData.rawInput)
        nInventories =  len(AnalysisData.rawInventory)
        nOutputs = len(AnalysisData.rawOutput)
        

        AnalysisData.ErrorMatrix = StatsPanelOps.getGUIErrorVals(self.parent,
                                                        nInputs,
                                                        nInventories,
                                                        nOutputs,
                                                        argz['GLoc'])
        
        (AnalysisData.inpCalibPeriod, 
         AnalysisData.invCalibPeriod, 
         AnalysisData.outCalibPeriod) = StatsPanelOps.getGUICalibVals(self.parent,
                                                                      nInputs,
                                                                      nInventories,
                                                                      nOutputs)
        

        MB1 = MBArea(rawInput = AnalysisData.rawInput,
                                rawInventory = AnalysisData.rawInventory,
                                rawOutput = AnalysisData.rawOutput,
                                rawInputTimes = AnalysisData.rawInputTimes,
                                rawInventoryTimes = AnalysisData.rawInventoryTimes,
                                rawOutputTimes = AnalysisData.rawOutputTimes,
                                inputErrorMatrix = AnalysisData.ErrorMatrix[:nInputs,],
                                inventoryErrorMatrix = AnalysisData.ErrorMatrix[nInputs:nInventories+nInputs],
                                outputErrorMatrix = AnalysisData.ErrorMatrix[nInputs+nInventories:,],
                                mbaTime = argz['MBP'],
                                iterations = IT,
                                GUIObject = self,
                                dataOffset = AnalysisData.offset,
                                inputCalibrationPeriod=AnalysisData.inpCalibPeriod,
                                inventoryCalibrationPeriod=AnalysisData.invCalibPeriod,
                                outputCalibrationPeriod=AnalysisData.outCalibPeriod,
                                inputTypes=AnalysisData.inputTypes,
                                outputTypes=AnalysisData.outputTypes) 



        if argz['doError'] == 1:        
             
            # because of how the pbar is structured it's not easy to
            # pass back the stages of input/inventory/output and I can't
            # use intederminate with text because (https://bugreports.qt.io/browse/QTBUG-74)
            # and (https://bugreports.qt.io/browse/QTBUG-16260, https://stackoverflow.com/questions/19995688/displaying-text-inside-qprogressbar)
            # so this is how it's going to be for a bit, maybe this bug is fixed
            # in QT6, but at least this provide some measure of progress even
            # if its local to the error type rather than global across all
            # errors

            self.pbartext.emit('Applying errors')
            MB1.calcErrors()
            AnalysisData.inputAppliedError = MB1.inputAppliedError
            AnalysisData.inventoryAppliedError = MB1.inventoryAppliedError
            AnalysisData.outputAppliedError = MB1.outputAppliedError


        else:
          #if no sim error, use what user supplied        

            MB1.inputAppliedError = MB1.rawInput
            MB1.inventoryAppliedError = MB1.rawInventory
            MB1.outputAppliedError = MB1.rawOutput

            AnalysisData.inputAppliedError = MB1.rawInput
            AnalysisData.inventoryAppliedError = MB1.rawInventory
            AnalysisData.outputAppliedError = MB1.rawOutput

        # Here we check to see if either the test itself is requested
        # or if any of the dependency calculations are requested
        # for example, SITMUF required the MUF sequence
        # rather than forcing these options in the GUI (old behavior)
        # we just enforce it here on the backend
        # it's debatable which behavior is the more intuitive


        if argz['doMUF']:
            self.pbartext.emit('Processing: '+GUIparams.labels['Box12L'])
            AnalysisData.MUF = MB1.calcMUF()


        if argz['doAI']:   
            self.pbartext.emit('Processing: '+GUIparams.labels['Box13L'])  

            AnalysisData.AI = MB1.calcActiveInventory()

        if argz['doCUMUF']:
            self.pbartext.emit('Processing: '+GUIparams.labels['Box14L'])

            AnalysisData.CUMUF = MB1.calcCUMUF()



        if argz['doSEMUF']:
            self.pbartext.emit('Processing: '+GUIparams.labels['Box15L'])

            
            AnalysisData.SEMUF, \
            AnalysisData.SEMUFContribR, \
            AnalysisData.SEMUFContribS, \
            AnalysisData.SEMUFContribI = MB1.calcSEMUF()

        if argz['doSEMUFAI']:
            self.pbartext.emit('Processing: '+GUIparams.labels['Box16L'])

            AnalysisData.SEMUFAI, \
            AnalysisData.SEMUFAIContribR, \
            AnalysisData.SEMUFAIContribS = MB1.calcSEMUFAI()

        if argz['doSITMUF']:
            self.pbartext.emit('Processing: '+GUIparams.labels['Box17L'])


            AnalysisData.SITMUF = MB1.calcSITMUF()

        if argz['doPage']:
            self.pbartext.emit('Processing: '+GUIparams.labels['Box18L'])

            AnalysisData.Page = MB1.calcPageTT()

        self.pbartext.emit('Ready')
        self.progress.emit(100)
        self.resultsReady.emit((AnalysisData, argz['doMUF'], argz['doAI'], argz['doCUMUF'],
                           argz['doSEMUF'], argz['doSEMUFAI'], argz['doSITMUF'], argz['doPage']))
        return


    def progress_cb(self,G):
        if G == -1:
            self.parent.PB.setMinimum(0)
            self.parent.PB.setMaximum(0)            
        elif G == 0:
            self.parent.PB.setMinimum(0) 
            self.parent.PB.setMaximum(100)
        else:
            self.parent.PB.setValue(G)
    
    def pbartext_callback(self,G):
        #self.parent.StatDlg.UpdateDispText(G)
        self.parent.PB.setValue(0) #sometimes the progress emitter can be slow so i
                                   #added it here instead
        self.parent.PB.setFormat(G+" (%p%)") 



class dataLoadThread(QtCore.QThread):
    finished = QtCore.Signal(dict)
    resultsReady = QtCore.Signal(tuple)
    

    def __init__(self, queue, resultsReady_cb, parent=None):
        QtCore.QThread.__init__(self,parent)
        self.resultsReady.connect(resultsReady_cb)
        self.queue = queue
        self.parent = parent

    def run(self):
        argz = self.queue.get()
        pbar_mssg = None

        if argz is None:
            return

        AnalysisData = argz['AnalysisData']
        GUIparams = argz['GUIparams']

        try:
            AnalysisData, GUIparams = GeneralOps.getSceneData(self.parent,AnalysisData,GUIparams)
        except:
            pbar_mssg = 'Warning! Failed to load data!'

        self.resultsReady.emit((AnalysisData,GUIparams, pbar_mssg))


class getExtData(QtCore.QThread):
    finished = QtCore.Signal(dict)
    progress = QtCore.Signal(float)
    pbartext = QtCore.Signal(str)
    resultsReady = QtCore.Signal(tuple)

    def __init__(self, queue, resultsReady_cb, parent=None):
        QtCore.QThread.__init__(self,parent)
        self.resultsReady.connect(resultsReady_cb)
        self.progress.connect(self.progress_cb)
        self.pbartext.connect(self.pbartext_callback)
        self.queue = queue
        self.parent = parent

    def run(self):

        n=0
        argz = self.queue.get()

        if argz is None:
            return
        
        Wizard = argz['Wizard']
        AnalysisData = argz['AnalysisData']
        GUIparams = argz['GUIparams']
        fileext = Wizard.dataType
        infiles = glob.glob(Wizard.InDir+'/*'+fileext)
        invfiles = glob.glob(Wizard.InvDir+'/*'+fileext)
        outfiles = glob.glob(Wizard.OutDir+'/*'+fileext)

        totf = len(infiles)+len(invfiles)+len(outfiles)

        self.progress.emit(0)
        self.pbartext.emit("Importing data")

        indat = []
        invdat = []
        outdat = []

        inTdat = []
        invTdat = []
        outTdat = []

        


        if fileext == '.csv':
            for i in range(len(infiles)):
                z = GeneralOps.checkImportAxes(np.loadtxt(infiles[i],delimiter=','))
                inTdat.append(z[:,0])
                indat.append(z[:,1])
                n+=1
                self.progress.emit(n/totf*100)


            for i in range(len(invfiles)):
                z = GeneralOps.checkImportAxes(np.loadtxt(invfiles[i],delimiter=','))
                invTdat.append(z[:,0])
                invdat.append(z[:,1])
                n+=1
                self.progress.emit(n/totf*100)


            for i in range(len(outfiles)):
                z = GeneralOps.checkImportAxes(np.loadtxt(outfiles[i],delimiter=','))
                outTdat.append(z[:,0])
                outdat.append(z[:,1])
                n+=1
                self.progress.emit(n/totf*100)


        elif fileext == '.mat':
            for i in range(len(infiles)):
                z = loadmat(infiles[i])
                nloc = z['in']['data'].squeeze().size
                if nloc == 1:
                    indat.append(z['in']['data'].squeeze()[()])
                    inTdat.append(z['in']['time'].squeeze()[()])
                else:
                    for j in range(nloc):
                        indat.append(z['in']['data'].squeeze()[j].squeeze())
                        inTdat.append(z['in']['time'].squeeze()[j].squeeze())
                n+=1
                self.progress.emit(n/totf*100)

            for i in range(len(invfiles)):
                z = loadmat(invfiles[i])
                nloc = z['invn']['data'].squeeze().size
                if nloc == 1:
                    invdat.append(z['invn']['data'].squeeze()[()])
                    invTdat.append(z['invn']['time'].squeeze()[()])
                else:
                    for j in range(nloc):
                        invdat.append(z['invn']['data'].squeeze()[j].squeeze())
                        invTdat.append(z['invn']['time'].squeeze()[j].squeeze())
                n+=1
                self.progress.emit(n/totf*100)

            for i in range(len(outfiles)):
                z = loadmat(outfiles[i])
                nloc = z['outn']['data'].squeeze().size
                if nloc == 1:
                    outdat.append(z['outn']['data'].squeeze()[()])
                    outTdat.append(z['outn']['time'].squeeze()[()])    
                else:                       
                    for j in range(nloc):
                        outdat.append(z['outn']['data'].squeeze()[j].squeeze())
                        outTdat.append(z['outn']['time'].squeeze()[j].squeeze()) 
                n+=1
                self.progress.emit(n/totf*100)


        elif fileext == '.npz':
            None
        
        else:
            return
        
        self.resultsReady.emit((AnalysisData,GUIparams,Wizard,self.parent, indat, inTdat, invdat, invTdat, outdat, outTdat))

    def progress_cb(self,G):
        if G == -1:
            self.parent.PB.setMinimum(0)
            self.parent.PB.setMaximum(0)            
        elif G == 0:
            self.parent.PB.setMinimum(0) 
            self.parent.PB.setMaximum(100)
        else:
            self.parent.PB.setValue(G)

    def pbartext_callback(self,G):
        self.parent.PB.setValue(0) 
        self.parent.PB.setFormat(G+" (%p%)") 
