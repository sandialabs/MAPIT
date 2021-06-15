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

          lddir = os.path.join(self.Wizard.InDir,
                               sorted(os.listdir(self.Wizard.InDir))[0])

          testM = np.loadtxt(lddir, delimiter=',')
        else:
          G = loadmat(
              self.Wizard.MatDir)  # should be only one .mat for all locations
          testM = G['in']['data'][0][0]

        # if there's only a single element it could be imported as
        # a single dimesion vector which we need to fix for code
        # further in to work as intended

        if len(
            np.shape(testM)
        ) == 1:  # adds a dimension in case single element is recorded as (X,) rather than (X,1)
          testM = np.expand_dims(testM, axis=0)

        eleInfer = np.min(np.shape(
            testM))  # assuming smallest dimension is number of elements

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
            lddir = os.path.join(self.Wizard.InDir,
                                 sorted(os.listdir(self.Wizard.InDir))[i])
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
            inpFrame = LiC2

        ##IO - Inventory
        liH = []
        if self.Wizard.IsMatV == 0:
          # need to infer the number of elements
          lddir = os.path.join(self.Wizard.InvDir,
                               sorted(os.listdir(self.Wizard.InvDir))[0])

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
            lddir = os.path.join(self.Wizard.InvDir,
                                 sorted(os.listdir(self.Wizard.InvDir))[i])
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
        # imported scene data
        # SS data is shape time, ele, loc

        # inputs

        self.SS.Inputs = np.swapaxes(self.SS.Inputs, 0, 2)
        self.SS.Inputs = np.swapaxes(self.SS.Inputs, 1, 2)
        inpFrame = self.SS.Inputs

        # inventories
        self.SS.Inventories = np.swapaxes(self.SS.Inventories, 0, 2)
        self.SS.Inventories = np.swapaxes(self.SS.Inventories, 1, 2)
        invFrame = self.SS.Inventories

        # outputs
        self.SS.Outputs = np.swapaxes(self.SS.Outputs, 0, 2)
        self.SS.Outputs = np.swapaxes(self.SS.Outputs, 1, 2)
        outFrame = self.SS.Outputs

        liH = ['U', 'Pu', 'Cs', 'Xe', 'Eu']  #predetermined elements
        self.GuessEles = 5

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

      #the lists are usually missing a dimension
      #required for later analysis
      if isinstance(self.inpFrame, list) == 0:
        if len(np.shape(self.inpFrame)) != 3:
          self.inpFrame = np.expand_dims(self.inpFrame, axis=2)

      if isinstance(self.invFrame, list) == 0:
        if len(np.shape(self.invFrame)) != 3:
          self.invFrame = np.expand_dims(self.invFrame, axis=2)

      if isinstance(self.outFrame, list) == 0:
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

    if hasattr(self, 'Wizard'):  #if data was imported
      TotalLocs = int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + int(
          self.Wizard.OutKMP)

      eleNames = self.Wizard.EleVec_IN
      O1 = int(self.Wizard.InKMP)
      O2 = O1 + int(self.Wizard.InvKMP)
    else:  #otherwise (scene selection)
      TotalLocs = np.shape(self.SS.Inputs)[0] + np.shape(
          self.SS.Inventories)[0] + np.shape(self.SS.Outputs)[0]

      eleNames = self.liH
      O1 = int(np.shape(self.SS.Inputs)[0])
      O2 = O1 + int(np.shape(self.SS.Inventories)[0])

    NumSamples = np.max(
        np.shape(self.invFrame)
    ) - self.offset  # samples should be max size of matrix less any offset

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

    ErrorMatrix = np.zeros((TotalLocs, 6))

    # setup error table using
    # previously described errors
    P = 0
    for i in range(0, self.EP.rowCount()):
      if self.EP.item(i, 0) is not None:
        for j in range(0, 6):
          ErrorMatrix[P, j] = float(self.EP.item(i, j).text()) / 100
        P += 1

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

    if hasattr(self,
               'Wizard'):  #if its imported get some information about the shape
      if self.Wizard.IsMatV == 1:
        GF = 1

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
          self.inpEFrame.append(np.zeros((IT, S1[i][0], S1[i][1])))
          self.inpSFrame.append(np.zeros((S1[i][0], S1[i][1])))
          self.inpRFrame.append(np.zeros((S1[i][0], S1[i][1])))

        self.invEFrame = []
        self.invSFrame = []
        self.invRFrame = []

        for i in range(0, len(self.invFrame)):
          self.invEFrame.append(np.zeros(
              (IT, S2[i][0], S2[i][1])))  #[Iterations, Locs, Samples, Elements]
          self.invSFrame.append(np.zeros((S2[i][0], S2[i][1])))
          self.invRFrame.append(np.zeros((S2[i][0], S2[i][1])))

        self.outEFrame = []
        self.outRFrame = []
        self.outSFrame = []

        for i in range(0, len(self.outFrame)):
          self.outEFrame.append(np.zeros(
              (IT, S3[i][0], S3[i][1])))  #[Iterations, Locs, Samples, Elements]
          self.outRFrame.append(np.zeros((S3[i][0], S3[i][1])))
          self.outSFrame.append(np.zeros((S3[i][0], S3[i][1])))

    if GF == 0:  #if it's not a mat assume uniform sampling
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

    ############################################ Error Propogation ################################################
    ##### This section is pretty ugly because I had originally written this to handle fixed-step sampled data such that it could be easily represented in matrix form     #####
    ##### However, that became problematic because for V&V purposes the MAPIT needed to be compared against SSPM, which was integrated in variable-time-step  #####
    ##### form. The MAT section uses potentially variable sample times to perform the error prop. This may be cleaned up in the future, but not enough budget now #####
    #######################################################################################################

    ############################################       Input       ###################################################
    ############################################        MAT        ###################################################
    # for each iteration
    # see github for more theory
    #observed = true(1+random*sys)
    if GF == 1:
      for Z in range(0, IT):
        QtCore.QCoreApplication.instance().processEvents(
        )  # ensures window isn't seen as unresponsive

        # locations, timesteps, elements
        self.inpRFrame = []
        self.inpSFrame = []

        # for each location
        for i in range(0, len(S1)):
          self.PB.setValue(
              np.floor((i + Z * len(S1)) /
                       ((len(S1) + len(S2) + len(S3)) * IT) * 100))
          QtCore.QCoreApplication.instance().processEvents(
          )  # ensures window isn't seen as unresponsive
          # for each element

          #assume sys differs by location only and doesn't change for different elements

          self.inpRFrame.append(np.random.normal(size=(S1[i][0], S1[i][1])))
          self.inpSFrame.append(
              np.ones((S1[i][0], S1[i][1])) * np.random.normal(size=(1,)))

          for j in range(0, S1[i][1]):

            # check to see if this element is u or pu
            key = 0
            if j in self.EMD:
              key = self.EMD[j]
            else:
              # location of generic errors
              key = 4


            self.inpEFrame[i][Z,:,j] = self.inpFrame[i][:,j] + \
                                                    self.inpFrame[i][:,j] * (self.inpSFrame[i][:,j] * ErrorMatrix[i, key + 1]) + \
                                                    self.inpFrame[i][:,j] * (self.inpRFrame[i][:,j] * ErrorMatrix[i, key])

      ############################################     Inventory     ################################################
      ############################################        MAT        ###################################################
      for Z in range(0, IT):
        QtCore.QCoreApplication.instance().processEvents(
        )  # ensures window isn't seen as unresponsive

        self.invRFrame = []
        self.invSFrame = []

        for i in range(0, len(S2)):

          self.PB.setValue(
              np.floor((i + Z * len(S2) + IT * len(S1)) /
                       ((len(S1) + len(S2) + len(S3)) * IT) * 100))
          QtCore.QCoreApplication.instance().processEvents()
          self.invRFrame.append(np.random.normal(size=(S2[i][0], S2[i][1])))
          self.invSFrame.append(
              np.ones((S2[i][0], S2[i][1])) * np.random.normal(size=(1,)))

          for j in range(0, S2[i][1]):

            key = 0
            if j in self.EMD:
              key = self.EMD[j]
            else:
              # location of generic errors
              key = 4



            self.invEFrame[i][Z,:,j] = self.invFrame[i][:,j] + \
                                                     self.invFrame[i][:,j] * (self.invSFrame[i][:,j] * ErrorMatrix[i + len(S1), key + 1]) + \
                                                     self.invFrame[i][:,j] * (self.invRFrame[i][:,j] * ErrorMatrix[i + len(S1), key])

      ############################################       Output       ################################################
      ############################################        MAT        ###################################################
      for Z in range(0, IT):
        QtCore.QCoreApplication.instance().processEvents(
        )  # ensures window isn't seen as unresponsive

        self.outRFrame = []
        self.outSFrame = []

        for i in range(0, len(S3)):  #location

          self.PB.setValue(
              np.floor((i + Z * len(S3) + IT * len(S1) + IT * len(S2)) /
                       ((len(S1) + len(S2) + len(S3)) * IT) * 100))
          QtCore.QCoreApplication.instance().processEvents()

          self.outRFrame.append(np.random.normal(size=(S3[i][0], S3[i][1])))
          self.outSFrame.append(
              np.ones((S3[i][0], S3[i][1])) * np.random.normal(size=(1,)))

          for j in range(0, S3[i][1]):  #elements

            key = 0
            if j in self.EMD:
              key = self.EMD[j]
            else:
              # location of generic errors
              key = 4

            #self.outSFrame[i][:, j] = np.random.normal(size=(S3[1],))

            self.outEFrame[i][Z, :, j] = self.outFrame[i][:, j] + \
                                         self.outFrame[i][:, j] * (self.outSFrame[i][:, j] * ErrorMatrix[i + len(S1) + len(S2), key + 1]) + \
                                         self.outFrame[i][:, j] * (self.outRFrame[i][:, j] * ErrorMatrix[i + len(S1) + len(S2), key])

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
                                         self.inpFrame[i, :, j] * (self.inpSFrame[i, :, j] * ErrorMatrix[i, key + 1]) + \
                                         self.inpFrame[i, :, j] * (self.inpRFrame[i, :, j] * ErrorMatrix[i, key])

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
                                         self.invFrame[i, :, j] * (self.invSFrame[i, :, j] * ErrorMatrix[i + S1[0], key + 1]) + \
                                         self.invFrame[i, :, j] * (self.invRFrame[i, :, j] * ErrorMatrix[i + S1[0], key])

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
                                         self.outFrame[i, :, j] * (self.outSFrame[i, :, j] * ErrorMatrix[i + S1[0] + S2[0], key + 1]) + \
                                         self.outFrame[i, :, j] * (self.outRFrame[i, :, j] * ErrorMatrix[i + S1[0] + S2[0], key])

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

    if hasattr(self, 'Wizard'):
      if self.Wizard.IsMatV == 1:
        GF = 1
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
        TotalLocs = int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + int(
            self.Wizard.OutKMP)
    else:
      TotalLocs = np.shape(self.SS.Inputs)[0] + np.shape(
          self.SS.Inventories)[0] + np.shape(self.SS.Outputs)[0]

    if GF == 0:
      S1 = np.shape(self.inpFrame)
      S2 = np.shape(self.invFrame)
      S3 = np.shape(self.outFrame)

    mbaTime = int(self.MBPBox.text())

    NumSamples = np.max(np.shape(self.inpFrame))
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
    GF = 0

    # start MUF calc here
    # sum(input) - sum(output) - delta(inventory)
    # use data from (i-1):i to set MUF for period i:i+1
    ############################################  MUF Calculation  ################################################
    # for each MUF test
    if hasattr(self, 'Wizard'):
      if self.Wizard.IsMatV == 1:
        GF = 1

        for ZZ in range(0, len(ck0)):  #for each test
          for i in range(1, int(MBPs)):  #each MBP

            for j in range(
                0, len(self.inpEFrame)
            ):  #for each location -- have to do individually because the elements is per location in the list

              IntV = np.logical_and(
                  self.inpTimeFrame[j] >= mbaTime * (i - 1),
                  self.inpTimeFrame[j] <= mbaTime * i).reshape(
                      (-1,))  #select the indices for the relevant time

              self.MUFCalcs[:, ZZ, i * mbaTime:(i + 1) * mbaTime] += \
              np.tile(AuxFunctions.trapSum(IntV,self.inpTimeFrame[j],self.inpEFrame[j],ck0[ZZ]), (mbaTime, 1)).transpose()

            for j in range(0, len(self.outEFrame)):
              IntV = np.logical_and(
                  self.outTimeFrame[j] >= mbaTime * (i - 1),
                  self.outTimeFrame[j] <= mbaTime * i).reshape((-1,))

              self.MUFCalcs[:, ZZ, i * mbaTime:(i + 1) * mbaTime] -= \
              np.tile(AuxFunctions.trapSum(IntV,self.outTimeFrame[j],self.outEFrame[j],ck0[ZZ]), (mbaTime, 1)).transpose()

            for j in range(0, len(self.invEFrame)):

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

    if GF == 0:  #basically if not mat type
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

    ErrorMatrix = np.zeros((TotalLocs, 6))

    # setup error table
    P = 0
    for i in range(0, self.EP.rowCount()):
      if self.EP.item(i, 0) is not None:
        for j in range(0, 6):
          ErrorMatrix[P, j] = float(self.EP.item(i, j).text()) / 100
        P += 1

    ck1 = self.CB_PuMUF.isChecked() + self.CB_PuSMUF.isChecked(
    ) + self.CB_PuSITMUF.isChecked() + self.CB_PuSPage.isChecked()
    ck2 = self.CB_UMUF.isChecked() + self.CB_USMUF.isChecked(
    ) + self.CB_USITMUF.isChecked() + self.CB_USPage.isChecked()
    ck3 = self.CB_GMUF.isChecked() + self.CB_GSMUF.isChecked(
    ) + self.CB_GSITMUF.isChecked() + self.CB_GSPage.isChecked()

    mbaTime = int(self.MBPBox.text())
    NumSamples = np.max(np.shape(self.inpFrame))
    IT = int(self.IterBox.text())

    GF = 0

    if hasattr(
        self,
        'Wizard'):  #some setup to later determine the length of data provided
      if self.Wizard.IsMatV == 1:
        GF = 1
        lddir = loadmat(self.Wizard.MatDir)
        S1 = []
        for JR in range(0, np.shape(lddir['in']['data'][0])[0]):
          S1.append(np.zeros(2,))
          S1[JR][0] = np.shape(lddir['in']['data'][0][JR])[0]
          S1[JR][1] = np.shape(lddir['in']['data'][0][0])[
              1]  #elements shouldn't change with location
          S1[JR] = S1[JR].astype(int)

        S2 = []
        for JR in range(0, np.shape(lddir['invn']['data'][0])[0]):
          S2.append(np.zeros(2,))
          S2[JR][0] = np.shape(lddir['invn']['data'][0][JR])[0]
          S2[JR][1] = np.shape(lddir['invn']['data'][0][0])[
              1]  #elements shouldn't change with location
          S2[JR] = S2[JR].astype(int)

        S3 = []
        for JR in range(0, np.shape(lddir['outn']['data'][0])[0]):
          S3.append(np.zeros(2,))
          S3[JR][0] = np.shape(lddir['outn']['data'][0][JR])[0]
          S3[JR][1] = np.shape(lddir['outn']['data'][0][0])[
              1]  #elements shouldn't change with location
          S3[JR] = S3[JR].astype(int)

        else:
          TotalLocs = int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + int(
              self.Wizard.OutKMP)
    else:
      TotalLocs = np.shape(self.SS.Inputs)[0] + np.shape(
          self.SS.Inventories)[0] + np.shape(self.SS.Outputs)[0]

    if GF == 0:
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

    GF = 0

    ############################################  SEID Calculation  ###############################################
    if hasattr(self, 'Wizard'):
      self.SEMUFContribI = np.zeros(
          (IT, TotalLocs, int(MBPs)))  #lazy, helps later
      #note that the integration for the mat case requires
      #the aux trap function
      if self.Wizard.IsMatV == 1:
        PBTot = len(ck0) * int(MBPs) * TotalLocs * IT
        GF = 1
        for ZZ in range(0, len(ck0)):  #each test type
          QtCore.QCoreApplication.instance().processEvents()

          if ck0[ZZ] in self.EMD:
            key = self.EMD[ck0[ZZ]]
          else:
            key = 4

          for Z in range(0, IT):  #iterations

            InpVar = np.zeros((int(MBPs * mbaTime),))

            for j in range(0, len(S1)):  #for each location
              for i in range(1, int(MBPs)):  #MBPs

                QtCore.QCoreApplication.instance().processEvents()
                self.PB.setValue(
                    ((ZZ * IT * TotalLocs * MBPs) + (Z * TotalLocs * MBPs) +
                     (j * MBPs) + i) / PBTot * 100)

                IntV = np.logical_and(
                    self.inpTimeFrame[j] >= mbaTime * (i - 1),
                    self.inpTimeFrame[j] <= mbaTime * i).reshape(
                        (-1,))  #select the indices for the relevant time

                VR =np.power(AuxFunctions.trapSum(IntV,self.inpTimeFrame[j],self.inpEFrame[j],ck0[ZZ],Z),2) *\
                    np.power(ErrorMatrix[j, key], 2) #random component

                VS = np.power(AuxFunctions.trapSum(IntV,self.inpTimeFrame[j],self.inpEFrame[j],ck0[ZZ],Z),2) *\
                     np.power(ErrorMatrix[j, key + 1], 2) #systematic component

                #variance is stored as a function of time, but contributions are
                #stored per MBP which makes it easier to put in a table later
                #especially considering the time might be variable
                InpVar[i * mbaTime:(i + 1) * mbaTime] += (VR + VS) * np.ones(
                    (mbaTime,))
                self.SEMUFContribR[Z, j, i] = VR
                self.SEMUFContribS[Z, j, i] = VS
                self.SEMUFContribI[Z, j, i] = AuxFunctions.trapSum(
                    IntV, self.inpTimeFrame[j], self.inpEFrame[j], ck0[ZZ], Z)

            InvVar = np.zeros((int(MBPs * mbaTime),))

            for j in range(0, len(S2)):
              for i in range(1, int(MBPs)):

                EMI = j + len(S1)
                StartT = np.abs(self.invTimeFrame[j].reshape((-1,)) - mbaTime *
                                (i - 1)).argmin()
                EndT = np.abs(self.invTimeFrame[j].reshape((-1,)) -
                              mbaTime * i).argmin()

                self.PB.setValue(
                    ((ZZ * IT * TotalLocs * MBPs) + (Z * TotalLocs * MBPs) +
                     ((EMI) * MBPs) + i) / PBTot * 100)

                if i == 1:
                  VR = np.power(
                  self.invEFrame[j][Z, EndT, ck0[ZZ]], 2) * \
                  np.power(ErrorMatrix[EMI, key], 2)

                  VS = np.power(
                  self.invEFrame[j][Z, EndT, ck0[ZZ]], 2) * \
                  np.power(ErrorMatrix[EMI, key + 1], 2)

                  self.SEMUFContribI[Z, j + len(S1),
                                     i] = self.invEFrame[j][Z, EndT, ck0[ZZ]]

                else:

                  VR = (np.power(self.invEFrame[j][Z, StartT, ck0[ZZ]], 2) + \
                        np.power(self.invEFrame[j][Z, EndT, ck0[ZZ]], 2)) * \
                        np.power(ErrorMatrix[EMI, key], 2)

                  VS = (np.power(self.invEFrame[j][Z, StartT, ck0[ZZ]], 2) + \
                       np.power(self.invEFrame[j][Z, EndT, ck0[ZZ]], 2)) * \
                       np.power(ErrorMatrix[EMI, key + 1], 2)

                  self.SEMUFContribI[Z, j + len(S1),
                                     i] = self.invEFrame[j][Z, EndT, ck0[ZZ]]

                InvVar[i * mbaTime:(i + 1) * mbaTime] += (VR + VS) * np.ones(
                    (mbaTime,))
                self.SEMUFContribR[Z, j + len(S1), i] = VR
                self.SEMUFContribS[Z, j + len(S1), i] = VS

            OutVar = np.zeros((int(MBPs * mbaTime),))

            for j in range(0, len(S3)):
              for i in range(1, int(MBPs)):

                IntV = np.logical_and(
                    self.outTimeFrame[j] >= mbaTime * (i - 1),
                    self.outTimeFrame[j] <= mbaTime * i).reshape((-1,))
                EMI = j + len(S1) + len(S2)

                self.PB.setValue(
                    ((ZZ * IT * TotalLocs * MBPs) + (Z * TotalLocs * MBPs) +
                     ((EMI) * MBPs) + i) / PBTot * 100)

                VR = np.power(
                     AuxFunctions.trapSum(IntV,self.outTimeFrame[j],self.outEFrame[j],ck0[ZZ],Z), 2) * \
                     np.power(ErrorMatrix[EMI, key + 1], 2)

                VS = np.power(
                     AuxFunctions.trapSum(IntV,self.outTimeFrame[j],self.outEFrame[j],ck0[ZZ],Z), 2) * \
                     np.power(ErrorMatrix[EMI, key + 1], 2)

                OutVar[i * mbaTime:(i + 1) * mbaTime] += (VR + VS) * np.ones(
                    (mbaTime,))
                self.SEMUFContribR[Z, j + len(S1) + len(S2), i] = VR
                self.SEMUFContribS[Z, j + len(S1) + len(S2), i] = VS
                self.SEMUFContribI[Z, j + len(S1) + len(S2),
                                   i] = AuxFunctions.trapSum(
                                       IntV, self.outTimeFrame[j],
                                       self.outEFrame[j], ck0[ZZ], Z)

            self.SEMUFCalcs[Z, ZZ, :] = np.sqrt(InpVar + InvVar + OutVar)

    if GF == 0:  #if not a mat
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
              self.PB.setValue(
                  ((ZZ * IT * TotalLocs * MBPs) + (Z * TotalLocs * MBPs) +
                   (j * MBPs) + i) / PBTot * 100)
              # inventory, sys and rand components
              VR = np.power(
                  np.sum(self.inpEFrame[Z, j, (i - 1) * mbaTime:i * mbaTime, ck0[ZZ]]), 2) * \
                                                        np.power(ErrorMatrix[j, key], 2)

              VS = np.power(
                    np.sum(self.inpEFrame[Z, j, (i - 1) * mbaTime:i * mbaTime, ck0[ZZ]]), 2) * \
                                                          np.power(ErrorMatrix[j, key + 1], 2)

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
                VR = np.power(
                                self.invEFrame[Z, j, i * mbaTime, ck0[ZZ]], 2) * \
                               np.power(ErrorMatrix[EMI, key], 2)

                VS = np.power(
                                self.invEFrame[Z, j, i * mbaTime, ck0[ZZ]], 2) * \
                               np.power(ErrorMatrix[EMI, key + 1], 2)

                InvVar[i * mbaTime:(i + 1) * mbaTime] += (VR + VS) * np.ones(
                    (mbaTime,))
                self.SEMUFContribR[Z, S1[0] + j, i] = VR
                self.SEMUFContribS[Z, S1[0] + j, i] = VS

              else:
                VR = (np.power(self.invEFrame[Z, j, (i - 1) * mbaTime, ck0[ZZ]], 2) + \
                            np.power(self.invEFrame[Z, j, i * mbaTime, ck0[ZZ]],2)) * \
                            np.power(ErrorMatrix[EMI, key], 2)

                VS = (np.power(self.invEFrame[Z, j, (i - 1) * mbaTime, ck0[ZZ]], 2) + \
                            np.power(self.invEFrame[Z, j, i * mbaTime, ck0[ZZ]],2)) * \
                            np.power(ErrorMatrix[EMI, key + 1], 2)

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

              VR = np.power(
                  np.sum(self.outEFrame[Z, j, (i - 1) * mbaTime:i * mbaTime, ck0[ZZ]]), 2) * \
                                                        np.power(ErrorMatrix[EMI, key], 2)

              VS = np.power(
                  np.sum(self.outEFrame[Z, j, (i - 1) * mbaTime:i * mbaTime, ck0[ZZ]]), 2) * \
                                                        np.power(ErrorMatrix[EMI, key + 1], 2)

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
    if hasattr(self, 'Wizard'):
      if self.Wizard.IsMatV == 1:
        GF = 1
        lddir = loadmat(self.Wizard.MatDir)
        S1 = []

        for JR in range(0, np.shape(lddir['in']['data'][0])[0]):
          S1.append(np.zeros(2,))
          S1[JR][0] = np.shape(lddir['in']['data'][0][JR])[0]
          S1[JR][1] = np.shape(lddir['in']['data'][0][0])[
              1]  # elements shouldn't change with location
          S1[JR] = S1[JR].astype(int)

        S2 = []
        for JR in range(0, np.shape(lddir['invn']['data'][0])[0]):
          S2.append(np.zeros(2,))
          S2[JR][0] = np.shape(lddir['invn']['data'][0][JR])[0]
          S2[JR][1] = np.shape(lddir['invn']['data'][0][0])[
              1]  # elements shouldn't change with location
          S2[JR] = S2[JR].astype(int)

        S3 = []

        for JR in range(0, np.shape(lddir['outn']['data'][0])[0]):
          S3.append(np.zeros(2,))
          S3[JR][0] = np.shape(lddir['outn']['data'][0][JR])[0]
          S3[JR][1] = np.shape(lddir['outn']['data'][0][0])[
              1]  # elements shouldn't change with location
          S3[JR] = S3[JR].astype(int)

        TotalLocs = len(S1) + len(S2) + len(S3)
      else:
        TotalLocs = int(self.Wizard.InKMP) + int(self.Wizard.InvKMP) + int(
            self.Wizard.OutKMP)
    else:
      TotalLocs = np.shape(self.SS.Inputs)[0] + np.shape(
          self.SS.Inventories)[0] + np.shape(self.SS.Outputs)[0]

    if GF == 0:
      S1 = np.shape(self.inpFrame)
      S2 = np.shape(self.invFrame)
      S3 = np.shape(self.outFrame)

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
    ErrorMatrix = np.zeros((TotalLocs, 6))

    # setup error table
    P = 0
    for i in range(0, self.EP.rowCount()):
      if self.EP.item(i, 0) is not None:
        for j in range(0, 6):
          ErrorMatrix[P, j] = float(self.EP.item(i, j).text()) / 100
        P += 1

    mbaTime = int(self.MBPBox.text())
    NumSamples = np.max(np.shape(self.inpFrame))
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
    PBTot = len(ck0) * IT * (MBPb / 2 - 0.5) * MBPb
    self.PB.setValue(0)

    if hasattr(self, 'Wizard'):
      if self.Wizard.IsMatV == 1:
        for ZZ in range(0, len(ck0)):
            if self.decompStatus == 1:
              if ck0[ZZ] in self.EMD:
                key = self.EMD[ck0[ZZ]]
              else:
                key = 4

              for Z in range(0, IT):
                QtCore.QCoreApplication.instance().processEvents(
                )  # ensures window isn't seen as unresponsive
                for P in range(
                    1, int(MBPs)
                ):  # the covmatrix grows over time so have to do this double loop
                  for j in range(0, P):

                    QtCore.QCoreApplication.instance().processEvents(
                    )  # ensures no freezing when box is dragged during exe
                    self.PB.setValue(((ZZ * IT * MBPb * (MBPb / 2 - 0.5)) +
                                      (Z * MBPb * (MBPb / 2 - 0.5)) +
                                      (P * (P / 2 - 0.5)) + j) / PBTot * 100)

                    t1 = j * mbaTime
                    t2 = t1 + mbaTime
                    t3 = P * mbaTime

                    if j == P - 1:
                      term1 = 0
                      for k in range(0, len(S1)):

                        IntV = np.logical_and(
                            self.inpTimeFrame[k] >= t1,
                            self.inpTimeFrame[k] <= t2).reshape(
                                (-1,))  #select the indices for the relevant time

                        term1 += np.power(AuxFunctions.trapSum(IntV,self.inpTimeFrame[k],self.inpEFrame[k],ck0[ZZ],Z), 2) * \
                                 (np.power(ErrorMatrix[k, key + 1], 2) +
                                  np.power(ErrorMatrix[k, key], 2))

                      term2 = 0

                      for k in range(0, len(S3)):
                        IntV = np.logical_and(self.outTimeFrame[k] >= t1,
                                              self.outTimeFrame[k] <= t2).reshape(
                                                  (-1,))
                        EMI = k + len(S1) + len(S2)

                        term2 += np.power(AuxFunctions.trapSum(IntV,self.outTimeFrame[k],self.outEFrame[k],ck0[ZZ],Z), 2) * \
                                   (np.power(ErrorMatrix[EMI, key + 1], 2) +
                                    np.power(ErrorMatrix[EMI, key], 2))

                      term3 = 0

                      for k in range(0, len(S2)):
                        EMI = k + len(S1)
                        StartT = np.abs(self.invTimeFrame[k].reshape((-1,)) -
                                        t1).argmin()
                        EndT = np.abs(self.invTimeFrame[k].reshape((-1,)) -
                                      t2).argmin()

                        term3 += np.power(self.invEFrame[k][Z,EndT,ck0[ZZ]], 2) * \
                                 (np.power(ErrorMatrix[EMI, key + 1], 2) +
                                  np.power(ErrorMatrix[EMI, key], 2))

                      if j == 0:
                        term4 = 0
                        term5 = 0
                      else:
                        term4 = 0
                        term5 = 0

                        for k in range(0, len(S2)):
                          EMI = k + len(S1)
                          StartT = np.abs(self.invTimeFrame[k].reshape((-1,)) -
                                          t1).argmin()
                          EndT = np.abs(self.invTimeFrame[k].reshape((-1,)) -
                                        t2).argmin()

                          term4 += np.power(self.invEFrame[k][Z,StartT,ck0[ZZ]], 2) * \
                                 (np.power(ErrorMatrix[EMI, key + 1], 2) +
                                  np.power(ErrorMatrix[EMI, key], 2))

                          term5 += self.invEFrame[k][Z,StartT,ck0[ZZ]] * \
                                 self.invEFrame[k][Z,EndT,ck0[ZZ]] * \
                                 np.power(ErrorMatrix[EMI, key + 1], 2)

                      covmatrix[j, j] = term1 + term2 + term3 + term4 - 2 * term5
                    else:
                      ################### Off-Diagonal Terms ####################
                      ###################    Term 1    ##########################
                      # inp_current * inv_P * sys^2
                      term1 = 0
                      A = 0
                      B = 0
                      C = 0
                      for k in range(0, len(S1)):
                        IntV = np.logical_and(
                            self.inpTimeFrame[k] >= t1,
                            self.inpTimeFrame[k] <= t2).reshape(
                                (-1,))  #select the indices for the relevant time
                        IntV2 = np.logical_and(
                            self.inpTimeFrame[k] >= t3 - mbaTime,
                            self.inpTimeFrame[k] <= t3).reshape(
                                (-1,))  #select the indices for the relevant time

                        A = AuxFunctions.trapSum(IntV, self.inpTimeFrame[k],
                                                 self.inpEFrame[k], ck0[ZZ], Z)
                        B = AuxFunctions.trapSum(IntV2, self.inpTimeFrame[k],
                                                 self.inpEFrame[k], ck0[ZZ], Z)
                        C = np.power(ErrorMatrix[k, key + 1], 2)

                        term1 += (A * B * C)

                      ###################    Term 2    ##########################
                      # out_current*out_P*sys^2
                      term2 = 0
                      A = 0
                      B = 0
                      C = 0
                      for k in range(0, len(S3)):
                        IntV = np.logical_and(
                            self.outTimeFrame[k] >= t1,
                            self.outTimeFrame[k] <= t2).reshape(
                                (-1,))  #select the indices for the relevant time
                        IntV2 = np.logical_and(
                            self.outTimeFrame[k] >= t3 - mbaTime,
                            self.outTimeFrame[k] <= t3).reshape(
                                (-1,))  #select the indices for the relevant time

                        EMI = k + len(S1) + len(S2)
                        A = AuxFunctions.trapSum(IntV, self.outTimeFrame[k],
                                                 self.outEFrame[k], ck0[ZZ], Z)
                        B = AuxFunctions.trapSum(IntV2, self.outTimeFrame[k],
                                                 self.outEFrame[k], ck0[ZZ], Z)
                        C = np.power(ErrorMatrix[k, key + 1], 2)

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

                      for k in range(0, len(S2)):
                        StartT = np.abs(self.invTimeFrame[k].reshape((-1,)) -
                                        t1).argmin()
                        EndT = np.abs(self.invTimeFrame[k].reshape((-1,)) -
                                      t2).argmin()
                        EndT2 = np.abs(self.invTimeFrame[k].reshape((-1,)) -
                                       t3).argmin()
                        EndT3 = np.abs(self.invTimeFrame[k].reshape((-1,)) -
                                       (t2 - mbaTime)).argmin()
                        EndT4 = np.abs(self.invTimeFrame[k].reshape((-1,)) -
                                       (t3 - 2 * mbaTime)).argmin()

                        EMI = k + len(S1)

                        term3a = self.invEFrame[k][
                            Z, EndT, ck0[ZZ]] * self.invEFrame[k][Z, EndT2, ck0[ZZ]]
                        term3b = self.invEFrame[k][
                            Z, EndT3, ck0[ZZ]] * self.invEFrame[k][Z, EndT4,
                                                                   ck0[ZZ]]
                        term3c = np.power(ErrorMatrix[k, key + 1], 2)

                        term3 += (term3a + term3b) * term3c

                        # the condition for term4 is if P-j == 1
                        # the condition for term5 is if j-P == 1
                        #related to the fact that there is some
                        #covariance from successive MBs due to
                        #the share inventory term

                        term4a = self.invEFrame[k][
                            Z, EndT, ck0[ZZ]] * self.invEFrame[k][Z, EndT4, ck0[ZZ]]
                        term4b = np.power(ErrorMatrix[k, key + 1], 2)
                        if P - j == 1:
                          term4c = np.power(ErrorMatrix[k, key], 2)
                        else:
                          term4c = 0

                        term4 += term4a * (term4b + term4c) * 0

                        term5a = self.invEFrame[k][
                            Z, EndT3, ck0[ZZ]] * self.invEFrame[k][Z, EndT2,
                                                                   ck0[ZZ]]
                        term5b = np.power(ErrorMatrix[k, key + 1], 2)

                        if j - P == 1:
                          term5c = np.power(ErrorMatrix[k, key], 2)
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

                  #yyy = np.linalg.cholesky(tempcovmatrix).T
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
                  #actually note that we could stop here as Picard (1985)
                  #showed that  np.linalg.inv(V) @ tempID = SITMUF
                  #including the below tricks for posteriority

                  #Update 5/2021: co-authored a paper on this
                  #for INMM, might want to come back
                  #and update this as Picard is a more
                  #elegant solution and is in some ways
                  #more realistic w.r.t NMA

                  U = np.diag(np.diag(V))
                  T = np.linalg.solve(
                      U.T,
                      V.T).T  #solves TU = V for T using the property U.T T.T = V.T
                  # (note the returned value is transposed so need to transpose again)
                  ITMUF = np.linalg.solve(T, tempID.T)
                  SITMUF = np.linalg.solve(U.T, ITMUF)

                  self.SITMUFCalcs[Z, ZZ,
                                   int((P - 1) *
                                       mbaTime):int(P * mbaTime)] = np.ones(
                                           (mbaTime,)) * SITMUF[P - 1]

                  # one sided page - remove negative values
                  #page
                  if len(ck1) > 0:
                    if ck0[ZZ] == ck1[ZZ]:
                      if P == 1:
                        RZN = SITMUF[P - 1]
                      else:
                        RZN = SITMUF[P - 2] + SITMUF[P - 1] - 0.5

                      if RZN < 0:
                        RZN = 0

                      self.PageCalcs[Z, ZZ,
                                     int((P - 1) *
                                         mbaTime):int(P * mbaTime)] = np.ones(
                                             (mbaTime,)) * RZN

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
                      self.PB.setValue(((ZZ * IT * MBPb * (MBPb / 2 - 0.5)) +
                                        (Z * MBPb * (MBPb / 2 - 0.5)) +
                                        (P * (P / 2 - 0.5)) + j) / PBTot * 100)

                      # loops r fubar
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
                          term1 += np.power(np.sum(self.inpEFrame[Z, k, t1:t2, ck0[ZZ]]), 2) * \
                                   (np.power(ErrorMatrix[k, key + 1], 2) +
                                    np.power(ErrorMatrix[k, key], 2))

                        ###################    Term 2    ##########################
                        # (current_out)^2 * (ran^2 +sys^2)
                        term2 = 0

                        for k in range(0, int(S3[0])):
                          EMI = k + int(S1[0]) + int(S2[0])

                          term2 += np.power(np.sum(self.outEFrame[Z, k, t1:t2, ck0[ZZ]]), 2) * \
                                   (np.power(ErrorMatrix[EMI, key + 1], 2) +
                                    np.power(ErrorMatrix[EMI, key], 2))

                        ###################    Term 3    ##########################
                        # (current_inv)^2 * (ran^2 + sys^2)
                        term3 = 0

                        for k in range(0, int(S2[0])):
                          EMI = k + int(S1[0])

                          term3 += np.power(self.invEFrame[Z, k, t2, ck0[ZZ]], 2) * \
                                   (np.power(ErrorMatrix[EMI, key + 1], 2) +
                                    np.power(ErrorMatrix[EMI, key], 2))

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

                            term4 += np.power(self.invEFrame[Z, k, t1, ck0[ZZ]], 2) * \
                                     (np.power(ErrorMatrix[EMI, key + 1], 2) +
                                      np.power(ErrorMatrix[EMI, key], 2))

                            term5 += self.invEFrame[Z, k, t1, ck0[ZZ]] * \
                                     self.invEFrame[Z, k, t2, ck0[ZZ]] * \
                                     np.power(ErrorMatrix[EMI, key + 1], 2)

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
                          C = np.power(ErrorMatrix[k, key + 1], 2)

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
                          C = np.power(ErrorMatrix[k, key + 1], 2)

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
                          term3c = np.power(ErrorMatrix[k, key + 1], 2)

                          term3 += (term3a + term3b) * term3c

                          # the condition for term4 is if P-j == 1
                          # the condition for term5 is if j-P == 1

                          term4a = self.invEFrame[Z, k, t2, ck0[ZZ]] * self.invEFrame[
                              Z, k, t3 - (2 * mbaTime), ck0[ZZ]]
                          term4b = np.power(ErrorMatrix[k, key + 1], 2)
                          if P - j == 1:
                            term4c = np.power(ErrorMatrix[k, key], 2)
                          else:
                            term4c = 0

                          term4 += term4a * (term4b + term4c) * 0

                          term5a = self.invEFrame[Z, k, t2 - mbaTime,
                                                  ck0[ZZ]] * self.invEFrame[Z, k, t3,
                                                                            ck0[ZZ]]
                          term5b = np.power(ErrorMatrix[k, key + 1], 2)

                          if j - P == 1:
                            term5c = np.power(ErrorMatrix[k, key], 2)
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

                        self.PageCalcs[Z, ZZ,
                                       int((P - 1) * mbaTime):int(P *
                                                                  mbaTime)] = np.ones(
                                                                      (mbaTime,)) * RZN

    self.StatDlg.UpdateDispText('SITMUF Finished')
    QtCore.QCoreApplication.instance().processEvents()


