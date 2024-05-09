import numpy as np
import os
import string
import copy
from scipy.io import loadmat

from tqdm import tqdm






def loadDataFromWizard(GUIObject):
      eleAppend = list(string.ascii_lowercase)

      ##IO - Inputs

      liH = []

      if GUIObject.Wizard.IsMatV == 0:
        # need to infer the number of elements

        lddir = os.path.join(GUIObject.Wizard.InDir,sorted(os.listdir(GUIObject.Wizard.InDir))[0])

        testM = np.loadtxt(lddir, delimiter=',')
      else:
        G = loadmat(GUIObject.Wizard.MatDir)  # should be only one .mat for all locations
        testM = G['in']['data'][0][0]

      # if there's only a single element it could be imported as
      # a single dimesion vector which we need to fix for code
      # further in to work as intended

      if len(np.shape(testM)) == 1:  # adds a dimension in case single element is recorded as (X,) rather than (X,1)
        testM = np.expand_dims(testM, axis=0)

      eleInfer = np.min(np.shape(testM))  # assuming smallest dimension is number of elements

      # try to number of elements in the input
      #also grab some information about the
      #labels for the elements if provided

      if len(GUIObject.Wizard.EleVec_IN) > 0:
        for i in range(0, int(GUIObject.Wizard.InKMP)):
          for j in range(0, len(GUIObject.Wizard.EleVec_IN)):
            liH.append(GUIObject.Wizard.EleVec_IN[j] + str(i))

        if len(liH) < eleInfer:
          for i in range(0, int(GUIObject.Wizard.InvKMP)):
            for j in range(int(len(liH)), int(eleInfer)):
              liH.append('ele' + eleAppend[j] + str(i))
      else:
        for i in range(0, int(GUIObject.Wizard.InKMP)):
          for j in range(0, eleInfer):
            liH.append('ele' + eleAppend[j] + str(i))

      GUIObject.eleIN = copy.copy(len(liH))
      LiC = []

      #begin to load the data
      if GUIObject.Wizard.IsMatV == 0:  # if CSV
        for i in range(0, int(GUIObject.Wizard.InKMP)):
          lddir = os.path.join(GUIObject.Wizard.InDir,sorted(os.listdir(GUIObject.Wizard.InDir))[i])
          r = np.loadtxt(lddir, delimiter=',')
          LiC.append(r)

        try:
          inpFrame = np.stack(LiC)
        except:
          pass

      else:  # if not CSV
        LiC = []
        LiC2 = []
        lddir = loadmat(GUIObject.Wizard.MatDir)
        JJ = np.shape(G['in']['data'][0])[0]

        for i in range(0, JJ):
          LiC.append(G['in']['data'][0][i])
          LiC2.append(G['in']['time'][0][i])

        try:
          inpFrame = np.stack(LiC)
          inpTimeFrame = np.stack(LiC2)
        except:
          inpFrame = LiC
          inpTimeFrame = LiC2

      ##IO - Inventory
      liH = []
      if GUIObject.Wizard.IsMatV == 0:
        # need to infer the number of elements
        lddir = os.path.join(GUIObject.Wizard.InvDir,sorted(os.listdir(GUIObject.Wizard.InvDir))[0])

        testM = np.loadtxt(lddir, delimiter=',')

        if len(np.shape(testM)) == 1:
          testM = np.expand_dims(testM, axis=0)

        eleInfer = np.min(np.shape(
            testM))  # assuming smallest dimension is number of elements

        if len(GUIObject.Wizard.EleVec_IN) > 0:
          for i in range(0, int(GUIObject.Wizard.InvKMP)):
            for j in range(0, len(GUIObject.Wizard.EleVec_IN)):
              liH.append(GUIObject.Wizard.EleVec_IN[j] + str(i))

          if len(liH) < eleInfer:
            for i in range(0, int(GUIObject.Wizard.InvKMP)):
              for j in range(int(len(liH)), int(eleInfer)):
                liH.append('ele' + eleAppend[j] + str(i))
        else:
          for i in range(0, int(GUIObject.Wizard.InvKMP)):
            for j in range(0, eleInfer):
              liH.append('ele' + eleAppend[j] + str(i))

        GUIObject.eleINV = copy.copy(len(liH))
        LiC = []

        for i in range(0, int(GUIObject.Wizard.InvKMP)):
          lddir = os.path.join(GUIObject.Wizard.InvDir,sorted(os.listdir(GUIObject.Wizard.InvDir))[i])
          r = np.loadtxt(lddir, delimiter=',')
          LiC.append(r)

        try:
          invFrame = np.stack(LiC)
        except:
          None

      else:
        LiC = []
        LiC2 = []
        lddir = loadmat(GUIObject.Wizard.MatDir)
        JJ = np.shape(G['invn']['data'][0])[0]



        for i in range(0, JJ):
          LiC.append(G['invn']['data'][0][i])
          LiC2.append(G['invn']['time'][0][i])

        nInferredEles = np.min(np.shape(
            G['invn']['data'][0][0]))  # assume elements is less than time
        try:
          invFrame = np.stack(LiC)
          invTimeFrame = np.stack(LiC2)
        except:
          invFrame = LiC
          invTimeFrame = LiC2

      ##IO -- Output
      liH = []

      if GUIObject.Wizard.IsMatV == 0:  # if CSV
        # need to infer the number of elements
        lddir = os.path.join(GUIObject.Wizard.OutDir,
                            sorted(os.listdir(GUIObject.Wizard.OutDir))[0])

        testM = np.loadtxt(lddir, delimiter=',')

        if len(np.shape(testM)) == 1:
          testM = np.expand_dims(testM, axis=0)

        eleInfer = np.min(np.shape(
            testM))  # assuming smallest dimension is number of elements

        if len(GUIObject.Wizard.EleVec_IN) > 0:

          for i in range(0, int(GUIObject.Wizard.OutKMP)):
            for j in range(0, len(GUIObject.Wizard.EleVec_IN)):
              liH.append(GUIObject.Wizard.EleVec_IN[j] + str(i))

          if len(liH) < eleInfer:
            for i in range(0, int(GUIObject.Wizard.OutKMP)):
              for j in range(int(len(liH)), int(eleInfer)):
                liH.append('ele' + eleAppend[j] + str(i))
        else:
          for i in range(0, int(GUIObject.Wizard.OutKMP)):
            for j in range(0, eleInfer):
              liH.append('ele' + eleAppend[j] + str(i))

        GUIObject.eleOUT = copy.copy(len(liH))
        LiC = []
        for i in range(0, int(GUIObject.Wizard.OutKMP)):
          lddir = os.path.join(GUIObject.Wizard.OutDir,
                              sorted(os.listdir(GUIObject.Wizard.OutDir))[i])
          r = np.loadtxt(lddir, delimiter=',')
          LiC.append(r)

        try:
          outFrame = np.stack(LiC)
        except:
          None

        nInferredEles = eleInfer

      else:
        LiC = []
        LiC2 = []
        lddir = loadmat(GUIObject.Wizard.MatDir)
        JJ = np.shape(G['outn']['data'][0])[0]

        for i in range(0, JJ):
          LiC.append(G['outn']['data'][0][i])
          LiC2.append(G['outn']['time'][0][i])

        try:
          outFrame = np.stack(LiC)
          outTimeFrame = np.stack(LiC2)
        except:
          outFrame = LiC
          outTimeFrame = LiC2

      return inpFrame, invFrame, outFrame



