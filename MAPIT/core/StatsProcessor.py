import ray
import numpy as np
from tqdm import tqdm
from MAPIT.core import StatsTests as Tests
from MAPIT.core import Preprocessing, AuxFunctions
import os
import logging
os.environ["RAY_verbose_spill_logs"] = "0"

import MAPIT

def to_iterator(obj_ids):
    while obj_ids:
        done, obj_ids = ray.wait(obj_ids)
        yield 0

class MBArea(object):
    """  

        Object representing a material balance area.

        Args:
            rawInput (list of ndarrays): Raw input data for the material balance area, list of 2D ndarrays. Each entry in the list should correspond to a different location and the shape of ndarray in the list should be [MxN] where M is the sample dimension (number of samples) and N is the isotopic dimension, if applicable. If only considering one isotope, each ndarray in the rawData list should be [Mx1]. It is expected that M will have rate units (i.e., kg/hr) as this quantity will be integrated.

            rawInventory (list of ndarrays): Raw inventory data for the material balance area, list of 2D ndarrays. Shape structure is the same as ``rawInput``. It is expected that M will have mass units (i.e., kg) as this quantity will not be integrated.

            rawOutput (list of ndarrays): Raw output data for the material balance area, list of 2D ndarrays. Shape structure is the same as ``rawInput``. It is expected that M will have rate units (i.e., kg/hr) as this quantity will be integrated.

            rawInputTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of input locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(rawInputTimes)` and the shape of each list entry (ndarray) should be the same as for `rawInput`. Each entry in each ndarray should correspond to a timestamp indicating when the value was taken. 

            rawInventoryTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of inventory locations. Shape structure is the same as ``rawInputTimes``.

            rawOutputTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of output locations. Shape structure is the same as ``rawInputTimes``.

            inputErrorMatrix (ndarray): 2D ndarray of shape [Mx2] describing the relative standard deviation to apply to ``rawInput``. M sample dimension in each input array and should be identical to M described in  ``rawInput``. The second dimension (e.g., 2) refers to the random and systematic error respectively such that ``ErrorMatrix[0,0]`` refers to the random relative standard deviation of the first location and ``ErrorMatrix[0,1]`` refers to the systematic relative standard deviation. 

            inventoryErrorMatrix (ndarray): 2D ndarray with the same shape structure as ``inputErrorMatrix`` describing errors to apply to ``rawInventory``.

            outputErrorMatrix (ndarray): 2D ndarray with the same shape structure as ``inputErrorMatrix`` describing errors to apply to ``rawOutput``.

            mbaTime (int): The material balance period. 

            iterations (int, default=1): Number of statistical realizations.

            doPar(bool, default=False): Controls the use of parallel processing provided by Ray. If used, progress can be monitored on a local dashboard that is accessible at http://127.0.0.1:8265. 

            ncpu(int, default=1): The number of CPUs to use if parallel processing is enabled.

            nbatch(int, default=1): The number of batches to process for each job. 

            GUIObject(object, default=None): An object containing MAPIT GUI parameters. Only used interally by the GUI.
            
            dataOffset(int, default=0): Offset to apply to the data. If specified, data before this value in time will be removed. For example, if dataOffset=273, then any data with a corresponding time before 273 will be excluded from calculations.

            rebaseToZero(bool, default=False): Used in conjunction with dataOffset. If true, then times after ``dataOffset`` will be rebased to start at zero (i.e., if dataOffset=273, then t=274 will be rebased to be t=1).

            doTQDM(bool, default=True): Boolean used to control progress bar of calculations.

        Returns:
            None



    """
    def __init__(self,rawInput, rawInventory, rawOutput, rawInputTimes, rawInventoryTimes, rawOutputTimes,
                 inputErrorMatrix, inventoryErrorMatrix, outputErrorMatrix, mbaTime, iterations=1, dopar=False, ncpu=1, nbatch=1,
                 GUIObject=None,dataOffset=0,rebaseToZero=True, doTQDM=True):
        

        # make sure data is present
        assert len(rawInput) > 0, "Input data missing"
        assert len(rawInputTimes) > 0, "Input data missing"

        assert len(rawInventory) > 0, "Inventory data missing"
        assert len(rawInventoryTimes) > 0, "Inventory data missing"

        assert len(rawOutput) > 0, "Output data missing"
        assert len(rawOutputTimes) > 0, "Output data missing"


        self.inputErrorMatrix = inputErrorMatrix
        self.inventoryErrorMatrix = inventoryErrorMatrix
        self.outputErrorMatrix = outputErrorMatrix
        self.totalErrorMatrix = np.vstack((inputErrorMatrix,inventoryErrorMatrix,outputErrorMatrix))
        self.mbaTime = mbaTime
        self.IT = iterations
        self.dopar = dopar
        self.ncpu = ncpu
        self.nbatch = nbatch
        self.doTQDM = doTQDM
        self.GUIObject = GUIObject

        self.processedInput, self.processedInputTimes, \
        self.processedInventory, self.processedInventoryTimes, \
        self.processedOutput, self.processedOutputTimes = Preprocessing.FormatInput(
                                                    rawInput = rawInput,
                                                    rawInventory = rawInventory,
                                                    rawOutput = rawOutput,
                                                    rawInputTimes = rawInputTimes,
                                                    rawInventoryTimes = rawInventoryTimes,
                                                    rawOutputTimes = rawOutputTimes,
                                                    GUIObject = GUIObject,
                                                    IT = iterations,
                                                    dataOffset = dataOffset,
                                                    rebaseToZero = rebaseToZero)
        
        self.inputAppliedError = None
        self.inventoryAppliedError = None
        self.outputAppliedError = None

        if self.dopar:
            ray.init(num_cpus=ncpu,ignore_reinit_error=True,runtime_env={"py_modules": [MAPIT], "excludes": ["/data/","/.git/"]},logging_level=logging.ERROR)

    
    def _checkForErrorData(self):
        if (self.inputAppliedError == None or self.inventoryAppliedError == None or self.outputAppliedError == None):
            if not self.dopar:
                self._recalcBatchSize()
            self.calcErrors()
                


    #performed in case batch size is changed after
    #initaliation
    def _recalcBatchSize(self):
        if self.dopar == False:
            return
        self.ntasks = np.floor(self.IT/self.nbatch).astype(np.int32) 
        if np.remainder(self.IT,self.nbatch) !=0: self.ntasks += 1
    
    def calcMUF(self):

        """
        
            Calculates MUF using ``StatsTests.MUF``. The result is returned and stored as an attribute after the calculation is complete. 
            
            Returns:
                ndarray: MUF sequence with shape :math:`[n,j]` where :math:`n` length equal to the maximum time based on the number of material balances that could be constructed given the user provided ``mbaTime`` and number of samples in the input data. :math:`j` is the number of iterations given as input. The term :math:`n` is calculated by finding the minimum of each of the provided input times.                 
        
                For example:

                .. highlight:: python
                .. code-block:: python

                    import numpy as np

                    time1[-1] = 400
                    time2[-1] = 300
                    time3[-1] = 800

                    n = np.floor(
                            np.min(
                            (time1,time2,time3)))

                .. TIP::

                    MAPIT doesn't assume that time series provided have zero value if unspecified. For example, if a time series starts at t=800, it is assumed that values before t=800 are undefined so MUF cannot be calculated before t=800. The user can modify input data such that values before t=800 are present, but zero, if that assumption is valid. 
        
        """

        self._recalcBatchSize()
        self._checkForErrorData()
        # if not parallel then do sequential processing
        if not self.dopar:
            
            # Do the MUF calculation
            MUF = Tests.MUF(inputAppliedError = self.inputAppliedError,
                            inventoryAppliedError= self.inventoryAppliedError,
                            outputAppliedError = self.outputAppliedError,
                            processedInputTimes = self.processedInputTimes,
                            processedInventoryTimes = self.processedInventoryTimes,
                            processedOutputTimes = self.processedOutputTimes,
                            MBP = self.mbaTime,
                            doTQDM = self.doTQDM,
                            ispar = False,
                            GUIObject = self.GUIObject)
            
        # if parallel
        else:
            # helpers for batching data
            idx1=0
            idx2=0

            # define the remote function
            gfunc = ray.remote(Tests.MUF)

            # setup the progressbar if necessary
            # NOTE: this is a crude progress bar
            # for large jobs, recommend using the
            # ray dashboard instead
            # NOTE: performance of the progressbar
            # is better in console


            tasklist = []

            for i in range(self.ntasks):
                idx2 = idx1 + self.nbatch

                # batch the data into ntasks of nbatch size
                inslice = self._parIterSlicer(idx1,idx2,'inputAppliedError')
                invslice = self._parIterSlicer(idx1,idx2,'inventoryAppliedError')
                outslice = self._parIterSlicer(idx1,idx2,'outputAppliedError')

                idx1 += self.nbatch

                # add the tasks
                tasklist.append(gfunc.remote(
                    inputAppliedError = inslice,
                    inventoryAppliedError= invslice,
                    outputAppliedError = outslice,
                    processedInputTimes = self.processedInputTimes,
                    processedInventoryTimes = self.processedInventoryTimes,
                    processedOutputTimes = self.processedOutputTimes,
                    MBP = self.mbaTime,
                    doTQDM=self.doTQDM,
                    ispar = True))


            if self.doTQDM:
                for x in tqdm(to_iterator(tasklist),total=len(tasklist),desc="MUF", leave=True, 
                    bar_format = "{desc:10}: {percentage:3.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=85):
                    pass
            
            res = ray.get(tasklist)
            # assemble an array of results
            for i in range(self.ntasks):
                if i == 0:
                    MUF = res[i]
                else:
                    MUF = np.vstack((MUF,res[i]))

        # assign the MUF calculation to the 
        # MBArea class for later use or
        # retrieval 
        self.MUF = MUF

        return MUF
    
    # NOTE: CUMUF has no parallel
    # implementation since it's already
    # very lightweight
    def calcCUMUF(self):
        """
        
            Calculates cumulative MUF using ``StatsTests.CUMUF``. The result is returned and stored as an attribute after the calculation is complete. Automatically calculates MUF if not present as an attribute.

            Returns:
                ndarray: CUMUF sequence with identical shape to the input MUF.
        
        """
        if not hasattr(self, "MUF"):
            self.calcMUF()
        else:
            if self.MUF is None:
                self.calcMUF()

        self.CUMUF = Tests.CUMUF(MUF=self.MUF,ispar=self.dopar, GUIObject=self.GUIObject)
        return self.CUMUF
    
    def calcActiveInventory(self):

        self._recalcBatchSize()
        self._checkForErrorData()


        # if not parallel then do sequential processing
        if not self.dopar:

            # Do the MUF calculation
            AI = Tests.ActiveInventory(inputAppliedError = self.inputAppliedError,
                            inventoryAppliedError= self.inventoryAppliedError,
                            outputAppliedError = self.outputAppliedError,
                            processedInputTimes = self.processedInputTimes,
                            processedInventoryTimes = self.processedInventoryTimes,
                            processedOutputTimes = self.processedOutputTimes,
                            MBP = self.mbaTime,
                            doTQDM = self.doTQDM,
                            ispar = False,
                            GUIObject = self.GUIObject)
            
        # if parallel
        else:
            # helpers for batching data
            idx1=0
            idx2=0

            # define the remote function
            gfunc = ray.remote(Tests.ActiveInventory)

            # setup the progressbar if necessary
            # NOTE: this is a crude progress bar
            # for large jobs, recommend using the
            # ray dashboard instead
            # NOTE: performance of the progressbar
            # is better in console


            tasklist = []

            for i in range(self.ntasks):
                idx2 = idx1 + self.nbatch

                # batch the data into ntasks of nbatch size
                inslice = self._parIterSlicer(idx1,idx2,'inputAppliedError')
                invslice = self._parIterSlicer(idx1,idx2,'inventoryAppliedError')
                outslice = self._parIterSlicer(idx1,idx2,'outputAppliedError')

                idx1 += self.nbatch

                # add the tasks
                tasklist.append(gfunc.remote(
                    inputAppliedError = inslice,
                    inventoryAppliedError= invslice,
                    outputAppliedError = outslice,
                    processedInputTimes = self.processedInputTimes,
                    processedInventoryTimes = self.processedInventoryTimes,
                    processedOutputTimes = self.processedOutputTimes,
                    MBP = self.mbaTime,
                    doTQDM=self.doTQDM,
                    ispar = True))

            # print the progress until all tasks
            # are completed 


            # do the tasks
            if self.doTQDM:
                for x in tqdm(to_iterator(tasklist),total=len(tasklist),desc="Active Inv", leave=True, 
                                bar_format = "{desc:10}: {percentage:3.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=85):
                    pass

            res = ray.get(tasklist)
            # assemble an array of results
            for i in range(self.ntasks):
                if i == 0:
                    AI = res[i]
                else:
                    AI = np.vstack((AI,res[i]))

        # assign the MUF calculation to the 
        # MBArea class for later use or
        # retrieval 
        self.AI = AI

        return AI
    
    def calcSEMUF(self):
        """
        
            Calculates :math:`\sigma` MUF using ``StatsTests.SEMUF``. The result is returned and stored as an attribute after the calculation is complete. Automatically calculates MUF if not present as an attribute.

            Returns:

                tuple (ndarray, ndarray, ndarray, ndarray):

                * SEID (ndarray): sequence with shape :math:`[n,j,1]` where :math:`n` is the number of material balances and :math:`j` is the number of iterations given as input. The term :math:`n` is calculated by finding the minimum of each of the provided input times. 

                * SEMUFContribR (ndarray): the random contribution to the overall SEMUF with shape :math:`[j,l,n]` where :math:`j` is the number of iterations given as input, :math:`l` is the total number of locations stacked in the order [inputs, inventories, outputs] and :math:`n` is the number of material balances. 

                * SEMUFContribS (ndarray): the systematic contribution to the overall SEMUF with shape :math:`[j,l,n]` where :math:`j` is the number of iterations given as input, :math:`l` is the total number of locations stacked in the order [inputs, inventories, outputs] and :math:`n` is the number of material balances. 

                * ObservedValues (ndarray): the observed values used to calculate SEMUF with shape :math:`[j,l,n]` where :math:`j` is the number of iterations given as input, :math:`l` is the total number of locations stacked in the order [inputs, inventories, outputs] and :math:`n` is the number of material balances. 
        
        """

        self._recalcBatchSize()
        self._checkForErrorData()

        if not hasattr(self, "MUF"):
            self.calcMUF()
        else:
            if self.MUF is None:
                self.calcMUF()


        # if not parallel then do sequential processing
        if not self.dopar:

            # Do the MUF calculation
            (SEMUF, 
            SEMUF_contribR, 
            SEMUF_contribS, 
            SEMUF_inv) = Tests.SEMUF(inputAppliedError = self.inputAppliedError,
                            inventoryAppliedError= self.inventoryAppliedError,
                            outputAppliedError = self.outputAppliedError,
                            processedInputTimes = self.processedInputTimes,
                            processedInventoryTimes = self.processedInventoryTimes,
                            processedOutputTimes = self.processedOutputTimes,
                            MBP = self.mbaTime,
                            ErrorMatrix = self.totalErrorMatrix,
                            doTQDM = self.doTQDM,
                            ispar = False,
                            GUIObject = self.GUIObject)
            
        # if parallel
        else:
            # helpers for batching data
            idx1=0
            idx2=0

            # define the remote function
            gfunc = ray.remote(Tests.SEMUF)

            # setup the progressbar if necessary
            # NOTE: this is a crude progress bar
            # for large jobs, recommend using the
            # ray dashboard instead
            # NOTE: performance of the progressbar
            # is better in console


            tasklist = []

            for i in range(self.ntasks):
                idx2 = idx1 + self.nbatch

                # batch the data into ntasks of nbatch size
                inslice = self._parIterSlicer(idx1,idx2,'inputAppliedError')
                invslice = self._parIterSlicer(idx1,idx2,'inventoryAppliedError')
                outslice = self._parIterSlicer(idx1,idx2,'outputAppliedError')

                idx1 += self.nbatch

                # add the tasks
                tasklist.append(gfunc.remote(
                    inputAppliedError = inslice,
                    inventoryAppliedError= invslice,
                    outputAppliedError = outslice,
                    processedInputTimes = self.processedInputTimes,
                    processedInventoryTimes = self.processedInventoryTimes,
                    processedOutputTimes = self.processedOutputTimes,
                    MBP = self.mbaTime,
                    ErrorMatrix = self.totalErrorMatrix,
                    doTQDM=False, #self.doTQDM
                    ispar = True))



            # do the tasks
            if self.doTQDM:
                for x in tqdm(to_iterator(tasklist),total=len(tasklist),desc="Sigma MUF", leave=True, 
                                bar_format = "{desc:10}: {percentage:3.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=85):
                    pass
            res = ray.get(tasklist)
            # TODO: check SEMUF for which vars are which since multiple returned
            # assemble an array of results
            for i in range(self.ntasks):
                if i == 0:
                    SEMUF = res[i][0]
                    SEMUF_contribR = res[i][1]
                    SEMUF_contribS = res[i][2]
                    SEMUF_inv = res[i][3]
                else:
                    SEMUF = np.vstack((SEMUF,res[i][0]))
                    SEMUF_contribR = np.vstack((SEMUF_contribR,res[i][1]))
                    SEMUF_contribS = np.vstack((SEMUF_contribS,res[i][2]))
                    SEMUF_inv = np.vstack((SEMUF_inv,res[i][3]))

        # assign the MUF calculation to the 
        # MBArea class for later use or
        # retrieval 
        self.SEMUF = SEMUF
        self.SEMUF_contribR = SEMUF_contribR
        self.SEMUF_contribS = SEMUF_contribS
        self.SEMUF_inv = SEMUF_inv

        return (self.SEMUF, self.SEMUF_contribR, self.SEMUF_contribS, self.SEMUF_inv)

    def calcSEMUFAI(self):

        if not hasattr(self, "AI"):
            self.calcActiveInventory()
        else:
            if self.MUF is None:
                self.calcMUF()

        (self.SEMUFAI, self.SEMUFAI_contribR, self.SEMUFAI_contribS) = Tests.SEMUFAI(self.AI,
                                                                                      self.SEMUF, 
                                                                                      self.SEMUF_contribR,
                                                                                      self.SEMUF_contribS,
                                                                                      self.mbaTime)
        return (self.SEMUFAI, self.SEMUFAI_contribR, self.SEMUFAI_contribS)
    
    def calcSITMUF(self):

        """
        

            Calculates SITMUF using ``StatsTests.SITMUF``. The result is returned and stored as an attribute after the calculation is complete. Automatically calculates MUF if not present as an attribute.


            Returns:
                ndarray: SITMUF sequence with shape :math:`[n,j]` where :math:`n` length equal to the maximum time based on the number of material balances that could be constructed given the user provided MBP and number of samples in the input data and :math:`j` is the number of iterations given as input. As is the case with MUF, the term :math:`n` is calculated by finding the minimum of each of the provided input times. 

        
        """
        
        self._recalcBatchSize()
        self._checkForErrorData()

        if not hasattr(self, "MUF"):
            self.calcMUF()
        else:
            if self.MUF is None:
                self.calcMUF()

        

        if not self.dopar:
            self.SITMUF = Tests.SITMUF(inputAppliedError = self.inputAppliedError,
                            inventoryAppliedError= self.inventoryAppliedError,
                            outputAppliedError = self.outputAppliedError,
                            processedInputTimes = self.processedInputTimes,
                            processedInventoryTimes = self.processedInventoryTimes,
                            processedOutputTimes = self.processedOutputTimes,
                            MBP = self.mbaTime,
                            ErrorMatrix = self.totalErrorMatrix,
                            MUF = self.MUF,
                            doTQDM = self.doTQDM,
                            ispar = False,
                            GUIObject = self.GUIObject)
        else:
            # helpers for batching data
            idx1=0
            idx2=0

            # define the remote function
            gfunc = ray.remote(Tests.SITMUF)


            tasklist = []
            for i in range(self.ntasks):
                idx2 = idx1 + self.nbatch

                # batch the data into ntasks of nbatch size
                inslice = self._parIterSlicer(idx1,idx2,'inputAppliedError')
                invslice = self._parIterSlicer(idx1,idx2,'inventoryAppliedError')
                outslice = self._parIterSlicer(idx1,idx2,'outputAppliedError')
                MUFslice = self._parIterSlicer(idx1,idx2,'MUF')

                idx1 += self.nbatch

                # add the tasks
                tasklist.append(gfunc.remote(
                    inputAppliedError = inslice,
                    inventoryAppliedError= invslice,
                    outputAppliedError = outslice,
                    processedInputTimes = self.processedInputTimes,
                    processedInventoryTimes = self.processedInventoryTimes,
                    processedOutputTimes = self.processedOutputTimes,
                    MBP = self.mbaTime,
                    MUF = MUFslice,
                    ErrorMatrix = self.totalErrorMatrix,
                    doTQDM=self.doTQDM,
                    ispar = True))

            # print the progress until all tasks
            # are completed 


            # do the tasks
            if self.doTQDM:
                for x in tqdm(to_iterator(tasklist),total=len(tasklist),desc="SITMUF", leave=True, 
                                bar_format = "{desc:10}: {percentage:3.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=85):
                    pass
            
            res = ray.get(tasklist)
            for i in range(self.ntasks):
                if i == 0:
                    self.SITMUF = res[i]
                else:
                    self.SITMUF = np.vstack((self.SITMUF,res[i]))


        return self.SITMUF
        
    def calcPageTT(self):

        """
        
            Calculates Page's trend test on SITMUF using ``StatsTests.PageTrendTest``. The result is returned and stored as an attribute after the calculation is complete. Automatically calculates SITMUF if not present as an attribute.

            Returns:
                ndarray: The results of the trend test which has shape :math:`[m,n]`. 

        
        """

        if not hasattr(self, "SITMUF"):
            self.calcSITMUF()
        else:
            if self.SITMUF is None:
                self.calcSITMUF()

        MBPs = AuxFunctions.getMBPs(self.processedInputTimes,self.processedInventoryTimes,self.processedOutputTimes,self.mbaTime)
        self.Page = Tests.PageTrendTest(self.SITMUF,self.mbaTime,MBPs,doTQDM=False, GUIObject=self.GUIObject)
        return self.Page
    

    def _parIterSlicer(self, I1, I2, attr):
        dat = getattr(self,attr)
        outdat = []
        if isinstance(dat,list):
            for i in range(len(dat)):
                outdat.append(dat[i][I1:I2,])
        else:
            outdat = dat[I1:I2]
        
        return outdat
            
    #bc list
    def _parErrorConcat(self,newdat,attstr):

        olddat = getattr(self,attstr)

        catdat = []


        for i in range(len(olddat)):
            catdat.append(np.concatenate((olddat[i],newdat[i]),axis=0))
        

        setattr(self,attstr,catdat)

        db = 0
    
    def calcErrors(self):
        """
        
            Function that applies the specified error matrices to the supplied raw data and stores the results as object attributes. Uses the ``Preprocessing.SimErrors`` implementation. 

            Returns:
                None

        
        """
        if not self.dopar:
            self.inputAppliedError = Preprocessing.SimErrors(
                                rawData = self.processedInput, 
                                ErrorMatrix =  self.inputErrorMatrix, 
                                iterations = self.IT,
                                GUIObject = self.GUIObject)

            self.inventoryAppliedError = Preprocessing.SimErrors(
                                        rawData = self.processedInventory,
                                        ErrorMatrix =  self.inventoryErrorMatrix, 
                                        iterations = self.IT,
                                        GUIObject = self.GUIObject)


            self.outputAppliedError = Preprocessing.SimErrors(
                                        rawData = self.processedOutput, 
                                        ErrorMatrix =  self.outputErrorMatrix, 
                                        iterations = self.IT,
                                        GUIObject = self.GUIObject)
        else:
            gfunc = ray.remote(Preprocessing.SimErrors)

            
            
            tasklist = []
            for i in range(self.ntasks):
                tasklist.append(gfunc.remote(
                            rawData = self.processedInput, 
                            ErrorMatrix =  self.inputErrorMatrix, 
                            iterations = self.nbatch,
                            batchSize = self.nbatch,
                            dopar=True))

                tasklist.append(gfunc.remote(
                            rawData = self.processedInventory, 
                            ErrorMatrix =  self.inventoryErrorMatrix, 
                            iterations = self.nbatch,
                            batchSize = self.nbatch,
                            dopar=True))

                tasklist.append(gfunc.remote(
                            rawData = self.processedOutput, 
                            ErrorMatrix =  self.outputErrorMatrix, 
                            iterations = self.nbatch,
                            batchSize = self.nbatch,
                            dopar=True))

            # kinda cursed
            # since the tasks aren't ordered by 
            # error type we have to cycle
            # throught the types in the order
            # [input, inventory, output]
            # so the rotation array helps determine
            # which task is which error type


            
            # order matters so do the pbar
            # then grab all the results at once,
            # in order
            if self.doTQDM:
                for x in tqdm(to_iterator(tasklist),total=len(tasklist),desc="Error Prop", leave=True, 
                               bar_format = "{desc:10}: {percentage:3.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=85):
                    pass

            res = ray.get(tasklist)

            # getting the results can be
            # quite slow depending
            # on the cpu/batch/iteration
            # configuration and dataset size
            # the use of lists is maximized
            # since append is O(1) versus
            # concatenate which is not O
            # still, converting lists
            # to array can be slow 

            

            rotation = np.array([1,0,0])
            inps = []
            invs = []
            outs = []


            for i in range(self.ntasks*3):
                match np.argmax(rotation):
                    case 0:
                        inps.append(res[i])
                        rotation = np.array([0,1,0])
                    case 1:
                        invs.append(res[i])
                        rotation = np.array([0,0,1])
                    case 2: 
                        outs.append(res[i])
                        rotation = np.array([1,0,0])
            inps2 = []
            invs2 = []
            outs2 = []

            for i in range(len(inps[0])):
                L = []
                for j in range(len(inps)):
                    L.append(inps[j][i])
                inps2.append(L)

            for i in range(len(invs[0])):
                L = []
                for j in range(len(invs)):
                    L.append(invs[j][i])
                invs2.append(L)
            
            for i in range(len(outs[0])):
                L = []
                for j in range(len(outs)):
                    L.append(outs[j][i])
                outs2.append(L)

            self.inputAppliedError = []
            self.inventoryAppliedError = []
            self.outputAppliedError = []


            for i in range(len(inps2)):
                self.inputAppliedError.append(np.vstack(inps2[i]))


            for i in range(len(invs2)):
                self.inventoryAppliedError.append(np.vstack(invs2[i]))


            for i in range(len(outs2)):
                self.outputAppliedError.append(np.vstack(outs2[i]))




