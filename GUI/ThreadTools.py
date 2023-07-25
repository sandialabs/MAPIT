from PySide2 import QtCore
import time
import MAPIT_internal.core.Preprocessing as Preprocessing
from MAPIT_internal.GUI import StatsPanelOps, GeneralOps
from MAPIT_internal.core import StatsTests as Tests
from MAPIT_internal.core import AuxFunctions as Aux
import numpy as np
import glob
from scipy.io import loadmat




class AnalysisThread(QtCore.QThread):

    finished = QtCore.Signal(dict) #pass back dict of results
    progress = QtCore.Signal(float) #pass float describing progress
    pbartext = QtCore.Signal(str) #progress bar text

    def __init__(self, queue, finished_callback, parent=None):
        QtCore.QThread.__init__(self,parent)
        self.finished.connect(finished_callback)
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


        processedInput, processedInputTimes, \
        processedInventory, processedInventoryTimes, \
        processedOutput, processedOutputTimes = Preprocessing.FormatInput(
                                                rawInput = AnalysisData.rawInput,
                                                rawInventory = AnalysisData.rawInventory,
                                                rawOutput = AnalysisData.rawOutput,
                                                rawInputTimes = AnalysisData.rawInputTimes,
                                                rawInventoryTimes = AnalysisData.rawInventoryTimes,
                                                rawOutputTimes = AnalysisData.rawOutputTimes,
                                                dataOffset = AnalysisData.offset,
                                                GUIObject = self,
                                                IT = IT)


        AnalysisData.ErrorMatrix = StatsPanelOps.getGUIErrorVals(self.parent,
                                                                len(processedInput),
                                                                len(processedInventory),
                                                                len(processedOutput),
                                                                argz['GLoc'])

        nInputs = len(processedInput)
        nInventories =  len(processedInventory)


        if argz['doError'] == 1:
            

            self.pbartext.emit('Processing: input errors')
            AnalysisData.inputAppliedError = Preprocessing.SimErrors(rawData = processedInput, 
                                                                    ErrorMatrix =  AnalysisData.ErrorMatrix[:nInputs,], 
                                                                    iterations = argz['IT'],
                                                                    GUIObject = self)

            self.pbartext.emit('Processing: inventory errors')
            AnalysisData.inventoryAppliedError = Preprocessing.SimErrors(rawData = processedInventory,
                                                                        ErrorMatrix =  AnalysisData.ErrorMatrix[nInputs:nInventories+nInputs], 
                                                                        iterations = argz['IT'],
                                                                        GUIObject = self)

            self.pbartext.emit('Processing: output errors')
            AnalysisData.outputAppliedError = Preprocessing.SimErrors(rawData = processedOutput, 
                                                                    ErrorMatrix =  AnalysisData.ErrorMatrix[nInputs+nInventories:,], 
                                                                    iterations = argz['IT'],
                                                                    GUIObject = self)



        else:
          #if no sim error, use what user supplied
            

            AnalysisData.inputAppliedError = processedInput
            AnalysisData.inventoryAppliedError = processedInventory
            AnalysisData.outputAppliedError = processedOutput

        # Here we check to see if either the test itself is requested
        # or if any of the dependency calculations are requested
        # for example, SITMUF required the MUF sequence
        # rather than forcing these options in the GUI (old behavior)
        # we just enforce it here on the backend
        # it's debatable which behavior is the more intuitive


        if (argz['doMUF'] or argz['doCUMUF'] or argz['doSITMUF'] or argz['doPage']):
            self.pbartext.emit('Processing: '+GUIparams.labels['Box12L'])


            AnalysisData.MUF = Tests.MUF(inputAppliedError = AnalysisData.inputAppliedError,
                                        inventoryAppliedError= AnalysisData.inventoryAppliedError,
                                        outputAppliedError = AnalysisData.outputAppliedError,
                                        processedInputTimes = processedInputTimes,
                                        processedInventoryTimes = processedInventoryTimes,
                                        processedOutputTimes = processedOutputTimes,
                                        MBP = argz['MBP'],
                                        GUIObject = self,
                                        GUIparams = GUIparams)



        if argz['doAI'] or argz['doSEIDAI']:   
            self.pbartext.emit('Processing: '+GUIparams.labels['Box13L'])  

            AnalysisData.AI = Tests.ActiveInventory(inputAppliedError = AnalysisData.inputAppliedError,
                    inventoryAppliedError= AnalysisData.inventoryAppliedError,
                    outputAppliedError = AnalysisData.outputAppliedError,
                    processedInputTimes = processedInputTimes,
                    processedInventoryTimes = processedInventoryTimes,
                    processedOutputTimes = processedOutputTimes,
                    MBP = argz['MBP'],
                    GUIObject = self,
                    GUIparams = GUIparams)



        if argz['doCUMUF']:
            self.pbartext.emit('Processing: '+GUIparams.labels['Box14L'])

            AnalysisData.CUMUF = Tests.CUMUF(AnalysisData.MUF,
                                            GUIObject = self)



        if argz['doSEID'] or argz['doSEIDAI']:
            self.pbartext.emit('Processing: '+GUIparams.labels['Box15L'])

            
            AnalysisData.SEMUF, \
            AnalysisData.SEMUFContribR, \
            AnalysisData.SEMUFContribS, \
            AnalysisData.SEMUFContribI = Tests.SEMUF(inputAppliedError = AnalysisData.inputAppliedError,
                                                    inventoryAppliedError= AnalysisData.inventoryAppliedError,
                                                    outputAppliedError = AnalysisData.outputAppliedError,
                                                    processedInputTimes = processedInputTimes,
                                                    processedInventoryTimes = processedInventoryTimes,
                                                    processedOutputTimes = processedOutputTimes,
                                                    MBP = argz['MBP'],
                                                    ErrorMatrix = AnalysisData.ErrorMatrix,
                                                    GUIObject = self)

        if argz['doSEIDAI']:
            self.pbartext.emit('Processing: '+GUIparams.labels['Box16L'])

            AnalysisData.SEMUFAI, \
            AnalysisData.SEMUFAIContribR, \
            AnalysisData.SEMUFAIContribS = Tests.SEMUFAI(AI = AnalysisData.AI,
                                                         SEMUF = AnalysisData.SEMUF, 
                                                         SEMUFContribR = AnalysisData.SEMUFContribR,
                                                         SEMUFContribS = AnalysisData.SEMUFContribS, 
                                                         MBP = argz['MBP'])

        if (argz['doSITMUF'] or argz['doPage']):
            self.pbartext.emit('Processing: '+GUIparams.labels['Box17L'])


            AnalysisData.SITMUF = Tests.SITMUF(inputAppliedError = AnalysisData.inputAppliedError,
                                                                inventoryAppliedError= AnalysisData.inventoryAppliedError,
                                                                outputAppliedError = AnalysisData.outputAppliedError,
                                                                processedInputTimes = processedInputTimes,
                                                                processedInventoryTimes = processedInventoryTimes,
                                                                processedOutputTimes = processedOutputTimes,
                                                                ErrorMatrix = AnalysisData.ErrorMatrix,
                                                                MBP = argz['MBP'],
                                                                MUF = AnalysisData.MUF,
                                                                GUIObject = self)  

        if argz['doPage']:
            self.pbartext.emit('Processing: '+GUIparams.labels['Box18L'])

            MBPs = Aux.getMBPs(processedInputTimes,processedInventoryTimes,processedOutputTimes,argz['MBP'])

            AnalysisData.Page = Tests.PageTrendTest(AnalysisData.SITMUF,argz['MBP'],MBPs,GUIObject = self)

        self.pbartext.emit('Ready')
        self.progress.emit(100)
        self.finished.emit((AnalysisData, argz['doMUF'], argz['doAI'], argz['doCUMUF'],
                           argz['doSEID'], argz['doSEIDAI'], argz['doSITMUF'], argz['doPage']))
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

    def __init__(self, queue, finished_callback, parent=None):
        QtCore.QThread.__init__(self,parent)
        self.finished.connect(finished_callback)
        self.queue = queue
        self.parent = parent

    def run(self):
        argz = self.queue.get()

        if argz is None:
            return

        AnalysisData = argz['AnalysisData']
        GUIparams = argz['GUIparams']
        AnalysisData, GUIparams = GeneralOps.getSceneData(self.parent,AnalysisData,GUIparams)

        self.finished.emit((AnalysisData,GUIparams))


