import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
from PySide2 import QtCore, QtWidgets, QtGui
from matplotlib.figure import Figure
from PIL import ImageFont   ## MH added to test label sizing
import time

class PropertyHolder:
  pass

class MPLCanvas(FigureCanvas):
  """
        Class with functions to control
        the plot in MAPIT
  """

  def __init__(self, parent=None, dpi=100):

    self.fig = Figure(dpi=dpi, frameon=True)
    self.fig.subplots_adjust(left=0.10, bottom=0.10, right=0.98, top=0.95)
    self.axes = self.fig.add_subplot(111)
    self.axes_defColor = self.axes.get_facecolor()
    self.axes.tick_params(axis='both', which='major', labelsize=15)
    self.axes.tick_params(axis='both', which='minor', labelsize=10)

    self.compute_initial_figure()

    FigureCanvas.__init__(self, self.fig)
    self.setParent(parent)

    FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                               QtWidgets.QSizePolicy.Expanding)
    self.Thresh = []

  def compute_initial_figure(self):
    pass

  def update_figure(self, data, isVariableFlag=0):
    #change the default color cycle
    #dark and light colors provided

    if self.window().MakeLight.isChecked() == 0:
      matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=[
          self.window().colorsD.lb,
          self.window().colorsD.t,
          self.window().colorsD.a,
          self.window().colorsD.p,
          self.window().colorsD.y,
          self.window().colorsD.r,
          self.window().colorsD.g,
          self.window().colorsD.la,
          self.window().colorsD.o
      ])
    else:
      matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=[
          self.window().colors.lb,
          self.window().colors.t,
          self.window().colors.a,
          self.window().colors.p,
          self.window().colors.y,
          self.window().colors.r,
          self.window().colors.g,
          self.window().colors.la,
          self.window().colors.o
      ])

    self.axes.cla()

    if isVariableFlag == 1:
      self.axes.plot(data[:, 0], data[:, 1])
    elif isVariableFlag == 2:
      if data[0].shape != data[1].shape:
        for J in range(data[1].shape[0]):
          self.axes.plot(data[0],data[1][J,])
      else:
        self.axes.plot(data[0], data[1])
    else:

      self.axes.plot(data)

    self.draw()

  def update_figure_title(self, data):
    self.axes.set_title(data.title, fontsize = 20)
#    font = ImageFont.truetype(size = 20)
    self.axes.title.set_color(self.axes.yaxis.label.get_color())
    self.axes.set_xlabel(data.xlabel, fontsize = 20)
    self.axes.set_ylabel(data.ylabel, fontsize = 20)
    self.fig.tight_layout()
    self.draw()

  def update_thresh(self, data,
                    data2):  #draw the threshold from the threshold calculator
    if hasattr(self.Thresh, '__len__'):
      TH = np.ones((int(self.axes.get_lines()[0]._x.max()),)) * data
      self.Thresh, = self.axes.plot(TH, 'k')
      self.draw()
    else:
      TH = np.ones((int(self.axes.get_lines()[0]._x.max()),)) * data
      self.Thresh.remove()
      self.Thresh, = self.axes.plot(TH, 'k')
      self.draw()

    TotOver = 0
    if len(np.shape(data2)) == 2:
      TotOver = np.sum(np.max(data2, axis=1) > data) / np.shape(data2)[0] * 100
    else:
      TotOver = (np.max(data2) > data) / np.shape(data2)[0] * 100

    # prob a better way/method to do this
    # future TODO: fix this abomination of a code line
    self.parent().parent().parent().StatThreshDisp.setText(
        str(round(TotOver, 2)))
def UpdatePlotOpts(GUIObj):
    """
            Function to add GT and observed
            data options after error propogation
            has run. Also accounts for if
            this function is called after
            an initial calculation has been
            run.
    """



    # some logic in here to reset boxes as well
    if GUIObj.metricBox.count() > 0:
      for i in range(0, GUIObj.metricBox.count()):
        GUIObj.metricBox.removeItem(0)
      GUIObj.metricBox.addItem('Ground Truth Data')
      GUIObj.metricBox.addItem('Observed Data')
    else:
      GUIObj.metricBox.addItem('Ground Truth Data')
      GUIObj.metricBox.addItem('Observed Data')

    if GUIObj.NumToPlot.count() < 0:
      for i in range(0, GUIObj.NumToPlot.count()):
        GUIObj.NumToPlot.removeItem(i)



def getNumToPlot(GUIObj):
  NumToPlot = 0
  if GUIObj.NumToPlot.currentText() == '1 Random Iteration':
    NumToPlot = 1
  elif GUIObj.NumToPlot.currentText() == 'Average of All Iterations':
    NumToPlot = -1
  elif GUIObj.NumToPlot.currentText(
  ) == 'All Iterations (' + GUIObj.IterBox.text() + ')':
    NumToPlot = -2
  elif GUIObj.NumToPlot.currentText() == '15 Random Iterations':
    NumToPlot = 15
  else:
    None

  return NumToPlot


