import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6 import QtCore, QtWidgets, QtGui
from matplotlib.figure import Figure
from PIL import ImageFont   ## MH added to test label sizing
import time
from MAPIT.GUI import StyleOps



class PropertyHolder:
  pass

class MPLCanvas(FigureCanvas):
  """
        Class with functions to control
        the plot in MAPIT
  """

  def parent(self):
    return self.main_gui

  def __init__(self, parent, dpi=100):

    #sself.currentFontSize = QtWidgets.QApplication.font().pointSize()
    #self.currentFontSize=20
    self.main_gui = parent
    matplotlib.rcParams.update({'font.size': parent.currentFontSize-2})


    

    self.fig = Figure(dpi=dpi, frameon=True)
    #self.fig.subplots_adjust(left=0.10, bottom=0.10, right=0.98, top=0.95)
    self.axes = self.fig.add_subplot(111)

    self.fig.set_facecolor(self.main_gui.colordict["WindowBackground"])
    self.axes.set_facecolor(self.main_gui.colordict["plotBg"])



    self.axes.spines['bottom'].set_color(self.main_gui.colordict["Text"])
    self.axes.spines['top'].set_color(self.main_gui.colordict["Text"])
    self.axes.spines['right'].set_color(self.main_gui.colordict["Text"])
    self.axes.spines['left'].set_color(self.main_gui.colordict["Text"])

    self.axes.tick_params(axis='x', colors=self.main_gui.colordict["Text"], which='both')
    self.axes.tick_params(axis='y', colors=self.main_gui.colordict["Text"], which='both')

    self.axes.yaxis.label.set_color(self.main_gui.colordict["Text"])
    self.axes.xaxis.label.set_color(self.main_gui.colordict["Text"])
    self.axes.title.set_color(self.main_gui.colordict["Text"])

    self.axes.tick_params(axis='both', which='major', labelsize=parent.currentFontSize-2)
    self.axes.tick_params(axis='both', which='minor', labelsize=parent.currentFontSize-2)

    self.compute_initial_figure()
    self.boxpos = self.axes.get_position()

    FigureCanvas.__init__(self, self.fig)
    #self.setParent(parent)
    

    #FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding,
                               #QtWidgets.QSizePolicy.Expanding)
    self.Thresh = []
  
  def update_offset_text_color(self):
    self.axes.yaxis.get_offset_text().set_color(self.main_gui.colordict["Text"])
    self.fig.canvas.draw_idle()

  def compute_initial_figure(self):
    pass

  def update_figure(self, data, isVariableFlag=0, usehatch = 0):
    #change the default color cycle
    #dark and light colors provided

    #self.fig.subplots_adjust(left=0.10, bottom=0.10, right=0.98, top=0.95)

    #required in case switching from legend figure (e.g., bar contrib)
    #to normal plot w/o legend
    box = self.boxpos
    self.axes.set_position([box.x0, box.y0, box.width, box.height])

    matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=[
        self.window().colordict["plot_lb"],
        self.window().colordict["plot_t"],
        self.window().colordict["plot_a"],
        self.window().colordict["plot_p"], 
        self.window().colordict["plot_y"],  
        self.window().colordict["plot_r"], 
        self.window().colordict["plot_g"], 
        self.window().colordict["plot_la"], 
        self.window().colordict["plot_o"]]) 


    self.axes.cla()

    if data[2] == 'line':
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
    elif data[2] == 'hist':
      if self.main_gui.metricBox.currentText().endswith("(Absolute)"):
        contrib_type='abs'
      else:
        contrib_type='rel'

      if hasattr(self.main_gui,'PlotLocLabels'):
        contribL = self.main_gui.PlotLocLabels
      else:
        contribL = None
      
      plotdat, idx_contrib_sorted, idx_mapping_loc, labels = getContribPlotData(data[1],contrib_type,internalLabels=contribL)
      xx = np.linspace(0,data[1].shape[2]-1,data[1].shape[2])
      width = 1

      c0 = 0
      c1 = 0
      for i in range(len(idx_contrib_sorted)):
          if i == 0:
              b = np.zeros(plotdat.shape[1])
          else:
              b = plotdat[i-1,]
        
          if usehatch == 1:
              if labels[idx_mapping_loc[i]].endswith('(rand)'):
                texture = ['--', '/', '+', 'x']
                self.axes.bar(xx,plotdat[i,]-b,width,bottom=b,label=labels[idx_mapping_loc[i]],edgecolor='k',color='C'+str(c0),hatch=texture[c0%4],alpha=0.6)
                c0+=1
              else:
                texture = ['.', '*', 'o', '\\']
                self.axes.bar(xx,plotdat[i,]-b,width,bottom=b,label=labels[idx_mapping_loc[i]],edgecolor='k',color='C'+str(c1),hatch=texture[c1%4],alpha=0.6)
                c1+=1
          else:
            texture = ['.', '*', 'o', '\\']
            self.axes.bar(xx,plotdat[i,]-b,width,bottom=b,label=labels[idx_mapping_loc[i]],edgecolor='k',hatch=texture[i%4],alpha=0.6)
          
          


    self.draw()

  def update_figure_legend(self):
      
      box = self.boxpos
      Z = 12/self.main_gui.currentFontSize*0.83
      self.axes.set_position([box.x0, box.y0, box.width * Z, box.height])

      handles, labels = self.axes.get_legend_handles_labels()
      labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))

      lgd = self.axes.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5),
                       facecolor=self.main_gui.colordict["plotBg"],
                       labelcolor=self.main_gui.colordict["Text"],
                       edgecolor=self.main_gui.colordict["Text"],
                       fontsize = self.main_gui.currentFontSize-2,
                       handleheight=3,
                       handlelength=4)
      #self.fig.subplots_adjust(right=0.75)
      #lgd.set_in_layout(True)
      #self.fig.tight_layout()
      
      self.draw()

  def update_figure_title(self, data):
    #fontsize = QtWidgets.QApplication.font().pointSize()
    tcolor = self.parent().colordict["Text"]
    self.axes.set_title(data.title,fontsize=self.main_gui.currentFontSize-2, color=tcolor)
    self.axes.set_xlabel(data.xlabel, fontsize = self.main_gui.currentFontSize-2, color=tcolor)
    self.axes.set_ylabel(data.ylabel, fontsize=self.main_gui.currentFontSize-2, color=tcolor)
    self.axes.ticklabel_format(axis='y', style='sci', useOffset=True,scilimits=(-4,4)) #use sci notation for large numbers
    #self.axes.yaxis.set_tick_params(labelsize=20)
    #self.axes.tick_params(labelsize=fontsize)
    #self.axes.yaxis.get_offset_text().set_size(fontsize)

    self.draw()

  def update_thresh(self, data, data2):  #draw the threshold from the threshold calculator
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
    self.main_gui.StatThreshDisp.setText(str(round(TotOver, 2)))
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
      GUIObj.metricBox.clear()
      GUIObj.metricBox.addItem('Ground Truth Data')
      GUIObj.metricBox.addItem('Observed Data')
    else:
      GUIObj.metricBox.addItem('Ground Truth Data')
      GUIObj.metricBox.addItem('Observed Data')

    if GUIObj.NumToPlot.count() < 0:
      GUIObj.NumToPlot.clear()



