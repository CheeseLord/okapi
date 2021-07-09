import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets


NUM_SEGMENTS = 1000
MAX_DISTANCE = 20


class Canvas(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # A bezier curve is defined by endpoints (p0, p3) and control points
        # (q1, q2).
        self.p0 = np.array([100, 100])
        self.q1 = np.array([200, 100])
        self.q2 = np.array([300, 100])
        self.p3 = np.array([400, 100])

        # Keep track of the points on the curve we're following.
        self.t1 = None
        self.t2 = None
        self.p1 = None
        self.p2 = None

    def mousePressEvent(self, event):
        mousePos = np.array([event.localPos().x(), event.localPos().y()])
        if event.buttons() & QtCore.Qt.LeftButton:
            # Find the nearest point on the cuve (within the threshold).
            minDist = MAX_DISTANCE
            for t in np.linspace(0, 1, NUM_SEGMENTS + 1):
                p = sum([
                    (1 - t) ** 3 * self.p0,
                    3 * t * (1 - t) ** 2 * self.q1,
                    3 * t ** 2 * (1 - t) * self.q2,
                    t ** 3 * self.p3,
                ])
                d = np.hypot(*(p - mousePos))
                if d < minDist:
                    minDist = d
                    self.t1 = t
                    self.p1 = p

        # Choose another point on the curve.
        # TODO: This looks terrible for most values of t.
        if self.t1 is not None:
            if self.t1 < 0.5:
                self.t2 = (1 + self.t1) / 2
            else:
                self.t2 = self.t1 / 2
            self.p2 = sum([
                (1 - self.t2) ** 3 * self.p0,
                3 * self.t2 * (1 - self.t2) ** 2 * self.q1,
                3 * self.t2 ** 2 * (1 - self.t2) * self.q2,
                self.t2 ** 3 * self.p3,
            ])

        self.repaint()

    def mouseReleaseEvent(self, event):
        self.t1 = None
        self.t2 = None
        self.p1 = None
        self.p2 = None

        self.repaint()

    def mouseMoveEvent(self, event):
        # NOTE: This requires mouse tracking switched off.

        if self.t1 is None:
            return

        r1 = np.array([event.localPos().x(), event.localPos().y()])
        r2 = self.p2 + (r1 - self.p1) / 2

        # Find the control points to make the curve pass through the target
        # points.
        self.q1 = (
            r1 - (1 - self.t1) ** 3 * self.p0 - self.t1 ** 3 * self.p3
        ) * self.t2 ** 2 * (1 - self.t2)
        self.q1 -= (
            r2 - (1 - self.t2) ** 3 * self.p0 - self.t2 ** 3 * self.p3
        ) * self.t1 ** 2 * (1 - self.t1)
        self.q1 /= (
            3 * self.t1 * (1 - self.t1) ** 2 * self.t2 ** 2 * (1 - self.t2)
            - 3 * self.t2 * (1 - self.t2) ** 2 * self.t1 ** 2 * (1 - self.t1)
        )

        self.q2 = (
            r1 - (1 - self.t1) ** 3 * self.p0 - self.t1 ** 3 * self.p3
            - 3 * self.t1 * (1 - self.t1) ** 2 * self.q1
        )
        self.q2 /= 3 * self.t1 ** 2 * (1 - self.t1)

        self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.red)
        path = QtGui.QPainterPath()
        path.moveTo(*self.p0)
        path.cubicTo(*self.q1, *self.q2, *self.p3)
        painter.drawPath(path)