def getDataWithoutLocations(inp,nPlot):
  dat = None
  IT = inp.shape[0]
  tMax = inp.shape[1]
  times = np.linspace(0,tMax-1,tMax)
  xx = np.linspace(0,IT-1,IT)

  if nPlot == 1:
    np.random.shuffle(xx)
    xidx = int(xx[0])
    dat = inp[xidx,]
  elif nPlot == -1:
    dat = np.mean(inp,axis=0)
  elif nPlot == -2:
    dat = inp
  elif nPlot == 15:
    np.shuffle(xx)
    xidx = int(xx[:15])
    dat = inp[xidx,]

  return dat, times

def getDataWithLocations(PlotIndex,GUIparams,AnalysisData,nPlot,raw):

  dat = None
  datT = None
  IT = AnalysisData.inputAppliedError[0].shape[0]
  xx = np.linspace(0,IT-1,IT)


  if PlotIndex < GUIparams.nInputLocations:
    
    if raw == True:
      dat = AnalysisData.rawInput[PlotIndex]
      datT = AnalysisData.rawInputTimes[PlotIndex]
    else:
      dat = AnalysisData.inputAppliedError[PlotIndex]
      datT = AnalysisData.rawInputTimes[PlotIndex]
    
  elif PlotIndex >= GUIparams.nInputLocations and PlotIndex < GUIparams.nInventoryLocations+GUIparams.nInputLocations:
    PlotIndex -= GUIparams.nInputLocations

    if raw == True:
      dat = AnalysisData.rawInventory[PlotIndex]
      datT = AnalysisData.rawInventoryTimes[PlotIndex]
    else:
      dat = AnalysisData.inventoryAppliedError[PlotIndex]
      datT = AnalysisData.rawInventoryTimes[PlotIndex]

  else:
    PlotIndex -= (GUIparams.nInputLocations + GUIparams.nInventoryLocations)
    if raw == True:
      dat = AnalysisData.rawOutput[PlotIndex]
      datT = AnalysisData.rawOutputTimes[PlotIndex]
    else:
      dat = AnalysisData.outputAppliedError[PlotIndex]
      datT = AnalysisData.rawOutputTimes[PlotIndex]

  if nPlot == 1:
    np.random.shuffle(xx)
    xidx = int(xx[0])
    dat = dat[xidx,]
  elif nPlot == -1:
    dat = np.mean(dat,axis=0)
  elif nPlot == -2:
    None
  elif nPlot == 15:
    np.shuffle(xx)
    xidx = int(xx[:15])
    dat = dat[xidx,]
  
  return dat, datT
  

def getData(GUIObject,GUIparams,AnalysisData):
    NumToPlot = getNumToPlot(GUIObject)
    CanvasElements = PropertyHolder()

    # --------------- common plot variables ---------------------

    if GUIObject.NucIDBox.currentText() in GUIparams.EleVecLabel:
       NucIndex = GUIparams.EleVecLabel.index(GUIObject.NucIDBox.currentText()) #this maps the name to an array index
    else:
      NucIndex = None
   
    PlotIndex = int(GUIObject.LocBox.currentIndex()) #this gets the location index
   
    CanvasElements.xlabel = 'Time (hr)'
    CanvasElements.ylabel = 'Mass (kg)'

    numToPlot = getNumToPlot(GUIObject)

    if GUIObject.metricBox.currentText() == 'Ground Truth Data' or GUIObject.metricBox.currentText() == 'Observed Data':
      CanvasElements.title = GUIObject.NucIDBox.currentText() + ' ' +\
                            GUIObject.metricBox.currentText() + ' at ' +\
                            GUIObject.LocBox.currentText()
    else:
      CanvasElements.title = GUIObject.NucIDBox.currentText() + ' ' +\
                          GUIObject.metricBox.currentText()

    if GUIObject.metricBox.currentText() == 'Ground Truth Data':
      dat, datT = getDataWithLocations(PlotIndex,GUIparams,AnalysisData,numToPlot,raw=True)
      if 'output' in GUIObject.LocBox.currentText() or 'input' in GUIObject.LocBox.currentText():
        dat, datT, _, _ = resolveSparsePulses(dat,datT)
    elif GUIObject.metricBox.currentText() == 'Observed Data':
      dat, datT = getDataWithLocations(PlotIndex,GUIparams,AnalysisData,numToPlot,raw=False)
      #print(np.shape(dat))
      #print(np.shape(datT))

      if 'output' in GUIObject.LocBox.currentText() or 'input' in GUIObject.LocBox.currentText():
       xnew = []
       tnew = []
       if len(dat.shape) == 2:
        dat = np.expand_dims(dat,0)
       for Q in range(dat.shape[0]):
         if Q == 0:
           #print(np.shape(dat[Q]))
           #print(np.squeeze(datT))
           a, b, LI, RI = resolveSparsePulses(np.squeeze(dat[Q]),np.squeeze(datT))
           xnew.append(a)
           tnew.append(b)
         else:
           a, _, _, _ = resolveSparsePulses(np.squeeze(dat[Q]),np.squeeze(datT), LI, RI)
           xnew.append(a)
      

       dat = np.squeeze(np.asarray(xnew))
       datT = np.squeeze(np.asarray(tnew))

       #dat, datT = resolveSparsePulses(dat,datT)
      else:
       dat = np.squeeze(dat)

    else:
      currentText = GUIObject.metricBox.currentText()
      if currentText.endswith(GUIparams.labels["Box18L"]):
        inp = AnalysisData.Page
        CanvasElements.ylabel = 'Unitless'
      elif currentText.endswith(GUIparams.labels["Box15L"]):
        inp = AnalysisData.SEMUF
      elif currentText.endswith(GUIparams.labels["Box17L"]):
        inp = AnalysisData.SITMUF
        CanvasElements.ylabel = 'Unitless'
      elif currentText.endswith(GUIparams.labels["Box14L"]):
        inp = AnalysisData.CUMUF
      elif currentText.endswith(GUIparams.labels["Box12L"]):
        inp = AnalysisData.MUF
      elif currentText.endswith(GUIparams.labels["Box16L"]):
        inp = AnalysisData.SEMUFAI
        CanvasElements.ylabel = '% Active Inventory'
      elif currentText.endswith(GUIparams.labels["Box13L"]):
        inp = AnalysisData.AI

      dat, datT = getDataWithoutLocations(inp,numToPlot)
    dh = []
    dh.append(datT)
    dh.append(dat)  
    dat = None
    datT = None
    debug = 0
    return dh, CanvasElements

