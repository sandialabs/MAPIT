from PySide6 import QtWidgets, QtCore
from MAPIT.GUI import AnimationTools


class AniButton(QtWidgets.QPushButton):
  """
        Class for animated buttons.

        These buttons animate when first active.

        They also have a linear gradient of color
        that changes once the mouse enters the area.
  """

  def __init__(self, parent, extra_space=0):
    super(AniButton, self).__init__()

    self.IsDone = 0

    #set animation parameters
    self._animation = QtCore.QVariantAnimation()
    self._animation.setStartValue(0.0)
    self._animation.setEndValue(2.0)
    self._animation.setDuration(1000)
    self._animation.valueChanged.connect(
        lambda: AnimationTools.runDualAnimation(self, extraspace=extra_space))

    self._animation.finished.connect(self.UpdateIState)
    self._animation.setLoopCount(3)

    self._animation2 = QtCore.QVariantAnimation()
    self._animation2.setStartValue(0.0)
    self._animation2.setEndValue(1.0)
    self._animation2.setDuration(150)
    self._animation2.valueChanged.connect(
        lambda: AnimationTools.GradButtonChange(self, extraspace=extra_space))

    self.doGradientAni = 1

  def UpdateIState(self):
    #check if the initial border animation
    #has finished
    self.IsDone = 1

  def enterEvent(self, event):
    if self.doGradientAni == 1:
      self._animation2.setDirection(QtCore.QAbstractAnimation.Forward)
      self._animation2.start()

      super().enterEvent(event)

  def leaveEvent(self, event):

    if self.doGradientAni == 1:
      self._animation2.setDirection(QtCore.QAbstractAnimation.Backward)
      self._animation2.start()

      super().leaveEvent(event)


class SubBoxAni(QtWidgets.QGroupBox):
  """
        This class defines animated boxes
        within MAPIT. Specifically, the
        boxes that contain dropdown elements
        in the plot area.

        Animation functions largely control
        changing border colors to bring
        attention to certain areas of MAPIT.

        A second animation has the border react
        when the mouse enters the area.
  """

  def __init__(self, parent):
    super(SubBoxAni, self).__init__()

    #note there animation values (start,end)
    #are required to be floats for some reason

    self._animation = QtCore.QVariantAnimation()
    self._animation.setStartValue(0.0)
    self._animation.setEndValue(1.0)
    self._animation.setDuration(150)
    self._animation.setLoopCount(1)
    self._animation.valueChanged.connect(
        lambda: AnimationTools.runAnimation(self))

    self.IsActive = 0


  def enterEvent(self, event):
    #on enter make border lighter
    if self.IsActive == 1:
      self._animation.setDirection(QtCore.QAbstractAnimation.Forward)
      self._animation.start()
    super().enterEvent(event)

  def leaveEvent(self, event):
    #on leave make border darker
    if self.IsActive == 1:
      self._animation.setDirection(QtCore.QAbstractAnimation.Backward)
      self._animation.start()
    super().leaveEvent(event)

  def ChangeActive(self, newState):
    self.IsActive = newState


class AniGBox(QtWidgets.QGroupBox):
  """
        Box containing multiple items that
        animates to bring attention. These
        are the larger 'containers' like
        the area that says 'plot controls'
  """

  def __init__(self, parent=None):
    super().__init__(parent)

    self._animation = QtCore.QVariantAnimation()
    self._animation.setStartValue(0.0)
    self._animation.setEndValue(2.0)
    self._animation.setDuration(1000)
    self._animation.valueChanged.connect(
        lambda: AnimationTools.runAnimationSB(self))

    self._animation.setLoopCount(3)
    self.colorBorder = 0

    #self.objectName() = 0