def FormatInput(rawInput,rawInputTimes,rawInventory,rawInventoryTimes,rawOutput,rawOutputTimes,GUIObject=None,dataOffset=0,IT=1, rebaseToZero=True):

    if GUIObject is not None:
      GUIObject.progress.emit(-1)
      GUIObject.pbartext.emit('Importing data...')

    # locations, timestep, element
    rawInput = list(rawInput)
    rawInventory = list(rawInventory)
    rawOutput = list(rawOutput)
    rawInputTimes = list(rawInputTimes)  #grab the times
    rawInventoryTimes = list(rawInventoryTimes)
    rawOutputTimes = list(rawOutputTimes)  
    

    #the arrays are usually missing a dimension
    #required for later analysis
    for i in range(0,len(rawInput)):
      if len(np.shape(rawInput[i])) != 2:
        rawInput[i] = np.expand_dims(rawInput[i],axis=1)

      #covers a case where there are no iterations/no applied error
      if len(np.shape(rawInput[i])) != 3 and IT == 0:
        rawInput[i] = np.expand_dims(rawInput[i],axis=0)

    for i in range(0,len(rawInventory)):
      if len(np.shape(rawInventory[i])) != 2:
        rawInventory[i] = np.expand_dims(rawInventory[i],axis=1)

      if len(np.shape(rawInventory[i])) != 3 and IT == 0:
        rawInventory[i] = np.expand_dims(rawInventory[i],axis=0)


    for i in range(0,len(rawOutput)):
      if len(np.shape(rawOutput[i])) != 2:
        rawOutput[i] = np.expand_dims(rawOutput[i],axis=1)

      if len(np.shape(rawOutput[i])) != 3 and IT == 0:
        rawOutput[i] = np.expand_dims(rawOutput[i],axis=0)
      


    # dealing with offset by modifying the data upfront is easier
    # than trying to modify the stats calculations themselves

    #offset deals with the temporal offset
    #which effectively starts the safeguards
    #calculations after the offset has ellapsed
    #useful if there is a long period of startup
    #data that has been collected
    #TODO: experimental

    #If the cutoff is greater than the max time
    #of the location then we just remove that
    #set as it's not applicable anymore

    
    if dataOffset > 0:

      #assumes raws are lists based on location
      idxToRemove=[]
      for JR in range(len(rawInput)):

        validtimeIdxs = np.where(rawInputTimes[JR]>=dataOffset)[0]

        if len(validtimeIdxs) >= 1:
          LI = validtimeIdxs[0]
          rawInput[JR] = rawInput[JR][LI:,]
          if rebaseToZero:
            rawInputTimes[JR] = rawInputTimes[JR][LI:,] - dataOffset
          else:
            rawInputTimes[JR] = rawInputTimes[JR][LI:,]
        else:
          print("Cutoff exceeds total input time, removing input")
          idxToRemove.append(JR)

      if len(idxToRemove) > 0:
        rawInput = [v for i, v in enumerate(rawInput) if i not in idxToRemove]
        rawInputTimes = [v for i, v in enumerate(rawInputTimes) if i not in idxToRemove]

      idxToRemove=[]
      for JR in range(len(rawInventory)):

        validtimeIdxs = np.where(rawInventoryTimes[JR]>=dataOffset)[0]

        if len(validtimeIdxs) >= 1:
          LI = validtimeIdxs[0]
          rawInventory[JR] = rawInventory[JR][LI:,]
          if rebaseToZero:
            rawInventoryTimes[JR] = rawInventoryTimes[JR][LI:,] - dataOffset
          else:
            rawInventoryTimes[JR] = rawInventoryTimes[JR][LI:,]
        else:
          print("Cutoff exceeds total input time, removing inventory")
          idxToRemove.append(JR)

      if len(idxToRemove) > 0:
        rawInventory = [v for i, v in enumerate(rawInventory) if i not in idxToRemove]
        rawInventoryTimes = [v for i, v in enumerate(rawInventoryTimes) if i not in idxToRemove]

      idxToRemove=[]
      for JR in range(len(rawOutput)):

        validtimeIdxs = np.where(rawOutputTimes[JR]>=dataOffset)[0]

        if len(validtimeIdxs) >= 1:
          LI = validtimeIdxs[0]
          rawOutput[JR] = rawOutput[JR][LI:,]
          if rebaseToZero:
            rawOutputTimes[JR] = rawOutputTimes[JR][LI:,] - dataOffset
          else:
            rawOutputTimes[JR] = rawOutputTimes[JR][LI:,]
        else:
          print("Cutoff exceeds total input time, removing inventory")
          idxToRemove.append(JR)

      
      if len(idxToRemove) > 0:
        rawOutput = [v for i, v in enumerate(rawOutput) if i not in idxToRemove]
        rawOutputTimes = [v for i, v in enumerate(rawOutputTimes) if i not in idxToRemove]






    return rawInput, rawInputTimes, rawInventory, rawInventoryTimes, \
      rawOutput, rawOutputTimes





