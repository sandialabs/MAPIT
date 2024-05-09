"""
    Code containing functions to run MAPIT's
    animations.
"""

from PySide6 import QtCore, QtWidgets, QtGui
from MAPIT.GUI import StyleOps

#All of these animations and stylesheets
#do have subtle differences if you can
#believe it


def runAnimationSB(self):
  """
        Main animation function that changes
        the border between light and dark.
  """


  value = self._animation.currentValue()

  if value > 1:
    valueA = 2.0 - value
  else:
    valueA = value

  if ((self._animation.loopCount()-1) == self._animation.currentLoop()) and value > 1:
    if value > 1:
      valueA = 1 - (value-1)



  StyleOps.update_aniGBoxLarge_styleSheet(self.window().colordict,self,isactive=1,valueA=valueA)



def runDualAnimation(self, extraspace):
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

  if value > 1:
    valueA = 2.0 - value
  else:
    valueA = value

  if ((self._animation.loopCount()-1) == self._animation.currentLoop()) and value > 1:
    if value > 1:
      valueA = 1 - (value-1)


  StyleOps.update_aniButton_styleSheet(self,self.window().colordict,isrunning=1,valueA=R4,valueB=valueA,colorborder=1, extraspace=extraspace)



def GradButtonChange(self, extraspace=0):

  value = self._animation2.currentValue()

  StyleOps.update_aniButton_styleSheet(self,self.window().colordict,isrunning=1,valueA=value,colorborder=1, extraspace=extraspace)


def runMsgAnimation(self):
  value = self._animation.currentValue()
  qss = """
            :disabled{color: rgb(0,0,0);
  """

  if value > 1:
    valueA = 2.0 - value
  else:
    valueA = value

  if ((self._animation.loopCount()-1) == self._animation.currentLoop()) and value > 1:
    if value > 1:
      valueA = 1 - (value-1)

  StyleOps.update_messageBox_styleSheet(self,self.window().colordict,valueA=valueA)




def runAnimation(self):


  value = self._animation.currentValue()

  if value > 1:
    valueA = 2.0 - value
  else:
    valueA = value

  StyleOps.update_aniGBoxSmall_styleSheet(self.window().colordict,self,isactive=1,valueA=valueA)