class getExtData(QtCore.QThread):
    finished = QtCore.Signal(dict)
    progress = QtCore.Signal(float)
    pbartext = QtCore.Signal(str)

    def __init__(self, queue, finished_callback, parent=None):
        QtCore.QThread.__init__(self,parent)
        self.finished.connect(finished_callback)
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
                for j in range(len(z['in']['data'].squeeze())):
                    indat.append(z['in']['data'].squeeze()[j].squeeze())
                    inTdat.append(z['in']['time'].squeeze()[j].squeeze())

            for i in range(len(invfiles)):
                z = loadmat(invfiles[i])
                for j in range(len(z['invn']['data'].squeeze())):
                    invdat.append(z['invn']['data'].squeeze()[j].squeeze())
                    invTdat.append(z['invn']['time'].squeeze()[j].squeeze())

            for i in range(len(outfiles)):
                z = loadmat(outfiles[i])
                for j in range(len(z['outn']['data'].squeeze())):
                    outdat.append(z['outn']['data'].squeeze()[j].squeeze())
                    outTdat.append(z['outn']['time'].squeeze()[j].squeeze())    


        elif fileext == '.npz':
            None
        
        else:
            return
        
        self.finished.emit((AnalysisData,GUIparams,Wizard,self.parent, indat, inTdat, invdat, invTdat, outdat, outTdat))

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