def ExecPlot(GUIObject,GUIparams,AnalysisData):
    """
            This function is responsible for plotting
            data selected by a user
    """  
    dh, CanvasElements = getData(GUIObject,GUIparams,AnalysisData)
    GUIObject.canvas.update_figure(dh,isVariableFlag=2)
    GUIObject.canvas.update_figure_title(CanvasElements)



#improve the look of sparse pulses
def resolveSparsePulses(indat,inT,LI=None,RI=None):

  if LI is None or RI is None:
    T = np.max(indat)/100
    p = np.where(np.ediff1d(indat)>T)[0]

    ZZ = np.argwhere(indat == 0).reshape((-1,))
    NZ = np.argwhere(indat != 0).reshape((-1,))
    ZZ +=1
    LI = np.intersect1d(ZZ,NZ)
    ZZ -=2
    RI = np.intersect1d(ZZ,NZ)
    LI = LI.reshape((-1,1))

    LI = np.squeeze(LI)
    RI = np.squeeze(RI)


  
  
  tvals2 = inT[RI]+1e-5
  tvals1 = inT[LI]-1e-5
  tvals = np.concatenate((tvals1,tvals2))
  xvals = np.zeros((len(tvals),))
  midx = np.concatenate((LI,RI+1))

  #HACK: fix a shape problem that can arise
  # for some reason
  if len(midx.shape) != len(tvals.shape):
    tvals = tvals.squeeze()

  if len(midx.shape) != len(xvals.shape):
    xvals = xvals.squeeze()


  xnew = np.insert(indat,midx,xvals)
  tnew = np.insert(inT,midx,tvals)

  return xnew, tnew, LI, RI

    # ---------------------------------------------------------------

    # if self.metricBox.currentText() == 'Ground Truth Data':

    #   if isinstance(AnalysisData.rawInput, list) == 0 and isinstance(AnalysisData.rawInventory, list) == 0 and isinstance(AnalysisData.rawOutput, list) == 0:
    #     PlotDat = np.concatenate((AnalysisData.rawInput, AnalysisData.rawInventory, AnalysisData.rawOutput),
    #                              axis=0,
    #                              dtype=object)
    #     self.canvas.update_figure(PlotDat[PlotIndex, :, NucIndex])
    #     self.canvas.update_figure_title(CanvasLabels)
    #     self.ThreshData = PlotDat[PlotIndex, :, NucIndex]

    #   else:
    #     #okay here is where we deal with variable
    #     #length arrays (i.e. non-constant sampling)

    #     #first find out what the plotindex belongs to
    #     #shape(list) is depreciated
    #     if isinstance(AnalysisData.rawInput, list):
    #       A1 = len(AnalysisData.rawInput)
    #     else:
    #       A1 = np.shape(AnalysisData.rawInput)[0]

    #     if isinstance(AnalysisData.rawInventory, list):
    #       A2 = len(AnalysisData.rawInventory)
    #     else:
    #       A2 = np.shape(AnalysisData.rawInventory)[0]

    #     if isinstance(AnalysisData.rawOutput, list):
    #       A3 = len(AnalysisData.rawOutput)
    #     else:
    #       A3 = np.shape(AnalysisData.rawOutput)[0]

    #     intervals = np.array([A1, A1 + A2, A1 + A2 + A3]) - 1
    #     plttyp = bisect.bisect_left(intervals, PlotIndex)

    #     localIndex = PlotIndex - (A1 * (plttyp >= 1) + A2 * (plttyp == 2))

    #     if plttyp == 0:
    #       #could be a list
    #       #could just do asarray(list) here later
    #       if isinstance(AnalysisData.rawInput, list):
    #         PDD = AnalysisData.rawInput[localIndex][:, NucIndex]
    #         PDD2 = AnalysisData.rawInputTimes[localIndex][:,NucIndex]
    #         EE = np.where(np.diff(PDD2) > 1)

    #         #list mode data is sometimes dense, but still represents pulses
    #         #for nicer plotting, add some zeros to make pulses more rounded
    #         for i in range(len(EE[0])): #len(EE[0])-1
    #             d = np.array([0])
    #             if i == 0:
    #                 RI = int(np.max(np.where(PDD[0:EE[0][0]]>0)))
    #                 xnew = np.concatenate(([np.array([PDD2[0]-1e-5]),PDD2[0:EE[0][0]][:RI],np.array([PDD2[:EE[0][0]][RI]+1e-5])]))
    #                 ynew = np.concatenate((d,PDD[0:EE[0][0]][:RI],d))
    #             else:
    #                 RI = int(np.max(np.where(PDD[EE[0][i-1]+1:EE[0][i]]>0)))
    #                 xnew = np.concatenate((xnew,np.array([PDD2[EE[0][i-1]+1]-1e-5]),PDD2[EE[0][i-1]+1:EE[0][i]][:RI],np.array([PDD2[EE[0][i-1]+1:EE[0][i]][RI]+1e-5])))
    #                 ynew = np.concatenate((ynew,d,PDD[EE[0][i-1]+1:EE[0][i]][:RI],d))

    #         if len(EE[0]) > 1:
    #           PDD2 = xnew
    #           PDD = ynew

    #       else:
    #         PDD = AnalysisData.rawInput[localIndex, :, NucIndex]
    #         PDD2 = AnalysisData.rawInputTimes[localIndex, :, NucIndex]

    #       self.canvas.update_figure(
    #           np.concatenate(
    #               (PDD2.reshape((-1,1)), PDD.reshape((-1, 1))),axis=1), 1)
    #       self.canvas.update_figure_title(CanvasLabels)
    #       self.ThreshData = PDD

    #     elif plttyp == 1:
    #       if isinstance(AnalysisData.rawInventory, list):
    #         PDD = AnalysisData.rawInventory[localIndex][:, NucIndex]
    #         PDD2 = AnalysisData.rawInventoryTimes[localIndex][:,NucIndex]
    #       else:
    #         PDD = AnalysisData.rawInventory[localIndex, :, NucIndex]
    #         PDD2 = AnalysisData.rawInventoryTimes[localIndex, :, NucIndex]

    #       self.canvas.update_figure(

    #           np.concatenate(
    #               (PDD2.reshape((-1,1)), PDD.reshape((-1, 1))),axis=1), 1)
    #       self.canvas.update_figure_title(CanvasLabels)
    #       self.ThreshData = PDD

    #     else:
    #       if isinstance(AnalysisData.rawOutput, list):
    #         PDD = AnalysisData.rawOutput[localIndex][:, NucIndex]
    #         PDD2 = AnalysisData.rawOutputTimes[localIndex][:,NucIndex]
    #         EE = np.where(np.diff(PDD2) > 1)

    #         for i in range(len(EE[0])): #len(EE[0])-1
    #             d = np.array([0])
    #             if i == 0:
    #                 RI = int(np.max(np.where(PDD[0:EE[0][0]]>0)))
    #                 xnew = np.concatenate(([np.array([PDD2[0]-1e-5]),PDD2[0:EE[0][0]][:RI],np.array([PDD2[:EE[0][0]][RI]+1e-5])]))
    #                 ynew = np.concatenate((d,PDD[0:EE[0][0]][:RI],d))
    #             else:
    #                 RI = int(np.max(np.where(PDD[EE[0][i-1]+1:EE[0][i]]>0)))
    #                 xnew = np.concatenate((xnew,np.array([PDD2[EE[0][i-1]+1]-1e-5]),PDD2[EE[0][i-1]+1:EE[0][i]][:RI],np.array([PDD2[EE[0][i-1]+1:EE[0][i]][RI]+1e-5])))
    #                 ynew = np.concatenate((ynew,d,PDD[EE[0][i-1]+1:EE[0][i]][:RI],d))
    #         if len(EE[0]) > 1:
    #           PDD2 = xnew
    #           PDD = ynew

    #       else:
    #         PDD = AnalysisData.rawOutput[localIndex, :, NucIndex]
    #         PDD2 = AnalysisData.rawOutputTimes[localIndex, :, NucIndex]

    #       self.canvas.update_figure(
    #           np.concatenate(
    #               (PDD2.reshape((-1,1)), PDD.reshape((-1, 1))),axis=1,dtype=object), 1)
    #       self.canvas.update_figure_title(CanvasLabels)
    #       self.ThreshData = PDD

    # elif self.metricBox.currentText() == 'Observed Data':

    #   # iter, location, timestep, element

    #   if isinstance(AnalysisData.inventoryAppliedError,list) == False:  #is this uniformly sampled (if so concatenate will succeed)

    #     PlotDat = np.concatenate(
    #         (AnalysisData.inputAppliedError, AnalysisData.inventoryAppliedError, AnalysisData.outputAppliedError),
    #         axis=1,
    #         dtype=object)

    #     if NumToPlot == 1:  #1
    #       IterIndex = np.random.randint(
    #           low=0, high=int(self.IterBox.text()) - 1)
    #       self.canvas.update_figure(PlotDat[IterIndex, PlotIndex, :, NucIndex])
    #       self.ThreshData = PlotDat[IterIndex, PlotIndex, :, NucIndex]

    #     elif NumToPlot == -1:  #average
    #       self.canvas.update_figure(
    #           np.mean(PlotDat[:, PlotIndex, :, NucIndex], axis=0))
    #       self.ThreshData = np.mean(PlotDat[:, PlotIndex, :, NucIndex], axis=0)

    #     elif NumToPlot == -2:  #all
    #       self.canvas.update_figure(PlotDat[:, PlotIndex, :, NucIndex].T)
    #       self.ThreshData = PlotDat[:, PlotIndex, :, NucIndex].T

    #     elif NumToPlot == 15:  #random 15
    #       indexes = np.zeros((15,))
    #       for i in range(0, 15):
    #         indexes[i] = np.random.randint(
    #             low=0, high=int(self.IterBox.text()) - 1)

    #       self.canvas.update_figure(PlotDat[indexes.astype('int'), PlotIndex, :,
    #                                         NucIndex].T)
    #       self.ThreshData = PlotDat[indexes.astype('int'), PlotIndex, :,
    #                                 NucIndex].T

    #     else:
    #       None

    #     self.canvas.update_figure_title(CanvasLabels)

    #   else:  #this is not uniformily sampled

    #     #which terms are not uniformly sampled
    #     if isinstance(AnalysisData.inputAppliedError, list):
    #       A1 = len(AnalysisData.inputAppliedError)
    #     else:
    #       A1 = np.shape(AnalysisData.inputAppliedError)[0]

    #     if isinstance(AnalysisData.inventoryAppliedError, list):
    #       A2 = len(AnalysisData.inventoryAppliedError)
    #     else:
    #       A2 = np.shape(AnalysisData.inventoryAppliedError)[0]

    #     if isinstance(AnalysisData.outputAppliedError, list):
    #       A3 = len(AnalysisData.outputAppliedError)
    #     else:
    #       A3 = np.shape(AnalysisData.outputAppliedError)[0]

    #     #breakdown the indicies into intervals
    #     intervals = np.array([A1, A1 + A2, A1 + A2 + A3]) - 1
    #     plttyp = bisect.bisect_left(
    #         intervals, PlotIndex
    #     )  #plotIndex is where in the array the requested quantity is, question is is it inp, inv, or out?

    #     localIndex = PlotIndex - (
    #         A1 * (plttyp >= 1) + A2 * (plttyp == 2)
    #     )  #what is the index in the specific quantity type (i.e. what's the index in the inventory array)

    #     PH = []
    #     if plttyp == 0:
    #       #could be a list
    #       #could just do asarray(list) here later
    #       if isinstance(AnalysisData.inputAppliedError, list):
    #         PDD = AnalysisData.inputAppliedError[localIndex][:, :,
    #                                          NucIndex]  #get the measured data
    #         PDD2 = AnalysisData.rawInputTimes[
    #             localIndex][:, NucIndex]  #get the corresponding time

    #       else:
    #         PDD = AnalysisData.inputAppliedError[localIndex, :, :, NucIndex]
    #         PDD2 = AnalysisData.rawInputTimes[localIndex, :, :, NucIndex]

    #       PH.append(PDD2)
    #       PH.append(PDD)

    #     elif plttyp == 1:
    #       if isinstance(AnalysisData.inventoryAppliedError, list):
    #         PDD = AnalysisData.inventoryAppliedError[localIndex][:, :, NucIndex]
    #         PDD2 = AnalysisData.rawInventoryTimes[localIndex][:, NucIndex]
    #       else:
    #         PDD = AnalysisData.inventoryAppliedError[localIndex, :, :, NucIndex]
    #         PDD2 = AnalysisData.rawInventoryTimes[localIndex, :, :, NucIndex]

    #       PH.append(PDD2)
    #       PH.append(PDD)

    #     else:
    #       if isinstance(AnalysisData.outputAppliedError, list):
    #         PDD = AnalysisData.outputAppliedError[localIndex][:, :, NucIndex]
    #         PDD2 = AnalysisData.rawOutputTimes[localIndex][:, NucIndex]
    #       else:
    #         PDD = AnalysisData.outputAppliedError[localIndex, :, :, NucIndex]
    #         PDD2 = AnalysisData.rawOutputTimes[localIndex, :, :, NucIndex]

    #       PH.append(PDD2)
    #       PH.append(PDD)

    #     #FH = np.zeros(np.shape(PH[1]))
    #     #improved plotting visuals for pulses
    #     #note this won't show noise for zero values
    #     #as usually only dense, non-zero data is recorded
    #     #so no noise can be added to zeros (as they are unrecorded)
    #     #this is just an improved visual
    #     if len(np.where(np.diff(PH[0]) > 1)[0]) > 0:
    #       for J in range(np.shape(PH[1])[0]):
    #         PDD = PH[1][J,:]
    #         PDD2 = PH[0]
    #         EE = np.where(np.diff(PDD2) > 1)


    #         for i in range(len(EE[0])): #len(EE[0])-1
    #             d = np.array([0])
    #             if i == 0:
    #                 RI = int(np.max(np.where(PDD[0:EE[0][0]]>0)))
    #                 xnew = np.concatenate(([np.array([PDD2[0]-1e-5]),PDD2[0:EE[0][0]][:RI],np.array([PDD2[:EE[0][0]][RI]+1e-5])]))
    #                 ynew = np.concatenate((d,PDD[0:EE[0][0]][:RI],d))
    #             else:
    #                 RI = int(np.max(np.where(PDD[EE[0][i-1]+1:EE[0][i]]>0)))
    #                 xnew = np.concatenate((xnew,np.array([PDD2[EE[0][i-1]+1]-1e-5]),PDD2[EE[0][i-1]+1:EE[0][i]][:RI],np.array([PDD2[EE[0][i-1]+1:EE[0][i]][RI]+1e-5])))
    #                 ynew = np.concatenate((ynew,d,PDD[EE[0][i-1]+1:EE[0][i]][:RI],d))

    #         if len(EE[0]) > 1:
    #           PDD2 = xnew
    #           PDD = ynew
    #         if J == 0:
    #           FH = np.zeros((np.shape(PH[1])[0],np.shape(ynew)[0]))
    #         FH[J,:] = ynew

    #       PH[1] = FH
    #       PH[0] = PDD2
    #       del FH #garbage cleanup

    #     #how many to plot?
    #     if NumToPlot == 1:  #1
    #       IterIndex = np.random.randint(
    #           low=0, high=int(self.IterBox.text()) - 1)
    #       PH[1] = PH[1][IterIndex, :].reshape((-1,))
    #       self.canvas.update_figure(
    #           PH, 2
    #       )  #the 2 flag indicates theres X and Y data (as it is not unformly sampled)
    #       self.ThreshData = PH[1]

    #     elif NumToPlot == -1:  #average
    #       PH[1] = np.mean(PH[1], axis=0)
    #       self.canvas.update_figure(PH, 2)
    #       self.ThreshData = PH[1]

    #     elif NumToPlot == -2:  #all

    #       PH[1] = PH[1].T
    #       self.canvas.update_figure(PH, 2)
    #       self.ThreshData = PH[1].T

    #     elif NumToPlot == 15:  #random 15
    #       indexes = np.zeros((15,))
    #       for i in range(0, 15):
    #         indexes[i] = np.random.randint(
    #             low=0, high=int(self.IterBox.text()) - 1)

    #       PH[1] = PH[1][indexes.astype('int'), :]
    #       if PH[1].shape[0] < PH[1].shape[1]:
    #         PH[1] = PH[1].T
    #       self.canvas.update_figure(PH, 2)
    #       self.ThreshData = PH[1]

    #     else:
    #       None

    #     self.canvas.update_figure_title(CanvasLabels)

    # elif self.metricBox.currentText() == 'Pu MUF':
    #   TP = MUFIter[0]
    # elif self.metricBox.currentText() == 'Pu SEID':
    #   TP2 = SEIDIter[0]
    # elif self.metricBox.currentText() == 'Pu SITMUF':
    #   TP3 = SITMUFIter[0]
    # elif self.metricBox.currentText() == 'Pu Page SITMUF':
    #   TP4 = PageIter[0]
    # elif self.metricBox.currentText() == 'U MUF':
    #   TP = MUFIter[1]
    # elif self.metricBox.currentText() == 'U SEID':
    #   TP2 = SEIDIter[1]
    # elif self.metricBox.currentText() == 'U SITMUF':
    #   TP3 = SITMUFIter[1]
    # elif self.metricBox.currentText() == 'U Page SITMUF':
    #   TP4 = PageIter[1]
    # elif self.metricBox.currentText() == 'Generic MUF':
    #   TP = MUFIter[2]
    # elif self.metricBox.currentText() == 'Generic SEID':
    #   TP2 = SEIDIter[2]
    # elif self.metricBox.currentText() == 'Generic SITMUF':
    #   TP3 = SITMUFIter[2]
    # elif self.metricBox.currentText() == 'Generic Page SITMUF':
    #   TP4 = PageIter[2]
    # else:
    #   None

    # # if plot MUF
    # if TP > -1:
    #   PlotDat = AnalysisData.MUF

    #   if len(PlotDat.shape) == 2:
    #     PlotDat = np.expand_dims(PlotDat,axis=1)

    #   if NumToPlot == 1:
    #     IterIndex = np.random.randint(
    #         low=0, high=int(self.IterBox.text()) - 1)  #get a random iteration
    #     self.canvas.update_figure(PlotDat[IterIndex, TP, :])

    #   elif NumToPlot == -1:
    #     self.canvas.update_figure(np.mean(PlotDat[:, TP, :],
    #                                       axis=0))  #plot the mean

    #   elif NumToPlot == -2:
    #     self.canvas.update_figure(PlotDat[:, MUFIter[2], :].T)  #plot them all

    #   elif NumToPlot == 15:
    #     indexes = np.zeros((15,))
    #     for i in range(0, 15):
    #       indexes[i] = np.random.randint(
    #           low=0, high=int(self.IterBox.text()) - 1)

    #     self.canvas.update_figure(PlotDat[indexes.astype('int'),
    #                                       TP, :].T)  #plot 15 iterations

    #   else:
    #     None

    #   #setup the plot label
    #   if hasattr(self, 'Wizard'):
    #     CanvasLabels[2] = ('MUF (' + self.Wizard.MassUnitVec + ')')

    #   else:
    #     CanvasLabels[2] = ('MUF (kg)')

    #   self.canvas.update_figure_title(CanvasLabels)
    #   self.ThreshData = PlotDat[:, TP, :]

    # # if plot SEID
    # #code largely mimics the plot
    # #code for MUF above
    # if TP2 > -1:
    #   PlotDat = AnalysisData.SEMUF

    #   if len(PlotDat.shape) == 2:
    #     PlotDat = np.expand_dims(PlotDat,axis=1)

    #   if NumToPlot == 1:
    #     IterIndex = np.random.randint(low=0, high=int(self.IterBox.text()) - 1)
    #     self.canvas.update_figure(PlotDat[IterIndex, TP2, :])

    #   elif NumToPlot == -1:
    #     self.canvas.update_figure(np.mean(PlotDat[:, TP2, :], axis=0))

    #   elif NumToPlot == -2:
    #     self.canvas.update_figure(PlotDat[:, TP2, :].T)

    #   elif NumToPlot == 15:
    #     indexes = np.zeros((15,))
    #     for i in range(0, 15):
    #       indexes[i] = np.random.randint(
    #           low=0, high=int(self.IterBox.text()) - 1)

    #     self.canvas.update_figure(PlotDat[indexes.astype('int'), TP2, :].T)

    #   else:
    #     None

    #   if hasattr(self, 'Wizard'):
    #     CanvasLabels[2] = ('SEID (' + self.Wizard.MassUnitVec + ')')

    #   else:
    #     CanvasLabels[2] = ('SEID (kg)')

    #   self.canvas.update_figure_title(CanvasLabels)
    #   self.ThreshData = PlotDat[:, TP2, :]

    # # if plot SITMUF
    # if TP3 > -1:
    #   PlotDat = AnalysisData.SITMUF

    #   if len(PlotDat.shape) == 2:
    #     PlotDat = np.expand_dims(PlotDat,axis=1)

    #   if NumToPlot == 1:
    #     IterIndex = np.random.randint(low=0, high=int(self.IterBox.text()) - 1)
    #     self.canvas.update_figure(PlotDat[IterIndex, TP3, :])

    #   elif NumToPlot == -1:
    #     self.canvas.update_figure(np.mean(PlotDat[:, TP3, :], axis=0))

    #   elif NumToPlot == -2:
    #     self.canvas.update_figure(PlotDat[:, TP3, :].T)

    #   elif NumToPlot == 15:
    #     indexes = np.zeros((15,))
    #     for i in range(0, 15):
    #       indexes[i] = np.random.randint(
    #           low=0, high=int(self.IterBox.text()) - 1)

    #     self.canvas.update_figure(PlotDat[indexes.astype('int'), TP3, :].T)

    #   else:
    #     None

    #   if hasattr(self, 'Wizard'):
    #     CanvasLabels[2] = ('SITMUF (' + self.Wizard.MassUnitVec + ')')

    #   else:
    #     CanvasLabels[2] = ('SITMUF (kg)')
    #   self.canvas.update_figure_title(CanvasLabels)
    #   self.ThreshData = PlotDat[:, TP3, :]

    # # if plot page
    # if TP4 > -1:
    #   PlotDat = AnalysisData.Page

    #   if len(PlotDat.shape) == 2:
    #     PlotDat = np.expand_dims(PlotDat,axis=1)

    #   if NumToPlot == 1:
    #     IterIndex = np.random.randint(low=0, high=int(self.IterBox.text()) - 1)
    #     self.canvas.update_figure(PlotDat[IterIndex, TP4, :])

    #   elif NumToPlot == -1:
    #     self.canvas.update_figure(np.mean(PlotDat[:, TP4, :], axis=0))

    #   elif NumToPlot == -2:
    #     self.canvas.update_figure(PlotDat[:, TP4, :].T)

    #   elif NumToPlot == 15:
    #     indexes = np.zeros((15,))
    #     for i in range(0, 15):
    #       indexes[i] = np.random.randint(
    #           low=0, high=int(self.IterBox.text()) - 1)

    #     self.canvas.update_figure(PlotDat[indexes.astype('int'), TP4, :].T)
    #   else:
    #     None

    #   # print("A")
    #   CanvasLabels[2] = 'Page Score'
    #   self.canvas.update_figure_title(CanvasLabels)
    #   self.ThreshData = PlotDat[:, TP4, :]

    # if self.CalcThresh.isEnabled() == 0:
    #   self.CalcThresh.setEnabled(1)
    #   self.CalcThresh.PassLoc('CTB')
    #   self.CalcThresh._animation.start()



