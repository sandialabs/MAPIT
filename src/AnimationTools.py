"""
    Code containing functions to run MAPIT's
    animations.
"""

from PySide2 import QtCore, QtWidgets, QtGui

#All of these animations and stylesheets
#do have subtle differences if you can
#believe it


def runAnimationSB(self):
  """
        Main animation function that changes
        the border between light and dark.
  """

  qss = "QWidget#{VAL}".format(VAL=self.Loc) + "{"
  value = self._animation.currentValue()

  #dark bright dark
  if value > 1:
    valueA = 2.0 - value
  else:
    valueA = value

  if ((self._animation.loopCount() - 1)
      == self._animation.currentLoop()) and value > 1:
    if value > 1:
      valueA = value - 1

      if self.window().MakeLight.isChecked() == 1:
        R = 0 + (153 - 0) * valueA
        R2 = 173 + (200 - 173) * valueA
        R3 = 208 + (221 - 208) * valueA
      else:
        R = 51 - (51 - 0) * valueA
        R2 = 145 - (145 - 83) * valueA
        R3 = 186 - (186 - 118) * valueA
    else:
      if self.window().MakeLight.isChecked() == 1:
        R = 211 - (211 - 0) * valueA
        R2 = 211 - (211 - 173) * valueA
        R3 = 211 - (211 - 208) * valueA
      else:
        R = 66 - (66 - 51) * valueA
        R2 = 66 + (145 - 66) * valueA
        R3 = 66 + (186 - 66) * valueA

  else:
    if self.window().MakeLight.isChecked() == 1:
      R = 211 - (211 - 0) * valueA
      R2 = 211 - (211 - 173) * valueA
      R3 = 211 - (211 - 208) * valueA
    else:
      R = 66 - (66 - 51) * valueA
      R2 = 66 + (145 - 66) * valueA
      R3 = 66 + (186 - 66) * valueA




  grad = "border-color: rgb({value},{value2},{value3});".format(value=int(R),value2=int(R2),value3=int(R3)) +\
         "border-width: 5px;" +\
         "border-style: solid;" +\
         "padding: 6px;" +\
         "color: black;" +\
         "border-radius: 3px;}"

  if self.window().MakeLight.isChecked() == 0:
    grad = grad.replace('black', 'white')
  qss += grad

  qss2 = "QWidget#{VAL}".format(
      VAL=self.Loc
  ) + ":title{subcontrol-origin:margin;padding:-6px 0px 0px 0px}"

  qss += qss2

  self.setStyleSheet(qss)


def runDualAnimation(self):
  """
        Two animations can be running at the same time
        the border (_animate) and the gradient change
        due to mouse interaction (_animate2).
        Need to get the status of (_animate2) so the
        border animation and mouse interaction both run
        together, if applicable.
  """

  #value of the linear gradient animation
  #(i.e. button color)
  value = self._animation.currentValue()
  R4 = self._animation2.currentValue()

  if self.window().MakeLight.isChecked() == 1:
    self.color2 = QtGui.QColor(247, 247, 247)
    self.color1 = QtGui.QColor(153, 200, 221)
  else:
    self.color2 = QtGui.QColor(66, 66, 66)
    self.color1 = QtGui.QColor(51, 145, 186)

  qss = "QWidget#{VAL}".format(VAL=self.Loc) + "{"

  if value > 1:
    valueA = 2.0 - value
  else:
    valueA = value

  if ((self._animation.loopCount() - 1)
      == self._animation.currentLoop()) and value > 1:
    if value > 1:
      valueA = value - 1

      if self.window().MakeLight.isChecked() == 1:
        R = 0 + (153 - 0) * valueA
        R2 = 173 + (200 - 173) * valueA
        R3 = 208 + (221 - 208) * valueA
      else:
        R = 51 - (51 - 0) * valueA
        R2 = 145 - (145 - 83) * valueA
        R3 = 186 - (186 - 118) * valueA
    else:
      if self.window().MakeLight.isChecked() == 1:
        R = 211 - (211 - 0) * valueA
        R2 = 211 - (211 - 173) * valueA
        R3 = 211 - (211 - 208) * valueA
      else:
        R = 66 - (66 - 51) * valueA
        R2 = 66 + (145 - 66) * valueA
        R3 = 66 + (186 - 66) * valueA

  else:
    if self.window().MakeLight.isChecked() == 1:
      R =  211 - (211 - 0) * valueA
      R2 = 211 - (211 - 173) * valueA
      R3 = 211 - (211 - 208) * valueA
    else:
      R =  66 - (66 - 51) * valueA
      R2 = 66 + (145 - 66) * valueA
      R3 = 66 + (186 - 66) * valueA

  #border
  grad = "border-color: rgb({value},{value2},{value3});".format(value=int(R),value2=int(R2),value3=int(R3)) +\
         "border-width: 2px;" +\
         "border-style: solid;" +\
         "padding: 6px;" +\
         "border-radius: 3px;" +\
         "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:5, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});".format(color1=self.color1.name(), color2=self.color2.name(), value=R4) +\
          "}"

  qss += grad

  if self.IsDone == 1:
    if self.window().MakeLight.isChecked() == 0:
      qss = qss.replace('rgb(153,200,221)', 'rgb(0,83,118)')
    else:
      qss = qss.replace('rgb(0,173,208)', 'rgb(153,200,221)')

  self.setStyleSheet(qss)


