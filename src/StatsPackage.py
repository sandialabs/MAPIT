"""
    Python file containing
    all the functions needed to perform
    the various safeguards calculations
    in the main part of MAPIT.
"""

from PySide2 import QtCore, QtWidgets, QtGui
import numpy as np
import os
import string
import copy
import time
from scipy.io import loadmat
from itertools import chain
import matplotlib
from scipy.integrate import trapz
import sys
from MAPIT import MissingIndex

#future TODO:
#consolidate some of the common
#ops in the Tests class


class ErrorHandle:
  """
        Class containing the
        initial setup and error
        propagation scripts.
  """

  def ExecIO(self):
    if len(self.OBox.text()) > 0:
      self.offset = int(self.OBox.text())
    else:
      self.offset = 0

    if self.hasRunIO == 0:

      self.StatDlg.UpdateDispText('Importing data...')
      QtCore.QCoreApplication.instance().processEvents()

      self.PB.setMaximum(0)
      self.PB.setMinimum(0)

      if hasattr(self, 'Wizard'):  #if is imported data

        eleAppend = list(string.ascii_lowercase)

        ##IO - Inputs

        liH = []

        if self.Wizard.IsMatV == 0:
          # need to infer the number of elements

          lddir = os.path.join(self.Wizard.InDir,sorted(os.listdir(self.Wizard.InDir))[0])

          testM = np.loadtxt(lddir, delimiter=',')
        else:
          G = loadmat(self.Wizard.MatDir)  # should be only one .mat for all locations
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

        if len(self.Wizard.EleVec_IN) > 0:
          for i in range(0, int(self.Wizard.InKMP)):
            for j in range(0, len(self.Wizard.EleVec_IN)):
              liH.append(self.Wizard.EleVec_IN[j] + str(i))

          if len(liH) < eleInfer:
            for i in range(0, int(self.Wizard.InvKMP)):
              for j in range(int(len(liH)), int(eleInfer)):
                liH.append('ele' + eleAppend[j] + str(i))
        else:
          for i in range(0, int(self.Wizard.InKMP)):
            for j in range(0, eleInfer):
              liH.append('ele' + eleAppend[j] + str(i))

        self.eleIN = copy.copy(len(liH))
        LiC = []

        #begin to load the data
        if self.Wizard.IsMatV == 0:  # if CSV
          for i in range(0, int(self.Wizard.InKMP)):
            lddir = os.path.join(self.Wizard.InDir,sorted(os.listdir(self.Wizard.InDir))[i])
            r = np.loadtxt(lddir, delimiter=',')
            LiC.append(r)

          try:
            inpFrame = np.stack(LiC)
          except:
            pass

        else:  # if not CSV
          LiC = []
          LiC2 = []
          lddir = loadmat(self.Wizard.MatDir)
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
        if self.Wizard.IsMatV == 0:
          # need to infer the number of elements
          lddir = os.path.join(self.Wizard.InvDir,sorted(os.listdir(self.Wizard.InvDir))[0])

          testM = np.loadtxt(lddir, delimiter=',')

          if len(np.shape(testM)) == 1:
            testM = np.expand_dims(testM, axis=0)

          eleInfer = np.min(np.shape(
              testM))  # assuming smallest dimension is number of elements

          if len(self.Wizard.EleVec_IN) > 0:
            for i in range(0, int(self.Wizard.InvKMP)):
              for j in range(0, len(self.Wizard.EleVec_IN)):
                liH.append(self.Wizard.EleVec_IN[j] + str(i))

            if len(liH) < eleInfer:
              for i in range(0, int(self.Wizard.InvKMP)):
                for j in range(int(len(liH)), int(eleInfer)):
                  liH.append('ele' + eleAppend[j] + str(i))
          else:
            for i in range(0, int(self.Wizard.InvKMP)):
              for j in range(0, eleInfer):
                liH.append('ele' + eleAppend[j] + str(i))

          self.eleINV = copy.copy(len(liH))
          LiC = []

          for i in range(0, int(self.Wizard.InvKMP)):
            lddir = os.path.join(self.Wizard.InvDir,sorted(os.listdir(self.Wizard.InvDir))[i])
            r = np.loadtxt(lddir, delimiter=',')
            LiC.append(r)

          try:
            invFrame = np.stack(LiC)
          except:
            None

        else:
          LiC = []
          LiC2 = []
          lddir = loadmat(self.Wizard.MatDir)
          JJ = np.shape(G['invn']['data'][0])[0]



          for i in range(0, JJ):
            LiC.append(G['invn']['data'][0][i])
            LiC2.append(G['invn']['time'][0][i])

          self.GuessEles = np.min(np.shape(
              G['invn']['data'][0][0]))  # assume elements is less than time
          try:
            invFrame = np.stack(LiC)
            invTimeFrame = np.stack(LiC2)
          except:
            invFrame = LiC
            invTimeFrame = LiC2

        ##IO -- Output
        liH = []

        if self.Wizard.IsMatV == 0:  # if CSV
          # need to infer the number of elements
          lddir = os.path.join(self.Wizard.OutDir,
                               sorted(os.listdir(self.Wizard.OutDir))[0])

          testM = np.loadtxt(lddir, delimiter=',')

          if len(np.shape(testM)) == 1:
            testM = np.expand_dims(testM, axis=0)

          eleInfer = np.min(np.shape(
              testM))  # assuming smallest dimension is number of elements

          if len(self.Wizard.EleVec_IN) > 0:

            for i in range(0, int(self.Wizard.OutKMP)):
              for j in range(0, len(self.Wizard.EleVec_IN)):
                liH.append(self.Wizard.EleVec_IN[j] + str(i))

            if len(liH) < eleInfer:
              for i in range(0, int(self.Wizard.OutKMP)):
                for j in range(int(len(liH)), int(eleInfer)):
                  liH.append('ele' + eleAppend[j] + str(i))
          else:
            for i in range(0, int(self.Wizard.OutKMP)):
              for j in range(0, eleInfer):
                liH.append('ele' + eleAppend[j] + str(i))

          self.eleOUT = copy.copy(len(liH))
          LiC = []
          for i in range(0, int(self.Wizard.OutKMP)):
            lddir = os.path.join(self.Wizard.OutDir,
                                 sorted(os.listdir(self.Wizard.OutDir))[i])
            r = np.loadtxt(lddir, delimiter=',')
            LiC.append(r)

          try:
            outFrame = np.stack(LiC)
          except:
            None

          self.GuessEles = eleInfer
        else:
          LiC = []
          LiC2 = []
          lddir = loadmat(self.Wizard.MatDir)
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

      else:
        inpFrame = list(self.SS.Inputs)

        # inventories
        invFrame = list(self.SS.Inventories)

        # outputs
        outFrame = list(self.SS.Outputs)

        #liH = ['U', 'Pu', 'Cs', 'Xe', 'Eu']  #predetermined elements
        #self.GuessEles = 5

        liH = ['U'] #the fuel fab only has U, other scenarios not yet included
        self.GuessEles = 1

      self.liH = liH

      # locations, timestep, element
      self.inpFrame = inpFrame
      self.invFrame = invFrame
      self.outFrame = outFrame

      ST = 0

      if hasattr(self, 'Wizard'):
        if self.Wizard.IsMatV == 1:  # needed for special matlab sampling blocks
          self.inpTimeFrame = inpTimeFrame  #grab the times
          self.invTimeFrame = invTimeFrame
          self.outTimeFrame = outTimeFrame

          ST = 1
      if hasattr(self,'SS'):
          self.inpTimeFrame = list(self.SS.InputsT)  #grab the times
          self.invTimeFrame = list(self.SS.InventoriesT)
          self.outTimeFrame = list(self.SS.OutputsT)

      #the lists are usually missing a dimension
      #required for later analysis
      if isinstance(self.inpFrame, list) == 0:
        if self.inpFrame.dtype != 'O':
          if len(np.shape(self.inpFrame)) != 3:
            self.inpFrame = np.expand_dims(self.inpFrame, axis=2)

      if isinstance(self.invFrame, list) == 0:
        if self.invFrame.dtype != 'O':
          if len(np.shape(self.invFrame)) != 3:
            self.invFrame = np.expand_dims(self.invFrame, axis=2)

      if isinstance(self.outFrame, list) == 0:
        if self.outFrame.dtype != 'O':
          if len(np.shape(self.outFrame)) != 3:
            self.outFrame = np.expand_dims(self.outFrame, axis=2)

    else:
      if hasattr(self, 'Wizard'):
        if self.Wizard.IsMatV == 1:  # needed for special matlab sampling blocks

          ST = 1

    # dealing with offset by modifying the data upfront is easier
    # than trying to modify the stats calculations themselves

    #offset deals with the temporal offset
    #which effectively starts the safeguards
    #calculations after the offset has ellapsed
    #useful if there is a long period of startup
    #data that has been collected
    if self.offset > 0:
      # if special, perhaps non-uniform matlab data
      # is present

      #basically check is list (i.e. variable time)
      #if so have to handle a list not an array
      #rebase time to be at zero at start for convenience
      if ST == 1:
        if isinstance(self.inpFrame, list):
          for JR in range(len(self.inpFrame)):
            fsh = np.shape(inpFrame[JR])

            self.inpFrame[JR] = self.inpFrame[JR][np.where(
                self.inpTimeFrame[JR] > self.offset)].reshape((-1, fsh[1]))

            self.inpTimeFrame[JR] = self.inpTimeFrame[JR][np.where(
                self.inpTimeFrame[JR] > self.offset)].reshape(
                    (-1, fsh[1])) - self.offset
        else:
          fsh = np.shape(self.inpFrame)

          self.inpFrame = self.inpFrame[np.where(
              self.inpTimeFrame > self.offset)].reshape((fsh[0], -1, fsh[2]))

          self.inpTimeFrame = self.inpTimeFrame[np.where(
              self.inpTimeFrame > self.offset)].reshape(
                  (fsh[0], -1, fsh[2])) - self.offset

        if isinstance(self.invFrame, list):
          for JR in range(len(self.invFrame)):
            fsh = np.shape(self.invFrame[JR])

            self.invFrame[JR] = self.invFrame[JR][np.where(
                self.inpTimeFrame[JR] > self.offset)].reshape((-1, fsh[1]))

            self.invTimeFrame[JR] = self.invTimeFrame[JR][np.where(
                self.invTimeFrame[JR] > self.offset)].reshape(
                    (-1, fsh[1])) - self.offset
        else:
          fsh = np.shape(self.invFrame)

          self.invFrame = self.invFrame[np.where(
              self.invTimeFrame > self.offset)].reshape((fsh[0], -1, fsh[2]))

          self.invTimeFrame = self.invTimeFrame[np.where(
              self.invTimeFrame > self.offset)].reshape(
                  (fsh[0], -1, fsh[2])) - self.offset

        if isinstance(self.outFrame, list):
          for JR in range(len(self.outFrame)):
            fsh = np.shape(self.outFrame[JR])

            self.outFrame[JR] = self.outFrame[JR][np.where(
                self.outTimeFrame[JR] > self.offset)].reshape((-1, fsh[1]))

            self.outTimeFrame[JR] = self.outTimeFrame[JR][np.where(
                self.outTimeFrame[JR] > self.offset)].reshape(
                    (-1, fsh[1])) - self.offset
        else:
          fsh = np.shape(self.outFrame)

          self.outFrame = self.outFrame[np.where(
              self.outTimeFrame > self.offset)].reshape((fsh[0], -1, fsh[2]))

          self.outTimeFrame = self.outTimeFrame[np.where(
              self.outTimeFrame > self.offset)].reshape(
                  (fsh[0], -1, fsh[2])) - self.offset

      else:
        self.inpFrame = self.inpFrame[:, self.offset:, :]
        self.invFrame = self.invFrame[:, self.offset:, :]
        self.outFrame = self.outFrame[:, self.offset:, :]

    # some checks here for the requested tests

    if self.CB_PuSPage.isChecked():
      self.CB_PuSITMUF.setChecked(1)
      self.CB_PuMUF.setChecked(1)

    if self.CB_PuSITMUF.isChecked():
      self.CB_PuMUF.setChecked(1)

    if self.CB_USPage.isChecked():
      self.CB_USITMUF.setChecked(1)
      self.CB_UMUF.setChecked(1)

    if self.CB_USITMUF.isChecked():
      self.CB_UMUF.setChecked(1)

    if self.CB_GSPage.isChecked():
      self.CB_GSITMUF.setChecked(1)
      self.CB_GMUF.setChecked(1)

    if self.CB_GSITMUF.isChecked():
      self.CB_GMUF.setChecked(1)

    QtCore.QCoreApplication.instance().processEvents()

    ErrorHandle.ErrorProp(self)

  def ErrorProp(self):
    """
      Function to perform the error propogation
    """
    self.RunStats._animation.setLoopCount(1)

    self.StatDlg.UpdateDispText('Applying and propogating error')
    QtCore.QCoreApplication.instance().processEvents()

    self.PB.setMaximum(100)

    self.decompStatus = 1 #sets a flag related to the cholesky decomp
                          #for sitmuf, in case it's called later

    if hasattr(self, 'Wizard'):  #if data was imported
      TotalLocs = int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + int(
          self.Wizard.OutKMP)

      eleNames = self.Wizard.EleVec_IN

    else:  #otherwise (scene selection)
      TotalLocs = len(self.SS.Inputs) + len(
          self.SS.Inventories) + len(self.SS.Outputs)

      eleNames = self.liH




    # determine OPindex (index to operate on) here
    # either its listed as label or needs popup to find index

    ck0 = self.CB_PuMUF.isChecked() + self.CB_PuSMUF.isChecked(
    ) + self.CB_PuSITMUF.isChecked() + self.CB_PuSPage.isChecked()
    ck1 = self.CB_UMUF.isChecked() + self.CB_USMUF.isChecked(
    ) + self.CB_USITMUF.isChecked() + self.CB_USPage.isChecked()
    ck2 = self.CB_GMUF.isChecked() + self.CB_GSMUF.isChecked(
    ) + self.CB_GSITMUF.isChecked() + self.CB_GSPage.isChecked()
    self.pmpt = []

    # if elenames were given
    if len(eleNames) > 0:

      # if imported from wizard this is required
      try:
        eleNames = eleNames.split(",")
      except:
        None

      # check for Pu
      for idx, val in enumerate(eleNames):
        if 'PU' == eleNames[idx].upper():
          self.PuLoc = idx
        else:
          None

      # check for U
      for idx, val in enumerate(eleNames):
        if 'U' == eleNames[idx].upper():
          self.ULoc = idx
        else:
          None

      if len(self.GEBox.text()) > 0:
        self.GLoc = int(self.GEBox.text())
      else:
        None

    else:
      if len(self.GEBox.text()) > 0:
        self.GLoc = int(self.GEBox.text())
      else:
        None

    # if no names requested but pu test was requested
    if self.PuLoc == -1 and ck0 > 0:
      # add prompt flag for pu
      self.pmpt.append(0)
    else:
      None

    if self.ULoc == -1 and ck1 > 0:
      self.pmpt.append(1)
    else:
      None

    if len(self.GEBox.text()) == 0 and ck2 > 0:
      self.pmpt.append(2)
    else:
      None

    if len(self.pmpt) > 0:
      dlg = MissingIndex(self)
      res = dlg.exec_()
      self.PuLoc = dlg.PuLoc
      self.ULoc = dlg.ULoc
      self.GLoc = dlg.GLoc

    # need to create a vector of elemental names for later
    self.EleVecLabel = [None] * self.GuessEles

    # set default names
    for i in range(0, int(self.GuessEles)):
      self.EleVecLabel[i] = 'Element ' + str(i + 1)

    # if names were given overwrite
    if len(eleNames) > 0:
      for i in eleNames:
        self.EleVecLabel[int(eleNames.index(i))] = i
    else:
      None

    # set Pu and U
    if self.PuLoc != -1:
      self.EleVecLabel[int(self.PuLoc)] = 'Pu'
    else:
      None

    if self.ULoc != -1:
      self.EleVecLabel[int(self.ULoc)] = 'U'
    else:
      None

    self.ErrorMatrix = np.zeros((TotalLocs, 6))

    # setup error table using
    # previously described errors

    #this ensures that the right items are placed correctly within the error matrix
    #as sometimes the GUI can have missing columns, added rows, etc for aesthetic purposes

    mapDict = {'U Rand':0, 'U Sys':1, 'Pu Rand':2, 'Pu Sys':3, 'Generic Rand':4, 'Generic Sys':5}


    P = 0
    for i in range(0, self.EP.rowCount()):
      for j in range(0, 6):
        if self.EP.item(i, j) is not None:
          C = mapDict[self.EP.horizontalHeaderItem(j).text().rstrip()]
          self.ErrorMatrix[P, C] = float(self.EP.item(i, j).text()) / 100

      if self.EP.item(i,0) is not None:
        P +=1



    # important -- going to assume every feature has different systematic error instance - in practice they might be shared
    # basically gonna propogate error to everything because its easier on me and probably doesn't have a lot
    # of overhead, might need to update later

    IT = int(self.IterBox.text())

    #if the data is in a list then it is because
    #there is uneven sample lengths from MATLAB
    #and the dimensions need to be unpacked
    #manually
    GF = 0  #flag to determine if data is mat
    #future TODO: update to be less
    #redunant with IsMatV
    if hasattr(self,'Wizard'):
      if self.Wizard.IsMatV == 1:
        GF = 1

    if hasattr(self,'SS'):
      GF = 1


    #in some cases not all mat data is sampled unevenly, so need to check
    #if list or array
    if GF == 1:

      if isinstance(self.inpFrame, list):
        S1 = []
        for JR in range(len(self.inpFrame)):
          S1.append(np.shape(self.inpFrame[JR]))
      else:
        S1 = []
        for JR in range(len(self.inpFrame)):
          S1.append(np.shape(self.inpFrame[JR, :, :]))

      if isinstance(self.invFrame, list):
        S2 = []
        for JR in range(len(self.invFrame)):
          S2.append(np.shape(self.invFrame[JR]))
      else:
        S2 = []
        for JR in range(len(self.invFrame)):
          S2.append(np.shape(self.invFrame[JR, :, :]))

      if isinstance(self.outFrame, list):
        S3 = []
        for JR in range(len(self.outFrame)):
          S3.append(np.shape(self.outFrame[JR]))
      else:
        S3 = []
        for JR in range(len(self.outFrame)):
          S3.append(np.shape(self.outFrame[JR, :, :]))

      self.inpEFrame = []  #list holding input with applied errors
      self.inpSFrame = [
      ]  #list holding the input's systematic error (unapplied)
      self.inpRFrame = []  #list holding the input's random error (unapplied)

      for i in range(0, len(self.inpFrame)):
        self.inpEFrame.append(np.zeros((IT, S1[i][0], S1[i][1]),dtype=np.float32))
        self.inpSFrame.append(np.zeros((S1[i][0], S1[i][1]),dtype=np.float32))
        self.inpRFrame.append(np.zeros((S1[i][0], S1[i][1]),dtype=np.float32))

      self.invEFrame = []
      self.invSFrame = []
      self.invRFrame = []

      for i in range(0, len(self.invFrame)):
        self.invEFrame.append(np.zeros(
            (IT, S2[i][0], S2[i][1]),dtype=np.float32))  #[Iterations, Locs, Samples, Elements]
        self.invSFrame.append(np.zeros((S2[i][0], S2[i][1]),dtype=np.float32))
        self.invRFrame.append(np.zeros((S2[i][0], S2[i][1]),dtype=np.float32))

      self.outEFrame = []
      self.outRFrame = []
      self.outSFrame = []

      for i in range(0, len(self.outFrame)):
        self.outEFrame.append(np.zeros(
            (IT, S3[i][0], S3[i][1]),dtype=np.float32))  #[Iterations, Locs, Samples, Elements]
        self.outRFrame.append(np.zeros((S3[i][0], S3[i][1]),dtype=np.float32))
        self.outSFrame.append(np.zeros((S3[i][0], S3[i][1]),dtype=np.float32))

    else:  #if it's not a mat assume uniform sampling
      #i.e. once every unit of time
      S1 = np.asarray(np.shape(self.inpFrame))
      S2 = np.asarray(np.shape(self.invFrame))
      S3 = np.asarray(np.shape(self.outFrame))

      self.inpEFrame = np.zeros((IT, S1[0], S1[1], S1[2]))
      self.inpSFrame = np.zeros((S1[0], S1[1], S1[2]))
      self.inpRFrame = np.zeros((S1[0], S1[1], S1[2]))

      self.invEFrame = np.zeros((IT, S2[0], S2[1], S2[2]))
      self.invSFrame = np.zeros((S2[0], S2[1], S2[2]))
      self.invRFrame = np.zeros((S2[0], S2[1], S2[2]))

      self.outEFrame = np.zeros((IT, S3[0], S3[1], S3[2]))
      self.outRFrame = np.zeros((S3[0], S3[1], S3[2]))
      self.outSFrame = np.zeros((S3[0], S3[1], S3[2]))

    # initalize holders for the errors which we will need
    # for some of the stats tests

    # [Iterations, Locs, Samples, Elements] OR [locations, timestep, element]
    #E = the total errors
    #RA = random applied
    #SA = system applied
    #S = raw sys
    #R = raw random

    # create a dictionary to map between the location
    # and the error matrix
    self.EMD = {}
    if ck0 > 0:
      self.EMD.update({self.PuLoc: 2})
    else:
      None

    if ck1 > 0:
      self.EMD.update({self.ULoc: 0})
    else:
      None

    # dont really need this since the condition we are going to use
    # is for U or Pu only, but for completeness
    if ck2 > 0:
      self.EMD.update({self.GLoc: 4})
    else:
      None

    #special case where if no tests are requested for the
    #scenario select but error propagation is requested
    #need to update this object to point correctly to
    #the relevant parts of the error matrix. In other cases
    #where the scenario selector is not used, the full error
    #matrix is filled in so MAPIT will just assume that
    #the generic element column errors are desired. However,
    #for the scene select, the generic columns are zero
    #(for aesthetic purposes) so pointing to the generic
    #columns results in zero error being applied
    if ck0+ck1+ck2 == 0 and hasattr(self,'SS'):
      self.EMD.update({self.ULoc: 0})


    """
    ----------------------------------------------------------------------------------------------------
                                                Error Propogation
    ----------------------------------------------------------------------------------------------------
    This section is pretty ugly because I had originally written this to handle fixed-step sampled data
    such that it could be easily represented in matrix form However, that became problematic because for
    V&V purposes the MAPIT needed to be compared against SSPM, which was integrated in variable-time-step
    form. The MAT section uses potentially variable sample times to perform the error prop. This may be
    cleaned up in the future.
    """


    ############################################       Input       ###################################################
    ############################################        MAT        ###################################################
    # for each iteration
    # see github for more theory
    #observed = true(1+random*sys)
    if GF == 1:
      QtCore.QCoreApplication.instance().processEvents(
      )  # ensures window isn't seen as unresponsive

      # locations, timesteps, elements

      # for each location
      for i in range(0, len(S1)):
        self.PB.setValue(
            np.floor((i) /
                      ((len(S1) + len(S2) + len(S3))) * 100))
        QtCore.QCoreApplication.instance().processEvents(
        )  # ensures window isn't seen as unresponsive
        # for each element

        #assume sys differs by location only and doesn't change for different elements


        for j in range(0, S1[i][1]):

          # check to see if this element is u or pu
          key = 0
          if j in self.EMD:
            key = self.EMD[j]
          else:
            # location of generic errors
            key = 4

          self.inpEFrame[i][:,:,j] = self.inpFrame[i][:,j].reshape((S1[i][1],-1)) * (1+np.random.normal(size=(IT,S1[i][1],1),loc=0,scale=self.ErrorMatrix[i, key + 1])+np.random.normal(size=(IT,S1[i][0], S1[i][1]),loc=0,scale=self.ErrorMatrix[i, key])).reshape((IT,-1))

      ############################################     Inventory     ################################################
      ############################################        MAT        ###################################################

      QtCore.QCoreApplication.instance().processEvents(
      )  # ensures window isn't seen as unresponsive


      for i in range(0, len(S2)):

        self.PB.setValue(np.floor((i + len(S1)) / ((len(S1) + len(S2) + len(S3))) * 100))
        QtCore.QCoreApplication.instance().processEvents()


        for j in range(0, S2[i][1]):

          key = 0
          if j in self.EMD:
            key = self.EMD[j]
          else:
            # location of generic errors
            key = 4

          self.invEFrame[i][:,:,j] = self.invFrame[i][:,j].reshape((S2[i][1],-1)) *\
           (1+np.random.normal(size=(IT,S2[i][1],1),loc=0,scale=self.ErrorMatrix[i + len(S1), key + 1])+\
           np.random.normal(size=(IT, S2[i][0], S2[i][1]),loc=0,scale=self.ErrorMatrix[i + len(S1), key])).reshape((IT,-1))


      ############################################       Output       ################################################
      ############################################        MAT        ###################################################

      QtCore.QCoreApplication.instance().processEvents(
      )  # ensures window isn't seen as unresponsive

      for i in range(0, len(S3)):  #location

        self.PB.setValue(
            np.floor((i +len(S1) + len(S2)) /
                      ((len(S1) + len(S2) + len(S3))) * 100))
        QtCore.QCoreApplication.instance().processEvents()


        for j in range(0, S3[i][1]):  #elements

          key = 0
          if j in self.EMD:
            key = self.EMD[j]
          else:
            # location of generic errors
            key = 4

          self.outEFrame[i][:,:,j] = self.outFrame[i][:,j].reshape((S3[i][1],-1)) *\
           (1+np.random.normal(size=(IT,S3[i][1],1),loc=0,scale=self.ErrorMatrix[i + len(S1) + len(S2), key + 1])+\
           np.random.normal(size=(IT,S3[i][0], S2[i][1]),loc=0,scale=self.ErrorMatrix[i + len(S1) + len(S2), key])).reshape((IT,-1))


    else:
      ############################################          Input            ###################################################
      ############################################        Non-MAT        ###################################################
      for Z in range(0, IT):
        QtCore.QCoreApplication.instance().processEvents(
        )  # ensures window isn't seen as unresponsive

        # locations, timesteps, elements
        self.inpRFrame = np.random.normal(size=(S1[0], S1[1], S1[2]))

        # for each location
        for i in range(0, S1[0]):
          self.PB.setValue(
              np.floor((i + Z * S1[0]) / ((S1[0] + S2[0] + S3[0]) * IT) * 100))
          QtCore.QCoreApplication.instance().processEvents(
          )  # ensures window isn't seen as unresponsive
          # for each element
          for j in range(0, S1[2]):

            # systematic error is constant for each element at each location, but not the same
            # possible that each element at each location should have same sys, but can revisit
            # that in the future

            self.inpSFrame[i, :, j] = np.random.normal(size=(S1[1],))

            # check to see if this element is u or pu
            key = 0
            if j in self.EMD:
              key = self.EMD[j]
            else:
              # location of generic errors
              key = 4

            self.inpEFrame[Z, i, :, j] = self.inpFrame[i, :, j] + \
                                         self.inpFrame[i, :, j] * (self.inpSFrame[i, :, j] * self.ErrorMatrix[i, key + 1]) + \
                                         self.inpFrame[i, :, j] * (self.inpRFrame[i, :, j] * self.ErrorMatrix[i, key])

      ############################################       Inventory       ###################################################
      ############################################        Non-MAT       ###################################################
      for Z in range(0, IT):
        QtCore.QCoreApplication.instance().processEvents(
        )  # ensures window isn't seen as unresponsive

        self.invRFrame = np.random.normal(size=(S2[0], S2[1], S2[2]))

        for i in range(0, S2[0]):

          self.PB.setValue(
              np.floor((i + Z * S2[0] + IT * S1[0]) /
                       ((S1[0] + S2[0] + S3[0]) * IT) * 100))
          QtCore.QCoreApplication.instance().processEvents()

          for j in range(0, S2[2]):

            key = 0
            if j in self.EMD:
              key = self.EMD[j]
            else:
              # location of generic errors
              key = 4

            self.invSFrame[i, :, j] = np.random.normal(size=(S2[1],))

            self.invEFrame[Z, i, :, j] = self.invFrame[i, :, j] + \
                                         self.invFrame[i, :, j] * (self.invSFrame[i, :, j] * self.ErrorMatrix[i + S1[0], key + 1]) + \
                                         self.invFrame[i, :, j] * (self.invRFrame[i, :, j] * self.ErrorMatrix[i + S1[0], key])

      ############################################       Output       ###################################################
      ############################################       Non-MAT    ###################################################
      for Z in range(0, IT):
        QtCore.QCoreApplication.instance().processEvents(
        )  # ensures window isn't seen as unresponsive

        self.outRFrame = np.random.normal(size=(S3[0], S3[1], S3[2]))

        for i in range(0, S3[0]):

          self.PB.setValue(
              np.floor((i + Z * S3[0] + IT * S1[0] + IT * S2[0]) /
                       ((S1[0] + S2[0] + S3[0]) * IT) * 100))
          QtCore.QCoreApplication.instance().processEvents()

          for j in range(0, S3[2]):

            key = 0
            if j in self.EMD:
              key = self.EMD[j]
            else:
              # location of generic errors
              key = 4

            self.outSFrame[i, :, j] = np.random.normal(size=(S3[1],))

            self.outEFrame[Z, i, :, j] = self.outFrame[i, :, j] + \
                                         self.outFrame[i, :, j] * (self.outSFrame[i, :, j] * self.ErrorMatrix[i + S1[0] + S2[0], key + 1]) + \
                                         self.outFrame[i, :, j] * (self.outRFrame[i, :, j] * self.ErrorMatrix[i + S1[0] + S2[0], key])

    self.PB.setValue(np.floor(TotalLocs / TotalLocs) * 100)

    #self.statusBar().clearMessage()
    self.StatDlg.UpdateDispText('Ready')
    QtCore.QCoreApplication.instance().processEvents()

    self.UpdatePlotOpts()  #add options to plot observed and ground truth

    #update style on some dropdown boxes
    #to show that the error prop has run
    #and that those options are available
    gradA = "QWidget#{VAL}"
    gradB = "{" + "border-color: rgb({value},{value2},{value3});".format(value=153,value2=200,value3=221) +\
   "border-width: 2px;" +\
   "border-style: solid;" +\
   "padding: 0px;" +\
   "border-radius: 3px;" +\
   "margin-top: 10px;" +\
   "background-color: rgb(239,239,239);" +\
    "}"
    gradC = "QWidget#{VAL}"
    gradD = ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}"

    if self.window().MakeLight.isChecked() == 0:
      gradB = gradB.replace('rgb(239,239,239)', 'rgb(51,51,51)')
      gradB = gradB.replace('rgb(153,200,221)', 'rgb(0,83,118)')

    self.mb1.ChangeActive(1)
    self.mb1.setStyleSheet(
        gradA.format(VAL='PB1') + gradB + gradC.format(VAL='PB1') + gradD)

    if self.CB_PuMUF.isChecked() == 1 or self.CB_UMUF.isChecked(
    ) == 1 or self.CB_GMUF.isChecked() == 1:
      Tests.MUF(self)
    if self.CB_PuSMUF.isChecked() == 1 or self.CB_USMUF.isChecked(
    ) == 1 or self.CB_GSMUF.isChecked() == 1:
      Tests.SEMUF(self)
    if self.CB_PuSITMUF.isChecked() == 1 or self.CB_USITMUF.isChecked(
    ) == 1 or self.CB_GSITMUF.isChecked() == 1:
      Tests.SITMUF(self)

    self.UpdateLocOpts(
    )  #add locations to plot since default plot option is ground truth



    grad2 = "border-color: rgb({value},{value2},{value3});".format(value=211,value2=211,value3=211) +\
    "border-width: 5px;" +\
    "border-style: solid;" +\
    "padding: 6px;" +\
    "border-radius: 3px;}"

    if self.window().MakeLight.isChecked() == 0:
      grad2 = grad2.replace('rgb(211,211,211)', 'rgb(66,66,66)')

    self.SGSetContainer.setStyleSheet(
        "QWidget#{VAL}".format(VAL=self.SGSetContainer.Loc) + "{" + grad2 +
        "QWidget#{VAL}".format(VAL=self.SGSetContainer.Loc) +
        ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")
    self.AnalysisContainer.setStyleSheet(
        "QWidget#{VAL}".format(VAL=self.AnalysisContainer.Loc) + "{" + grad2 +
        "QWidget#{VAL}".format(VAL=self.AnalysisContainer.Loc) +
        ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}")

    #resets button animation and turns off after running, but
    #since the GUI supports new runs without restarting probably
    #better to leave them on
    #self.HasRunOnce=1

    self.threshContainer.PassLoc('PB8')
    self.threshContainer._animation.setLoopCount(3)
    self.threshContainer._animation.start()

    self.PlotControls.PassLoc('PB5')
    self.PlotControls._animation.setLoopCount(3)
    self.PlotControls._animation.start()

    self.PlotRunner.setEnabled(1)
    self.PlotRunner.PassLoc('PRB')
    self.PlotRunner._animation.setLoopCount(3)
    self.PlotRunner._animation.start()

    self.ExportFig.setEnabled(1)
    self.ExportFigL.setEnabled(1)
    self.ExportDat.setEnabled(1)

    if self.CB_PuSMUF.isChecked() == 1 or self.CB_USMUF.isChecked(
    ) == 1 or self.CB_GSMUF.isChecked() == 1:
      self.TabView.setEnabled(1)
      self.TabOpt.setToolTip('')




    if self.decompStatus == 0:
        self.StatDlg.UpdateDispText('Decomposition error, restart calculation')
        self.PB.setValue(0)
    else:
        self.StatDlg.UpdateDispText('Execution Finished')
        self.PB.setValue(100)

    QtCore.QCoreApplication.instance().processEvents()

    # need to reset rcparam defaults incase some were changed
    # during scene select

    matplotlib.rcParams.update(matplotlib.rcParamsDefault)
    self.hasRunIO = 1


class Tests:
  """
        Class containing functions
        for the currently implemented
        statistical tests.

        Details including both derivations
        and theory can be found in the
        github documents.

        GH: https://github.com/sandialabs/MAPIT
  """

  def MUF(self):
    """
            Function to calculate
            MUF (Material Unaccounted
            For).
    """

    ck0 = []
    if self.CB_PuMUF.isChecked() == 1:
      ck0.append(self.PuLoc)
      self.metricBox.addItem('Pu MUF')
    else:
      None

    if self.CB_UMUF.isChecked() == 1:
      ck0.append(self.ULoc)
      self.metricBox.addItem('U MUF')
    else:
      None

    if self.CB_GMUF.isChecked() == 1:
      ck0.append(self.GLoc)
      self.metricBox.addItem('Generic MUF')
    else:
      None

    #Gathering variables to make calc easier
    #-------------------------------------------------------
    #-------------------------------------------------------

    GF = 0
    if hasattr(self,'Wizard'):
      if self.Wizard.IsMatV == 1:
        GF = 1

    if hasattr(self,'SS'):
      GF = 1

    if GF == 1:
      if isinstance(self.inpFrame, list):
        S1 = []
        for JR in range(len(self.inpFrame)):
          S1.append(np.shape(self.inpFrame[JR]))
      else:
        S1 = []
        for JR in range(len(self.inpFrame)):
          S1.append(np.shape(self.inpFrame[JR, :, :]))

      if isinstance(self.invFrame, list):
        S2 = []
        for JR in range(len(self.invFrame)):
          S2.append(np.shape(self.invFrame[JR]))
      else:
        S2 = []
        for JR in range(len(self.invFrame)):
          S2.append(np.shape(self.invFrame[JR, :, :]))

      if isinstance(self.outFrame, list):
        S3 = []
        for JR in range(len(self.outFrame)):
          S3.append(np.shape(self.outFrame[JR]))
      else:
        S3 = []
        for JR in range(len(self.outFrame)):
          S3.append(np.shape(self.outFrame[JR, :, :]))

    else:
      S1 = np.shape(self.inpFrame)
      S2 = np.shape(self.invFrame)
      S3 = np.shape(self.outFrame)

    mbaTime = int(self.MBPBox.text())


    IT = int(self.IterBox.text())

    #if one of the datasets are a list
    #then need check them all to figure
    #out how long the imported data is
    #as it cannot be assumed (len(data)) = time
    if isinstance(S1, list) or isinstance(S2, list) or isinstance(S3, list):
      if isinstance(S1, list):
        A1 = np.max(np.asarray(list(chain.from_iterable(
            self.inpTimeFrame))))  #unroll list
      else:
        A1 = np.max(self.inpTimeFrame)

      if isinstance(S2, list):
        A2 = np.max(np.asarray(list(chain.from_iterable(self.invTimeFrame))))
      else:
        A2 = np.max(self.invTimeFrame)

      if isinstance(S3, list):
        A3 = np.max(np.asarray(list(chain.from_iterable(self.outTimeFrame))))
      else:
        A3 = np.max(self.outTimeFrame)

      timeSteps = np.round(np.max(np.array([A1, A2, A3])))

    else:
      timeSteps = S1[1]

    MBPs = np.ceil(timeSteps / mbaTime)

    #iterations, elements, time
    self.MUFCalcs = np.zeros((IT, len(ck0), int(mbaTime * MBPs)))

    # Iterations, Locs, Samples, Elements
    # self.invEFrame
    self.PB.setValue(0)
    #self.statusBar().clearMessage()
    self.StatDlg.UpdateDispText('Calculating MUF')
    QtCore.QCoreApplication.instance().processEvents()
    self.PB.setValue(0)
    loopcounter = 0
    totalloops = (len(ck0)*(MBPs-1)*(len(self.inpEFrame)+len(self.outEFrame)+len(self.invEFrame)))
    # start MUF calc here
    # sum(input) - sum(output) - delta(inventory)
    # use data from (i-1):i to set MUF for period i:i+1
    ############################################  MUF Calculation  ################################################
    # for each MUF test
    if GF == 1:
      for ZZ in range(0, len(ck0)):  #for each test

        if ck0[ZZ] in self.EMD:
          key = self.EMD[ck0[ZZ]]
        else:
          key = 4

        for i in range(1, int(MBPs)):  #each MBP
          #print(p)
          QtCore.QCoreApplication.instance().processEvents()
          self.PB.setValue(loopcounter / totalloops*100)
          #self.PB.setValue((ZZ*(MBPs-1) + i)/(len(ck0)*(MBPs-1))*100)


          for j in range(
              0, len(self.inpEFrame)
          ):  #for each location -- have to do individually because the elements is per location in the list


            EMI = j

            QtCore.QCoreApplication.instance().processEvents()
            self.PB.setValue(loopcounter / totalloops*100)
            loopcounter +=1
            IntV = np.logical_and(
                self.inpTimeFrame[j] >= mbaTime * (i - 1),
                self.inpTimeFrame[j] <= mbaTime * i).reshape(
                    (-1,))  #select the indices for the relevant time


            self.MUFCalcs[:, ZZ, i * mbaTime:(i + 1) * mbaTime] += \
            np.tile(AuxFunctions.trapSum(IntV,self.inpTimeFrame[j],self.inpEFrame[j],ck0[ZZ],self.ErrorMatrix[EMI, key]), (mbaTime, 1)).transpose()


          for j in range(0, len(self.outEFrame)):

            EMI = j + len(S1) + len(S2)

            QtCore.QCoreApplication.instance().processEvents()
            self.PB.setValue(loopcounter / totalloops*100)
            loopcounter +=1

            IntV = np.logical_and(
                self.outTimeFrame[j] >= mbaTime * (i - 1),
                self.outTimeFrame[j] <= mbaTime * i).reshape((-1,))

            self.MUFCalcs[:, ZZ, i * mbaTime:(i + 1) * mbaTime] -= \
            np.tile(AuxFunctions.trapSum(IntV,self.outTimeFrame[j],self.outEFrame[j],ck0[ZZ],self.ErrorMatrix[EMI, key]), (mbaTime, 1)).transpose()

          for j in range(0, len(self.invEFrame)):

            EMI = j + len(S1)

            QtCore.QCoreApplication.instance().processEvents()
            self.PB.setValue(loopcounter / totalloops*100)
            loopcounter +=1

            StartT = np.abs(self.invTimeFrame[j].reshape((-1,)) - mbaTime *
                            (i - 1)).argmin()
            EndT = np.abs(self.invTimeFrame[j].reshape((-1,)) -
                          mbaTime * i).argmin()

            if i == 1:
              self.MUFCalcs[:, ZZ, i * mbaTime:(i + 1) * mbaTime] -= \
              np.tile((self.invEFrame[j][:, EndT, ck0[ZZ]]), (mbaTime, 1)).transpose()

            else:
              self.MUFCalcs[:, ZZ, i * mbaTime:(i + 1) * mbaTime] -= \
              np.tile((self.invEFrame[j][:, EndT, ck0[ZZ]] - self.invEFrame[j][:, StartT,ck0[ZZ]]), (mbaTime, 1)).transpose()

    else:  #basically if not mat type
      for ZZ in range(0, len(ck0)):
        # for each MBP
        for i in range(1, int(MBPs)):
          QtCore.QCoreApplication.instance().processEvents(
          )  # ensures window isn't seen as unresponsive
          # [all iterations, MUF test #, mba interval] = [all iterations, all locations, mba interval, element]
          # collapse over location and sum over interval
          # this is like 70x faster than doing loops

          # Input #
          self.MUFCalcs[:, ZZ, i * mbaTime:(i + 1) * mbaTime] += \
          np.tile(np.sum(np.sum(self.inpEFrame[:, :, (i - 1) * mbaTime:i * mbaTime, ck0[ZZ]], axis=2), axis=1),(mbaTime, 1)).transpose()

          # Output #
          self.MUFCalcs[:, ZZ, i * mbaTime:(i + 1) * mbaTime] -= \
          np.tile(np.sum(np.sum(self.outEFrame[:, :, (i - 1) * mbaTime:i * mbaTime, ck0[ZZ]], axis=2), axis=1),(mbaTime, 1)).transpose()

          # Inventory #
          if i == 1:
            self.MUFCalcs[:, ZZ, i * mbaTime:(i + 1) * mbaTime] -= \
            np.tile(np.sum((self.invEFrame[:, :, i * mbaTime, ck0[ZZ]]),axis=1), (mbaTime, 1)).transpose()
          else:
            self.MUFCalcs[:, ZZ, i * mbaTime:(i + 1) * mbaTime] -= \
            np.tile(np.sum((self.invEFrame[:, :, (i) * mbaTime, ck0[ZZ]] - self.invEFrame[:, :, (i - 1) * mbaTime,ck0[ZZ]]),axis=1), (mbaTime, 1)).transpose()

    self.StatDlg.UpdateDispText('Finished MUF Calculation')
    self.PB.setValue(100)
    QtCore.QCoreApplication.instance().processEvents()

  def SEMUF(self):
    """
            Function for calculating Sigma MUF
            and logging the error contributions
            by location and error type.
    """
    self.StatDlg.UpdateDispText('Calculating SEID')
    QtCore.QCoreApplication.instance().processEvents()

    if hasattr(self, 'Wizard'):  #if data has been imported
      TotalLocs = int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + int(
          self.Wizard.OutKMP)
    else:
      TotalLocs = np.shape(self.SS.Inputs)[0] + np.shape(
          self.SS.Inventories)[0] + np.shape(self.SS.Outputs)[0]

    #what location within the dataset
    #was requested to be operated on?
    ck0 = []
    if self.CB_PuSMUF.isChecked() == 1:
      ck0.append(self.PuLoc)
      self.metricBox.addItem('Pu SEID')
    else:
      None

    if self.CB_USMUF.isChecked() == 1:
      ck0.append(self.ULoc)
      self.metricBox.addItem('U SEID')
    else:
      None

    if self.CB_GSMUF.isChecked() == 1:
      ck0.append(self.GLoc)
      self.metricBox.addItem('Generic SEID')
    else:
      None





    ck1 = self.CB_PuMUF.isChecked() + self.CB_PuSMUF.isChecked(
    ) + self.CB_PuSITMUF.isChecked() + self.CB_PuSPage.isChecked()
    ck2 = self.CB_UMUF.isChecked() + self.CB_USMUF.isChecked(
    ) + self.CB_USITMUF.isChecked() + self.CB_USPage.isChecked()
    ck3 = self.CB_GMUF.isChecked() + self.CB_GSMUF.isChecked(
    ) + self.CB_GSITMUF.isChecked() + self.CB_GSPage.isChecked()

    mbaTime = int(self.MBPBox.text())
    IT = int(self.IterBox.text())

    GF = 0
    if hasattr(self,'Wizard'):
      if self.Wizard.IsMatV == 1:
        GF = 1

    if hasattr(self,'SS'):
      GF = 1

    if GF == 1:
      if isinstance(self.inpFrame, list):
        S1 = []
        for JR in range(len(self.inpFrame)):
          S1.append(np.shape(self.inpFrame[JR]))
      else:
        S1 = []
        for JR in range(len(self.inpFrame)):
          S1.append(np.shape(self.inpFrame[JR, :, :]))

      if isinstance(self.invFrame, list):
        S2 = []
        for JR in range(len(self.invFrame)):
          S2.append(np.shape(self.invFrame[JR]))
      else:
        S2 = []
        for JR in range(len(self.invFrame)):
          S2.append(np.shape(self.invFrame[JR, :, :]))

      if isinstance(self.outFrame, list):
        S3 = []
        for JR in range(len(self.outFrame)):
          S3.append(np.shape(self.outFrame[JR]))
      else:
        S3 = []
        for JR in range(len(self.outFrame)):
          S3.append(np.shape(self.outFrame[JR, :, :]))

    else:
      S1 = np.shape(self.inpFrame)
      S2 = np.shape(self.invFrame)
      S3 = np.shape(self.outFrame)

    if isinstance(S1, list) or isinstance(S2, list) or isinstance(S3, list):
      if isinstance(S1, list):
        A1 = np.max(np.asarray(list(chain.from_iterable(
            self.inpTimeFrame))))  #unroll list
      else:
        A1 = np.max(self.inpTimeFrame)

      if isinstance(S2, list):
        A2 = np.max(np.asarray(list(chain.from_iterable(self.invTimeFrame))))
      else:
        A2 = np.max(self.invTimeFrame)

      if isinstance(S3, list):
        A3 = np.max(np.asarray(list(chain.from_iterable(self.outTimeFrame))))
      else:
        A3 = np.max(self.outTimeFrame)

      timeSteps = np.round(np.max(np.array([A1, A2, A3])))

    else:
      timeSteps = S1[1]

    MBPs = np.ceil(timeSteps / mbaTime)

    #SEMUF contribution from individual components is difficult to
    #determine in some ways, but it is assumed that, for example,
    #the random component is (value)**2 * (rand)**2
    #probably reasonable for a simple MB, but changes if
    #covariance arises
    self.SEMUFCalcs = np.zeros((IT, len(ck0), int(MBPs * mbaTime)))
    self.SEMUFContribR = np.zeros((IT, TotalLocs, int(MBPs)))
    self.SEMUFContribS = np.zeros((IT, TotalLocs, int(MBPs)))

    # SEID is the sqrt of Input Variance + Inventory Variance + Output Variance
    # sys and rand are the error for the measurement tech
    # Variance is (observed_value)^2 * (sys^2 + rand^2) for in and out
    # first inv is
    # (inventory^2) * (sys^2 +rand^2)
    # else
    # (Begin^2+End^2) * (sys^2 + rand^2)


    loopcounter = 0
    totalloops = (len(ck0)*(MBPs-1)*(len(self.inpEFrame)+len(self.outEFrame)+len(self.invEFrame)))

    ############################################  SEID Calculation  ###############################################
    if GF == 1:
      self.SEMUFContribI = np.zeros(
        (IT, TotalLocs, int(MBPs)))  #lazy, helps later
    #note that the integration for the mat case requires
    #the aux trap function
      PBTot = len(ck0) * int(MBPs) * TotalLocs * IT
      GF = 1
      for ZZ in range(0, len(ck0)):  #each test type



        if ck0[ZZ] in self.EMD:
          key = self.EMD[ck0[ZZ]]
        else:
          key = 4


        InpVar = np.zeros((IT,int(MBPs * mbaTime)))
        InvVar = np.zeros((IT,int(MBPs * mbaTime)))
        OutVar = np.zeros((IT,int(MBPs * mbaTime)))

        for i in range(1, int(MBPs)):  #for each location


          for j in range(0, len(S1)):  #MBPs
            EMI = j

            QtCore.QCoreApplication.instance().processEvents()
            self.PB.setValue(loopcounter / totalloops*100)
            loopcounter +=1

            IntV = np.logical_and(
                self.inpTimeFrame[j] >= mbaTime * (i - 1),
                self.inpTimeFrame[j] <= mbaTime * i).reshape(
                    (-1,))  #select the indices for the relevant time

            AFTS = AuxFunctions.trapSum(IntV,self.inpTimeFrame[j],self.inpEFrame[j],ck0[ZZ],self.ErrorMatrix[EMI, key])
            VR = AFTS**2 * self.ErrorMatrix[j, key]**2
            VS = AFTS**2 * self.ErrorMatrix[j, key + 1]**2

            #variance is stored as a function of time, but contributions are
            #stored per MBP which makes it easier to put in a table later
            #especially considering the time might be variable
            InpVar[:,i * mbaTime:(i + 1) * mbaTime] += ((VR + VS) * np.ones(
              (mbaTime,IT))).T
            self.SEMUFContribR[:, j, i] = VR
            self.SEMUFContribS[:, j, i] = VS
            self.SEMUFContribI[:, j, i] = AFTS



          for j in range(0, len(S2)):
            EMI = j + len(S1)
            StartT = np.abs(self.invTimeFrame[j].reshape((-1,)) - mbaTime *
                            (i - 1)).argmin()
            EndT = np.abs(self.invTimeFrame[j].reshape((-1,)) -
                          mbaTime * i).argmin()

            QtCore.QCoreApplication.instance().processEvents()
            self.PB.setValue(loopcounter / totalloops*100)
            loopcounter +=1

            if i == 1:
              VR = self.invEFrame[j][:, EndT, ck0[ZZ]]**2 * self.ErrorMatrix[EMI, key]**2
              VS = self.invEFrame[j][:, EndT, ck0[ZZ]]**2 * self.ErrorMatrix[EMI, key + 1]**2

              self.SEMUFContribI[:, j + len(S1),
                                i] = self.invEFrame[j][:, EndT, ck0[ZZ]]

            else:

              VR = (self.invEFrame[j][:, StartT, ck0[ZZ]]**2 + self.invEFrame[j][:, EndT, ck0[ZZ]]**2) * self.ErrorMatrix[EMI, key]**2

              VS = (self.invEFrame[j][:, StartT, ck0[ZZ]]**2 + self.invEFrame[j][:, EndT, ck0[ZZ]]**2) * self.ErrorMatrix[EMI, key+1]**2

              self.SEMUFContribI[:, j + len(S1),
                  i] = self.invEFrame[j][:, EndT, ck0[ZZ]]

            self.SEMUFContribR[:, j + len(S1), i] = VR
            self.SEMUFContribS[:, j + len(S1), i] = VS
            InvVar[:,i * mbaTime:(i + 1) * mbaTime] += ((VR + VS) * np.ones(
                (mbaTime,IT))).T



          for j in range(0, len(S3)):
            IntV = np.logical_and(
                self.outTimeFrame[j] >= mbaTime * (i - 1),
                self.outTimeFrame[j] <= mbaTime * i).reshape((-1,))
            EMI = j + len(S1) + len(S2)

            QtCore.QCoreApplication.instance().processEvents()
            self.PB.setValue(loopcounter / totalloops*100)
            loopcounter +=1

            AFTS = AuxFunctions.trapSum(IntV,self.outTimeFrame[j],self.outEFrame[j],ck0[ZZ],self.ErrorMatrix[EMI, key])
            VR = AFTS**2 * self.ErrorMatrix[EMI, key]**2
            VS = AFTS**2 * self.ErrorMatrix[EMI, key+1]**2


            OutVar[:,i * mbaTime:(i + 1) * mbaTime] += ((VR + VS) * np.ones(
              (mbaTime,IT))).T
            self.SEMUFContribR[:, j + len(S1) + len(S2), i] = VR
            self.SEMUFContribS[:, j + len(S1) + len(S2), i] = VS
            self.SEMUFContribI[:, j + len(S1) + len(S2), i] = AFTS

        self.SEMUFCalcs[:, ZZ, :] = np.sqrt(InpVar + InvVar + OutVar)

    else:  #if not a mat
      #assumes data is collected
      #once per unit of time
      PBTot = len(ck0) * int(MBPs) * TotalLocs * IT
      self.PB.setValue(0)
      for ZZ in range(0, len(ck0)):  # test type
        QtCore.QCoreApplication.instance().processEvents(
        )  # ensures window isn't seen as unresponsive

        if ck0[ZZ] in self.EMD:
          key = self.EMD[ck0[ZZ]]
        else:
          key = 4

        for Z in range(0, IT):  # iteration

          # inputs
          InpVar = np.zeros((int(MBPs * mbaTime),))
          for j in range(0, int(S1[0])):

            for i in range(1, int(MBPs)):
              QtCore.QCoreApplication.instance().processEvents()
             # self.PB.setValue(
               #   ((ZZ * IT * TotalLocs * MBPs) + (Z * TotalLocs * MBPs) +
               #    (j * MBPs) + i) / PBTot * 100)
              # inventory, sys and rand components
              VR = (np.sum(self.inpEFrame[Z, j, (i - 1) * mbaTime:i * mbaTime, ck0[ZZ]]))**2 * \
                                                       (self.ErrorMatrix[j, key])**2

              VS = (np.sum(self.inpEFrame[Z, j, (i - 1) * mbaTime:i * mbaTime, ck0[ZZ]]))**2 * \
                                                         (self.ErrorMatrix[j, key + 1])**2

              InpVar[i * mbaTime:(i + 1) * mbaTime] += (VR + VS) * np.ones(
                  (mbaTime,))
              self.SEMUFContribR[Z, j, i] = VR
              self.SEMUFContribS[Z, j, i] = VS

          # inventory
          InvVar = np.zeros((int(MBPs * mbaTime),))
          for j in range(0, int(S2[0])):

            for i in range(1, int(MBPs)):

              EMI = j + int(S1[0])

              self.PB.setValue(
                  ((ZZ * IT * TotalLocs * MBPs) + (Z * TotalLocs * MBPs) +
                   ((EMI) * MBPs) + i) / PBTot * 100)

              if i == 1:
                VR = (self.invEFrame[Z, j, i * mbaTime, ck0[ZZ]])**2 * \
                               (self.ErrorMatrix[EMI, key])**2

                VS =(self.invEFrame[Z, j, i * mbaTime, ck0[ZZ]])**2 * \
                              (self.ErrorMatrix[EMI, key + 1])**2

                InvVar[i * mbaTime:(i + 1) * mbaTime] += (VR + VS) * np.ones(
                    (mbaTime,))
                self.SEMUFContribR[Z, S1[0] + j, i] = VR
                self.SEMUFContribS[Z, S1[0] + j, i] = VS

              else:
                VR = ((self.invEFrame[Z, j, (i - 1) * mbaTime, ck0[ZZ]])**2 + \
                           (self.invEFrame[Z, j, i * mbaTime, ck0[ZZ]],2)) * \
                           (self.ErrorMatrix[EMI, key])**2

                VS = ((self.invEFrame[Z, j, (i - 1) * mbaTime, ck0[ZZ]])**2 + \
                           (self.invEFrame[Z, j, i * mbaTime, ck0[ZZ]],2)) * \
                           (self.ErrorMatrix[EMI, key + 1])**2

                InvVar[i * mbaTime:(i + 1) * mbaTime] += (VR + VS) * np.ones(
                    (mbaTime,))
                self.SEMUFContribR[Z, S1[0] + j, i] = VR
                self.SEMUFContribS[Z, S1[0] + j, i] = VS

          # output
          OutVar = np.zeros((int(MBPs * mbaTime),))
          for j in range(0, int(S3[0])):

            for i in range(1, int(MBPs)):
              EMI = j + int(S1[0]) + int(S2[0])

              self.PB.setValue(
                  ((ZZ * IT * TotalLocs * MBPs) + (Z * TotalLocs * MBPs) +
                   ((EMI) * MBPs) + i) / PBTot * 100)

              VR =(np.sum(self.outEFrame[Z, j, (i - 1) * mbaTime:i * mbaTime, ck0[ZZ]]))**2 * \
                                                       (self.ErrorMatrix[EMI, key])**2

              VS =(np.sum(self.outEFrame[Z, j, (i - 1) * mbaTime:i * mbaTime, ck0[ZZ]]))**2 * \
                                                       (self.ErrorMatrix[EMI, key + 1])**2

              OutVar[i * mbaTime:(i + 1) * mbaTime] += (VR + VS) * np.ones(
                  (mbaTime,))
              self.SEMUFContribR[Z, S1[0] + S2[0] + j, i] = VR
              self.SEMUFContribS[Z, S1[0] + S2[0] + j, i] = VS

          self.SEMUFCalcs[Z, ZZ, :] = np.sqrt(InpVar + InvVar + OutVar)

    self.StatDlg.UpdateDispText('SEID Finished')
    QtCore.QCoreApplication.instance().processEvents()

  def SITMUF(self):
    """
            Function responsible for
            carrying out the SITMUF transform.

            More information available
            on the github.
    """

    self.decompStatus = 1

    #the procedure below should
    #look familiar to the MUF
    #and SEMUF calculations
    GF = 0
    if hasattr(self,'Wizard'):
        GF = 1

    if hasattr(self,'SS'):
      GF = 1

    if GF == 1:
      if isinstance(self.inpFrame, list):
        S1 = []
        for JR in range(len(self.inpFrame)):
          S1.append(np.shape(self.inpFrame[JR]))
      else:
        S1 = []
        for JR in range(len(self.inpFrame)):
          S1.append(np.shape(self.inpFrame[JR, :, :]))

      if isinstance(self.invFrame, list):
        S2 = []
        for JR in range(len(self.invFrame)):
          S2.append(np.shape(self.invFrame[JR]))
      else:
        S2 = []
        for JR in range(len(self.invFrame)):
          S2.append(np.shape(self.invFrame[JR, :, :]))

      if isinstance(self.outFrame, list):
        S3 = []
        for JR in range(len(self.outFrame)):
          S3.append(np.shape(self.outFrame[JR]))
      else:
        S3 = []
        for JR in range(len(self.outFrame)):
          S3.append(np.shape(self.outFrame[JR, :, :]))

      TotalLocs = len(S1) + len(S2) + len(S3)


    else:
      S1 = np.shape(self.inpFrame)
      S2 = np.shape(self.invFrame)
      S3 = np.shape(self.outFrame)
      TotalLocs = int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + int(
          self.Wizard.OutKMP)

    ck0 = []
    ck1 = []
    if self.CB_PuSITMUF.isChecked() == 1:
      ck0.append(self.PuLoc)
      self.metricBox.addItem('Pu SITMUF')
    else:
      None

    if self.CB_USITMUF.isChecked() == 1:
      ck0.append(self.ULoc)
      self.metricBox.addItem('U SITMUF')
    else:
      None

    if self.CB_GSITMUF.isChecked() == 1:
      ck0.append(self.GLoc)
      self.metricBox.addItem('Generic SITMUF')
    else:
      None

    if self.CB_PuSPage.isChecked() == 1:
      ck1.append(self.PuLoc)
      self.metricBox.addItem('Page Pu SITMUF')
    else:
      None

    if self.CB_USPage.isChecked() == 1:
      ck1.append(self.ULoc)
      self.metricBox.addItem('Page U SITMUF')
    else:
      None

    if self.CB_GSPage.isChecked() == 1:
      ck1.append(self.GLoc)
      self.metricBox.addItem('Generic Page SITMUF')
    else:
      None

    self.statusBar().clearMessage()
    if len(ck1) > 0:
      self.StatDlg.UpdateDispText('Calculating SITMUF + Page')
    else:
      self.StatDlg.UpdateDispText('Calculating SITMUF')
    QtCore.QCoreApplication.instance().processEvents()


    # setup error table


    mbaTime = int(self.MBPBox.text())
    IT = int(self.IterBox.text())

    if isinstance(S1, list) or isinstance(S2, list) or isinstance(S3, list):
      if isinstance(S1, list):
        A1 = np.max(np.asarray(list(chain.from_iterable(
            self.inpTimeFrame))))  #unroll list
      else:
        A1 = np.max(self.inpTimeFrame)

      if isinstance(S2, list):
        A2 = np.max(np.asarray(list(chain.from_iterable(self.invTimeFrame))))
      else:
        A2 = np.max(self.invTimeFrame)

      if isinstance(S3, list):
        A3 = np.max(np.asarray(list(chain.from_iterable(self.outTimeFrame))))
      else:
        A3 = np.max(self.outTimeFrame)

      timeSteps = np.round(np.max(np.array([A1, A2, A3])))

    else:
      timeSteps = S1[1]

    MBPs = np.ceil(timeSteps / mbaTime)

    self.SITMUFCalcs = np.zeros((IT, len(ck0), int((MBPs - 1) * mbaTime)))
    self.PageCalcs = np.zeros((IT, len(ck0), int((MBPs - 1) * mbaTime)))
    covmatrix = np.zeros((int(MBPs), int(MBPs)))
    k = 0.5
    # Iterations, Locs, Samples, Elements eFrame

    ############################################  SITMUF Calculation  ###############################################
    #
    # The first part is to calculate the covariance with consists of off-diagonal and diagonal terms
    # Need to optimize this later as I think I could do better than what was originally implimented in matlab
    #################################################################################################################
    MBPb = MBPs + 1

    totalloops = ((MBPs-1)**2 + MBPs) / 2 #nth triangle number, like factorial but addition
    self.PB.setValue(0)
    loopcounter = 0
    covmatrix = np.zeros((IT,int(MBPs), int(MBPs)))
    if GF == 1:
      for ZZ in range(len(ck0)):
        if self.decompStatus == 1:

          if ck0[ZZ] in self.EMD:
            key = self.EMD[ck0[ZZ]]
          else:
            key = 4

          for P in range(1,int(MBPs)):
              for j in range(0,P):
                  QtCore.QCoreApplication.instance().processEvents()
                  self.PB.setValue(loopcounter/totalloops*100)
                  loopcounter +=1


                  t1 = j*mbaTime
                  t2 = t1+mbaTime
                  t3 = P*mbaTime


                  #diagonal terms
                  if j == P-1:

                      term1 = np.zeros((IT,))
                      term2 = np.zeros((IT,))
                      term3 = np.zeros((IT,))
                      term4 = np.zeros((IT,))
                      term5 = np.zeros((IT,))

                      for k in range(len(S1)):
                          IntV = np.logical_and(self.inpTimeFrame[k] >= t1,self.inpTimeFrame[k] <= t2).reshape((-1,))  #select the indices for the relevant time
                          term1 += AuxFunctions.trapSum(IntV,self.inpTimeFrame[k],self.inpEFrame[k],ck0[ZZ],self.ErrorMatrix[k, key]) **2 * (self.ErrorMatrix[k, key]**2 + self.ErrorMatrix[k, key+1]**2)

                      for k in range(len(S3)):
                          IntV = np.logical_and(self.outTimeFrame[k] >= t1,self.outTimeFrame[k] <= t2).reshape((-1,))
                          EMI = k + len(S1) + len(S2)
                          term2 += AuxFunctions.trapSum(IntV,self.outTimeFrame[k],self.outEFrame[k],ck0[ZZ],self.ErrorMatrix[EMI, key])**2 * (self.ErrorMatrix[EMI, key]**2 + self.ErrorMatrix[EMI, key+1]**2)

                      for k in range(len(S2)):
                          EMI = k+len(S1)
                          StartT = np.abs(self.invTimeFrame[k].reshape((-1,)) - t1).argmin()
                          EndT = np.abs(self.invTimeFrame[k].reshape((-1,)) - t2).argmin()
                          term3 += self.invEFrame[k][:,EndT,ck0[ZZ]]**2 * (self.ErrorMatrix[EMI, key]**2 + self.ErrorMatrix[EMI, key+1]**2)


                      if j != 0:
                          for k in range(len(S2)):
                              EMI = k + len(S1)
                              StartT = np.abs(self.invTimeFrame[k].reshape((-1,)) -t1).argmin()
                              EndT = np.abs(self.invTimeFrame[k].reshape((-1,)) - t2).argmin()

                              term4 += self.invEFrame[k][:,StartT,ck0[ZZ]]**2 * (self.ErrorMatrix[EMI, key]**2 + self.ErrorMatrix[EMI, key+1]**2)
                              term5 += self.invEFrame[k][:,StartT,ck0[ZZ]] * self.invEFrame[k][:,EndT,ck0[ZZ]] * self.ErrorMatrix[EMI, key + 1]**2

                      covmatrix[:,j,j] = term1 + term2 + term3 + term4 - 2 * term5

                  #off-diagonal terms
                  else:
                      term1 = np.zeros((IT,))
                      term2 = np.zeros((IT,))
                      term3 = np.zeros((IT,))
                      term4 = np.zeros((IT,))
                      term5 = np.zeros((IT,))

                      term3a = np.zeros((IT,))
                      term3b = np.zeros((IT,))
                      term3c = np.zeros((IT,))

                      term4a = np.zeros((IT,))
                      term4b = np.zeros((IT,))
                      term4c = np.zeros((IT,))

                      term5a = np.zeros((IT,))
                      term5b = np.zeros((IT,))
                      term5c = np.zeros((IT,))

                      A = np.zeros((IT,))
                      B = np.zeros((IT,))
                      C = np.zeros((IT,))

                      for k in range(len(S1)):
                          IntV = np.logical_and(self.inpTimeFrame[k] >= t1,self.inpTimeFrame[k] <= t2).reshape((-1,))  #select the indices for the relevant time
                          IntV2 = np.logical_and(self.inpTimeFrame[k] >= t3 - mbaTime,self.inpTimeFrame[k] <= t3).reshape((-1,))  #select the indices for the relevant time

                          A = AuxFunctions.trapSum(IntV, self.inpTimeFrame[k],self.inpEFrame[k], ck0[ZZ],self.ErrorMatrix[k, key])
                          B = AuxFunctions.trapSum(IntV2, self.inpTimeFrame[k],self.inpEFrame[k], ck0[ZZ],self.ErrorMatrix[k, key])
                          C = self.ErrorMatrix[k, key + 1]**2
                          term1 += (A*B*C)

                      for k in range(len(S3)):
                          IntV = np.logical_and(self.outTimeFrame[k] >= t1,self.outTimeFrame[k] <= t2).reshape((-1,))  #select the indices for the relevant time
                          IntV2 = np.logical_and(self.outTimeFrame[k] >= t3 - mbaTime,self.outTimeFrame[k] <= t3).reshape((-1,))  #select the indices for the relevant time
                          EMI = k + len(S1) + len(S2)

                          A = AuxFunctions.trapSum(IntV, self.outTimeFrame[k],self.outEFrame[k], ck0[ZZ],self.ErrorMatrix[EMI, key])
                          B = AuxFunctions.trapSum(IntV2, self.outTimeFrame[k],self.outEFrame[k], ck0[ZZ],self.ErrorMatrix[EMI, key])
                          C = self.ErrorMatrix[EMI, key + 1]**2
                          term2 += (A*B*C)

                      for k in range(len(S2)):
                          StartT = np.abs(self.invTimeFrame[k].reshape((-1,)) - t1).argmin()
                          EndT =  np.abs(self.invTimeFrame[k].reshape((-1,)) -  t2).argmin()
                          EndT2 = np.abs(self.invTimeFrame[k].reshape((-1,)) -  t3).argmin()
                          EndT3 = np.abs(self.invTimeFrame[k].reshape((-1,)) - (t2 - mbaTime)).argmin()
                          EndT4 = np.abs(self.invTimeFrame[k].reshape((-1,)) - (t3 - 2 * mbaTime)).argmin()
                          EMI = k + len(S1)

                          term3a = self.invEFrame[k][:, EndT, ck0[ZZ]] * self.invEFrame[k][:, EndT2, ck0[ZZ]]
                          term3b = self.invEFrame[k][:, EndT3, ck0[ZZ]] * self.invEFrame[k][:, EndT4,ck0[ZZ]]
                          term3c = self.ErrorMatrix[EMI, key + 1]**2
                          term3 += (term3a+term3b)*term3c

                          term4a = self.invEFrame[k][:, EndT, ck0[ZZ]] * self.invEFrame[k][:, EndT4, ck0[ZZ]]
                          term4b = self.ErrorMatrix[EMI, key + 1]**2
                          if P - j == 1:
                              term4c = self.ErrorMatrix[EMI, key]**2
                          else:
                              term4c = np.zeros((IT,))

                          #TODO: ???
                          term4 += term4a*(term4b+term4c)*0

                          term5a = self.invEFrame[k][:, EndT3, ck0[ZZ]] * self.invEFrame[k][:, EndT2,ck0[ZZ]]
                          term5b = self.ErrorMatrix[EMI, key+1]**2
                          if j-P == 1:
                              term5c = self.ErrorMatrix[EMI, key]**2
                          else:
                              term5c = np.zeros((IT,))

                          covmatrix[:,j,P-1] = term1+term2+term3-term4-term5
                          covmatrix[:,P-1,j] = term1+term2+term3-term4-term5

              for k in range(IT):
                tempcovmatrix = covmatrix[k,:P,:P]
                tempID = np.zeros((P,))

                for ZR in range(0,P):
                    tempID[ZR] = self.MUFCalcs[k,ZZ,ZR*mbaTime]

                try:
                    V = np.linalg.cholesky(tempcovmatrix)
                except:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Critical)
                    msg.setText("Covariance decomposition failure")
                    msg.setInformativeText("This usually occurs when the material balance is not setup correctly")
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    self.decompStatus = 0
                    break

                SITMUF = np.matmul(np.linalg.inv(V),tempID)
                self.SITMUFCalcs[k,ZZ,int((P - 1) * mbaTime):int(P * mbaTime)] = np.ones((mbaTime,)) * SITMUF[P - 1]

                if len(ck1) > 0:
                    if ck0[ZZ] == ck1[ZZ]:
                        if P == 1:
                          RZN = SITMUF[P - 1]
                        else:
                          RZN = SITMUF[P - 2] + SITMUF[P - 1] - 0.5

                        if RZN < 0:
                          RZN = 0

                        self.PageCalcs[k,ZZ,int((P - 1) * mbaTime):int(P * mbaTime)] = np.ones((mbaTime,)) * RZN

    else:

      for ZZ in range(0, len(ck0)):  # type of calc

        if ck0[ZZ] in self.EMD:
          key = self.EMD[ck0[ZZ]]
        else:
          key = 4

        for Z in range(0, IT):  # iterations
          QtCore.QCoreApplication.instance().processEvents(
          )  # ensures window isn't seen as unresponsive
          if self.decompStatus == 1:
              for P in range(
                  1, int(MBPs)
              ):  # the covmatrix grows over time so have to do this double loop
                    for j in range(0, P):
                      QtCore.QCoreApplication.instance().processEvents(
                      )  # ensures no freezing when box is dragged during exe



                      # first entry needs to be 0,0 in covmatrix
                      t1 = j * mbaTime
                      t2 = t1 + mbaTime
                      t3 = P * mbaTime

                      if j == P - 1:

                        ################### Diagonal Terms ########################
                        ###################    Term 1    ##########################
                        # (current_inp)^2 * (ran^2 + sys^2)
                        term1 = 0
                        for k in range(0, int(S1[0])):
                          term1 +=(np.sum(self.inpEFrame[Z, k, t1:t2, ck0[ZZ]]))**2 * \
                                   ((self.ErrorMatrix[k, key + 1])**2 +
                                   (self.ErrorMatrix[k, key])**2)

                        ###################    Term 2    ##########################
                        # (current_out)^2 * (ran^2 +sys^2)
                        term2 = 0

                        for k in range(0, int(S3[0])):
                          EMI = k + int(S1[0]) + int(S2[0])

                          term2 +=(np.sum(self.outEFrame[Z, k, t1:t2, ck0[ZZ]]))**2 * \
                                   ((self.ErrorMatrix[EMI, key + 1])**2 +
                                   (self.ErrorMatrix[EMI, key])**2)

                        ###################    Term 3    ##########################
                        # (current_inv)^2 * (ran^2 + sys^2)
                        term3 = 0

                        for k in range(0, int(S2[0])):
                          EMI = k + int(S1[0])

                          term3 += (self.invEFrame[Z, k, t2, ck0[ZZ]])**2 * \
                                   ((self.ErrorMatrix[EMI, key + 1])**2 +
                                    (self.ErrorMatrix[EMI, key])**2)

                        ###################    Term 4+5    ########################
                        # 0 at first MBP
                        # else term4 is previous_inv^2 (ran^2+sys^2)
                        # term5 is -2*(current_inv*prev_inv*sys^2)
                        if j == 0:
                          term4 = 0
                          term5 = 0
                        else:
                          term4 = 0
                          term5 = 0

                          for k in range(0, int(S2[0])):
                            EMI = k + int(S1[0])

                            term4 += (self.invEFrame[Z, k, t1, ck0[ZZ]])**2 * \
                                     ((self.ErrorMatrix[EMI, key + 1])**2 +
                                      (self.ErrorMatrix[EMI, key])**2)

                            term5 += self.invEFrame[Z, k, t1, ck0[ZZ]] * \
                                     self.invEFrame[Z, k, t2, ck0[ZZ]] * \
                                     (self.ErrorMatrix[EMI, key + 1])**2

                        covmatrix[j, j] = term1 + term2 + term3 + term4 - 2 * term5

                      else:
                        ################### Off-Diagonal Terms ####################
                        ###################    Term 1    ##########################
                        # inp_current * inv_P * sys^2
                        term1 = 0
                        A = 0
                        B = 0
                        C = 0
                        for k in range(0, int(S1[0])):
                          A = np.sum(self.inpEFrame[Z, k, t1:t2, ck0[ZZ]])
                          B = np.sum(self.inpEFrame[Z, k, t3 - mbaTime:t3, ck0[ZZ]])
                          C = (self.ErrorMatrix[k, key + 1])**2

                          term1 += (A * B * C)

                        ###################    Term 2    ##########################
                        # out_current*out_P*sys^2
                        term2 = 0
                        A = 0
                        B = 0
                        C = 0
                        for k in range(0, int(S3[0])):
                          EMI = k + int(S1[0]) + int(S2[0])
                          A = np.sum(self.outEFrame[Z, k, t1:t2, ck0[ZZ]])
                          B = np.sum(self.outEFrame[Z, k, t3 - mbaTime:t3, ck0[ZZ]])
                          C = (self.ErrorMatrix[EMI, key + 1])**2

                          term2 += (A * B * C)

                        ###################    Term 3,4,5    #######################
                        # 3 - (inv_current*inv_P + inv_current-1*inv_P-1)sys^2
                        term3 = 0
                        term3a = 0
                        term3b = 0
                        term3c = 0

                        term4 = 0
                        term4a = 0
                        term4b = 0
                        term4c = 0

                        term5 = 0
                        term5a = 0
                        term5b = 0
                        term5c = 0

                        for k in range(0, int(S2[0])):
                          EMI = k + int(S1[0])

                          term3a = self.invEFrame[Z, k, t2,
                                                  ck0[ZZ]] * self.invEFrame[Z, k, t3,
                                                                            ck0[ZZ]]
                          term3b = self.invEFrame[Z, k, t2 - mbaTime,
                                                  ck0[ZZ]] * self.invEFrame[
                                                      Z, k, t3 - (2 * mbaTime), ck0[ZZ]]
                          term3c = (self.ErrorMatrix[EMI, key + 1])**2

                          term3 += (term3a + term3b) * term3c

                          # the condition for term4 is if P-j == 1
                          # the condition for term5 is if j-P == 1

                          term4a = self.invEFrame[Z, k, t2, ck0[ZZ]] * self.invEFrame[
                              Z, k, t3 - (2 * mbaTime), ck0[ZZ]]
                          term4b = (self.ErrorMatrix[EMI, key + 1])**2
                          if P - j == 1:
                            term4c = (self.ErrorMatrix[EMI, key])**2
                          else:
                            term4c = 0

                          term4 += term4a * (term4b + term4c) * 0

                          term5a = self.invEFrame[Z, k, t2 - mbaTime,
                                                  ck0[ZZ]] * self.invEFrame[Z, k, t3,
                                                                            ck0[ZZ]]
                          term5b = (self.ErrorMatrix[EMI, key + 1])**2

                          if j - P == 1:
                            term5c = (self.ErrorMatrix[EMI, key])**2
                          else:
                            term5c = 0

                          term5 += term5a * (term5b + term5c) * 0

                        covmatrix[j, P - 1] = term1 + term2 + term3 - term4 - term5
                        covmatrix[P - 1, j] = term1 + term2 + term3 - term4 - term5

                    tempcovmatrix = np.zeros((P, P))
                    tempID = np.zeros((P,))
                    tempcovmatrix = covmatrix[0:P, 0:P]

                    for ZR in range(0, P):
                      tempID[ZR] = self.MUFCalcs[Z, ZZ, ZR * mbaTime]


                    try:
                        yyy = np.linalg.cholesky(tempcovmatrix)
                    except:
                        msg = QtWidgets.QMessageBox()
                        msg.setIcon(QtWidgets.QMessageBox.Critical)
                        msg.setText("Covariance decomposition failure")
                        msg.setInformativeText("This usually occurs when the material balance is not setup correctly")
                        msg.setWindowTitle("Error")
                        msg.exec_()
                        self.decompStatus = 0
                        break
                    ptemp = np.zeros((P, P))

                    for z in range(0, P):
                      ptemp[z, z] = yyy[z, z]

                    zzz = np.linalg.solve(ptemp.T, yyy).T
                    ITMUF = np.linalg.solve(zzz, tempID.T)
                    SITMUF = np.linalg.solve(ptemp.T, ITMUF)

                    self.SITMUFCalcs[Z, ZZ,
                                     int((P - 1) * mbaTime):int(P * mbaTime)] = np.ones(
                                         (mbaTime,)) * SITMUF[P - 1]

                    # one sided page - remove negative values
                    if len(ck1) > 0:
                      if ck0[ZZ] == ck1[ZZ]:
                        if P == 1:
                          RZN = SITMUF[P - 1]
                        else:
                          RZN = SITMUF[P - 2] + SITMUF[P - 1] - 0.5

                        if RZN < 0:
                          RZN = 0

                        self.PageCalcs[Z,ZZ,int((P-1)*mbaTime):int(P*mbaTime)]=np.ones((mbaTime,))*RZN

    self.StatDlg.UpdateDispText('SITMUF Finished')
    QtCore.QCoreApplication.instance().processEvents()