def UpdateLocOpts(self,GUIparams):
    """
            Function to control
            GUI options once a GUI
            change has been detected
    """




    grad = "border-color: rgb({value},{value2},{value3});".format(value=153,value2=200,value3=221) +\
   "border-width: 2px;" +\
   "border-style: solid;" +\
   "padding: 0px;" +\
   "border-radius: 7px;" +\
   "margin-top: 20px;" +\
   "background-color: rgb(239,239,239);" +\
    "}"

    grad2 = "border-color: rgb({value},{value2},{value3});".format(value=211,value2=211,value3=211) +\
   "border-width: 2px;" +\
   "border-style: solid;" +\
   "padding: 0px;" +\
   "border-radius: 7px;" +\
   "margin-top: 20px;" +\
   "background-color: rgb(239,239,239);" +\
    "}"

    if self.window().MakeLight.isChecked() == 0:
      grad = grad.replace('rgb(239,239,239)', 'rgb(52,52,52)')
      grad = grad.replace('rgb(153,200,221)', 'rgb(0,83,118)')
      grad2 = grad2.replace('rgb(239,239,239)', 'rgb(52,52,52)')
      grad2 = grad2.replace('rgb(211,211,211)', 'rgb(66,66,66)')

    #not all combinations of plot options should have the same options
    #for example, ground truth shouldn't have iterations available
    #and MUF shouldn't have locations available

    # GT remove iterations
    if self.metricBox.currentText() == 'Ground Truth Data':
      for i in range(0, self.NumToPlot.count()):
        self.NumToPlot.removeItem(0)
      self.NumToPlot.setEnabled(0)
      self.mb4.ChangeActive(0)
      self.mb4.setStyleSheet(
          "QWidget#{VAL}".format(VAL=self.mb4.Loc) + "{" + grad2 +
          "QWidget#{VAL}".format(VAL=self.mb4.Loc) )
    # OD add iterations
    elif self.metricBox.currentText() == 'Observed Data':
      if int(self.IterBox.text()) <= 100:
        if self.NumToPlot.count() > 0:
          for i in range(0, self.NumToPlot.count()):
            self.NumToPlot.removeItem(0)
        self.NumToPlot.addItem('1 Random Iteration')
        self.NumToPlot.addItem('Average of All Iterations')
        self.NumToPlot.addItem('All Iterations (' + self.IterBox.text() + ')')

      else:
        #if there's more than 100 iterations set a max of 15
        #to plot at once (keeps MPL backend from imploding)
        for i in range(0, self.NumToPlot.count()):
          self.NumToPlot.removeItem(0)

        self.NumToPlot.addItem('1 Random Iteration')
        self.NumToPlot.addItem('15 Random Iterations')
        self.NumToPlot.addItem('Average of All Iterations')
      self.NumToPlot.setEnabled(1)
      self.mb4.ChangeActive(1)
      self.mb4.setStyleSheet(
          "QWidget#{VAL}".format(VAL=self.mb4.Loc) + "{" + grad +
          "QWidget#{VAL}".format(VAL=self.mb4.Loc) )
    else:
      None

    # GT/OD data - add ele and locs
    if self.metricBox.currentText(
    ) == 'Ground Truth Data' or self.metricBox.currentText() == 'Observed Data':
      if self.LocBox.count() == 0:
        for i in self.PlotLocLabels:
          if i != '':
            self.LocBox.addItem(i)
        for i in GUIparams.EleVecLabel:
          self.NucIDBox.addItem(i)
        self.LocBox.setEnabled(1)
        self.mb2.ChangeActive(1)
        self.mb2.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) + "{" + grad +
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) )

        self.NucIDBox.setEnabled(1)
        self.mb3.ChangeActive(1)
        self.mb3.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) + "{" + grad +
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) )

      else:
        None
    else:
      #self.mb2.setStyleSheet('QGroupBox:title {' 'padding-right: 10px}')
      #self.mb3.setStyleSheet('QGroupBox:title {' 'padding-right: 10px}')
      if self.LocBox.count(
      ) != 0:  # statistical test boxes - add iterations and remove location / ele ID
        for i in range(0, int(self.LocBox.count())):
          self.LocBox.removeItem(0)
        for i in range(0, int(self.NucIDBox.count())):
          self.NucIDBox.removeItem(0)

        self.LocBox.setEnabled(0)
        self.mb2.ChangeActive(0)
        self.mb2.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) + "{" + grad2 +
            "QWidget#{VAL}".format(VAL=self.mb2.Loc))

        self.NucIDBox.setEnabled(0)
        self.mb3.ChangeActive(0)
        self.mb3.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) + "{" + grad2 +
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) )

        if int(self.IterBox.text()) <= 100:  #check options for iterations
          if self.NumToPlot.count() > 0:
            for i in range(0, self.NumToPlot.count()):
              self.NumToPlot.removeItem(0)
          self.NumToPlot.addItem('1 Random Iteration')
          self.NumToPlot.addItem('Average of All Iterations')
          self.NumToPlot.addItem('All Iterations (' + self.IterBox.text() + ')')
        else:
          for i in range(0, self.NumToPlot.count()):
            self.NumToPlot.removeItem(0)
          self.NumToPlot.addItem('1 Random Iteration')
          self.NumToPlot.addItem('15 Random Iterations')
          self.NumToPlot.addItem('Average of All Iterations')
        self.NumToPlot.setEnabled(1)
        self.mb4.ChangeActive(1)
        self.mb4.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb4.Loc) + "{" + grad +
            "QWidget#{VAL}".format(VAL=self.mb4.Loc) )
      else:
        #if not included then style will look weird when no changes
        #are made to the options, due to the style sheet change
        #at the top of this if block
        self.mb2.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) + "{" + grad2 +
            "QWidget#{VAL}".format(VAL=self.mb2.Loc) )
        self.mb3.setStyleSheet(
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) + "{" + grad2 +
            "QWidget#{VAL}".format(VAL=self.mb3.Loc) )