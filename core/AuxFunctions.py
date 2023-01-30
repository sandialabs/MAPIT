import numpy as np
from itertools import chain
import warnings


def trapSum(relevantIndex,time,data,IT=None):
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

        Returns:
          ndarray: An array of shape :math:`[1,j]` containing the integrated total for each iteration over the time specified by **time[relevantIndex]**. 



      """

      #this is for indexing the data array
      #sometimes specific positions are
      #required by other functions
      if IT is not None:
          IDXC = IT
      else:
          IDXC = 0



      #these are actually fairly expensive to keep computing
      #calculate them here rather than in loop
      relevantDataVals = data[IDXC,relevantIndex]
      relevantTimeVals = time[relevantIndex]

      if np.sum(relevantDataVals.shape) == 0:
        return np.zeros((np.shape(data)[0],))

      #find pairs
      #this uses regions where the dataset is zero and not zero
      #(note this could be problematic with noisy zero signals)
      # to find the bounds of individual pulses
      #the intersection of area = 0 and != 0 should be able
      #to provide the left and right bounds of pulses
      ZZ = np.argwhere(relevantDataVals == 0).reshape((-1,))
      NZ = np.argwhere(relevantDataVals != 0).reshape((-1,))
      ZZ +=1
      LI = np.intersect1d(ZZ,NZ)
      ZZ -=2
      RI = np.intersect1d(ZZ,NZ)
      LI = LI.reshape((-1,1))
      RI = RI.reshape((-1,1))
      if np.shape(LI)[0] > np.shape(RI)[0]:
        pairs = np.concatenate((LI[:-1],RI),axis=1)
      elif np.shape(LI)[0] < np.shape(RI)[0]:
        pairs = np.concatenate((LI,RI[1:]),axis=1)
      else:
        pairs = np.concatenate((LI[:-1],RI[1:]),axis=1)

      #HACK: for one pair, the above code can result
      # in a zero sized array
      if pairs.size == 0:
        pairs = np.array([LI[0],RI[0]]).reshape((1,2))
      
      pairs[:,1] += 1 #this ensures a zero is included which facilitates proper
                      #integration using the trapz function

      checkRightPulse = np.ones((len(LI),))

      #HACK: sometimes there will be a bit hanging on the edge
      # of the pulse, which is technically a misspecified MBP
      # we try to resolve it by just ignoring that part
      for Q in range(pairs.shape[0]):
        if pairs[Q,0] > pairs[Q,1]:
          pairs[Q,0] = 0
          checkRightPulse[Q] = 0
          warnings.warn("Misspecified MBP, results might be inaccurate")

      if IT is not None:
        dataArray = relevantDataVals.reshape((1,-1))
        timeArray = relevantTimeVals
        S0 = 1
      else:
        dataArray = np.swapaxes(data[:,relevantIndex],0,1)
        bt = relevantTimeVals.reshape((-1,1))
        S0 = dataArray.shape[1]
        timeArray = np.repeat(bt,S0,axis=1)

      #look for nonzero locations in the data
      RR = relevantDataVals[relevantDataVals!=0]
      T = np.mean(RR)*0.10




      timesegs=[]
      datasegs=[]


      #time to collect the segments using the previously calculated pairs
      for i in range(len(pairs)):

          #this checks for the time difference for the pulse trailing zero
          #sometimes it can be recorded quite a bit after the
          #actual pulse end, and if so, needs to be accounted for
          G = np.ediff1d(np.asarray(relevantTimeVals[pairs[i][0]:pairs[i][1]]))
          if relevantDataVals[pairs[i][1]] == 0 and relevantTimeVals[pairs[i][1]] - relevantTimeVals[pairs[i][1]-1] < np.max(G):
            offset = 1
          else:
            offset = 0
          timesegs.append(np.swapaxes(timeArray[pairs[i,0]:pairs[i,1]+offset,],0,1))
          datasegs.append(np.swapaxes(dataArray[pairs[i,0]:pairs[i,1]+offset,],0,1))

      #look to see if there was a pulse on the left of the timeseries
      #that wasn't quite accounted for
      if np.sum(relevantDataVals[0:pairs[0,0]]) > T and checkRightPulse[i] == 1:
          RS = np.max(np.where(relevantDataVals[0:pairs[0,0]] > T))
          LS = np.min(np.where(relevantDataVals[0:pairs[0,0]] > T))
          seg = np.array([LS,RS]).reshape((1,-1))
          pairs = np.concatenate((seg,pairs),axis=0)
          timesegs.append(np.swapaxes(timeArray[LS:RS+1],0,1))
          datasegs.append(np.swapaxes(dataArray[LS:RS+1,],0,1))

      #look for a final pulse on the right of the timeseries that
      #might not have been accounted for
      if np.sum(data[0,relevantIndex][pairs[-1,1]+5:]) > T:
          RS = pairs[-1][1] + np.max(np.where(relevantDataVals[pairs[-1,1]:] > T))
          LS = pairs[-1][1] + np.min(np.where(relevantDataVals[pairs[-1,1]+5:] > T)) #the +5 helps prevent an edge case where the final pairing cuts off a little of the data (this can occur
          #if the pulse takes a long time to decrease (which makes it not really a pulse))
          seg = np.array([LS+5,RS]).reshape((1,-1))
          pairs = np.concatenate((pairs,seg),axis=0)
          timesegs.append(np.swapaxes(timeArray[LS+5:RS],0,1))
          datasegs.append(np.swapaxes(dataArray[LS+5:RS,],0,1))

      #if there's a phantom final pulse, remove it
      if np.shape(datasegs[-1])[1] == 0:
          del timesegs[-1]
          del datasegs[-1]
          pairs = pairs[:-1,:]

      traptot = np.zeros((S0,))
      #peform the numerical integration
      #the second term accounts for how the pulse is expressed in the trapz function
      #if not included it would underestimate the area
      for i in range(len(datasegs)):
          # traptot.append(np.trapz(datasegs[i],timesegs[i]) + 0.5*(timesegs[i][:,-1]-timesegs[i][:,-2])*datasegs[i][:,-2])

          traptot += (np.trapz(datasegs[i],timesegs[i]) + 0.5*(timesegs[i][:,-1]-timesegs[i][:,-2])*datasegs[i][:,-2])

      #traptot = np.sum(traptot) #sum across all segments

      return traptot

def removeExtraDims(inp,inv,out):
    inp_formatted = []
    inv_formatted = []
    out_formatted = []

    for i in range(len(inp)):
      inp_formatted.append(np.squeeze(inp[i]))

    for i in range(len(inv)):
      inv_formatted.append(np.squeeze(inv[i]))

    for i in range(len(out)):
      out_formatted.append(np.squeeze(out[i]))


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
  