def GradButtonChange(self):

  value = self._animation2.currentValue()
  if self.window().MakeLight.isChecked() == 1:
    self.color2 = QtGui.QColor(247, 247, 247)
    self.color1 = QtGui.QColor(153, 200, 221)
  else:
    self.color2 = QtGui.QColor(66, 66, 66)
    self.color1 = QtGui.QColor(51, 145, 186)

  if self.IsDone == 1:
    #if the border animation is done
    #then only change the background color

    qss = "QWidget#{VAL}".format(VAL=self.Loc) + "{"
    qss +=  "border-width: 2px;" +\
           "border-color: rgb(153,200,221);" +\
           "border-style: solid;" +\
           "padding: 6px;" +\
           "border-radius: 3px;"
    grad = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:5, y2:0, stop:0 {color1}, stop:{value} {color2}, stop: 1.0 {color1});".format(
        color1=self.color1.name(), color2=self.color2.name(), value=value)
    qss += grad
    qss += "}"

    if self.window().MakeLight.isChecked() == 0:
      qss = qss.replace('rgb(153,200,221)', 'rgb(0,83,118)')

    self.setStyleSheet(qss)


def runMsgAnimation(self):
  value = self._animation.currentValue()
  qss = """
            :disabled{color: rgb(0,0,0);
  """

  if value > 1:
    valueA = 2.0 - value
  else:
    valueA = value

  if ((self._animation.loopCount() - 1)
      == self._animation.currentLoop()) and value > 1:
    if value > 1:
      valueA = value - 1

      if self.window().MakeLight.isChecked() == 1:
        R = 0 + (153 - 0) * valueA
        R2 = 173 + (200 - 173) * valueA
        R3 = 208 + (221 - 208) * valueA
      else:
        R = 51 - (51 - 0) * valueA
        R2 = 145 - (145 - 83) * valueA
        R3 = 186 - (186 - 118) * valueA
    else:
      if self.window().MakeLight.isChecked() == 1:
        R = 211 - (211 - 0) * valueA
        R2 = 211 - (211 - 173) * valueA
        R3 = 211 - (211 - 208) * valueA
      else:
        R = 66 - (66 - 51) * valueA
        R2 = 66 + (145 - 66) * valueA
        R3 = 66 + (186 - 66) * valueA

  else:
    if self.window().MakeLight.isChecked() == 1:
      R = 211 - (211 - 0) * valueA
      R2 = 211 - (211 - 173) * valueA
      R3 = 211 - (211 - 208) * valueA
    else:
      R = 66 - (66 - 51) * valueA
      R2 = 66 + (145 - 66) * valueA
      R3 = 66 + (186 - 66) * valueA


  grad = "border-color: rgb({value},{value2},{value3});".format(value=int(R),value2=int(R2),value3=int(R3)) +\
         "border-width: 5px;" +\
         "border-style: solid;" +\
         "padding: 6px;" +\
         "border-radius: 3px;"

  qss += grad

  if self.window().MakeLight.isChecked() == 1:
    qss += 'background-color: rgb(239,239,239);color: black;}'
  else:
    qss += 'background-color: rgb(52,52,52);color: white;}'

  self.setStyleSheet(qss)


def runAnimation(self):
  qss = "QWidget#{VAL}".format(VAL=self.Loc) + "{"
  value = self._animation.currentValue()

  if value > 1:
    valueA = 2.0 - value
  else:
    valueA = value

  if self.window().MakeLight.isChecked() == 1:

    #dark bright dark
    R = 153 - (153 - 0) * valueA
    R2 = 200 - (200 - 173) * valueA
    R3 = 221 - (221 - 208) * valueA

  else:
    #dark bright dark
    #0, 83, 118
    #51, 92, 122
    R = 0 + (51 - 0) * valueA
    R2 = 83 + (145 - 83) * valueA
    R3 = 118 + (186 - 118) * valueA

  #whole button
  #grad = "background-color: rgba({value2},{value3},{value},1.0);".format(value=R,value2=R2,value3=R3) + "}"

  #border
  grad = "border-color: rgb({value},{value2},{value3});".format(value=int(R),value2=int(R2),value3=int(R3)) +\
         "border-width: 2px;" +\
         "border-style: solid;" +\
         "padding: 0px;" +\
         "border-radius: 3px;" +\
         "margin-top: 10px;" +\
         "background-color: rgb(239,239,239);" +\
          "}"

  #print(grad)

  qss += grad

  grad = "QWidget#{VAL}".format(VAL=self.Loc) +\
          ":title{subcontrol-origin:margin;padding: -6px 0px 0px 0px}"

  qss += grad

  if self.window().MakeLight.isChecked() == 0:
    qss = qss.replace('rgb(239,239,239)', 'rgb(52,52,52)')

  self.setStyleSheet(qss)