def getNumToPlot(GUIObj):
  NumToPlot = 0
  if GUIObj.NumToPlot.currentText(
  ) == 'All Iterations (' + GUIObj.IterBox.text() + ')':
    NumToPlot = -2
  elif GUIObj.NumToPlot.currentText() == '15 Random Iterations':
    NumToPlot = 15
  elif GUIObj.NumToPlot.currentText() == '1 Random Iteration' or GUIObj.NumToPlot.currentText() == '1 Iteration':
    NumToPlot = 1
  elif GUIObj.NumToPlot.currentText() == 'Average of All Iterations':
    NumToPlot = -1
  else:
    None

  return NumToPlot


def getDataWithoutLocations(inp,nPlot):

  #list strictly for the total seid
  #contrib plot 
  #if len(inp.shape) == 3:
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
    np.random.shuffle(xx)
    xidx = xx[:15].astype(int)
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
    dat = dat[xidx,].reshape((1,-1))
  elif nPlot == -1:
    dat = np.mean(dat,axis=0)
  elif nPlot == -2:
    None
  elif nPlot == 15:
    np.random.shuffle(xx)
    xidx = xx[:15].astype(int)
    dat = dat[xidx,]
  
  return dat, datT
  

def getContribPlotData(indat,contrib_type,internalLabels=None):

  if len(indat.shape) == 4:
    A = indat[:,:,:,0].squeeze()
    B = indat[:,:,:,1].squeeze()
    indat = np.concatenate((A,B),axis=1)

    labels = []

    if internalLabels == None:          
      for i in range(A.shape[1]):
        labels.append('location '+str(i) + ' (rand)')    

      for i in range(A.shape[1]):
        labels.append('location '+str(i) + ' (sys)')
    
    else:
      for i in range(A.shape[1]):
        labels.append(internalLabels[i] + ' (rand)')    

      for i in range(A.shape[1]):
        labels.append(internalLabels[i] + ' (sys)')

    labels.append('All other locations (rand)')
    labels.append('All other locations (sys)')

    extra_slots = 2

  else:
    labels = []
    A = indat

    if internalLabels == None:
      for i in range(indat.shape[1]):
        labels.append('location '+str(i))
      labels.append('All other locations')
    else:
      for i in range(indat.shape[1]):
        labels.append(internalLabels[i])
      labels.append('All other locations') 

    extra_slots = 1



  rdat = indat.mean(axis=0) #average across iterations
  rtot = rdat.sum(axis=0)
  rtot[rtot==0]=-1 #this solves a divide by zero error later on, if there's zero error contribution it's generally caused by  
                   #a zero total inventory for MBP 0, this might have unintended consequences if a user enters a "0" measurement
                   #error rather than just disabling error propagation generally

  thresh=0.01 #thereshold for error contribution

  max_contrib = rdat.max(axis=1)/rdat.mean(axis=1).sum()
  idx_over_thresh = np.argwhere(max_contrib>thresh).squeeze() #good
  sorted_idx_over = idx_over_thresh[np.argsort(-rdat[idx_over_thresh,:].squeeze().mean(axis=1))] #good

  rcontribholder = np.zeros((len(sorted_idx_over)+extra_slots,rdat.shape[1]))
  rcontribholder_abs = np.zeros((len(sorted_idx_over)+extra_slots,rdat.shape[1]))

  c=0
  for i in range(rdat.shape[0]):
      if i in sorted_idx_over:
          rcontribholder[c,] = rdat[i,:]/rtot
          rcontribholder_abs[c,] = rdat[i,:]
          c+=1
      else:
          if i <= A.shape[1]-1 and extra_slots==2:
            rcontribholder[-2,] += rdat[i,:]/rtot
            rcontribholder_abs[-2,] += rdat[i,:]
          else:
            rcontribholder[-1,] += rdat[i,:]/rtot
            rcontribholder_abs[-1,] += rdat[i,:]


  idx_contrib_sorted = (-np.mean(rcontribholder,axis=1)).argsort() #sort again for purposes of the bar plot

  idx_mapping_loc = np.zeros(len(idx_contrib_sorted),)

  for i in range(len(idx_mapping_loc)):
      if i == len(idx_mapping_loc)-1:
        idx_mapping_loc[i] = -1 #systematic or total 
      elif i == len(idx_mapping_loc)-2 and extra_slots==2: 
          idx_mapping_loc[i] = -2 #random
      else:
        idx_mapping_loc[i] = sorted_idx_over[i]
          

  idx_mapping_loc = idx_mapping_loc.astype(int)

  if contrib_type == 'abs':
    cs = np.cumsum(rcontribholder_abs[idx_contrib_sorted],axis=0)
  else:
    cs = np.cumsum(rcontribholder[idx_contrib_sorted],axis=0)*100

  return cs, idx_contrib_sorted, idx_mapping_loc, labels


