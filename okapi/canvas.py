import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from okapi.frame import Frame
from okapi.tools.line import Line
from okapi.ui import parseModifiers


class Canvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.frame = Frame()
        self.line = Line(self.frame)

        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        mousePos = np.array([event.localPos().x(), event.localPos().y()])
        modifiers = parseModifiers(event.modifiers())
        self.line.onMousePress(mousePos, modifiers)

        self.repaint()

    def mouseReleaseEvent(self, event):
        mousePos = np.array([event.localPos().x(), event.localPos().y()])
        modifiers = parseModifiers(event.modifiers())
        self.line.onMouseRelease(mousePos, modifiers)

        self.repaint()

    def mouseMoveEvent(self, event):
        mousePos = np.array([event.localPos().x(), event.localPos().y()])
        modifiers = parseModifiers(event.modifiers())
        self.line.onMouseMove(mousePos, modifiers)

        # FIXME: Only repaint when something happens.
        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        for i, curve in enumerate(self.frame.curves):
            if curve in self.frame.active:
                continue
            colors = [
                QtCore.Qt.red,
                QtCore.Qt.magenta,
                QtCore.Qt.blue,
                QtCore.Qt.cyan,
                QtCore.Qt.green,
                QtCore.Qt.yellow,
            ]
            painter.setPen(colors[i % 6])
            path = QtGui.QPainterPath()
            path.moveTo(*curve.p0)
            path.cubicTo(*curve.p1, *curve.p2, *curve.p3)
            painter.drawPath(path)

        for curve in self.frame.active:
            painter.setPen(QtCore.Qt.black)
            path = QtGui.QPainterPath()
            path.moveTo(*curve.p0)
            path.cubicTo(*curve.p1, *curve.p2, *curve.p3)
            painter.drawPath(path)

