import numpy as np
from itertools import chain
import warnings


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
        relevantIndex (ndarray): An array that expresses the relevant time slice, in terms of indicies, with shape :math:`[m,j]` where :math:`m` is the total number of relevant samples and :math:`j` is the total number of iterations.

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

    pairs = np.concatenate((LeftIndicies, RightIndicies), axis=1)


    # Generally, the final interval of a pulse is required to produce the proper integration value
    # however, as MAPIT is primarly used in and around Simulink, it's been observed that in some cases,
    # simulink will not record the final part of a pulse until several time steps later.
    # this logic below checks to see if the "final" value of a pulse is more than one timestep
    # after all the other data in that pulse. If so, we ignore that part of the pulse as it
    # is an error in Simulink. If not accounted for, the integration will provide an incorrect, inflated
    # value. This occurs on the second input of the fuel fab dataset, for example.
    if len(relevantTimeVals)-1 != pairs[0, 1]:
        if (relevantTimeVals[pairs[0, 1]+1] - relevantTimeVals[pairs[0, 1]]) <= np.max(np.diff(relevantTimeVals[pairs[0, 0]:pairs[0, 1]].squeeze())):
            pairs[:, 1] += 1

    pairs = pairs.astype(int)

    rowfordelete = []



    # remove zero length pairs
    # zero length pairs can occur in some
    # edge cases where pulses have just started
    # or ended and the pulse is undefined
    for Q in range(len(pairs)):
        if pairs[Q, 0] - pairs[Q, 1] == 0:
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
  