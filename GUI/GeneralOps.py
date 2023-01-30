from PySide2 import QtCore,QtWidgets, QtGui
import os
import numpy as np
from pathlib import Path
import sys
import csv
from scipy.io import savemat
import pickle
import glob

def updatePB(GUIObject,loopcounter, totalloops):

        QtCore.QCoreApplication.instance().processEvents()
        GUIObject.PB.setValue(loopcounter / totalloops*100)
        loopcounter +=1

        return GUIObject, loopcounter


def SaveStats(self, AnalysisData, GUIparams):
    """
            This function exports
            results generated by MAPIT
            to (potentially multiple)
            .csv files.
    """

    #create a directory for output if doesnt exist
    outdir = os.path.join(Path(sys.argv[0]).resolve().parents[1], 'MAPIT_Output')
    if not os.path.isdir(outdir):
      os.makedirs(outdir)

    self.PB.setMaximum(0)
    self.PB.setMinimum(0)
    self.StatDlg.UpdateDispText('Saving Data')
    QtCore.QCoreApplication.instance().processEvents()


    #TODO: add output format options for tests as
    # currently only different formats for
    # process data is supported

    QtCore.QCoreApplication.instance().processEvents(
    )  #makes sure the GUI doesnt look frozen

    if hasattr(AnalysisData,'MUF'):
      np.savetxt(
        os.path.join(outdir,GUIparams.TestType+'_MUF.csv'),
        AnalysisData.MUF.T,
        delimiter=',')

    if hasattr(AnalysisData,'CUMUF'):
      np.savetxt(
        os.path.join(outdir,GUIparams.TestType+'_CUMUF.csv'),
        AnalysisData.CUMUF.T,
        delimiter=',')


    if hasattr(AnalysisData,'SEMUF'):
      np.savetxt(
        os.path.join(outdir,GUIparams.TestType+'_SEID.csv'),
        AnalysisData.SEMUF.T,
        delimiter=',')


    if hasattr(AnalysisData,'SITMUF'):
      np.savetxt(
        os.path.join(outdir,GUIparams.TestType+'_SITMUF.csv'),
        AnalysisData.SITMUF.T,
        delimiter=',')

    if hasattr(AnalysisData,'Page'):
      np.savetxt(
        os.path.join(outdir,GUIparams.TestType+'_SITMUF_Page.csv'),
        AnalysisData.Page.T,
        delimiter=',')
    # print observed data
    #future TODO
    #will require some extra thought for
    #how to handle non-uniformly sampled data
    #save to .xlsx? separate .csv for time?

    CheckPrint = QtWidgets.QMessageBox(self)
    CheckPrint.setText('Save observed data?')
    CheckPrint.setInformativeText(
        'Observed data is the user supplied ground truth with applied specified errors'
    )
    CheckPrint.setStandardButtons(QtWidgets.QMessageBox.Yes
                                  | QtWidgets.QMessageBox.No)

    #this reorders the buttons from the default no,yes to yes,no
    hlay = CheckPrint.findChild(QtWidgets.QHBoxLayout)
    litem = hlay.takeAt(1)
    w = litem.widget()
    hlay.addWidget(w)
    CPE = CheckPrint.exec_()



    ck1 = self.CB_MUF.isChecked() + self.CB_SMUF.isChecked(
    ) + self.CB_SITMUF.isChecked() + self.CB_PAGE.isChecked() +\
    self.CB_CUMUF.isChecked()



    # [iter, location, timestep, element]
    #if labels exist use them to help
    #write the name of the output files
    if QtWidgets.QMessageBox.Yes == CPE:

      getOutType = QtWidgets.QMessageBox()
      getOutType.setText('Select output format.')
      getOutType.setInformativeText(
        'Order by iteration: Group data into run iteration, better for manual human analysis \n \n' \
        'Order by location: Group data by location, better for importing into secondary analytical pipelines')
    
      # getOutType.setStandardButtons(QtWidgets.QMessageBox.Ok
      #                             | QtWidgets.QMessageBox.No
      #                             | QtWidgets.QMessageBox.YesAll
      #                             | QtWidgets.QMessageBox.NoAll
      #                             | QtWidgets.QMessageBox.Cancel)

      buttonCSVL = getOutType.addButton('.csv: by location',QtWidgets.QMessageBox.ResetRole) #this is arbitrary, but if accept and reject roles aren't present then the red X to close the dialog wont work
      buttonCSVI = getOutType.addButton('.csv: by iteration',QtWidgets.QMessageBox.ApplyRole)
      buttonNPZ = getOutType.addButton('.npz archive',QtWidgets.QMessageBox.RejectRole)
      buttonMAT = getOutType.addButton('.mat archive', QtWidgets.QMessageBox.NoRole)
      buttonPKL = getOutType.addButton('.pkl archive', QtWidgets.QMessageBox.NoRole)


      CT = getOutType.exec_()
      
      IT = AnalysisData.inputAppliedError[0].shape[0]
      if getOutType.clickedButton() == buttonCSVL:
        
        headers = np.empty((IT+1,),dtype='U13')
        headers[0] = 'Time'
        for J in range(IT):
          headers[J+1] = 'Iteration ' + str(J)

        

        #by run or by location
        #by location here
        for J in range(len(AnalysisData.inputAppliedError)):
          holder = headers.reshape((-1,1))
          holder = np.concatenate((holder,
            np.concatenate((AnalysisData.rawInputTimes[J].reshape((1,-1)),np.squeeze(AnalysisData.inputAppliedError[J])),axis=0,dtype='U13')),axis=1)

          np.savetxt(
            os.path.join(outdir,GUIparams.TestType+'_Input'+str(J)+'.csv'),
            holder.T,
            delimiter=',',
            fmt="%s")

          QtCore.QCoreApplication.instance().processEvents()

        for J in range(len(AnalysisData.inventoryAppliedError)):
          holder = headers.reshape((-1,1))
          holder = np.concatenate((holder,
            np.concatenate((AnalysisData.rawInventoryTimes[J].reshape((1,-1)),np.squeeze(AnalysisData.inventoryAppliedError[J])),axis=0,dtype='U13')),axis=1)

          np.savetxt(
            os.path.join(outdir,GUIparams.TestType+'_Inventory'+str(J)+'.csv'),
            holder.T,
            delimiter=',',
            fmt="%s")

          QtCore.QCoreApplication.instance().processEvents()

        for J in range(len(AnalysisData.outputAppliedError)):
          holder = headers.reshape((-1,1))
          holder = np.concatenate((holder,
            np.concatenate((AnalysisData.rawOutputTimes[J].reshape((1,-1)),np.squeeze(AnalysisData.outputAppliedError[J])),axis=0,dtype='U13')),axis=1)

          np.savetxt(
            os.path.join(outdir,GUIparams.TestType+'_Output'+str(J)+'.csv'),
            holder.T,
            delimiter=',',
            fmt="%s")

          QtCore.QCoreApplication.instance().processEvents()

      elif getOutType.clickedButton() == buttonCSVI:
        

        for J in range(IT): #IT

          h = []
          spacer = ['']

          for K in range(len(AnalysisData.inputAppliedError)):
            
            h.append(AnalysisData.rawInputTimes[K].tolist()) 
            h[-1].insert(0,'input'+str(K))
            h.append(np.squeeze(AnalysisData.inputAppliedError[K][J,]).tolist())
            h[-1].insert(0,'time')
            h.append(spacer)
            
          
          for K in range(len(AnalysisData.inventoryAppliedError)):

            h.append(AnalysisData.rawInventoryTimes[K].tolist()) 
            h[-1].insert(0,'inventory'+str(K))
            h.append(np.squeeze(AnalysisData.inventoryAppliedError[K][J,]).tolist())
            h[-1].insert(0,'time')
            h.append(spacer)
            
          
          for K in range(len(AnalysisData.outputAppliedError)):

            h.append(AnalysisData.rawOutputTimes[K].tolist()) 
            h[-1].insert(0,'output'+str(K))
            h.append(np.squeeze(AnalysisData.outputAppliedError[K][J,]).tolist())
            h[-1].insert(0,'time')
            h.append(spacer)
            


          # export_data = zip_longest(*h, fillvalue = None)
          # with open(os.path.join(outdir,GUIparams.TestType+'_Iteration'+str(J)+'.csv'), 'w', ) as myfile:
          #   wr = csv.writer(myfile)
          #   wr.writerows(export_data)

          with open(os.path.join(outdir,GUIparams.TestType+'_Iteration'+str(J)+'.csv'), 'w', ) as myfile:
            wr = csv.writer(myfile)
            for word in h:
              wr.writerow(word)

      elif getOutType.clickedButton() == buttonNPZ:
        
        
        #because of the headaches of ragged arrays it's easiest to store
        #at each location rather than per iteration (which is ideal), so
        #maybe this can be improved in the future


        
        for K in range(len(AnalysisData.inputAppliedError)):
            t = AnalysisData.rawInputTimes[K].reshape((1,-1))
            x = np.squeeze(AnalysisData.inputAppliedError[K])
            np.savez(os.path.join(outdir,GUIparams.TestType+'input'+str(K)+'.npz'),
            time = t,
            values = x)

        for K in range(len(AnalysisData.inventoryAppliedError)):
            t = AnalysisData.rawInventoryTimes[K].reshape((1,-1))
            x = np.squeeze(AnalysisData.inventoryAppliedError[K])
            np.savez(os.path.join(outdir,GUIparams.TestType+'inventory'+str(K)+'.npz'),
            time = t,
            values = x)

        for K in range(len(AnalysisData.outputAppliedError)):
            t = AnalysisData.rawOutputTimes[K].reshape((1,-1))
            x = np.squeeze(AnalysisData.outputAppliedError[K])
            np.savez(os.path.join(outdir,GUIparams.TestType+'output'+str(K)+'.npz'),
            time = t,
            values = x)




      elif getOutType.clickedButton() == buttonMAT:

        

        for K in range(len(AnalysisData.inputAppliedError)):
            t = AnalysisData.rawInputTimes[K].reshape((1,-1))
            x = np.squeeze(AnalysisData.inputAppliedError[K])
            mdict = {"time": t, "values": x}
            savemat(os.path.join(outdir,GUIparams.TestType+'input'+str(K)+'.mat'),mdict)

        for K in range(len(AnalysisData.inventoryAppliedError)):
            t = AnalysisData.rawInventoryTimes[K].reshape((1,-1))
            x = np.squeeze(AnalysisData.inventoryAppliedError[K])
            mdict = {"time": t, "values": x}
            savemat(os.path.join(outdir,GUIparams.TestType+'inventory'+str(K)+'.mat'),mdict)

        for K in range(len(AnalysisData.outputAppliedError)):
            t = AnalysisData.rawOutputTimes[K].reshape((1,-1))
            x = np.squeeze(AnalysisData.outputAppliedError[K])
            mdict = {"time": t, "values": x}
            savemat(os.path.join(outdir,GUIparams.TestType+'output'+str(K)+'.mat'),mdict)

      elif getOutType.clickedButton() == buttonPKL:

        for J in range(IT): #IT

          x = []
          t = []


          for K in range(len(AnalysisData.inputAppliedError)):
            
            t.append(AnalysisData.rawInputTimes[K].tolist()) 
            x.append(np.squeeze(AnalysisData.inputAppliedError[K][J,]).tolist())


            
          
          for K in range(len(AnalysisData.inventoryAppliedError)):

            t.append(AnalysisData.rawInventoryTimes[K].tolist()) 
            x.append(np.squeeze(AnalysisData.inventoryAppliedError[K][J,]).tolist())


            
          
          for K in range(len(AnalysisData.outputAppliedError)):

            t.append(AnalysisData.rawOutputTimes[K].tolist()) 
            x.append(np.squeeze(AnalysisData.outputAppliedError[K][J,]).tolist())

          with open(os.path.join(outdir,GUIparams.TestType+'_Iteration'+str(J)+'.pkl'), 'wb') as f:
            pickle.dump([x,t],f)

      else:
        None










    self.PB.setMaximum(100)
    self.PB.setValue(100)
    self.StatDlg.UpdateDispText('Execution Finished')
    