def getData(GUIObject,GUIparams,AnalysisData,ThresholdL = False):
    CanvasElements = PropertyHolder()
    plotType = 'line'

    # --------------- common plot variables ---------------------

    if GUIObject.NucIDBox.currentText() in GUIparams.EleVecLabel:
       NucIndex = GUIparams.EleVecLabel.index(GUIObject.NucIDBox.currentText()) #this maps the name to an array index
    else:
      NucIndex = None
   
    PlotIndex = int(GUIObject.LocBox.currentIndex()) #this gets the location index
   
    if GUIparams.labels["Box46L"] in GUIObject.metricBox.currentText()  or GUIparams.labels["Box47L"] in GUIObject.metricBox.currentText():
      CanvasElements.xlabel = 'Material Balance Period'
    else:
      CanvasElements.xlabel = 'Time (hr)'

    if GUIparams.labels["Box47L"] in GUIObject.metricBox.currentText() or GUIparams.labels["Box50L"] in GUIObject.metricBox.currentText():
      CanvasElements.ylabel = 'Cumulative Contribution (%)'
    elif GUIparams.labels["Box46L"] in GUIObject.metricBox.currentText() or GUIparams.labels["Box49L"] in GUIObject.metricBox.currentText():
      CanvasElements.ylabel = 'Cumulative Contribution (kg)'
    else:
      CanvasElements.ylabel = 'Mass (kg)'

    if ThresholdL == True:
      numToPlot = -2
    else:
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
        dat = np.expand_dims(dat,2)
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
      elif currentText.endswith(GUIparams.labels["Box46L"]) or currentText.endswith(GUIparams.labels["Box47L"]):
        numToPlot = -2
        plotType='hist'
        if GUIObject.NucIDBox.currentText() == GUIparams.labels["Box44L"]:
          inp = AnalysisData.SEMUFContribR
        elif GUIObject.NucIDBox.currentText() == GUIparams.labels["Box45L"]:
          inp = AnalysisData.SEMUFContribS
        elif GUIObject.NucIDBox.currentText() == GUIparams.labels["Box48L"]:
          inp = np.concatenate((np.expand_dims(AnalysisData.SEMUFContribR,axis=3),np.expand_dims(AnalysisData.SEMUFContribS,axis=3)),axis=-1)
      elif currentText.endswith(GUIparams.labels["Box49L"]) or currentText.endswith(GUIparams.labels["Box50L"]):
        numToPlot = -2
        plotType='hist'
        if GUIObject.NucIDBox.currentText() == GUIparams.labels["Box44L"]:
          inp = AnalysisData.SEMUFAIContribR
        elif GUIObject.NucIDBox.currentText() == GUIparams.labels["Box45L"]:
          inp = AnalysisData.SEMUFAIContribS
        elif GUIObject.NucIDBox.currentText() == GUIparams.labels["Box48L"]:
          inp = np.concatenate((np.expand_dims(AnalysisData.SEMUFContribR,axis=3),np.expand_dims(AnalysisData.SEMUFContribS,axis=3)),axis=-1)

      #TODO: continue SEID plot stuff here
      dat, datT = getDataWithoutLocations(inp,numToPlot)
    dh = []
    dh.append(datT)
    dh.append(dat)
    dh.append(plotType)  
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
    hatchflag=1 if len(dh[1].shape)==4 else 0
    GUIObject.canvas.update_figure(dh,isVariableFlag=2,usehatch=hatchflag)
    GUIObject.canvas.update_figure_title(CanvasElements)
    GUIObject.canvas.update_figure_legend() if dh[2] == 'hist' else None #add a legend for SEID contrib plot
    GUIObject.canvas.update_offset_text_color()


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