class AuxFunctions:

  #trapezoidal integration, presumably this is
  #for square-like pulses of material
  def trapSum(relevantIndex,time,data,ele,TS,IT=None):

      #this is for indexing the data array
      #sometimes specific positions are
      #required by other functions
      if IT is not None:
          IDXC = IT
      else:
          IDXC = 0



      #these are actually fairly expensive to keep computing
      #calculate them here rather than in loop
      relevantDataVals = data[IDXC,relevantIndex,ele]
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

      pairs[:,1] += 1 #this ensures a zero is included which facilitates proper
                      #integration using the trapz function


      if IT is not None:
        dataArray = relevantDataVals.reshape((1,-1))
        timeArray = relevantTimeVals
        S0 = 1
      else:
        dataArray = np.swapaxes(data[:,relevantIndex,ele],0,1)
        bt = relevantTimeVals
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
      if np.sum(relevantDataVals[0:pairs[0,0]]) > T:
          RS = np.max(np.where(relevantDataVals[0:pairs[0,0]] > T))
          LS = np.min(np.where(relevantDataVals[0:pairs[0,0]] > T))
          seg = np.array([LS,RS]).reshape((1,-1))
          pairs = np.concatenate((seg,pairs),axis=0)
          timesegs.append(np.swapaxes(timeArray[LS:RS+1],0,1))
          datasegs.append(np.swapaxes(dataArray[LS:RS+1,],0,1))

      #look for a final pulse on the right of the timeseries that
      #might not have been accounted for
      if np.sum(data[0,relevantIndex,0][pairs[-1,1]+5:]) > T:
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