def SimErrors(rawData,ErrorMatrix,iterations,GUIObject=None,doTQDM=True,batchSize=10,dopar=False,bar=None):
    """
      Function to add simulated measurement error. Supports variable sample rates. 
      Assumes the traditional multiplicative measurement error model:

      :math:`M_{i,j} = T(1+R_{i,j}+S_j)`      

      Random errors: :math:`R_{i,j} \\sim \\mathcal{N}(0,{\\delta_R}_j^2)`

      Systematic errors: :math:`S_{j} \\sim \\mathcal{N}(0,{\\delta_S}_j^2)`

      where :math:`i` is the measurement time and :math:`j` is the location

      

      Args:
        rawData (list): Raw data to apply errors to, list of 2D ndarrays. Each entry in the list should correspond to a different location and the shape of ndarray in the list should be [MxN] where M is the sample dimension (number of samples) and N is the elemental dimension, if applicable. If only considering one element, each ndarray in the rawData list should be [Mx1].

        ErrorMatrix (ndarray): 2D ndarray of shape [Mx2] describing the relative standard deviation to apply to ``rawData``. M sample dimension in each input array and should be identical to M described in  ``rawData``. The second dimension (e.g., 2) refers to the random and systematic error respectively such that ``ErrorMatrix[0,0]`` refers to the random relative standard deviation of the first location and ``ErrorMatrix[0,1]`` refers to the systematic relative standard deviation. 

        iterations (int): Number of iterations to calculate

        GUIObject (obj, default=None): GUI object for internal MAPIT use

        doTQDM (bool, default=True): Controls the use of TQDM progress bar for command line or notebook operation. 

      Returns:
        list: List of arrays identical in shape to ``rawData``. A list is returned so that each location can have a different sample rate. 
    """

    if GUIObject is not None:
      doTQDM = False


    # important -- going to assume every feature has different systematic error instance - in practice they might be shared
    # basically gonna propogate error to everything because its easier on me and probably doesn't have a lot
    # of overhead, might need to update later



    AppliedError = [] #list holding input with applied errors



    # initalize holders for the errors which we will need
    # for some of the stats tests

    # [Iterations, Locs, Samples, Elements] OR [locations, timestep, element]
    #E = the total errors
    #RA = random applied
    #SA = system applied
    #S = raw sys
    #R = raw random

    #len(list) = locations
    #list[n] = (iterations, samples, elements)
    for i in range(0, len(rawData)):
        AppliedError.append(np.zeros((iterations, rawData[i].shape[0]),dtype=np.float32))


    loopcounter = 0





    # for each iteration
    # see github for more theory
    #observed = true(1+random*sys)




    #assume sys differs by location only and doesn't change for different elements

    if doTQDM and not dopar:
      if iterations > batchSize:
        outerloop = int(np.floor(iterations/batchSize))
        pbar = tqdm(desc="Error Prop", total=int((outerloop+1)*len(rawData)), leave=True, bar_format = "{desc:10}: {percentage:3.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]",ncols=85)   
      else:
        pbar = tqdm(desc="Error Prop", total=int(len(rawData)), leave=True, bar_format = "{desc:10}: {percentage:3.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]",ncols=85)
    #------------ Start error prop ------------#
    for i in range(0, len(rawData)):


      if iterations > batchSize:
        outerloop = int(np.floor(iterations/batchSize))
        remruns = iterations%batchSize


        for j in range(0,outerloop):
          startIdx = j*batchSize
          endIdx = startIdx+batchSize
          sysRSD = np.random.normal(size=(batchSize,1,1),loc=0,scale=ErrorMatrix[i,1])
          randRSD = np.random.normal(size=(batchSize,rawData[i].shape[0],1),loc=0,scale=ErrorMatrix[i,0])
          AppliedError[i][startIdx:endIdx,] = rawData[i][:,0].reshape((1,-1)) * (1+sysRSD+randRSD).reshape((batchSize,-1))

          if GUIObject is not None:
            totalloops = (outerloop+1)*len(rawData)
            GUIObject.progress.emit(loopcounter / totalloops*100)
            loopcounter+=1
          
          if doTQDM and not dopar:
            pbar.update(1)
        
        if remruns > 0:
          sysRSD = np.random.normal(size=(remruns,1,1),loc=0,scale=ErrorMatrix[i,1])
          randRSD = np.random.normal(size=(remruns,rawData[i].shape[0],1),loc=0,scale=ErrorMatrix[i,0])
          AppliedError[i][endIdx:,] = rawData[i][:,0].reshape((1,-1)) * (1+sysRSD+randRSD).reshape((remruns,-1))

          if GUIObject is not None:
              totalloops = (outerloop+1)*len(rawData)
              GUIObject.progress.emit(loopcounter / totalloops*100)
              loopcounter+=1 
          
          if doTQDM and not dopar:
            pbar.update(1)
      
      else:
          sysRSD = np.random.normal(size=(iterations,1,1),loc=0,scale=ErrorMatrix[i,1])
          randRSD = np.random.normal(size=(iterations,rawData[i].shape[0],1),loc=0,scale=ErrorMatrix[i,0])
          AppliedError[i] = rawData[i][:,0].reshape((1,-1)) * (1+sysRSD+randRSD).reshape((iterations,-1))

          if GUIObject is not None:
            GUIObject.progress.emit(i/len(rawData)*100)
          
          if doTQDM and not dopar:
            pbar.update(1)


    if doTQDM and not dopar:
      pbar.n=pbar.total
    
    if doTQDM and bar is not None:
      bar.update.remote(1)

    if GUIObject is not None:
      GUIObject.progress.emit(100)
      
    


    return AppliedError