def UpdateLocOpts(self,GUIparams):
    """
            Function to control
            GUI options once a GUI
            change has been detected
    """



    #not all combinations of plot options should have the same options
    #for example, ground truth shouldn't have iterations available
    #and MUF shouldn't have locations available

    # GT remove iterations
    if self.metricBox.currentText() == 'Ground Truth Data':
      for i in range(0, self.NumToPlot.count()):
        self.NumToPlot.removeItem(0)
      self.NumToPlot.setEnabled(0)
      self.mb4.ChangeActive(0)
      self.mb4.setEnabled(0)
      self.mb4.setTitle('')
      StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb4)
    # OD add iterations
    elif self.metricBox.currentText() == 'Observed Data':
      if self.IterBox.text() == "":
        if self.NumToPlot.count() > 0:
          for i in range(0, self.NumToPlot.count()):
            self.NumToPlot.removeItem(0)
        self.NumToPlot.addItem('1 Iteration')
      elif int(self.IterBox.text()) <= 100:
        if self.NumToPlot.count() > 0:
          for i in range(0, self.NumToPlot.count()):
            self.NumToPlot.removeItem(0)
#        self.NumtoPlot.addItem('All Iterations (' + self.IterBox.text() + ')')
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
      self.mb4.setEnabled(1)
      self.mb4.setTitle(GUIparams.labels["Box34L"])
      StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb4,isactive=1)
    else:
      #re-add iterations here in case they were removed
      #due to previous selection
      if self.IterBox.text() == "":
        if self.NumToPlot.count() > 0:
          for i in range(0, self.NumToPlot.count()):
            self.NumToPlot.removeItem(0)
        self.NumToPlot.addItem('1 Iteration')
      elif int(self.IterBox.text()) <= 100:
        if self.NumToPlot.count() > 0:
          for i in range(0, self.NumToPlot.count()):
            self.NumToPlot.removeItem(0)
        self.NumToPlot.addItem('All Iterations (' + self.IterBox.text() + ')')
        self.NumToPlot.addItem('1 Random Iteration')
        self.NumToPlot.addItem('Average of All Iterations')

      else:
        #if there's more than 100 iterations set a max of 15
        #to plot at once (keeps MPL backend from imploding)
        for i in range(0, self.NumToPlot.count()):
          self.NumToPlot.removeItem(0)

        self.NumToPlot.addItem('15 Random Iterations')
        self.NumToPlot.addItem('1 Random Iteration')
        self.NumToPlot.addItem('Average of All Iterations')
      self.NumToPlot.setEnabled(1)
      self.mb4.ChangeActive(1)
      self.mb4.setEnabled(1)
      self.mb4.setTitle(GUIparams.labels["Box34L"])
      StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb4,isactive=1)



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
        self.mb2.setEnabled(1)
        self.mb2.setTitle(GUIparams.labels["Box32L"])
        StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb2,isactive=1)

        self.NucIDBox.setEnabled(1)


      else:
        None
    else:
      if self.LocBox.count(
      ) != 0:  # statistical test boxes - add iterations and remove location / ele ID
        for i in range(0, int(self.LocBox.count())):
          self.LocBox.removeItem(0)
        for i in range(0, int(self.NucIDBox.count())):
          self.NucIDBox.removeItem(0)

        self.LocBox.setEnabled(0)
        self.mb2.ChangeActive(0)
        self.mb2.setEnabled(0)
        self.mb2.setTitle('')
        StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb2)


        #StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb3)
        if self.IterBox.text() == "":
          if self.NumToPlot.count() > 0:
            for i in range(0, self.NumToPlot.count()):
              self.NumToPlot.removeItem(0)
          self.NumToPlot.addItem('1 Iteration')
        elif int(self.IterBox.text()) <= 100:  #check options for iterations
          if self.NumToPlot.count() > 0:
            for i in range(0, self.NumToPlot.count()):
              self.NumToPlot.removeItem(0)

          self.NumToPlot.addItem('All Iterations (' + self.IterBox.text() + ')')
          self.NumToPlot.addItem('1 Random Iteration')
          self.NumToPlot.addItem('Average of All Iterations')
        else:
          for i in range(0, self.NumToPlot.count()):
            self.NumToPlot.removeItem(0)

          self.NumToPlot.addItem('15 Random Iterations')
          self.NumToPlot.addItem('1 Random Iteration')
          self.NumToPlot.addItem('Average of All Iterations')
        self.NumToPlot.setEnabled(1)
        self.mb4.ChangeActive(1)
        self.mb4.setEnabled(1)
        self.mb4.setTitle(GUIparams.labels["Box34L"])
        StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb4,isactive=1)
      else:
        #if not included then style will look weird when no changes
        #are made to the options, due to the style sheet change
        #at the top of this if block
        StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb2)
        #StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb3)

    #SEID contrib plot options, activate flex box
    #ends with used since element is prepended
    if self.metricBox.currentText().endswith(GUIparams.labels["Box46L"]) or self.metricBox.currentText().endswith(GUIparams.labels["Box47L"]) \
    or self.metricBox.currentText().endswith(GUIparams.labels["Box49L"]) or self.metricBox.currentText().endswith(GUIparams.labels["Box50L"]) :
      self.NucIDBox.clear()
      self.NucIDBox.addItem(GUIparams.labels["Box44L"])
      self.NucIDBox.addItem(GUIparams.labels["Box45L"])
      self.NucIDBox.addItem(GUIparams.labels["Box48L"])
      self.mb3.setTitle(GUIparams.labels["Box33Lb"])
      self.mb3.ChangeActive(1)
      self.mb3.setEnabled(1)
      StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb3,isactive=1)
      #HACK: overwrite previous code that adds items bc lazy and this
      #whole module needs a cleaner rewrite
      self.NumToPlot.setEnabled(0)
      self.NumToPlot.clear()
      self.mb4.ChangeActive(0)
      self.mb4.setEnabled(0)
      self.mb4.setTitle("")
      StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb4,isactive=0)
    else:
      self.mb3.setTitle("")
      self.mb3.ChangeActive(0)
      self.mb3.setEnabled(0)
      StyleOps.update_aniGBoxSmall_styleSheet(self.colordict,self.mb3,isactive=0)
      self.NucIDBox.clear()

def fontresize(self):
  matplotlib.rcParams.update({'font.size': self.currentFontSize-2})
  self.canvas.axes.tick_params(axis='both', which='major', labelsize=self.currentFontSize-2)
  self.canvas.axes.tick_params(axis='both', which='minor', labelsize=self.currentFontSize-2)
  self.canvas.axes.cla()
