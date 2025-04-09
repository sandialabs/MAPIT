import numpy as np
from itertools import chain
from tqdm import tqdm

def trapSum(relevantIndex, time, data, IT=None, baseline_zero=1e-10):
    """
      Function performs trapezoidal integration on a dataset segment. This is required for bulk facility flows that
      might need integration before use within statistical tests.

      In some cases, flows might be represented as discontinuous pulses of material, in which case, special care
      is needed to identify the non-zero regions of the dataset to enable proper integration.

      This function first identified a list of non-zero pulses of material before performing trapezoidal integration
      on each non-zero pulse segment. `np.trapz` is used to perform the integration. See the `numpy documentation <https://numpy.org/doc/stable/reference/generated/numpy.trapz.html>`_
      for more information.

      :math:`\\int y(x) dx`

      Args:
        relevantIndex (ndarray): An array that expresses the relevant time slice, with boolean values (0 = not relevant, 1 = relevant), with shape :math:`[m,j]` where :math:`m` is the total number of relevant samples and :math:`j` is the total number of iterations.

        time(ndarray): An array containing the total number of timestep values under consideration for the analysis. Has shape :math:`[n,j]` where :math:`n` is the total number of samples under consideration and :math:`n>m` for :math:`m` in `relevantIndex` and :math:`j` is the total number of iterations.

        data (ndarray): An array containing the total number of samples under consideration for the analysis. Should have the same shape as **time**.

        baseline_zero (float): A float that expresses the threshold below which values are considered zero. Important as datasets often do not represent zero as exactly zero for a variety of reasons.

      Returns:
        ndarray: An array of shape :math:`[1,j]` containing the integrated total for each iteration over the time specified by **time[relevantIndex]**.



    """
    if IT is not None:
        IDXC = IT
    else:
        IDXC = 0

    #if no relevant times return here
    if np.sum(relevantIndex) == 0:
        return np.zeros((data.shape[0],))

    LI = np.argmin(relevantIndex == False)
    RI = len(relevantIndex) - np.argmin(relevantIndex[::-1] == False)
    relevantDataVals = data[IDXC, LI:RI:1]
    relevantDataValsAbs = np.abs(relevantDataVals)
    relevantTimeVals = time[LI:RI:1]


  #   relevantDataValsAbs = np.abs(data[IDXC,relevantIndex])
  #   relevantTimeVals = time[relevantIndex]

    # if no relevant data, stop here and return zeros
    if np.sum(relevantDataValsAbs.shape) == 0:
        None
        # return np.zeros((np.shape(data)[0],))

    # check for different scenarios
    partialLeft = False
    partialRight = False

    if relevantDataValsAbs[0] > baseline_zero:
        partialLeft = True

    if relevantDataValsAbs[-1] > baseline_zero:
        partialRight = True

    # Find the indicies associated with pulses of material
    # basically use the intersection between (near) zero regions
    # and non-zero regions to find bounds of pulses
    NZ_mask = (relevantDataValsAbs >= baseline_zero)
    Z_mask = np.abs(NZ_mask-1)

    # add padding since np rolls values around to beginning
    # and we don't want that
    Z_mask = np.roll(np.concatenate(
        (np.zeros((1,)), Z_mask, np.zeros((1,)))), 1)[1:-1]

    mask = NZ_mask*Z_mask
    LeftIndicies = np.where(mask)[0].reshape((-1, 1))

    Z_mask = np.roll(np.concatenate(
        (np.zeros((2,)), Z_mask, np.zeros((2,)))), -2)[2:-2]

    mask = NZ_mask*Z_mask
    RightIndicies = np.where(mask)[0].reshape((-1, 1))


    # partialLeft is when a pulse intersects with the left
    # bounary for time (i.e., pulse in progress during MBP opening)
    if partialLeft == True:
        if len(LeftIndicies) > 0:
            if len(RightIndicies) > 0:
                # if indicies have been found, then like len(LeftIndicies) > len(RightIndicies), so only need to specify
                # an additional corresponding left index for the first part, which is found at the first non-zero value,
                # usually index 0
                LeftIndicies = np.insert(LeftIndicies, 0, np.array(
                    [np.min(np.argwhere(relevantDataValsAbs > baseline_zero))]).astype(int), axis=0)
            else:
                # if the pulse spans the entire window, we need to specify the right index as only
                # the left will be found
                RightIndicies = np.array(
                    [len(relevantDataValsAbs)-2]).reshape((-1, 1)).astype(int)
        else:
            # if the left index isn't present, establish it. Differs from the earlier case above in that there's
            # no left indicies found yet for this case
            LeftIndicies = np.array(
                [np.min(np.where(relevantDataValsAbs > baseline_zero))]).reshape((-1, 1)).astype(int)



    # partialRight is the complementary case to partialLeft
    # same reasoning follows, just that the pulse stretches past the
    # MBP rather than streching before
    if partialRight == True:
        if len(RightIndicies) > 0:
            if len(LeftIndicies) > 0:
                RightIndicies = np.concatenate((RightIndicies,
                                                np.array([len(relevantTimeVals)-2]).reshape((1, 1)).astype(int)), axis=0)
        else:
            RightIndicies = np.array(
                len(relevantTimeVals)-1).reshape((-1, 1)).astype(int)
            if len(LeftIndicies) == 0:
                LeftIndicies = np.array([np.min(np.argwhere(
                    relevantDataValsAbs > baseline_zero))]).reshape((-1, 1)).astype(int)

    if len(RightIndicies) < len(LeftIndicies):
        RightIndicies = np.append(RightIndicies,[len(relevantDataVals)-1]).reshape((-1,1))

    pairs = np.concatenate((LeftIndicies, RightIndicies), axis=1)

    #if there's no pairs because datavals are zero then
    #return
    if len(pairs) == 0:
        assert np.sum(relevantDataVals) == 0, "There's a problem"
        return np.zeros((data.shape[0],))
    # Generally, the final interval of a pulse is required to produce the proper integration value
    # however, as MAPIT is primarly used in and around Simulink, it's been observed that in some cases,
    # simulink will not record the final part of a pulse until several time steps later.
    # this logic below checks to see if the "final" value of a pulse is more than one timestep
    # after all the other data in that pulse. If so, we ignore that part of the pulse as it
    # is an error in Simulink. If not accounted for, the integration will provide an incorrect, inflated
    # value. This occurs on the second input of the fuel fab dataset, for example.
    if len(relevantTimeVals)-1 != pairs[0, 1] and pairs[0,1]-pairs[0,0] > 1:
        if (relevantTimeVals[pairs[0, 1]+1] - relevantTimeVals[pairs[0, 1]]) <= np.max(np.diff(relevantTimeVals[pairs[0, 0]:pairs[0, 1]].squeeze())):
            pairs[:, 1] += 1

    pairs = pairs.astype(int)

    rowfordelete = []



    # remove zero length pairs
    # zero length pairs can occur in some
    # edge cases where pulses have just started
    # or ended and the pulse is undefined

    # NOTE: 7/8/2024
    # changed to be GEQ as pairs
    # that are greater than one
    # are erronous and occur when
    # the last time step of a series
    # is non-zero but the proceding is zero;
    # this is a undefined quantity for the integral
    # (since it's a point not an area) and should
    # be discarded
    for Q in range(len(pairs)):
        if pairs[Q, 0] - pairs[Q, 1] >= 0:
            rowfordelete.append(Q)

    rowfordelete = np.asarray(rowfordelete).astype(int)
    pairs = np.delete(pairs, rowfordelete, axis=0)


    # reshapping data for processing
    if IT is not None:
        dataArray = relevantDataVals.reshape((1, -1))
        timeArray = relevantTimeVals
        S0 = 1
    else:
        dataArray = np.swapaxes(data[:, LI:RI:1], 0, 1)
        bt = relevantTimeVals.reshape((-1, 1))
        S0 = dataArray.shape[1]
        #timeArray = np.repeat(bt, S0, axis=1) #required for trapz function
        timeArray = np.empty((bt.shape[0],S0),bt.dtype)
        timeArray[...] = bt

    datasegs = []
    timesegs = []



    # create a list of segments for later trapezoidal integration
    for Q in range(len(pairs)):
        timesegs.append(np.swapaxes(
            timeArray[pairs[Q, 0]:pairs[Q, 1]+1], 0, 1))
        datasegs.append(np.swapaxes(
            dataArray[pairs[Q, 0]:pairs[Q, 1]+1], 0, 1))


    traptot = np.zeros((S0,))
    # peform the numerical integration
    # the second term accounts for how the pulse is expressed in the trapz function
    # if not included it would underestimate the area
    for Q in range(len(datasegs)):
        
        if datasegs[Q][0, -1] == 0:
            traptot += (np.trapz(datasegs[Q], timesegs[Q]) + 0.5 *
                        (timesegs[Q][:, -1]-timesegs[Q][:, -2])*datasegs[Q][:, -2])
        else:
            traptot += (np.trapz(datasegs[Q], timesegs[Q]))


    return traptot