def checkImportAxes(d):
  if d.shape[0] < d.shape[1]:
    np.swapaxes(d,0,1)
  
  return d

def processWizardData(WizardObj):
  fileext = WizardObj.dataType

  #list(locs,)

  infiles = glob.glob(WizardObj.InDir+'/*'+fileext)
  invfiles = glob.glob(WizardObj.InvDir+'/*'+fileext)
  outfiles = glob.glob(WizardObj.OutDir+'/*'+fileext)

  indat = []
  invdat = []
  outdat = []

  inTdat = []
  invTdat = []
  outTdat = []

  if fileext == '.csv':
    for i in range(len(infiles)):
      z = checkImportAxes(np.loadtxt(infiles[i],delimiter=','))
      inTdat.append(z[:,0])
      indat.append(z[:,1])
      QtCore.QCoreApplication.instance().processEvents()

    for i in range(len(invfiles)):
      z = checkImportAxes(np.loadtxt(invfiles[i],delimiter=','))
      invTdat.append(z[:,0])
      invdat.append(z[:,1])
      QtCore.QCoreApplication.instance().processEvents()

    for i in range(len(outfiles)):
      z = checkImportAxes(np.loadtxt(outfiles[i],delimiter=','))
      outTdat.append(z[:,0])
      outdat.append(z[:,1])
      QtCore.QCoreApplication.instance().processEvents()




    # AnalysisData.rawInventory = SS.Inventories
    # AnalysisData.rawInput = SS.Inputs
    # AnalysisData.rawOutput = SS.Outputs

    # AnalysisData.rawInventoryTimes = SS.InventoriesT
    # AnalysisData.rawInputTimes = SS.InputsT
    # AnalysisData.rawOutputTimes = SS.OutputsT

    # GUIparams.sceneName = SS.sceneName
    # GUIparams.nInputLocations = np.shape(AnalysisData.rawInput)[0]
    # GUIparams.nInventoryLocations =  np.shape(AnalysisData.rawInventory)[0]
    # GUIparams.nOutputLocations = np.shape(AnalysisData.rawOutput)[0]
    # GUIparams.nTotalLocations = np.shape(AnalysisData.rawInput)[0] + np.shape(AnalysisData.rawInventory)[0] + np.shape(AnalysisData.rawOutput)[0]
    # GUIparams.rowNames = A['arr2']

  return indat, inTdat, invdat, invTdat, outdat, outTdat

def processWizardGUI(AnalysisData,WizardObj):
  ninputloc = len(AnalysisData.rawInput)
  ninvloc = len(AnalysisData.rawInventory)
  noutloc = len(AnalysisData.rawOutput)
  ntotalloc = ninputloc + ninvloc + noutloc

  innames = []
  invnames = []
  outnames = []
  if len(WizardObj.InKMP_names) != ninputloc:
    for i in range(ninputloc):
      innames.append('input'+str(i))
  else:
    innames = WizardObj.InKMP_names
  
  if len(WizardObj.InvKMP_names) != ninvloc:
    for i in range(ninvloc):
      invnames.append('inventory'+str(i))
  else:
    invnames = WizardObj.InvKMP_names
  
  if len(WizardObj.OutKMP_names) != noutloc:
    for i in range(noutloc):
      outnames.append('output'+str(i))
  else:
    outnames = WizardObj.OutKMP_names

  spacer = ['']
  rownames = innames + spacer + invnames + spacer + outnames


  return ninputloc, ninvloc, noutloc, ntotalloc, rownames