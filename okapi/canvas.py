import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from okapi.frame import Frame
from okapi.tools.line import Line


class Canvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.frame = Frame()
        self.line = Line(self.frame)

    def mousePressEvent(self, event):
        mousePos = np.array([event.localPos().x(), event.localPos().y()])
        self.line.onClick(mousePos)

        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        for curve in self.frame.curves:
            painter.setPen(QtCore.Qt.red)
            path = QtGui.QPainterPath()
            path.moveTo(*curve.p0)
            path.cubicTo(*curve.p1, *curve.p2, *curve.p3)
            painter.drawPath(path)