def removeExtraDims(inp,inv,out):
    inp_formatted = []
    inv_formatted = []
    out_formatted = []

    if inp[0].shape[0] == 1:
        #only 1 iteration, special
        #formatting applies
        doSingleIterate = True
    else:
        doSingleIterate = False

    for i in range(len(inp)):
        if doSingleIterate == False:
            inp_formatted.append(np.squeeze(inp[i]))
        else:
            inp_formatted.append(inp[i][:,:,0])

    for i in range(len(inv)):
        if doSingleIterate == False:
            inv_formatted.append(np.squeeze(inv[i]))
        else:
            inv_formatted.append(inv[i][:,:,0])

    for i in range(len(out)):
        if doSingleIterate == False:
            out_formatted.append(np.squeeze(out[i]))
        else:
            out_formatted.append(out[i][:,:,0])


    return inp_formatted, inv_formatted, out_formatted


def getMBPs(processedInputTimes,processedInventoryTimes,processedOutputTimes,MBP):
  
      A1 = np.max(np.asarray(list(chain.from_iterable(processedInputTimes))))  #unroll list
      A2 = np.max(np.asarray(list(chain.from_iterable(processedInventoryTimes))))
      A3 = np.max(np.asarray(list(chain.from_iterable(processedOutputTimes))))


      timeSteps = np.round(np.max(np.array([A1, A2, A3])))


      MBPs = np.ceil(timeSteps / MBP)

      return MBPs


