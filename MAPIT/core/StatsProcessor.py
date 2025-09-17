import concurrent
from functools import partial
import numpy as np
from MAPIT.core import StatsTests as Tests
from MAPIT.core import Preprocessing, AuxFunctions
from itertools import chain
from alive_progress import alive_bar
from alive_progress.animations.spinners import frame_spinner_factory
from yaspin import yaspin


import MAPIT


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Reset to default color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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


            inputTypes (list of strings): Defines the type of input. This should be a list of strings that is the same length as the number of input locations. The strings should be one of the following: `'discrete'` or `'continuous'`.

            outputTypes (list of strings): Defines the type of output. This should be a list of strings that is the same length as the number of output locations. The strings should be one of the following: `'discrete'` or `'continuous'`. 

            inputCalibrationPeriod (list of float, default=None): List of floats of length M describing the calibration period for each location in `rawInput`. If not supplied, no recalibration is performed and it is assumed a single calibration period is applied to the length of the data.

            inventoryCalibrationPeriod (list of float, default=None): List of floats of length M describing the calibration period for each location in `rawInventory`. If not supplied, no recalibration is performed and it is assumed a single calibration period is applied to the length of the data.

            outputCalibrationPeriod (list of float, default=None): List of floats of length M describing the calibration period for each location in `rawOutput`. If not supplied, no recalibration is performed and it is assumed a single calibration period is applied to the length of the data.

            iterations (int, default=1): Number of statistical realizations.

            doPar(bool, default=False): Controls the use of parallel processing provided by concurrent.futures. 

            ncpu(int, default=1): The number of CPUs to use if parallel processing is enabled.

            nbatch(int, default=1): The number of batches to process for each job. 

            GUIObject(object, default=None): An object containing MAPIT GUI parameters. Only used interally by the GUI.
            
            dataOffset(int, default=0): Offset to apply to the data. If specified, data before this value in time will be removed. For example, if dataOffset=273, then any data with a corresponding time before 273 will be excluded from calculations.

            rebaseToZero(bool, default=False): Used in conjunction with dataOffset. If true, then times after ``dataOffset`` will be rebased to start at zero (i.e., if dataOffset=273, then t=274 will be rebased to be t=1).

            doPbar(bool, default=True): Boolean used to control progress bar of calculations.

        Returns:
            None



    """
    def __init__(self,rawInput, rawInventory, rawOutput, rawInputTimes, rawInventoryTimes, rawOutputTimes,
                 inputErrorMatrix, inventoryErrorMatrix, outputErrorMatrix, mbaTime, inputTypes, outputTypes, inputCalibrationPeriod=None, inventoryCalibrationPeriod=None,
                 outputCalibrationPeriod=None, iterations=1, dopar=False, ncpu=1, nbatch=1,
                 GUIObject=None,dataOffset=0,rebaseToZero=True, doPbar=True, ):
        

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
        self.doPbar = doPbar
        self.GUIObject = GUIObject
        self.keepCovMat = False
        self.covmatrix = None

        self.inputCalibrationPeriod = inputCalibrationPeriod
        self.inventoryCalibrationPeriod = inventoryCalibrationPeriod
        self.outputCalibrationPeriod = outputCalibrationPeriod

        # check to see if data format is provided
        # valid types are 'continuous' and 'discrete'
        if inputTypes is None:
            self.inputTypes  = ['continuous']*len(rawInput)
        else:
            self.inputTypes = inputTypes       


        if outputTypes is None:
            self.outputTypes  = ['continuous']*len(rawOutput)
        else:
            self.outputTypes = outputTypes


        self.processedInput, self.processedInputTimes, \
        self.processedInventory, self.processedInventoryTimes, \
        self.processedOutput, self.processedOutputTimes, idxRemoved = Preprocessing.FormatInput(
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
        
        if len(idxRemoved[0]) != 0:
            idxs = idxRemoved[0]
            self.inputCalibrationPeriod = [v for i, v in enumerate( self.inputCalibrationPeriod) if i not in idxs]
            self.inputTypes = [v for i, v in enumerate(self.inputTypes) if i not in idxs]

        if len(idxRemoved[1]) != 0:
            idxs = idxRemoved[1]
            self.inventoryCalibrationPeriod = [v for i, v in enumerate( self.inventoryCalibrationPeriod) if i not in idxs]

        if len(idxRemoved[2]) != 0:
            idxs = idxRemoved[2]
            self.outputCalibrationPeriod = [v for i, v in enumerate( self.outputCalibrationPeriod) if i not in idxs]
            self.outputTypes = [v for i, v in enumerate(self.outputTypes) if i not in idxs]
            


        self.inputAppliedError = None
        self.inventoryAppliedError = None
        self.outputAppliedError = None

        if self.doPbar:
            d13 = ("⠋",
                    "⠙",
                    "⠹",
                    "⠸",
                    "⠼",
                    "⠴",
                    "⠦",
                    "⠧",
                    "⠇",
                    "⠏")

            self.dots13 = frame_spinner_factory(d13)
            self.longestBarStr = len('Calculating Page trend test')


    
    def _checkForErrorData(self):
        if (self.inputAppliedError == None or self.inventoryAppliedError == None or self.outputAppliedError == None):
            if not self.dopar:
                self._recalcBatchSize()

            print(f"{bcolors.WARNING}[W]:{bcolors.ENDC} Error data not found. Calculating...")
            self.calcErrors()
    
   
    #performed in case batch size is changed after
    #initaliation
    def _recalcBatchSize(self):
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
                            doPbar = self.doPbar,
                            ispar = False,
                            GUIObject = self.GUIObject,
                            inputTypes=self.inputTypes,
                            outputTypes=self.outputTypes
                            )
            
        # if parallel
        else:

            # helpers for batching data
            idx1=0
            idx2=0

            futures = []

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.ncpu) as executor:

                with yaspin(text="Configuring jobs", spinner='dots'):
                    for _ in range(self.ntasks):
                        idx2 = idx1 + self.nbatch

                        inslice = self._parIterSlicer(idx1,idx2,'inputAppliedError')
                        invslice = self._parIterSlicer(idx1,idx2,'inventoryAppliedError')
                        outslice = self._parIterSlicer(idx1,idx2,'outputAppliedError')

                        idx1 += self.nbatch

                        futures.append(
                            executor.submit(
                                partial(Tests.MUF,
                                        inputAppliedError = inslice,
                                        inventoryAppliedError= invslice,
                                        outputAppliedError = outslice,
                                        processedInputTimes = self.processedInputTimes,
                                        processedInventoryTimes = self.processedInventoryTimes,
                                        processedOutputTimes = self.processedOutputTimes,
                                        inputTypes=self.inputTypes,
                                        outputTypes=self.outputTypes,
                                        MBP = self.mbaTime,
                                        doPbar=self.doPbar,
                                        ispar = True
                                )
                            )
                        )

                title = 'Calculating MUF'
                with alive_bar(force_tty=True, total=len(futures), spinner=self.dots13, bar='circles', title=title+' '*(self.longestBarStr - len(title))) as bar:
                    for J, future in enumerate(futures):
                        if J == 0:
                            MUF = future.result()
                        else:
                            MUF = np.vstack((MUF,future.result()))
                        
                        bar()


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
                            doPbar = self.doPbar,
                            ispar = False,
                            GUIObject = self.GUIObject,
                            inputTypes=self.inputTypes,
                            outputTypes=self.outputTypes)
            
        # if parallel
        else:
            # helpers for batching data
            idx1=0
            idx2=0

            # define the remote function

            # setup the progressbar if necessary
            # NOTE: this is a crude progress bar
            # for large jobs, recommend using the
            # ray dashboard instead
            # NOTE: performance of the progressbar
            # is better in console


            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.ncpu) as executor:

                
                with yaspin(text="Configuring jobs", spinner='dots'):
                    for i in range(self.ntasks):
                        idx2 = idx1 + self.nbatch

                        # batch the data into ntasks of nbatch size
                        inslice = self._parIterSlicer(idx1,idx2,'inputAppliedError')
                        invslice = self._parIterSlicer(idx1,idx2,'inventoryAppliedError')
                        outslice = self._parIterSlicer(idx1,idx2,'outputAppliedError')

                        idx1 += self.nbatch

                        

                        # add the tasks                    
                        futures.append(
                            executor.submit(
                                partial(Tests.ActiveInventory,
                                        inputAppliedError = inslice,
                                        inventoryAppliedError= invslice,
                                        outputAppliedError = outslice,
                                        processedInputTimes = self.processedInputTimes,
                                        processedInventoryTimes = self.processedInventoryTimes,
                                        processedOutputTimes = self.processedOutputTimes,
                                        inputTypes=self.inputTypes,
                                        outputTypes=self.outputTypes,
                                        MBP = self.mbaTime,
                                        doPbar=self.doPbar,
                                        ispar = True
                                    )
                            )
                        )

                # print the progress until all tasks
                # are completed 
                title = 'Calculating active inventory'
                with alive_bar(force_tty=True, total=len(futures), spinner=self.dots13, bar='circles', title=title+' '*(self.longestBarStr - len(title))) as bar:
                    for J, future in enumerate(futures):
                        if J == 0:
                            AI = future.result()
                        else:
                            AI = np.vstack((AI,future.result()))
                        
                        bar()

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
                            doPbar = self.doPbar,
                            ispar = False,
                            GUIObject = self.GUIObject,
                            inputTypes=self.inputTypes,
                            outputTypes=self.outputTypes)
            
        # if parallel
        else:
            # helpers for batching data
            idx1=0
            idx2=0

            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.ncpu) as executor:
                with yaspin(text="Configuring jobs", spinner='dots'):
                    for _ in range(self.ntasks):
                        idx2 = idx1 + self.nbatch

                        # batch the data into ntasks of nbatch size
                        inslice = self._parIterSlicer(idx1,idx2,'inputAppliedError')
                        invslice = self._parIterSlicer(idx1,idx2,'inventoryAppliedError')
                        outslice = self._parIterSlicer(idx1,idx2,'outputAppliedError')

                        idx1 += self.nbatch

                        

                        # add the tasks                    
                        futures.append(
                            executor.submit(
                                partial(Tests.SEMUF,
                                        inputAppliedError = inslice,
                                        inventoryAppliedError= invslice,
                                        outputAppliedError = outslice,
                                        processedInputTimes = self.processedInputTimes,
                                        processedInventoryTimes = self.processedInventoryTimes,
                                        processedOutputTimes = self.processedOutputTimes,
                                        inputTypes=self.inputTypes,
                                        outputTypes=self.outputTypes,
                                        MBP = self.mbaTime,
                                        ErrorMatrix = self.totalErrorMatrix,
                                        doPbar=False, #self.doPbar
                                        ispar = True
                                    )
                            )
                        )

                # print the progress until all tasks
                # are completed 
                title = 'Calculating sigma MUF'
                with alive_bar(force_tty=True, total=len(futures), spinner=self.dots13, bar='circles', title=title+' '*(self.longestBarStr - len(title))) as bar:
                    for J, future in enumerate(futures):
                        res = future.result()
                        if J == 0:
                            SEMUF = res[0]
                            SEMUF_contribR = res[1]
                            SEMUF_contribS = res[2]
                            SEMUF_inv = res[3]
                        else:
                            SEMUF = np.vstack((SEMUF,res[0]))
                            SEMUF_contribR = np.vstack((SEMUF_contribR,res[1]))
                            SEMUF_contribS = np.vstack((SEMUF_contribS,res[2]))
                            SEMUF_inv = np.vstack((SEMUF_inv,res[3]))
                        
                        bar()

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
        self._recalcBatchSize()
        self._checkForErrorData()


        # TODO: if parallel, calcMUF should also be parallel
        if not hasattr(self, "MUF"):
            print(f"{bcolors.WARNING}[W]:{bcolors.ENDC} MUF sequence not found. Calculating...")
            self.calcMUF()
        else:
            if self.MUF is None:
                print(f"{bcolors.WARNING}[W]:{bcolors.ENDC} MUF sequence not found. Calculating...")
                self.calcMUF()
        

        
        if not self.dopar:
            
            #check for covariance matrix presence
            if not hasattr(self, "covmatrix"):
                print(f"{bcolors.WARNING}[W]:{bcolors.ENDC} Covariance matrix not found. Calculating...")
                self._calcCovMat()
            elif self.covmatrix is None:
                print(f"{bcolors.WARNING}[W]:{bcolors.ENDC} Covariance matrix not found. Calculating...")
                self._calcCovMat()

            SITMUF = Tests.SITMUF(self.MUF, self.covmatrix, self.mbaTime, self.GUIObject, self.doPbar, self.dopar)
        
        else:

            # check for covariance matrix presence
            if not hasattr(self, "covmatrix"):
                print(f"{bcolors.WARNING}[W]:{bcolors.ENDC} Covariance matrix not found. Calculating...")
                self.covmatrix = self._calcCovMatPar()
            elif self.covmatrix is None:
                print(f"{bcolors.WARNING}[W]:{bcolors.ENDC} Covariance matrix not found. Calculating...")
                self.covmatrix = self._calcCovMatPar()
        


            # helpers for batching data
            idx1=0
            idx2=0

            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.ncpu) as executor:
                with yaspin(text="Configuring jobs", spinner='dots'):
                    for _ in range(self.ntasks):
                        idx2 = idx1 + self.nbatch

                        # batch the data into ntasks of nbatch size
                        MUFslice = self._parIterSlicer(idx1,idx2,'MUF')
                        covslice = self._parIterSlicer(idx1,idx2,'covmatrix')

                        idx1 += self.nbatch

                        

                        # add the tasks                    
                        futures.append(
                            executor.submit(
                                partial(Tests.SITMUF,
                                        MUF = MUFslice,
                                        covmatrix = covslice,
                                        MBP = self.mbaTime,
                                        doPbar=False,
                                        ispar=True
                                    )
                            )
                        )

                # print the progress until all tasks
                # are completed 
                title = 'Calculating SITMUF'
                with alive_bar(force_tty=True, total=len(futures), spinner=self.dots13, bar='circles', title=title+' '*(self.longestBarStr - len(title))) as bar:
                    for J, future in enumerate(futures):
                        if J == 0:
                            SITMUF = future.result()
                        else:
                            SITMUF = np.vstack((SITMUF,future.result()))
                        
                        bar()



        self.SITMUF = SITMUF

        return SITMUF

    def calcGEMUF_V1(self):
        self._recalcBatchSize()
        self._checkForErrorData()

        # TODO: update for parallel check here
        if not hasattr(self, "MUF"):
            self.calcMUF()
        else:
            if self.MUF is None:
                self.calcMUF()
        

        
        if not self.dopar:
            if not hasattr(self, "covmatrix"):
                self._calcCovMat()
            elif self.covmatrix is None:
                self._calcCovMat()
            self.GEMUFV1 = Tests.GEMUF_V1(self.MUF, self.covmatrix, self.mbaTime, self.GUIObject, self.doPbar, self.dopar)
        else:

            # check for covariance matrix presence
            if not hasattr(self, "covmatrix"):
                self.covmatrix = self._calcCovMatPar()
            elif self.covmatrix is None:
                self.covmatrix = self._calcCovMatPar()
        


            # helpers for batching data
            idx1=0
            idx2=0

            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.ncpu) as executor:
                with yaspin(text="Configuring jobs", spinner='dots'):
                    for _ in range(self.ntasks):
                        idx2 = idx1 + self.nbatch

                        # batch the data into ntasks of nbatch size
                        MUFslice = self._parIterSlicer(idx1,idx2,'MUF')
                        covslice = self._parIterSlicer(idx1,idx2,'covmatrix')

                        idx1 += self.nbatch

                        

                        # add the tasks                    
                        futures.append(
                            executor.submit(
                                partial(Tests.GEMUF_V1,
                                        MUF = MUFslice,
                                        covmatrix = covslice,
                                        MBP = self.mbaTime,
                                        doPbar=False,
                                        ispar=True
                                    )
                            )
                        )

                # print the progress until all tasks
                # are completed 
                title = 'Calculating GEMUFV1'
                with alive_bar(force_tty=True, total=len(futures), spinner=self.dots13, bar='circles', title=title+' '*(self.longestBarStr - len(title))) as bar:
                    for J, future in enumerate(futures):
                        if J == 0:
                            GEMUFV1 = future.result()
                        else:
                            GEMUFV1 = np.vstack((GEMUFV1,future.result()))
                        
                        bar()

                self.GEMUFV1 = GEMUFV1
                
        return self.GEMUFV1
    
    def calcGEMUF_V5B3(self):
        self._recalcBatchSize()
        self._checkForErrorData()

        if not hasattr(self, "MUF"):
            self.calcMUF()
        else:
            if self.MUF is None:
                self.calcMUF()
        
        if not self.dopar:
            if not hasattr(self, "covmatrix"):
                self._calcCovMat()
            elif self.covmatrix is None:
                self._calcCovMat()
            self.GEMUFV5B3 = Tests.GEMUF_V5B3(self.MUF, self.covmatrix, self.mbaTime, self.GUIObject, self.doPbar, self.dopar)
        else:

            # check for covariance matrix presence
            if not hasattr(self, "covmatrix"):
                self.covmatrix = self._calcCovMatPar()
            elif self.covmatrix is None:
                self.covmatrix = self._calcCovMatPar()
        


            # helpers for batching data
            idx1=0
            idx2=0

            # define the remote function
            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.ncpu) as executor:
                with yaspin(text="Configuring jobs", spinner='dots'):
                    for _ in range(self.ntasks):
                        idx2 = idx1 + self.nbatch

                        # batch the data into ntasks of nbatch size
                        MUFslice = self._parIterSlicer(idx1,idx2,'MUF')
                        covslice = self._parIterSlicer(idx1,idx2,'covmatrix')

                        idx1 += self.nbatch

                        

                        # add the tasks                    
                        futures.append(
                            executor.submit(
                                partial(Tests.GEMUF_V5B3,
                                        MUF = MUFslice,
                                        covmatrix = covslice,
                                        MBP = self.mbaTime,
                                        doPbar=False,
                                        ispar=True
                                    )
                            )
                        )

                # print the progress until all tasks
                # are completed 
                title = 'Calculating GEMUFV5B3'
                with alive_bar(force_tty=True, total=len(futures), spinner=self.dots13, bar='circles', title=title+' '*(self.longestBarStr - len(title))) as bar:
                    for J, future in enumerate(futures):
                        if J == 0:
                            GEMUFV5B3 = future.result()
                        else:
                            GEMUFV5B3 = np.vstack((GEMUFV5B3,future.result()))
                        
                        bar()

                self.GEMUFV5B3 = GEMUFV5B3

        return self.GEMUFV5B3
    
    def _calcCovMat(self):
        params = {
            "inputAppliedError": self.inputAppliedError,
            "inventoryAppliedError": self.inventoryAppliedError,
            "outputAppliedError": self.outputAppliedError,
            "processedInputTimes": self.processedInputTimes,
            "processedInventoryTimes": self.processedInventoryTimes,
            "processedOutputTimes": self.processedOutputTimes,
            "MBP": self.mbaTime,
            "ErrorMatrix": self.totalErrorMatrix,
            "inputTypes": self.inputTypes, 
            "outputTypes": self.outputTypes, 
            "GUIObject": self.GUIObject,
            "ispar": self.dopar,
            "doPbar": self.doPbar
        }

        self.covmatrix = AuxFunctions.calcCovMat(**params)

    def _calcCovMatPar(self):
        idx1 = 0
        idx2 = 0

        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.ncpu) as executor:
            with yaspin(text="Configuring jobs", spinner='dots'):
                for _ in range(self.ntasks):
                    idx2 = idx1 + self.nbatch

                    # batch the data into ntasks of nbatch size
                    inpslice = self._parIterSlicer(idx1, idx2, 'inputAppliedError')
                    invslice = self._parIterSlicer(idx1, idx2, 'inventoryAppliedError')
                    outslice = self._parIterSlicer(idx1, idx2, 'outputAppliedError')

                    idx1 += self.nbatch

                    

                    # add the tasks                    
                    futures.append(
                        executor.submit(
                            partial(AuxFunctions.calcCovMat,
                                    inputAppliedError = inpslice,
                                    inventoryAppliedError = invslice,
                                    outputAppliedError = outslice,
                                    processedInputTimes = self.processedInputTimes,
                                    processedInventoryTimes = self.processedInventoryTimes,
                                    processedOutputTimes = self.processedOutputTimes,
                                    ErrorMatrix = self.totalErrorMatrix,
                                    MBP = self.mbaTime,
                                    inputTypes = self.inputTypes,
                                    outputTypes = self.outputTypes,
                                    doPbar = False,
                                    ispar = True
                                )
                        )
                    )

            # print the progress until all tasks
            # are completed 
            title = 'Calculating CovMatrix'
            with alive_bar(force_tty=True, total=len(futures), spinner=self.dots13, bar='circles', title=title+' '*(self.longestBarStr - len(title))) as bar:
                for J, future in enumerate(futures):
                    if J == 0:
                        covmatrix = future.result()
                    else:
                        covmatrix = np.concatenate((covmatrix, future.result()), axis = 0)
                    
                    bar()


        return covmatrix

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
        self.Page = Tests.PageTrendTest(self.SITMUF,self.mbaTime,MBPs,doPbar=False, GUIObject=self.GUIObject)
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
                                times = self.processedInputTimes, 
                                calibrationPeriod = self.inputCalibrationPeriod,
                                ErrorMatrix =  self.inputErrorMatrix, 
                                iterations = self.IT,
                                GUIObject = self.GUIObject)

            self.inventoryAppliedError = Preprocessing.SimErrors(
                                        rawData = self.processedInventory,
                                        times = self.processedInventoryTimes,
                                        calibrationPeriod = self.inventoryCalibrationPeriod,
                                        ErrorMatrix =  self.inventoryErrorMatrix, 
                                        iterations = self.IT,
                                        GUIObject = self.GUIObject)


            self.outputAppliedError = Preprocessing.SimErrors(
                                        rawData = self.processedOutput, 
                                        times = self.processedOutputTimes,
                                        calibrationPeriod = self.outputCalibrationPeriod,
                                        ErrorMatrix =  self.outputErrorMatrix, 
                                        iterations = self.IT,
                                        GUIObject = self.GUIObject)
        else:

            futures = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.ncpu) as executor:
                for i in range(self.ntasks):
                    futures.append(
                        executor.submit(
                            partial(Preprocessing.SimErrors,
                                    rawData = self.processedInput, 
                                    times = self.processedInputTimes, 
                                    calibrationPeriod = self.inputCalibrationPeriod,
                                    ErrorMatrix =  self.inputErrorMatrix, 
                                    iterations = self.nbatch,
                                    batchSize = self.nbatch,
                                    dopar=True

                            )
                        )
                    )

                    futures.append(
                        executor.submit(
                            partial(Preprocessing.SimErrors,
                                    rawData = self.processedInventory, 
                                    times = self.processedInventoryTimes, 
                                    calibrationPeriod = self.inventoryCalibrationPeriod,
                                    ErrorMatrix =  self.inventoryErrorMatrix, 
                                    iterations = self.nbatch,
                                    batchSize = self.nbatch,
                                    dopar=True
                            )
                        )
                    )

                    futures.append(
                        executor.submit(
                            partial(Preprocessing.SimErrors,
                                rawData = self.processedOutput, 
                                times = self.processedOutputTimes, 
                                calibrationPeriod = self.outputCalibrationPeriod,
                                ErrorMatrix =  self.outputErrorMatrix, 
                                iterations = self.nbatch,
                                batchSize = self.nbatch,
                                dopar=True
                            )
                        )
                    )


            res = []
            title = 'Calculating errors'
            with alive_bar(force_tty=True, total=len(futures), spinner=self.dots13, bar='circles', title=title+' '*(self.longestBarStr - len(title))) as bar:
                for _, future in enumerate(futures):
                    res.append(future.result())                        
                    bar()


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
                c = np.argmax(rotation)
                if c == 0:
                    inps.append(res[i])
                    rotation = np.array([0,1,0])
                elif c == 1:
                    invs.append(res[i])
                    rotation = np.array([0,0,1])
                elif c == 2:
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




