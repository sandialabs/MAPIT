from PySide2 import QtCore, QtWidgets, QtGui
import numpy as np
from itertools import chain
from scipy.integrate import trapz
import sys
#from MAPIT_internal.GUI import GeneralOps
import MAPIT_internal.core.AuxFunctions as AuxFunctions
import MAPIT_internal.GUI.GeneralOps as GeneralOps


def MUF(inputAppliedError,processedInputTimes,inventoryAppliedError,processedInventoryTimes,outputAppliedError,processedOutputTimes,MBP,GUIObject=None,GUIparams=None):
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


        GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 


        GUIParams (object, default=None): An optional object that carries GUI related parameters when the API is used inside the MAPIT GUI. 

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

    if GUIObject is not None:
        Loc = GUIparams.Loc
        GUIObject.PB.setValue(0)
        GUIObject.StatDlg.UpdateDispText('Calculating ' + GUIparams.labels['Box12L'])
        QtCore.QCoreApplication.instance().processEvents()
        GUIObject.PB.setValue(0)

        #removes extra elements
        #these are len(lists) = locations
        # and each element in the list is [MxN]
        # M = iterations
        # N = samples

    inputAppliedError, \
    inventoryAppliedError, \
    outputAppliedError = AuxFunctions.removeExtraDims(inputAppliedError,
                                                        inventoryAppliedError,
                                                        outputAppliedError)  


    

    
  

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

    #-------------------------------------------------------------------------------#
    #------------------------------  MUF Calculation  ------------------------------#
    #-------------------------------------------------------------------------------#

    MUFTermHolder0 = []
    MUFTermHolder1 = []

    for i in range(1, int(MBPs)):  #each MBP


      #------------ Input terms ------------#
      for j in range(0, len(inputAppliedError)):  #for each location -- have to do individually because the elements is per location in the list

        if GUIObject is not None:
          GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,totalloops)

        #select the indices for the relevant time
        logicalInterval = np.logical_and(
            processedInputTimes[j] >= MBP * (i - 1),
            processedInputTimes[j] <= MBP * i).reshape((-1,))  


        MUF[:, i * MBP:(i + 1) * MBP] += \
        np.tile(AuxFunctions.trapSum(logicalInterval,processedInputTimes[j],inputAppliedError[j]), (MBP, 1)).transpose()


      #------------ Output terms ------------#
      for j in range(0, len(outputAppliedError)):
        
        if GUIObject is not None:
          GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,totalloops)

        logicalInterval = np.logical_and(
            processedOutputTimes[j] >= MBP * (i - 1),
            processedOutputTimes[j] <= MBP * i).reshape((-1,))

        MUF[:, i * MBP:(i + 1) * MBP] -= \
        np.tile(AuxFunctions.trapSum(logicalInterval,processedOutputTimes[j],outputAppliedError[j]), (MBP, 1)).transpose()


      #------------ Inventory terms ------------#
      for j in range(0, len(inventoryAppliedError)):

        if GUIObject is not None:
          GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,totalloops)

        startIdx = np.abs(processedInventoryTimes[j].reshape((-1,)) - MBP *
                        (i - 1)).argmin()
        endIdx = np.abs(processedInventoryTimes[j].reshape((-1,)) -
                      MBP * i).argmin()

        if i == 1:
          MUF[:, i * MBP:(i + 1) * MBP] -= \
          np.tile((inventoryAppliedError[j][:, endIdx]), (MBP, 1)).transpose()

        else:
          MUF[:, i * MBP:(i + 1) * MBP] -= \
          np.tile((inventoryAppliedError[j][:, endIdx] - inventoryAppliedError[j][:, startIdx]), (MBP, 1)).transpose()


    if GUIObject is not None:
      GUIObject.StatDlg.UpdateDispText('Finished '+ GUIparams.labels['Box12L'] +  ' Calculation')
      GUIObject.PB.setValue(100)      
      QtCore.QCoreApplication.instance().processEvents()

    return MUF


