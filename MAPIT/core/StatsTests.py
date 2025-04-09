from PySide6 import QtWidgets
import numpy as np
from itertools import chain
import MAPIT.core.AuxFunctions as AuxFunctions


from tqdm import tqdm


def MUF(inputAppliedError,processedInputTimes,inventoryAppliedError,processedInventoryTimes,outputAppliedError,processedOutputTimes,MBP,inputTypes,outputTypes,GUIObject=None,doTQDM=True,ispar=False):
    """
      Function to calculate Material Unaccounted For (MUF), which is sometimes also called ID (inventory difference). 
      Specifically calculates the material balance sequence given some input time series. 

      :math:`\\text{MUF}_t = I_t - O_t - (C_t - C_{t-1})` 

      :math:`I_t` is input at time :math:`t`

      :math:`O_t` is output at :math:`t`

      :math:`C_t` is inventory at time :math:`t` (note C is used to denote `container` to have clearer notation rather than using :math:`I` with subscripts for both inventory and input)

      .. IMPORTANT::
        The lengths and shapes of appliedErrors and processedTimes should be the same. For example:

        .. highlight:: python
        .. code-block:: python

           assert(len(inputAppliedError) == len(processedInputTimes)
           assert(inputAppliedError[0].shape == processedInputTimes[0].shape)
           
        See the :ref:`Input guide` for more information. 





      Args:
        inputAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of input locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites (as opposed to ground truths). Inputs are assumed to be flows in units of :math:`\\frac{1}{s}` and will be integrated. 


        processedInputTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of input locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedInputTimes)` and the shape of each list entry (ndarray) should be the same as for `inputAppliedError`. Each entry in the ndarray should correspond to a timestamp indicating when the value was taken. 


        inventoryAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of inventory locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites. Inventories are assumed to be in units of mass and will *not* be integrated.


        processedInventoryTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of inventory locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedInventoryTimes)` and shape of each list entry (ndarray) should be the same as for `inventoryAppliedError`. Each entry in the ndarray should corresond to a timestamp indicating when the value was taken. 


        outputAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of output locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites. Outputs are assumed to be in flows with units of :math:`\\frac{1}{s}` and will be integrated.


        processedOutputTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of output locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedOutputTimes)` and shape of each list entry (ndarray) should be the same as for `outputAppliedError`. Each entry in the ndarray should correspond to a timestamp indicating when the value was taken. 


        MBP (float): Defines the material balance period. 

        inputTypes (list of strings): Defines the type of input. This should be a list of strings that is the same length as the number of input locations. The strings should be one of the following: `'discrete'` or `'continuous'`. 

        outputTypes (list of strings): Defines the type of output. This should be a list of strings that is the same length as the number of output locations. The strings should be one of the following: `'discrete'` or `'continuous'`. 


        GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 


        GUIParams (object, default=None): An optional object that carries GUI related parameters when the API is used inside the MAPIT GUI. 

        doTQDM (bool, default=True): Controls the use of TQDM progress bar for command line or notebook operation. 

      Returns:

        ndarray: MUF sequence with shape :math:`[n,j]` where :math:`n` length equal to the maximum time based on the number of material balances that could be constructed given the user provided MBP and number of samples in the input data and :math:`j` is the number of iterations given as input. The term :math:`n` is calculated by finding the minimum of each of the provided input times. 
        
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
                


      
    


    """

    # if GUIObject is not None:
    #     Loc = GUIparams.Loc
    #     GUIObject.PB.setValue(0)
    #     GUIObject.StatDlg.UpdateDispText('Calculating ' + GUIparams.labels['Box12L'])
    #     QtCore.QCoreApplication.instance().processEvents()
    #     GUIObject.PB.setValue(0)

        #removes extra elements
        #these are len(lists) = locations
        # and each element in the list is [MxN]
        # M = iterations
        # N = samples

    if GUIObject is not None:
      doTQDM = False
     

    #if one of the datasets are a list
    #then need check them all to figure
    #out how long the imported data is
    #as it cannot be assumed (len(data)) = time

    iterations = inputAppliedError[0].shape[0]

    A1 = np.max(np.asarray(list(chain.from_iterable(processedInputTimes))))  #unroll list
    A2 = np.max(np.asarray(list(chain.from_iterable(processedInventoryTimes))))
    A3 = np.max(np.asarray(list(chain.from_iterable(processedOutputTimes))))


    timeSteps = np.round(np.max(np.array([A1, A2, A3])))


    MBPs = np.ceil(timeSteps / MBP)


    MUF = np.zeros((iterations, int(MBP * MBPs)))




    loopcounter = 0
    totalloops = ((MBPs-1)*(len(inputAppliedError)+len(outputAppliedError)+len(inventoryAppliedError)))
    # start MUF calc here
    # sum(input) - sum(output) - delta(inventory)
    # use data from (i-1):i to set MUF for period i:i+1
    #TODO: this needs to be updated for csv

    if doTQDM and ispar == False:
       pbar = tqdm(desc="MUF", total=int(totalloops), leave=True, bar_format = "{desc:10}: {percentage:06.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=None)

    #-------------------------------------------------------------------------------#
    #------------------------------  MUF Calculation  ------------------------------#
    #-------------------------------------------------------------------------------#

    MUFTermHolder0 = []
    MUFTermHolder1 = []

    for i in range(1, int(MBPs)):  #each MBP


      #------------ Input terms ------------#
      for j in range(0, len(inputAppliedError)):  #for each location -- have to do individually because the elements is per location in the list

        if GUIObject is not None:
          GUIObject.progress.emit(loopcounter / totalloops*100)
          loopcounter+=1
        if doTQDM:
          if ispar == False:
            pbar.update(1)

        #select the indices for the relevant time
        # TODO: convert tile to broadcasting in some places
        # because broadcasting is quicker and more memory efficient
        # than tiling
        logicalInterval = np.logical_and(
            processedInputTimes[j] >= MBP * (i - 1),
            processedInputTimes[j] <= MBP * i).reshape((-1,))  

        if inputTypes[j] == 'continuous':
          MUF[:, i * MBP:(i + 1) * MBP] += AuxFunctions.trapSum(logicalInterval,processedInputTimes[j],inputAppliedError[j])[:, np.newaxis]
        elif inputTypes[j] == 'discrete':
          MUF[:, i * MBP:(i + 1) * MBP] += inputAppliedError[j][:, logicalInterval].sum(axis=1)[:,np.newaxis]
        else:
          raise Exception("inputTypes[j] is not 'continuous' or 'discrete'")
           


      #------------ Output terms ------------#
      for j in range(0, len(outputAppliedError)):
        
        if GUIObject is not None:
          GUIObject.progress.emit(loopcounter / totalloops*100)
          loopcounter+=1
        if doTQDM:
          if ispar == False:
            pbar.update(1)

        logicalInterval = np.logical_and(
            processedOutputTimes[j] >= MBP * (i - 1),
            processedOutputTimes[j] <= MBP * i).reshape((-1,))
        
        if outputTypes[j] == 'continuous':
          MUF[:, i * MBP:(i + 1) * MBP] -= AuxFunctions.trapSum(logicalInterval,processedOutputTimes[j],outputAppliedError[j])[:, np.newaxis]
        elif outputTypes[j] == 'discrete':
          MUF[:, i * MBP:(i + 1) * MBP] -= outputAppliedError[j][:, logicalInterval].sum(axis=1)[:,np.newaxis]
        else:
          raise Exception("outputTypes[j] is not 'continuous' or 'discrete'")




      #------------ Inventory terms ------------#
      for j in range(0, len(inventoryAppliedError)):

        if GUIObject is not None:
          GUIObject.progress.emit(loopcounter / totalloops*100)
          loopcounter+=1
        if doTQDM:
          if ispar == False:
            pbar.update(1)

        startIdx = np.abs(processedInventoryTimes[j].reshape((-1,)) - MBP *
                        (i - 1)).argmin()
        endIdx = np.abs(processedInventoryTimes[j].reshape((-1,)) -
                      MBP * i).argmin()

        # if i == 1:
        #   MUF[:, i * MBP:(i + 1) * MBP] -= \
        #   (inventoryAppliedError[j][:, endIdx])[:, np.newaxis]

        # else:
        MUF[:, i * MBP:(i + 1) * MBP] -= \
        (inventoryAppliedError[j][:, endIdx] - inventoryAppliedError[j][:, startIdx])[:, np.newaxis]





    return MUF


def ActiveInventory(inputAppliedError,processedInputTimes,inventoryAppliedError,processedInventoryTimes,outputAppliedError,processedOutputTimes,MBP,inputTypes,outputTypes,GUIObject=None,doTQDM=True,ispar=False):




    #if one of the datasets are a list
    #then need check them all to figure
    #out how long the imported data is
    #as it cannot be assumed (len(data)) = time

    iterations = inputAppliedError[0].shape[0]

    A1 = np.max(np.asarray(list(chain.from_iterable(processedInputTimes))))  #unroll list
    A2 = np.max(np.asarray(list(chain.from_iterable(processedInventoryTimes))))
    A3 = np.max(np.asarray(list(chain.from_iterable(processedOutputTimes))))


    timeSteps = np.round(np.max(np.array([A1, A2, A3])))

    MBPs = np.ceil(timeSteps / MBP)
    AI = np.zeros((iterations, int(MBP * MBPs)))

    loopcounter = 0
    totalloops = ((MBPs-1)*(len(inputAppliedError)+len(outputAppliedError)+len(inventoryAppliedError)))
    
    if GUIObject is not None:
      doTQDM = False

    if doTQDM and ispar == False:
      pbar = tqdm(desc="Active Inventory", total=int(totalloops), leave=True, bar_format = "{desc:10}: {percentage:06.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=None)

    for i in range(1, int(MBPs)):  #each MBP
        for j in range(0, len(inputAppliedError)):  

          if GUIObject is not None:
            GUIObject.progress.emit(loopcounter / totalloops*100)
            loopcounter+=1
          if doTQDM:
            if ispar == False:
              pbar.update(1)

          logicalInterval = np.logical_and(
              processedInputTimes[j] >= MBP * (i - 1),
              processedInputTimes[j] <= MBP * i).reshape((-1,))  


          if inputTypes[j] == 'continuous':
            AI[:, i * MBP:(i + 1) * MBP] += AuxFunctions.trapSum(logicalInterval,processedInputTimes[j],inputAppliedError[j])[:, np.newaxis]
          elif inputTypes[j] == 'discrete':
            AI[:, i * MBP:(i + 1) * MBP] += inputAppliedError[j][:, logicalInterval].sum(axis=1)[:,np.newaxis]
          else:
            raise Exception("inputTypes[j] is not 'continuous' or 'discrete'")

        
        for j in range(0, len(outputAppliedError)):

          if GUIObject is not None:
            GUIObject.progress.emit(loopcounter / totalloops*100)
            loopcounter+=1
          if doTQDM:
            if ispar == False:
              pbar.update(1)

          logicalInterval = np.logical_and(
              processedOutputTimes[j] >= MBP * (i - 1),
              processedOutputTimes[j] <= MBP * i).reshape((-1,))

        if outputTypes[j] == 'continuous':
          AI[:, i * MBP:(i + 1) * MBP] += AuxFunctions.trapSum(logicalInterval,processedOutputTimes[j],outputAppliedError[j])[:, np.newaxis]
        elif outputTypes[j] == 'discrete':
          AI[:, i * MBP:(i + 1) * MBP] += outputAppliedError[j][:, logicalInterval].sum(axis=1)[:,np.newaxis]
        else:
          raise Exception("outputTypes[j] is not 'continuous' or 'discrete'")
        
        for j in range(0, len(inventoryAppliedError)):

          if GUIObject is not None:
            GUIObject.progress.emit(loopcounter / totalloops*100)
            loopcounter+=1
          if doTQDM:
            if ispar == False:
              pbar.update(1)

          startIdx = np.abs(processedInventoryTimes[j].reshape((-1,)) - MBP *
                          (i - 1)).argmin()
          endIdx = np.abs(processedInventoryTimes[j].reshape((-1,)) -
                        MBP * i).argmin()

          if i == 1:
              AI[:, i * MBP:(i + 1) * MBP] += \
              (inventoryAppliedError[j][:, endIdx])[:, np.newaxis]

          else:
              AI[:, i * MBP:(i + 1) * MBP] += \
              (inventoryAppliedError[j][:, endIdx] - inventoryAppliedError[j][:, startIdx])[:, np.newaxis]



    return AI

def CUMUF(MUF,GUIObject=None,doTQDM=True, ispar=False):
  """

      This function performs the cumulative MUF test. This is simply the sum of all previous MUF values at a particular time. 

      :math:`\\text{CUMUF}_t = \sum_{t=0}^t \\text{MUF}_t` 

      Args:
        MUF (ndarray): MUF sequence with shape :math:`[n,j]` where :math:`n` is the number of iterations and :math:`j` is the temporal dimension. Expects a continuous valued MUF sequence that is similar in format to what is returned by `core.StatsTests.MUF`.

        GUIParams (object, default=None): An optional object that carries GUI related parameters when the API is used inside the MAPIT GUI. 

        doTQDM (bool, default=True): Controls the use of TQDM progress bar for command line or notebook operation. 

      Returns:
        ndarray: CUMUF sequence with identical shape to the input MUF.

  """


  if GUIObject is not None:
    doTQDM = False  

  z = np.diff(MUF[0,])
  idxs = np.concatenate(([0,],np.argwhere(z!=0).squeeze().reshape((-1,)),[int(MUF.shape[1]-1),])).astype(int)
  cumuf = np.zeros_like(MUF)

  if doTQDM and ispar == False:
      pbar = tqdm(desc="CUMUF", total=int(len(idxs)-1), leave=True, bar_format = "{desc:10}: {percentage:06.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=None)



  for i in range(1,len(idxs)): 
    cumuf[:,idxs[i-1]:idxs[i]] = (cumuf[:,idxs[i-1]-1] + MUF[:,idxs[i]])[:, np.newaxis] * np.ones((1, int(idxs[i] - idxs[i-1])))

    if GUIObject is not None:
      GUIObject.progress.emit(i/(len(idxs)-1))
    if doTQDM:
      if ispar == False:
        pbar.update(1)



  #HACK: this is just due to how the indexing was done above
  #particularly due to the final index
  cumuf[:,-1] = cumuf[:,-2]


  
  return cumuf


def SEMUF(inputAppliedError,processedInputTimes,inventoryAppliedError,processedInventoryTimes,outputAppliedError,processedOutputTimes,MBP,inputTypes,outputTypes,ErrorMatrix,GUIObject=None,doTQDM=True,ispar=False):
      """
        Function for calculating standard error of the material balance sequence (often called SEID or Standard Error of Inventory Difference; :math:`\\sigma _\\text{ID}`). This is accomplished by assuming the error incurred at each location (specified in the ErrorMatrix) rather than estimating it emperically, which is difficult in practice. The equation used here is suitable for most traditional bulk facilities such as enrichment or reprocessing where input and output flows are independent. This function should **not** be used for facilitiy types where there are more complex statistical dependencies between input, inventory, and output terms (e.g., molten salt reactors). See guide XX for more information.

        Args:

          inputAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of input locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites (as opposed to ground truths). Inputs are assumed to be flows in units of :math:`\\frac{1}{s}` and will be integrated. 


          processedInputTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of input locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedInputTimes)` and the shape of each list entry (ndarray) should be the same as for `inputAppliedError`. Each entry in the ndarray should correspond to a timestamp indicating when the value was taken. 


          inventoryAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of inventory locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites. Inventories are assumed to be in units of mass and will *not* be integrated.


          processedInventoryTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of inventory locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedInventoryTimes)` and shape of each list entry (ndarray) should be the same as for `inventoryAppliedError`. Each entry in the ndarray should corresond to a timestamp indicating when the value was taken. 


          outputAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of output locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites. Outputs are assumed to be in flows with units of :math:`\\frac{1}{s}` and will be integrated.


          processedOutputTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of output locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedOutputTimes)` and shape of each list entry (ndarray) should be the same as for `outputAppliedError`. Each entry in the ndarray should correspond to a timestamp indicating when the value was taken. 


          MBP (float): Defines the material balance period. 

          inputTypes (list of strings): Defines the type of input. This should be a list of strings that is the same length as the number of input locations. The strings should be one of the following: `'discrete'` or `'continuous'`. 

          outputTypes (list of strings): Defines the type of output. This should be a list of strings that is the same length as the number of output locations. The strings should be one of the following: `'discrete'` or `'continuous'`. 

          ErrorMatrix (ndarray): mx1 A ndarray shaped :math:`[M,2]` where :math:`M` is the *total* number of locations across inputs, inventories, and outputs stacked together (in that order) and 2 refers to the relative random and systematic errors. For example with 2 inputs, 2 inventories, and 2 outputs, ErrorMatrix[3,1] would be the relative systematic error of inventory 2. See guide XX for more information. 


          GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 


          GUIParams (object, default=None): An optional object that carries GUI related parameters when the API is used inside the MAPIT GUI. 

          doTQDM (bool, default=True): Controls the use of TQDM progress bar for command line or notebook operation. 

        Returns:

          (tuple): tuple containing:

            SEID (ndarray): sequence with shape :math:`[n,j,1]` where :math:`n` is the number of material balances and :math:`j` is the number of iterations given as input. The term :math:`n` is calculated by finding the minimum of each of the provided input times. 

            SEMUFContribR (ndarray): the random contribution to the overall SEMUF with shape :math:`[j,l,n]` where :math:`j` is the number of iterations given as input, :math:`l` is the total number of locations stacked in the order [inputs, inventories, outputs] and :math:`n` is the number of material balances. 

            SEMUFContribS (ndarray): the systematic contribution to the overall SEMUF with shape :math:`[j,l,n]` where :math:`j` is the number of iterations given as input, :math:`l` is the total number of locations stacked in the order [inputs, inventories, outputs] and :math:`n` is the number of material balances. 

            ObservedValues (ndarray): the observed values used to calculate SEMUF with shape :math:`[j,l,n]` where :math:`j` is the number of iterations given as input, :math:`l` is the total number of locations stacked in the order [inputs, inventories, outputs] and :math:`n` is the number of material balances. 



      """

      if GUIObject is not None:
        doTQDM = False
      

      



      TotalLocs = len(inputAppliedError)+len(inventoryAppliedError) + len(outputAppliedError)
      iterations = inputAppliedError[0].shape[0]


      A1 = np.max(np.asarray(list(chain.from_iterable(processedInputTimes))))  #unroll list
      A2 = np.max(np.asarray(list(chain.from_iterable(processedInventoryTimes))))
      A3 = np.max(np.asarray(list(chain.from_iterable(processedOutputTimes))))
      timeSteps = np.round(np.max(np.array([A1, A2, A3])))


      MBPs = np.ceil(timeSteps / MBP)

      #SEMUF contribution from individual components is difficult to
      #determine in some ways, but it is assumed that, for example,
      #the random component is (value)**2 * (rand)**2
      #probably reasonable for a simple MB, but changes if
      #covariance arises
      SEMUFCalcs = np.zeros((iterations, int(MBPs * MBP)))
      SEMUFContribR = np.zeros((iterations, TotalLocs, int(MBPs)))
      SEMUFContribS = np.zeros((iterations, TotalLocs, int(MBPs)))
      SEMUFContribI = np.zeros((iterations, TotalLocs, int(MBPs)))

      # SEID is the sqrt of Input Variance + Inventory Variance + Output Variance
      # sys and rand are the error for the measurement tech
      # Variance is (observed_value)^2 * (sys^2 + rand^2) for in and out
      # first inv is
      # (inventory^2) * (sys^2 +rand^2)
      # else
      # (Begin^2+End^2) * (sys^2 + rand^2)


      loopcounter = 0
      totalloops = ((MBPs-1)*(len(inputAppliedError)+len(outputAppliedError)+len(inventoryAppliedError)))

      if doTQDM and ispar == False:
        pbar = tqdm(desc="Sigma MUF", total=int(totalloops), leave=True, bar_format = "{desc:10}: {percentage:06.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=None)


      InpVar = np.zeros((iterations,int(MBPs * MBP)))
      InvVar = np.zeros((iterations,int(MBPs * MBP)))
      OutVar = np.zeros((iterations,int(MBPs * MBP)))

      #-------------------------------------------------------------------------------#
      #------------------------------  SEID Calculation  -----------------------------#
      #-------------------------------------------------------------------------------#

      for i in range(1, int(MBPs)):  #for each location

        #------------ Input terms ------------#
        for j in range(0, len(inputAppliedError)):  #MBPs
          locMatrixRow = j

          if GUIObject is not None:
            GUIObject.progress.emit(loopcounter / totalloops*100)
            loopcounter+=1
          if doTQDM:
            if ispar == False:
              pbar.update(1)


          logicalInterval = np.logical_and(
              processedInputTimes[j] >= MBP * (i - 1),
              processedInputTimes[j] <= MBP * i).reshape((-1,))  #select the indices for the relevant time


          if inputTypes[j] == 'continuous':
            AFTS = AuxFunctions.trapSum(logicalInterval,processedInputTimes[j],inputAppliedError[j])
          elif inputTypes[j] == 'discrete':
            AFTS = inputAppliedError[j][:, logicalInterval].sum(axis=1)
          else:
            raise Exception("inputTypes[j] is not 'continuous' or 'discrete'")
          
          VR = AFTS**2 * ErrorMatrix[j, 0]**2
          VS = AFTS**2 * ErrorMatrix[j, 1]**2

          #variance is stored as a function of time, but contributions are
          #stored per MBP which makes it easier to put in a table later
          #especially considering the time might be variable
          InpVar[:,i * MBP:(i + 1) * MBP] += ((VR + VS) * np.ones((MBP,iterations))).T
          SEMUFContribR[:, j, i] = VR
          SEMUFContribS[:, j, i] = VS
          SEMUFContribI[:, j, i] = AFTS


        #------------ Inventory terms ------------#
        for j in range(0, len(inventoryAppliedError)):

          locMatrixRow = j + len(inputAppliedError)
          startIdx = np.abs(processedInventoryTimes[j].reshape((-1,)) - MBP *(i - 1)).argmin()
          endIdx = np.abs(processedInventoryTimes[j].reshape((-1,)) -   MBP * i).argmin()

          if GUIObject is not None:
            GUIObject.progress.emit(loopcounter / totalloops*100)
            loopcounter+=1
          if doTQDM:
            if ispar == False:
              pbar.update(1)


          if i == 1:
            VR = inventoryAppliedError[j][:, endIdx]**2 * ErrorMatrix[locMatrixRow, 0]**2
            VS = inventoryAppliedError[j][:, endIdx]**2 * ErrorMatrix[locMatrixRow, 1]**2

            SEMUFContribI[:, j + len(inputAppliedError), i] = inventoryAppliedError[j][:, endIdx]

          else:

            VR = (inventoryAppliedError[j][:, startIdx]**2 + inventoryAppliedError[j][:, endIdx]**2) * ErrorMatrix[locMatrixRow, 0]**2
            VS = (inventoryAppliedError[j][:, startIdx]**2 + inventoryAppliedError[j][:, endIdx]**2) * ErrorMatrix[locMatrixRow, 1]**2

            SEMUFContribI[:, j + len(inputAppliedError), i] = inventoryAppliedError[j][:, endIdx]

          SEMUFContribR[:, j + len(inputAppliedError), i] = VR
          SEMUFContribS[:, j + len(inputAppliedError), i] = VS
          InvVar[:,i * MBP:(i + 1) * MBP] += ((VR + VS) * np.ones((MBP,iterations))).T


        #------------ Output terms ------------#
        for j in range(0, len(outputAppliedError)):
          logicalInterval = np.logical_and(
              processedOutputTimes[j] >= MBP * (i - 1),
              processedOutputTimes[j] <= MBP * i).reshape((-1,))

          locMatrixRow = j + len(inputAppliedError) + len(inventoryAppliedError)

          if GUIObject is not None:
            GUIObject.progress.emit(loopcounter / totalloops*100)
            loopcounter+=1
          if doTQDM:
            if ispar == False:
              pbar.update(1)


          if outputTypes[j] == 'continuous':
            AFTS = AuxFunctions.trapSum(logicalInterval,processedOutputTimes[j],outputAppliedError[j])
          elif outputTypes[j] == 'discrete':
            AFTS = outputAppliedError[j][:, logicalInterval].sum(axis=1)
          else:
            raise Exception("outputTypes[j] is not 'continuous' or 'discrete'")
          VR = AFTS**2 * ErrorMatrix[locMatrixRow, 0]**2
          VS = AFTS**2 * ErrorMatrix[locMatrixRow, 1]**2


          OutVar[:,i * MBP:(i + 1) * MBP] += ((VR + VS) * np.ones((MBP,iterations))).T
          SEMUFContribR[:, j + len(inputAppliedError) + len(inventoryAppliedError), i] = VR
          SEMUFContribS[:, j + len(inputAppliedError) + len(inventoryAppliedError), i] = VS
          SEMUFContribI[:, j + len(inputAppliedError) + len(inventoryAppliedError), i] = AFTS




      SEMUFCalcs = np.sqrt(InpVar + InvVar + OutVar)

      return SEMUFCalcs, SEMUFContribR, SEMUFContribS, SEMUFContribI

#NOTE: parallel not supported given the relatively
#simple nature of the calc
def SEMUFAI(AI, SEMUF, SEMUFContribR, SEMUFContribS, MBP):

  SEMUFAI = np.zeros(np.shape(SEMUF))
  SEMUFAIContribR = np.zeros(np.shape(SEMUFContribR))
  SEMUFAIContribS = np.zeros(np.shape(SEMUFContribS))
  
  it, kmps, mbps = np.shape(SEMUFContribR)
  
  AI_MBPs = []
  for i in range(len(AI[0])):
    if i%MBP == 0:
        AI_MBPs.append(AI[:,i])
  AI_MBPs = np.transpose(np.array(AI_MBPs))

  for i in range(len(AI[0])):
    if AI[0, i] != 0:
        SEMUFAI[:, i] = SEMUF[:, i]/AI[:, i] * 100
  for j in range(1,mbps):
      for k in range(kmps):
        SEMUFAIContribR[:,k,j] = (SEMUFContribR[:, k, j])/AI_MBPs[:,j] * 100
        SEMUFAIContribS[:,k,j] = (SEMUFContribS[:, k, j])/AI_MBPs[:,j] * 100      

  return SEMUFAI, SEMUFAIContribR, SEMUFAIContribS

def SITMUF(MUF, covmatrix, MBP, GUIObject=None, doTQDM=True, ispar=False):

  """
    Function to calculate the standardized independent transformed MUF (SITMUF).

    Args:

        MUF (ndarray): The previously calculated MUF array. Should have shape [M, T] where M is the number of iterations (realizations) calculated and T is the total number of timesteps.

        covmatrix (ndarray): The covariance matrix of the data. A symmetric [M, N, N] matrix where M is the number of iterations (realizations) N is the total number of balance periods calculated.
        
        MBP (float): The material balance period.
        
        GUIObject (object, default=None): Optional object used by MAPIT GUI to warn users in the case of a Cholesky decomposition error. Defaults to None.
        
        doTQDM (bool, default=True): Whether to use a tqdm progress bar for the calculation. Defaults to True.
        
        ispar (bool, default=False): Whether to use a parallel calculation for the calculation. Defaults to False.

    Returns:

        ndarray: SITMUF sequence with shape [M, T] where M is number of iterations and T is the total number of timesteps.
  """
  if GUIObject is not None:
    doTQDM = False

  required_params = ["MUF", "covmatrix", "iterations", "nMBP", "MBP"]
  missing_params = [param for param, value in locals().items() if value is None and param in required_params]

  nMBP = covmatrix.shape[-1]

  pbar = None
  iterations = MUF.shape[0]
  if doTQDM and not ispar:
    pbar = tqdm(desc="SITMUF", total=int(iterations), leave=True, bar_format = "{desc:10}: {percentage:06.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=None)

  if missing_params:
      raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
  
  
  SITMUFCalcs = np.zeros((iterations,  int((nMBP - 1) * MBP)))

  P = int(nMBP) - 1
  for k in range(iterations):
    if GUIObject is not None:
      GUIObject.progress.emit((k+1) / (iterations+1)*100)
    tempcovmatrix = covmatrix[k,:P,:P]
    tempID = np.zeros((P,))
    
    #_sitmuf_IDs-start
    for ZR in range(0,P):
        tempID[ZR] = MUF[k,ZR*MBP]
    #_sitmuf_IDs-end

    #_sitmuf_chol-start
    try:
        V = np.linalg.cholesky(tempcovmatrix)
    #_sitmuf_chol-end
    except:                 
        if GUIObject is not None:
          msg = QtWidgets.QMessageBox()
          msg.setIcon(QtWidgets.QMessageBox.Critical)
          msg.setText("Covariance decomposition failure")
          msg.setInformativeText("This usually occurs when the material balance is not setup correctly")
          msg.setWindowTitle("Error")
          msg.exec_()
        else:
          print('Covariance decomposition failure; This usually occurs when the material balance is not setup correctly')                    
          return None

    #_sitmuf_transform-start
    SITMUF = np.matmul(np.linalg.inv(V),tempID)    
    #_sitmuf_transform-end

    for P in range(1, int(nMBP)):
      SITMUFCalcs[k,int((P - 1) * MBP):int(P * MBP)] = np.ones((MBP,)) * SITMUF[P-1]
    
    if pbar is not None:
      pbar.update(1)
    
  return SITMUFCalcs

def GEMUF_V1(MUF, covmatrix, MBP, GUIObject=None, doTQDM=True, ispar=False):
  """
  
    Function that calculates the V1 version of GEMUF. Here, only the current value of MUF is used to estimate the loss vector for the GEMUF test statistic.


    Args:

        MUF (ndarray): The previously calculated MUF array. Should have shape [M, T] where M is the number of iterations (realizations) calculated and T is the total number of timesteps.

        covmatrix (ndarray): The covariance matrix of the data. A symmetric [M, N, N] matrix where M is the number of iterations (realizations) N is the total number of balance periods calculated.
        
        MBP (float): The material balance period.

        GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 
        
        doTQDM (bool, default=True): Whether to use a tqdm progress bar for the calculation. Defaults to True.
        
        ispar (bool, default=False): Whether to use a parallel calculation for the calculation. Defaults to False.

    Returns:

        ndarray: GEMUF-V1 sequence with shape [M, T] where M is number of iterations and T is the total number of timesteps.


  """
  if GUIObject is not None:
    doTQDM = False
  required_params = ["MUF", "covmatrix", "iterations", "nMBP", "MBP"]
  missing_params = [param for param, value in locals().items() if value is None and param in required_params]

  nMBP = covmatrix.shape[-1]

  if missing_params:
      raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

  iterations = MUF.shape[0]
  pbar = None
  if doTQDM and not ispar:
    pbar = tqdm(desc="GEMUFV1", total=int(iterations), leave=True, bar_format = "{desc:10}: {percentage:06.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=None)

  GEMUFCalcsV1 = np.zeros((iterations,  int((nMBP - 1) * MBP)))
  P = int(nMBP)
  for k in range(iterations):
    if GUIObject is not None:
      GUIObject.progress.emit((k+1) / (iterations+1)*100)

    
    IDs = np.zeros((P,)) 
    IDs[0] = MUF[k, 0]
    #_GEMUF_V1-start
    for ZR in range(1, int(nMBP)):
        IDs[ZR] = MUF[k,ZR*MBP]
        tempID = IDs[:ZR]
        tempcovmatrix = covmatrix[k,:ZR,:ZR]
        ZG = np.matmul(np.matmul(np.transpose(tempID), np.linalg.inv(tempcovmatrix)), tempID)
        GEMUFCalcsV1[k,int((ZR - 1) * MBP):int(ZR * MBP)] = np.ones((MBP,)) * ZG
    #_GEMUF_V1-end



    # _GEMUF_V1-end

    if pbar is not None:
      pbar.update(1)

  return GEMUFCalcsV1

def GEMUF_V5B3(MUF, covmatrix, MBP, GUIObject=None, doTQDM=True, ispar=False):
  """
  
    Function that calculates the V5B3 version of GEMUF. A weighted window of MUF values are used to estimate the loss vector when calculating the test statistic. Note that the V5B3 version is only valid for only certain parts of the sequence. For example, at balance period 1 and balance period 2, V5B3 cannot be calculated as there isn't two past values to weigh. Similarly, V5B3 can't be calculated for the last two balance periods. Rather than modifying this from Seifert's original paper, we represent those values as zero.

    .. IMPORTANT::
      The first and last two material balance periods have undefined GEMUF values when using V5B3. We represent these as zero, but they are not truely zero!


    Args:

        MUF (ndarray): The previously calculated MUF array. Should have shape [M, T] where M is the number of iterations (realizations) calculated and T is the total number of timesteps.

        covmatrix (ndarray): The covariance matrix of the data. A symmetric [M, N, N] matrix where M is the number of iterations (realizations) N is the total number of balance periods calculated.
        
        MBP (float): The material balance period.

        GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 
        
        doTQDM (bool, default=True): Whether to use a tqdm progress bar for the calculation. Defaults to True.
        
        ispar (bool, default=False): Whether to use a parallel calculation for the calculation. Defaults to False.

    Returns:

        ndarray: GEMUF-V5B3 sequence with shape [M, T] where M is number of iterations and T is the total number of timesteps.


  """
  if GUIObject is not None:
    doTQDM = False
  required_params = ["MUF", "covmatrix", "iterations", "nMBP", "MBP"]
  missing_params = [param for param, value in locals().items() if value is None and param in required_params]

  nMBP = covmatrix.shape[-1]

  if missing_params:
      raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

  iterations = MUF.shape[0]
  pbar = None
  if doTQDM and not ispar:
    pbar = pbar = tqdm(desc="GEMUFV5B3", total=int(iterations), leave=True, bar_format = "{desc:10}: {percentage:06.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=None)
  
  GEMUFCalcsV5B3 = np.zeros((iterations,  int((nMBP - 1) * MBP)))
  MSSeq = np.zeros((iterations, int(nMBP - 1)))
  P = int(nMBP)
  for k in range(iterations):
    if GUIObject is not None:
      GUIObject.progress.emit((k+1) / (iterations+1)*100)

    
    IDs = np.zeros((P,)) 
    IDs[0] = MUF[k, 0]

    for ZR in range(1, int(nMBP)):
        IDs[ZR] = MUF[k,ZR*MBP]
        tempID = IDs[:ZR]
        tempcovmatrix = covmatrix[k,:ZR,:ZR]
        IDWindow = np.zeros((5,))

        #_GEMUF_V5B3Window-start
        if ZR>=2 and ZR+2<int(nMBP):
          msc = 0
          for ZR2 in range(ZR-2,ZR+3):
            IDWindow[msc] = MUF[k, ZR2*MBP]
            msc += 1
        #_GEMUF_V5B3Window-end

        #_GEMUF_V5B3C-start
        if ZR>=2 and ZR+2<int(nMBP):
          MS = (1/7)*(IDWindow[0] + IDWindow[1] + 3*IDWindow[2] + IDWindow[3] + IDWindow[4])
          MSSeq[k,ZR] = MS
          ZG = np.matmul(np.matmul(np.transpose(MSSeq[k,:ZR].reshape((-1,))), np.linalg.inv(tempcovmatrix)), tempID)
        #_GEMUF_V5B3C-end
        else:
          ZG = np.nan
    
        GEMUFCalcsV5B3[k,int((ZR - 1) * MBP):int(ZR * MBP)] = np.ones((MBP,)) * ZG 



  
    if pbar is not None:
      pbar.update(1)

  return GEMUFCalcsV5B3


def PageTrendTest(inQty,MBP,MBPs,K=0.5,GUIObject=None,doTQDM=True):
  """
  Function for calculating Page's trend test, which is commonly applied to the SITMUF sequence. Formally compares the null hypothesis that there is no trend versus the alternate trend where there is a trend.

  Args:

    inQty (ndarray): A ndarray with shape :math:`[m,n]` where :math:`m` is the number of iterations and :math:`n` is the total number of timesteps.

    MBP (float): A float expressing the material balance period.

    MBPs (float): The total number of material balance periods present in **inQty**.

    K (float, default = 0.5): Parameter in the trend test.

    GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 

    GUIParams (object, default=None): An optional object that carries GUI related parameters when the API is used inside the MAPIT GUI. 

    doTQDM (bool, default=True): Controls the use of TQDM progress bar for command line or notebook operation. 

  Returns:
    ndarray: The results of the trend test which has shape :math:`[m,n]`. 

  """
  if GUIObject is not None:
    doTQDM = False

  PageCalcs = np.zeros((inQty.shape[0:2]))
  totalloops = int(MBPs-1) * PageCalcs.shape[0]
  loopcounter = 0

  if doTQDM:
    pbar = tqdm(total=totalloops)


      


  for k in range(PageCalcs.shape[0]):
    for P in range(1,int(MBPs)):
      
      if P == 1:
        RZN = inQty[k,int((P - 1) * MBP)]
      else:
        RZN = inQty[k,int((P - 2) * MBP)] + inQty[k,int((P - 1) * MBP)] - K
      
      if RZN < 0:
        RZN = 0
      
      PageCalcs[k,int((P - 1) * MBP):int(P * MBP)] = np.ones((MBP,)) * RZN

      if GUIObject is not None:
        GUIObject.progress.emit(loopcounter / totalloops*100)
        loopcounter+=1
      if doTQDM:
        pbar.update(1)



  return PageCalcs
  