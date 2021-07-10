import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from geometry import Bezier

NUM_SEGMENTS = 1000
MAX_DISTANCE = 20


class Canvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # A bezier curve is defined by four control points.
        self.curve = Bezier((100, 100), (200, 100), (300, 100), (400, 100))

        # Keep track of the points on the curve we're following.
        self.t1 = None
        self.t2 = None
        self.q1 = None
        self.q2 = None

    def mousePressEvent(self, event):
        mousePos = np.array([event.localPos().x(), event.localPos().y()])
        if event.buttons() & QtCore.Qt.LeftButton:
            # Find the nearest point on the curve (within the threshold).
            minDist = MAX_DISTANCE
            for t in np.linspace(0, 1, NUM_SEGMENTS + 1):
                q = self.curve(t)
                d = np.hypot(*(q - mousePos))
                if d < minDist:
                    minDist = d
                    self.t1 = t
                    self.q1 = q

        # Choose another point on the curve.
        # TODO: This looks terrible for most values of t.
        if self.t1 is not None:
            if self.t1 < 0.5:
                self.t2 = (1 + self.t1) / 2
            else:
                self.t2 = self.t1 / 2
            self.q2 = self.curve(self.t2)

        self.repaint()

    def mouseReleaseEvent(self, event):
        self.t1 = None
        self.t2 = None
        self.q1 = None
        self.q2 = None

        self.repaint()

    def mouseMoveEvent(self, event):
        # NOTE: This requires mouse tracking switched off.

        if self.t1 is None:
            return

        r1 = np.array([event.localPos().x(), event.localPos().y()])
        r2 = self.q2 + (r1 - self.q1) / 2

        # TODO: This should update itself instead of creating a new curve.
        self.curve = Bezier.fromPoints(
            self.curve.p0, r1, r2, self.curve.p3, self.t1, self.t2
        )

        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.setPen(QtCore.Qt.red)
        path = QtGui.QPainterPath()
        path.moveTo(*self.curve.p0)
        path.cubicTo(*self.curve.p1, *self.curve.p2, *self.curve.p3)
        painter.drawPath(path)

        left, right = self.curve.split(0.3)
        offset = np.array([0, 0])

        painter.setPen(QtCore.Qt.blue)
        path = QtGui.QPainterPath()
        path.moveTo(*(left.p0 + offset))
        path.cubicTo(
            *(left.p1 + offset),
            *(left.p2 + offset),
            *(left.p3 + offset),
        )
        painter.drawPath(path)

        painter.setPen(QtCore.Qt.green)
        path = QtGui.QPainterPath()
        path.moveTo(*(right.p0 + offset))
        path.cubicTo(
            *(right.p1 + offset),
            *(right.p2 + offset),
            *(right.p3 + offset),
        )
        painter.drawPath(path)