def ActiveInventory(inputAppliedError,processedInputTimes,inventoryAppliedError,processedInventoryTimes,outputAppliedError,processedOutputTimes,MBP,GUIObject=None,GUIparams=None):

    if GUIObject is not None:
        Loc = GUIparams.Loc
        GUIObject.PB.setValue(0)
        GUIObject.StatDlg.UpdateDispText('Calculating ' + GUIparams.labels['Box13L'])
        QtCore.QCoreApplication.instance().processEvents()
        GUIObject.PB.setValue(0)


    inputAppliedError, \
    inventoryAppliedError, \
    outputAppliedError = AuxFunctions.removeExtraDims(inputAppliedError,
                                                        inventoryAppliedError,
                                                        outputAppliedError)  
    
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

    for i in range(1, int(MBPs)):  #each MBP
        for j in range(0, len(inputAppliedError)):  

          if GUIObject is not None:
            GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,totalloops)

          logicalInterval = np.logical_and(
              processedInputTimes[j] >= MBP * (i - 1),
              processedInputTimes[j] <= MBP * i).reshape((-1,))  

          AI[:, i * MBP:(i + 1) * MBP] += \
          np.tile(AuxFunctions.trapSum(logicalInterval,processedInputTimes[j],inputAppliedError[j]), (MBP, 1)).transpose()

        
        for j in range(0, len(outputAppliedError)):

          if GUIObject is not None:
            GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,totalloops)

          logicalInterval = np.logical_and(
              processedOutputTimes[j] >= MBP * (i - 1),
              processedOutputTimes[j] <= MBP * i).reshape((-1,))

          AI[:, i * MBP:(i + 1) * MBP] += \
          np.tile(AuxFunctions.trapSum(logicalInterval,processedOutputTimes[j],outputAppliedError[j]), (MBP, 1)).transpose()
        
        for j in range(0, len(inventoryAppliedError)):

          if GUIObject is not None:
            GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,totalloops)
          startIdx = np.abs(processedInventoryTimes[j].reshape((-1,)) - MBP *
                          (i - 1)).argmin()
          endIdx = np.abs(processedInventoryTimes[j].reshape((-1,)) -
                         MBP * i).argmin()

          if i == 1:
              AI[:, i * MBP:(i + 1) * MBP] += \
              np.tile((inventoryAppliedError[j][:, endIdx]), (MBP, 1)).transpose()

          else:
              AI[:, i * MBP:(i + 1) * MBP] += \
              np.tile((inventoryAppliedError[j][:, endIdx] - inventoryAppliedError[j][:, startIdx]), (MBP, 1)).transpose()

    if GUIObject is not None:
      GUIObject.StatDlg.UpdateDispText('Finished ' + GUIparams.labels['Box13L'] + ' Calculation')
      GUIObject.PB.setValue(100)      
      QtCore.QCoreApplication.instance().processEvents()

    return AI


def CUMUF(MUF,GUIObject=None, GUIparams=None):
  """

      This function performs the cumulative MUF test. This is simply the sum of all previous MUF values at a particular time. 

      :math:`\\text{CUMUF}_t = \sum_{t=0}^t \\text{MUF}_t` 

      Args:
        MUF (ndarray): MUF sequence with shape :math:`[n,j]` where :math:`n` is the number of iterations and :math:`j` is the temporal dimension. Expects a continuous valued MUF sequence that is similar in format to what is returned by `core.StatsTests.MUF`.

        GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 


        GUIParams (object, default=None): An optional object that carries GUI related parameters when the API is used inside the MAPIT GUI. 

      Returns:
        ndarray: CUMUF sequence with identical shape to the input MUF.

  """

  if GUIObject is not None:
    GUIObject.PB.setValue(0)
    GUIObject.StatDlg.UpdateDispText('Calculating ' +  GUIparams.labels['Box14L'])
    QtCore.QCoreApplication.instance().processEvents()
    GUIObject.PB.setValue(0)
  
  z = np.diff(MUF[0,])
  idxs = np.concatenate(([0,],np.argwhere(z!=0).squeeze(),[int(MUF.shape[1]-1),])).astype(int)
  cumuf = np.zeros_like(MUF)



  for i in range(1,len(idxs)): 
    cumuf[:,idxs[i-1]:idxs[i]] = np.tile(cumuf[:,idxs[i-1]-1] + MUF[:,idxs[i]],
                                          (int(idxs[i] - idxs[i-1]),1)).swapaxes(0,1)

    if GUIObject is not None:
      GUIObject.PB.setValue(i/(len(idxs)-1))


  #HACK: this is just due to how the indexing was done above
  #particularly due to the final index
  cumuf[:,-1] = cumuf[:,-2]

  if GUIObject is not None:
    GUIObject.StatDlg.UpdateDispText('Finished ' + GUIparams.labels['Box14L'] + ' Calculation')
    GUIObject.PB.setValue(100)      
    QtCore.QCoreApplication.instance().processEvents()
  
  return cumuf

  