def SEIDcontrib(inArray,loc,time,typ='error',avg=True,Iter=None,):

    if avg == True:
      out = np.mean(inArray[:,loc,time],axis=0)
    else:
      out = inArray[Iter,loc,time]

    if typ=='error':
      out = np.sqrt(out)
    
    return out
  
def calcCovMat(inputAppliedError, inventoryAppliedError, outputAppliedError, processedInputTimes, processedInventoryTimes, processedOutputTimes, ErrorMatrix, MBP, inputTypes, outputTypes, GUIObject=None, doTQDM=True,ispar=False):
    """    
        Function to calculate the material balance covariance matrix. 

        Args: 
            inputAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of input locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites (as opposed to ground truths). Inputs are assumed to be flows in units of :math:`\\frac{1}{s}` and will be integrated. 


            processedInputTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of input locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedInputTimes)` and the shape of each list entry (ndarray) should be the same as for `inputAppliedError`. Each entry in the ndarray should correspond to a timestamp indicating when the value was taken. 


            inventoryAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of inventory locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites. Inventories are assumed to be in units of mass and will *not* be integrated.


            processedInventoryTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of inventory locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedInventoryTimes)` and shape of each list entry (ndarray) should be the same as for `inventoryAppliedError`. Each entry in the ndarray should corresond to a timestamp indicating when the value was taken. 


            outputAppliedError (list of ndarrays): A list of ndarrays that has length equal to the total number of output locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. This array should reflect observed quantites. Outputs are assumed to be in flows with units of :math:`\\frac{1}{s}` and will be integrated.


            processedOutputTimes (list of ndarrays): A list of ndarrays that has length equal to the total number of output locations. Each array should be :math:`[m,1]` in shape where :math:`m` is the number of samples. `len(processedOutputTimes)` and shape of each list entry (ndarray) should be the same as for `outputAppliedError`. Each entry in the ndarray should correspond to a timestamp indicating when the value was taken. 

            ErrorMatrix (ndarray): mx1 A ndarray shaped :math:`[M,2]` where :math:`M` is the *total* number of locations across inputs, inventories, and outputs stacked together (in that order) and 2 refers to the relative random and systematic errors. For example with 2 inputs, 2 inventories, and 2 outputs, ErrorMatrix[3,1] would be the relative systematic error of inventory 2. See guide XX for more information. 

            MBP (float): Defines the material balance period. 
            
            inputTypes (list of strings): Defines the type of input. This should be a list of strings that is the same length as the number of input locations. The strings should be one of the following: `'discrete'` or `'continuous'`. 

            outputTypes (list of strings): Defines the type of output. This should be a list of strings that is the same length as the number of output locations. The strings should be one of the following: `'discrete'` or `'continuous'`. 

            GUIObject (object, default=None): An optional object that carries GUI related references when the API is used inside the MAPIT GUI. 

            doTQDM (bool, default=True): Controls the use of TQDM progress bar for command line or notebook operation. 

            isPar (bool, default=False): Flag indicating if the function is being run in a parallel context. Only controls output formatting.

        Returns:
            (tuple):         
                * SITMUF sequence (ndarray if `doSITMUF` otherwise None): SITMUF sequence with the shape :math:`[n,j]` where :math:`n` is the length equal to the maximum time based on the number of material balances that could be constructed given the user-provided MBP and number of samples in the input data, and :math:`j` is the number of iterations given as input.
                
                * GEMUF sequence (ndarray if `doGEMUF` otherwise None): GEMUF sequence with the shape :math:`[n,j]` where :math:`n` is the length equal to the maximum time based on the number of material balances that could be constructed given the user-provided MBP and number of samples in the input data, and :math:`j` is the number of iterations given as input.

        The maximum time of the sequence is based on the minimum of all material balance components (e.g., input, inventories, and outputs) used for the calculation:

        .. highlight:: python
        .. code-block:: python

            import numpy as np

            time1[-1] = 400
            time2[-1] = 300
            time3[-1] = 800

            j = np.floor(
                np.min(
                    (time1, time2, time3)))

    """
    if GUIObject is not None:
      doTQDM = False
      loopcounter = 0

    A1 = np.max(np.asarray(list(chain.from_iterable(processedInputTimes))))  #unroll list
    A2 = np.max(np.asarray(list(chain.from_iterable(processedInventoryTimes))))
    A3 = np.max(np.asarray(list(chain.from_iterable(processedOutputTimes))))


    timeSteps = np.round(np.max(np.array([A1, A2, A3])))


    totalMBPs = np.ceil(timeSteps / MBP)

    iterations = inputAppliedError[0].shape[0]

    #it's easier to implement SITMUF using the actual indicies
    #from the statistical papers rather than the python loop variables
    #so this translates python loop variables to indicides and times
    #more closely aligned to the papers
    covmatrix = np.zeros((iterations, int(totalMBPs), int(totalMBPs)))
    pbar = None

    totalloops = int(((totalMBPs-2)*(totalMBPs-1))/2)
    if doTQDM and not ispar:        
        pbar = tqdm(desc="CovMat", total=int(totalloops), leave=True, bar_format = "{desc:10}: {percentage:06.2f}% |{bar}|  [Elapsed: {elapsed} || Remaining: {remaining}]", ncols=None)

    #_covmat_loop-start
    for currentMB in range(1, int(totalMBPs)):
        for j in range(0, currentMB):
    #_covmat_loop-end

            if GUIObject is not None:
                GUIObject.progress.emit(loopcounter / totalloops*100)
                loopcounter+=1

            I = j + 1 
            IPrevious = j - 1               
            IPrime = currentMB 
            IPrimePrevious = currentMB-1

            I_time = float(I*MBP)
            IPrevious_time = float(IPrevious*MBP)
            IPrime_time = float(IPrime*MBP)
            IPrimePrevious_time = float(IPrimePrevious*MBP)




            #------------ Diagonal terms ------------#
            if j == currentMB-1:

                term1 = np.zeros((iterations,))
                term2 = np.zeros((iterations,))
                term3 = np.zeros((iterations,))
                term4 = np.zeros((iterations,))
                term5 = np.zeros((iterations,))

                #------------ Input terms ------------#

                # _covmat_D1-start
                for k in range(len(inputAppliedError)):

                    logicalInterval = np.logical_and(processedInputTimes[k] >= IPrevious_time,processedInputTimes[k] <= I_time).reshape((-1,))  #select the indices for the relevant time

                    if inputTypes[k] == 'continuous':
                        term1 += trapSum(logicalInterval,processedInputTimes[k],inputAppliedError[k]) **2 * (ErrorMatrix[k, 0]**2 + ErrorMatrix[k, 1]**2)
                    elif inputTypes[k] == 'discrete':
                        term1 += (inputAppliedError[k][:, logicalInterval].sum(axis=1)**2 * (ErrorMatrix[k, 0]**2 + ErrorMatrix[k, 1]**2 ))
                    else:
                        raise Exception("inputTypes[j] is not 'continuous' or 'discrete'")                      
                # _covmat_D1-end

                    

                #------------ Output terms ------------#
                # _covmat_D2-start
                for k in range(len(outputAppliedError)):

                    logicalInterval = np.logical_and(processedOutputTimes[k] >= IPrevious_time,processedOutputTimes[k] <= I_time).reshape((-1,))
                    locMatrixRow = k + len(inputAppliedError) + len(inventoryAppliedError)                      

                    if outputTypes[k] == 'continuous':
                        term2 += trapSum(logicalInterval,processedOutputTimes[k],outputAppliedError[k])**2 * (ErrorMatrix[locMatrixRow, 0]**2 + ErrorMatrix[locMatrixRow, 1]**2)
                    elif outputTypes[k] == 'discrete':
                        term2 += (outputAppliedError[k][:, logicalInterval].sum(axis=1)**2 * (ErrorMatrix[locMatrixRow, 0]**2 + ErrorMatrix[locMatrixRow, 1]**2 ))
                    else:
                        raise Exception("outputTypes[j] is not 'continuous' or 'discrete'")
                # _covmat_D2-end

                #------------ Inventory terms ------------#
                # _covmat_D345-start
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
                # _covmat_D345-end

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
                # _covmat_OD1-start
                for k in range(len(inputAppliedError)):
                    logicalInterval = np.logical_and(processedInputTimes[k] >= IPrevious_time, processedInputTimes[k] <= I_time).reshape((-1,))  #select the indices for the relevant time
                    logicalInterval2 = np.logical_and(processedInputTimes[k] >= IPrimePrevious_time, processedInputTimes[k] <= IPrime_time).reshape((-1,))  #select the indices for the relevant time
                    
                    if inputTypes[k] == 'continuous':
                        A = trapSum(logicalInterval, processedInputTimes[k],inputAppliedError[k])
                        B = trapSum(logicalInterval2, processedInputTimes[k],inputAppliedError[k])
                    elif inputTypes[k] == 'discrete': 
                        A = inputAppliedError[k][:, logicalInterval].sum(axis=1)
                        B = inputAppliedError[k][:, logicalInterval2].sum(axis=1)
                    else:
                        raise Exception("inputTypes[j] is not 'continuous' or 'discrete'")                   

                    C = ErrorMatrix[k, 1]**2
                    term1 += (A*B*C)
                # _covmat_OD1-end

                #------------ Output terms ------------#
                # _covmat_OD2-start
                for k in range(len(outputAppliedError)):
                    logicalInterval = np.logical_and(processedOutputTimes[k] >= IPrevious_time,processedOutputTimes[k] <= I_time).reshape((-1,))  #select the indices for the relevant time
                    logicalInterval2 = np.logical_and(processedOutputTimes[k] >= IPrimePrevious_time,processedOutputTimes[k] <= IPrime_time).reshape((-1,))  #select the indices for the relevant time
                    locMatrixRow = k + len(inputAppliedError) + len(inventoryAppliedError)

                    

                    if outputTypes[k] == 'continuous':
                        A = trapSum(logicalInterval, processedOutputTimes[k],outputAppliedError[k])
                        B = trapSum(logicalInterval2, processedOutputTimes[k],outputAppliedError[k])
                    elif outputTypes[k] == 'discrete': 
                        A = outputAppliedError[k][:, logicalInterval].sum(axis=1)
                        B = outputAppliedError[k][:, logicalInterval2].sum(axis=1)
                    else:
                        raise Exception("outputTypes[j] is not 'continuous' or 'discrete'")  
                    
                    C = ErrorMatrix[locMatrixRow, 1]**2
                    term2 += (A*B*C)
                # _covmat_OD2-end

                #------------ Inventory terms ------------#
                # _covmat_OD345-start
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
                    
                    

                covmatrix[:,j,currentMB-1] = term1+term2+term3-term4-term5
                covmatrix[:,currentMB-1,j] = term1+term2+term3-term4-term5
                # _covmat_OD345-end

                if pbar is not None:
                    pbar.update(1)

                

    return covmatrix