class AuxFunctions:

  def trapSum(
      relevantIndex,
      time,
      data,
      ele,
      IT=None
  ):
    #TODO - update for new scheme, probably just a little bit of code to filter zeros
    #function uses trapz to integrate
    #non uniform sampled quantities
    #by breaking them into segments
    #designed to integrate SSPM signals

    #note strange things can happen with non-square
    #pulses

    #note, there are several repeating statements
    #that are if IT is not None, this is basically done
    #due to how different stats tests call the integral
    #function, some process all iterations once, others
    #dont, so if there's an iteration specified the data
    #matrix has one less axis so that needs to be
    #accounted for

    #find the relevant segment of time

    if len(relevantIndex) == 0:
      if IT is not None:
        trapTot = 0
      else:
        trapTot = np.zeros((np.shape(data)[0]))
    else:

      relTime = time.reshape((-1,)) * relevantIndex  # relevantTimes

      timeSegs = []
      dataSegs = []

      #generally speaking, inputs and outputs from simulink
      #are discontunities. It's assumed that they are sampled
      #with inhereted time and largely only when the signal is
      #positive, else the signals would be large for memory.

      #this diffS represents the right side of pulses
      #so recorded time might be like;
      #[0, 0.001, 0.003, 0.005, 10, 10.001]
      #obviously time 10 is a new pulse
      #note it is the RIGHT side of the pulse
      #this will be important later

      diffS = np.ediff1d(relTime)
      relTimeIndex = np.squeeze(np.argwhere(diffS > 1) + 1)

      #TODO - need some logic for when size of relTimeIndex is 0
      #also potential bug with IT not being passed on MUF line 1055?

      #in the event there's only one pulse of input material
      #during the first MBP
      if np.size(relTimeIndex) == 0:
        relTimeIndex = np.argmin(diffS)

      indSeg = np.zeros(2,)

      #in some edge cases relTimeIndex can be a scalar
      relTimeIndex = np.asarray(relTimeIndex).reshape((-1, 1))

      #The A and B function help for when the pulse is the first.
      #suppose we have an interval of recorded like so;
      #time [0,0.3,0.6,0.9,1.2,5.3,5.6,5.9 ...]
      #that represents the first pulse, but the diffS
      #will only record a spike between 1.2 and 5.3,
      #but we need to acount for the left side of the pulse
      #on the other hand, when the pulse starts at a non-zero
      #value there is one less segment

      #indSeg is just the last index of the relevant pulse basically,
      #and it does that by looking at the values about 5e-5 in
      #the relevant interal. The reason for 5e-5 rather than 0
      #is because sometimes small values (<5e-5) will be
      #recorded and can't be well approximated by a trapezoid.

      #note that there are SOME zero values recorded after the output
      #and inputs using the recommended sample block in Simulink.
      #this is a rather detailed technical reason, but a pulse is essentially
      # a discontunity. At the right edge of the pulse Simulink records a value
      #of zero, but on the left edge it records the pulse height. The issue is that
      #the last slice of the pulse in the Riemann sum isn't really a trapezoid, but
      #a rectangle. So we to trap integration for all slices except the right
      #most slice, which we approximate as a rectangle instead. Approximating
      #as a trapezoid actually gives the wrong answer. There's some more
      #details on this on the gitlab issue page.

      #IT = None means process as entire set,
      #It is Not None means process individual runs

      if relTimeIndex[
          0,
          0] != 0:  #if material is actually present in the requested interval
        maxIndex = np.argmax(np.where(relevantIndex == True))
        # is there an extra pulse?
        OP = 0
        if maxIndex < np.max(
            np.argwhere(data[0, :int(maxIndex), ele] > 5e-5)) + 1:
          OP = 1

        if IT is not None:
          IDXC = IT
        else:
          IDXC = 0

        if int(np.min(
            np.argwhere(data[IDXC, :, ele] *
                        relevantIndex > 5e-5))) == 0:  #is this the first MBP?
          isFirstMBP = 1
          loopCalcs = len(relTimeIndex)
        else:
          isFirstMBP = 0
          loopCalcs = len(relTimeIndex) - 1

        #the loop count changes if it's the first MBP
        #imagine MBP1: [30, 60, 90]
        #and MBP2: [120, 150, 180] (relevant times for pulses of material)
        # indSeg[0] is first at [0] for MBP1
        #but at 120 for MBP2 so there's a different number of intervals
        #to loop over (0,30 ... 30,60 ... 60,90)
        #versus (120,150 ... 150,180)

        for i in range(0, loopCalcs):

          if i == 0:  # if first interval
            # left side
            indSeg[0] = int(
                np.min(np.argwhere(data[IDXC, :, ele] * relevantIndex > 5e-5)))
          else:
            if isFirstMBP == 1:
              indSeg[0] = int(
                  np.min(
                      np.where(data[IDXC,
                                    int(indSeg[1]):int(relTimeIndex[i]),
                                    ele])) + indSeg[1])
            else:
              indSeg[0] = int(
                  np.min(
                      np.where(data[IDXC,
                                    int(indSeg[1]):int(relTimeIndex[i + 1]),
                                    ele])) + indSeg[1])

          # right side
          if isFirstMBP == 1:
            indSeg[1] = int(
                np.max(
                    np.where(data[IDXC,
                                  int(indSeg[0]):int(relTimeIndex[i]), ele])) +
                indSeg[0] + 1)
          else:
            indSeg[1] = int(
                np.max(
                    np.where(data[IDXC,
                                  int(indSeg[0]):int(relTimeIndex[i + 1]),
                                  ele])) + indSeg[0] + 1)

          timeSegs.append(time[int(indSeg[0]):int(indSeg[1] +
                                                  1)])  # length of time

          if IT is not None:
            dataSegs.append(data[IT, int(indSeg[0]):int(indSeg[1] + 1),
                                 ele])  #iterations, length of data
          else:
            dataSegs.append(
                data[:, int(indSeg[0]):int(indSeg[1] + 1), ele]
            )  #iterations, length of data, +1 is because need the final piece of the pulse (at 0) to integrate

        # final pulse
        indSeg[0] = int(
            np.min(np.argwhere(data[0, int(indSeg[1]):, ele] > 5e-5)) +
            indSeg[1])
        if indSeg[0] < maxIndex:
          indSeg[1] = int(
              np.max(np.where(data[IDXC,
                                   int(indSeg[0]):int(maxIndex), ele])) +
              indSeg[0] + 1)

          timeSegs.append(time[int(indSeg[0]):int(indSeg[1] +
                                                  1)])  # length of time
          if IT is not None:
            dataSegs.append(data[IT, int(indSeg[0]):int(indSeg[1] + 1),
                                 ele])  # iterations, length of data
          else:
            dataSegs.append(
                data[:, int(indSeg[0]):int(indSeg[1] + 1), ele]
            )  # iterations, length of data, +1 is because need the final piece of the pulse (at 0) to integrate

        if IT is not None:
          trapTot = np.zeros((len(dataSegs,)))

        else:
          trapTot = np.zeros((len(dataSegs), int(np.shape(dataSegs[0])[0])))

        #technically don't need to have separate rows for the trapTots, but
        #it helps for debugging purposes

        if IT is not None:
          for i in range(0, len(dataSegs)):

            trapTot[i] = trapz(dataSegs[i][:-1], timeSegs[i][:-1].T) + (timeSegs[i][-1] - timeSegs[i][-2]) * \
                         dataSegs[i][-2]

        else:
          for i in range(0, len(dataSegs)):
            trapTot[i] = trapz(dataSegs[i][:, :-1], timeSegs[i][:-1].T,axis=1) + (timeSegs[i][-1] - timeSegs[i][-2]) * \
                         dataSegs[i][:, -2]

        trapTot = np.sum(trapTot, axis=0)

      else:
        if IT is not None:
          trapTot = 0
        else:
          trapTot = np.zeros((np.shape(data)[0]))

    return trapTot