def SEMUF(inputAppliedError,processedInputTimes,inventoryAppliedError,processedInventoryTimes,outputAppliedError,processedOutputTimes,MBP,ErrorMatrix,GUIObject=None,GUIparams=None):
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

          ErrorMatrix (ndarray): mx1 A ndarray shaped :math:`[M,2]` where :math:`M` is the *total* number of locations across inputs, inventories, and outputs stacked together (in that order) and 2 refers to the relative random and systematic errors. For example with 2 inputs, 2 inventories, and 2 outputs, ErrorMatrix[3,1] would be the relative systematic error of inventory 2. See guide XX for more information. 


          GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 


          GUIParams (object, default=None): An optional object that carries GUI related parameters when the API is used inside the MAPIT GUI. 

        Returns:

          (tuple): tuple containing:

            SEID (ndarray): sequence with shape :math:`[n,j,1]` where :math:`n` is the number of material balances and :math:`j` is the number of iterations given as input. The term :math:`n` is calculated by finding the minimum of each of the provided input times. 

            SEMUFContribR (ndarray): the random contribution to the overall SEMUF with shape :math:`[j,l,n]` where :math:`j` is the number of iterations given as input, :math:`l` is the total number of locations stacked in the order [inputs, inventories, outputs] and :math:`n` is the number of material balances. 

            SEMUFContribS (ndarray): the systematic contribution to the overall SEMUF with shape :math:`[j,l,n]` where :math:`j` is the number of iterations given as input, :math:`l` is the total number of locations stacked in the order [inputs, inventories, outputs] and :math:`n` is the number of material balances. 

            ObservedValues (ndarray): the observed values used to calculate SEMUF with shape :math:`[j,l,n]` where :math:`j` is the number of iterations given as input, :math:`l` is the total number of locations stacked in the order [inputs, inventories, outputs] and :math:`n` is the number of material balances. 



      """

      if GUIObject is not None:
        GUIObject.StatDlg.UpdateDispText('Calculating ' + GUIparams.labels['Box15L'])
        QtCore.QCoreApplication.instance().processEvents()
        Loc = GUIparams.Loc

      inputAppliedError, \
      inventoryAppliedError, \
      outputAppliedError = AuxFunctions.removeExtraDims(inputAppliedError,
                                                          inventoryAppliedError,
                                                          outputAppliedError)  



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
            GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,totalloops)


          logicalInterval = np.logical_and(
              processedInputTimes[j] >= MBP * (i - 1),
              processedInputTimes[j] <= MBP * i).reshape((-1,))  #select the indices for the relevant time

          AFTS = AuxFunctions.trapSum(logicalInterval,processedInputTimes[j],inputAppliedError[j])
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
            GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,totalloops)


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

          locMatrixRow = j + len(inputAppliedError) + len(outputAppliedError)

          if GUIObject is not None:
            GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,totalloops)


          AFTS = AuxFunctions.trapSum(logicalInterval,processedOutputTimes[j],outputAppliedError[j])
          VR = AFTS**2 * ErrorMatrix[locMatrixRow, 0]**2
          VS = AFTS**2 * ErrorMatrix[locMatrixRow, 1]**2


          OutVar[:,i * MBP:(i + 1) * MBP] += ((VR + VS) * np.ones((MBP,iterations))).T
          SEMUFContribR[:, j + len(inputAppliedError) + len(inventoryAppliedError), i] = VR
          SEMUFContribS[:, j + len(inputAppliedError) + len(inventoryAppliedError), i] = VS
          SEMUFContribI[:, j + len(inputAppliedError) + len(inventoryAppliedError), i] = AFTS

      SEMUFCalcs = np.sqrt(InpVar + InvVar + OutVar)


      if GUIObject is not None:
        GUIObject.StatDlg.UpdateDispText('Finished ' + GUIparams.labels['Box15L'] + ' Calculation')        
        QtCore.QCoreApplication.instance().processEvents()

      return SEMUFCalcs, SEMUFContribR, SEMUFContribS, SEMUFContribI


def SEMUFAI(AI, SEMUF,GUIObject=None,GUIparams=None):

  if GUIObject is not None:
    Loc = GUIparams.Loc
    GUIObject.PB.setValue(0)
    GUIObject.StatDlg.UpdateDispText('Calculating ' + GUIparams.labels['Box16L'])
    QtCore.QCoreApplication.instance().processEvents()
    GUIObject.PB.setValue(0)

  SEMUFAI = SEMUF/AI*100

  if GUIObject is not None:
    GUIObject.StatDlg.UpdateDispText('Finished ' + GUIparams.labels['Box16L'] + ' Calculation')
    GUIObject.PB.setValue(100)      
    QtCore.QCoreApplication.instance().processEvents()

  return SEMUFAI

def SITMUF(inputAppliedError,processedInputTimes,inventoryAppliedError,processedInventoryTimes,outputAppliedError,processedOutputTimes,ErrorMatrix,MUF,MBP,GUIObject=None,GUIparams=None):
      """
       Function that carries out the standardized independent transformation of MUF. More detailed information can be found in the guide XX. 

       Args: 

          inputAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of input locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites (as opposed to ground truths). Inputs are assumed to be flows in units of :math:`\\frac{1}{s}` and will be integrated. 


          processedInputTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of input locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedInputTimes)` and the shape of each list entry (ndarray) should be the same as for `inputAppliedError`. Each entry in the ndarray should correspond to a timestamp indicating when the value was taken. 


          inventoryAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of inventory locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites. Inventories are assumed to be in units of mass and will *not* be integrated.


          processedInventoryTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of inventory locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedInventoryTimes)` and shape of each list entry (ndarray) should be the same as for `inventoryAppliedError`. Each entry in the ndarray should corresond to a timestamp indicating when the value was taken. 


          outputAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of output locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites. Outputs are assumed to be in flows with units of :math:`\\frac{1}{s}` and will be integrated.


          processedOutputTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of output locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedOutputTimes)` and shape of each list entry (ndarray) should be the same as for `outputAppliedError`. Each entry in the ndarray should correspond to a timestamp indicating when the value was taken. 


          MBP (float): Defines the material balance period. 



          GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 


          GUIParams (object, default=None): An optional object that carries GUI related parameters when the API is used inside the MAPIT GUI. 

        Returns:
          ndarray: SITMUF sequence with shape :math:`[n,j]` where :math:`n` length equal to the maximum time based on the number of material balances that could be constructed given the user provided MBP and number of samples in the input data and :math:`j` is the number of iterations given as input. The term :math:`n` is calculated by finding the minimum of each of the provided input times. 
        
          For example:

          .. highlight:: python
          .. code-block:: python

            import numpy as np

            time1[-1] = 400
            time2[-1] = 300
            time3[-1] = 800

            j = np.floor(
                  np.min(
                    (time1,time2,time3)))

      """

      if GUIObject is not None:
        GUIObject.statusBar().clearMessage()
        GUIObject.StatDlg.UpdateDispText('Calculating ' + GUIparams.labels['Box17L'])
        GUIObject.PB.setValue(0)
        QtCore.QCoreApplication.instance().processEvents()

        Loc = GUIparams.Loc

      inputAppliedError, \
      inventoryAppliedError, \
      outputAppliedError = AuxFunctions.removeExtraDims(inputAppliedError,
                                                          inventoryAppliedError,
                                                          outputAppliedError)  

      decompStatus = 1
      iterations = inputAppliedError[0].shape[0]


      A1 = np.max(np.asarray(list(chain.from_iterable(processedInputTimes))))  #unroll list
      A2 = np.max(np.asarray(list(chain.from_iterable(processedInventoryTimes))))
      A3 = np.max(np.asarray(list(chain.from_iterable(processedOutputTimes))))


      timeSteps = np.round(np.max(np.array([A1, A2, A3])))


      MBPs = np.ceil(timeSteps / MBP)

      SITMUFCalcs = np.zeros((iterations,  int((MBPs - 1) * MBP)))
      PageCalcs = np.zeros((iterations,  int((MBPs - 1) * MBP)))
      covmatrix = np.zeros((int(MBPs), int(MBPs)))
      # Iterations, Locs, Samples, Elements eFrame

      #----------------------------------------- SITMUF Calculation  ----------------------------------------#
      #
      # The first part is to calculate the covariance with consists of off-diagonal and diagonal terms
      # Need to optimize this later as I think I could do better than what was originally implimented in matlab
      #
      #------------------------------------------------------------------------------------------------------#

      totalloops = ((MBPs-1)**2 + MBPs) / 2 #nth triangle number, like factorial but addition
      loopcounter = 0
      covmatrix = np.zeros((iterations,int(MBPs), int(MBPs)))


      if decompStatus == 1:

        for P in range(1,int(MBPs)):
            for j in range(0,P): 

              if GUIObject is not None:
                GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,totalloops)

                #it's easier to implement SITMUF using the actual indicies
                #from the statistical papers rather than the python loop variables
                #so this translates python loop variables to indicides and times
                #more closely aligned to the papers
              I = j + 1 
              IPrevious = j - 1               
              IPrime = P 
              IPrimePrevious = P-1

              I_time = I*MBP
              IPrevious_time = IPrevious*MBP
              IPrime_time = IPrime*MBP
              IPrimePrevious_time = IPrimePrevious*MBP




              #------------ Diagonal terms ------------#
              if j == P-1:

                  term1 = np.zeros((iterations,))
                  term2 = np.zeros((iterations,))
                  term3 = np.zeros((iterations,))
                  term4 = np.zeros((iterations,))
                  term5 = np.zeros((iterations,))

                  #------------ Input terms ------------#
                  for k in range(len(inputAppliedError)):

                      logicalInterval = np.logical_and(processedInputTimes[k] >= IPrevious_time,processedInputTimes[k] <= I_time).reshape((-1,))  #select the indices for the relevant time
                      term1 += AuxFunctions.trapSum(logicalInterval,processedInputTimes[k],inputAppliedError[k]) **2 * (ErrorMatrix[k, 0]**2 + ErrorMatrix[k, 1]**2)

                  #------------ Output terms ------------#
                  for k in range(len(outputAppliedError)):

                      logicalInterval = np.logical_and(processedOutputTimes[k] >= IPrevious_time,processedOutputTimes[k] <= I_time).reshape((-1,))
                      locMatrixRow = k + len(inputAppliedError) + len(inventoryAppliedError)

                      term2 += AuxFunctions.trapSum(logicalInterval,processedOutputTimes[k],outputAppliedError[k])**2 * (ErrorMatrix[locMatrixRow, 0]**2 + ErrorMatrix[locMatrixRow, 1]**2)

                  #------------ Inventory terms ------------#
                  for k in range(len(inventoryAppliedError)):
                      locMatrixRow = k+len(inputAppliedError)

                      startIdx = np.abs(processedInventoryTimes[k].reshape((-1,)) - IPrevious_time).argmin()
                      endIdx = np.abs(processedInventoryTimes[k].reshape((-1,)) - I_time).argmin()

                      term3 += inventoryAppliedError[k][:,endIdx]**2 * (ErrorMatrix[locMatrixRow, 0]**2 + ErrorMatrix[locMatrixRow, 1]**2)


                  if j != 0:
                      for k in range(len(inventoryAppliedError)):
                          locMatrixRow = k + len(inputAppliedError)
                          startIdx = np.abs(processedInventoryTimes[k].reshape((-1,)) -IPrevious_time).argmin()
                          endIdx = np.abs(processedInventoryTimes[k].reshape((-1,)) - I_time).argmin()

                          term4 += inventoryAppliedError[k][:,startIdx]**2 * (ErrorMatrix[locMatrixRow, 0]**2 + ErrorMatrix[locMatrixRow, 1]**2)
                          term5 += inventoryAppliedError[k][:,startIdx] * inventoryAppliedError[k][:,endIdx] * ErrorMatrix[locMatrixRow, 1]**2

                  covmatrix[:,j,j] = term1 + term2 + term3 + term4 - 2 * term5

              #------------ Off-diagonal terms ------------#
              else:
                  term1 = np.zeros((iterations,))
                  term2 = np.zeros((iterations,))
                  term3 = np.zeros((iterations,))
                  term4 = np.zeros((iterations,))
                  term5 = np.zeros((iterations,))

                  term3a = np.zeros((iterations,))
                  term3b = np.zeros((iterations,))
                  term3c = np.zeros((iterations,))

                  term4a = np.zeros((iterations,))
                  term4b = np.zeros((iterations,))
                  term4c = np.zeros((iterations,))

                  term5a = np.zeros((iterations,))
                  term5b = np.zeros((iterations,))
                  term5c = np.zeros((iterations,))

                  A = np.zeros((iterations,))
                  B = np.zeros((iterations,))
                  C = np.zeros((iterations,))

                  #------------ Input terms ------------#
                  for k in range(len(inputAppliedError)):
                      logicalInterval = np.logical_and(processedInputTimes[k] >= IPrevious_time, processedInputTimes[k] <= I_time).reshape((-1,))  #select the indices for the relevant time
                      logicalInterval2 = np.logical_and(processedInputTimes[k] >= IPrimePrevious_time, processedInputTimes[k] <= IPrime_time).reshape((-1,))  #select the indices for the relevant time

                      A = AuxFunctions.trapSum(logicalInterval, processedInputTimes[k],inputAppliedError[k])
                      B = AuxFunctions.trapSum(logicalInterval2, processedInputTimes[k],inputAppliedError[k])
                      C = ErrorMatrix[k, 1]**2
                      term1 += (A*B*C)

                  #------------ Output terms ------------#
                  for k in range(len(outputAppliedError)):
                      logicalInterval = np.logical_and(processedOutputTimes[k] >= IPrevious_time,processedOutputTimes[k] <= I_time).reshape((-1,))  #select the indices for the relevant time
                      logicalInterval2 = np.logical_and(processedOutputTimes[k] >= IPrimePrevious_time,processedOutputTimes[k] <= IPrime_time).reshape((-1,))  #select the indices for the relevant time
                      locMatrixRow = k + len(inputAppliedError) + len(inventoryAppliedError)

                      A = AuxFunctions.trapSum(logicalInterval, processedOutputTimes[k],outputAppliedError[k])
                      B = AuxFunctions.trapSum(logicalInterval2, processedOutputTimes[k],outputAppliedError[k])
                      C = ErrorMatrix[locMatrixRow, 1]**2
                      term2 += (A*B*C)

                  #------------ Inventory terms ------------#
                  for k in range(len(inventoryAppliedError)):
                      startIdx =  np.abs(processedInventoryTimes[k].reshape((-1,)) -  I_time).argmin() #I
                      endIdx = np.abs(processedInventoryTimes[k].reshape((-1,)) -  IPrime_time).argmin() 
                      startIdx2 = np.abs(processedInventoryTimes[k].reshape((-1,)) - IPrevious_time).argmin() 
                      endIdx2 = np.abs(processedInventoryTimes[k].reshape((-1,)) - IPrimePrevious_time).argmin() 
                      locMatrixRow = k + len(inputAppliedError)

                      term3a = inventoryAppliedError[k][:, startIdx] * inventoryAppliedError[k][:, endIdx]
                      term3b = inventoryAppliedError[k][:, startIdx2] * inventoryAppliedError[k][:, endIdx2]
                      term3c = ErrorMatrix[locMatrixRow, 1]**2
                      term3 += (term3a+term3b)*term3c

                      term4a = inventoryAppliedError[k][:, startIdx] * inventoryAppliedError[k][:, endIdx2]
                      term4b = ErrorMatrix[locMatrixRow, 1]**2
                      if IPrime-1 == I:
                          term4c = ErrorMatrix[locMatrixRow, 0]**2
                      else:
                          term4c = np.zeros((iterations,))


                      term4 += term4a*(term4b+term4c)

                      term5a = inventoryAppliedError[k][:, startIdx2] * inventoryAppliedError[k][:, endIdx]
                      term5b = ErrorMatrix[locMatrixRow, 1]**2

                      if I - 1 == IPrime:
                          term5c = ErrorMatrix[locMatrixRow, 0]**2
                      else:
                          term5c = np.zeros((iterations,))

                      term5 += term5a*(term5b+term5c)
                      
                      

                  covmatrix[:,j,P-1] = term1+term2+term3-term4-term5
                  covmatrix[:,P-1,j] = term1+term2+term3-term4-term5

            #------------ SITMUF Transform ------------#
            for k in range(iterations):
              tempcovmatrix = covmatrix[k,:P,:P]
              tempID = np.zeros((P,))

              for ZR in range(0,P):
                  tempID[ZR] = MUF[k,ZR*MBP]

              try:
                  V = np.linalg.cholesky(tempcovmatrix)
              except:
                  decompStatus = 0                  
                  if GUIObject is not None:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Critical)
                    msg.setText("Covariance decomposition failure")
                    msg.setInformativeText("This usually occurs when the material balance is not setup correctly")
                    msg.setWindowTitle("Error")
                    msg.exec_()
                  else:
                    print('Covariance decomposition failure; This usually occurs when the material balance is not setup correctly')                    
                    break

              SITMUF = np.matmul(np.linalg.inv(V),tempID)
              SITMUFCalcs[k,int((P - 1) * MBP):int(P * MBP)] = np.ones((MBP,)) * SITMUF[P - 1]


      if GUIObject is not None:
        GUIObject.StatDlg.UpdateDispText('Finished ' + GUIparams.labels['Box17L'] + ' Calculation')        
        QtCore.QCoreApplication.instance().processEvents()

      return SITMUFCalcs


def PageTrendTest(inQty,MBP,MBPs,K=0.5,GUIObject=None,GUIparams=None):
  """
  Function for calculating Page's trend test, which is commonly applied to the SITMUF sequence. Formally compares the null hypothesis that there is no trend versus the alternate trend where there is a trend.

  Args:

    inQty (ndarray): A ndarray with shape :math:`[m,n]` where :math:`m` is the number of iterations and :math:`n` is the total number of timesteps.

    MBP (float): A float expressing the material balance period.

    MBPs (float): The total number of material balance periods present in **inQty**.

    K (float, default = 0.5): Parameter in the trend test.

    GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 

    GUIParams (object, default=None): An optional object that carries GUI related parameters when the API is used inside the MAPIT GUI. 

  Returns:
    ndarray: The results of the trend test which has shape :math:`[m,n]`. 

  """

  PageCalcs = np.zeros((inQty.shape[0:2]))

  if GUIObject is not None:
      GUIObject.statusBar().clearMessage()
      GUIObject.StatDlg.UpdateDispText('Calculating ' + GUIparams.labels['Box18L'])
      GUIObject.PB.setValue(0)
      QtCore.QCoreApplication.instance().processEvents()
      loopcounter = 0
      nloops = int(MBPs) * PageCalcs.shape[0]

 
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
        GUIObject, loopcounter = GeneralOps.updatePB(GUIObject,loopcounter,nloops)
        GUIObject.StatDlg.UpdateDispText('Finished ' + GUIparams.labels['Box18L'] + ' Calculation')        
        QtCore.QCoreApplication.instance().processEvents()

  return PageCalcs
    