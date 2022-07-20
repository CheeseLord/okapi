from collections import namedtuple
from PyQt5 import QtCore


Modifiers = namedtuple('Modifiers', ['ctrl', 'shift', 'alt'])


def parseModifiers(modifiers: int) -> Modifiers:
    ctrl = bool(modifiers & QtCore.Qt.ControlModifier)
    shift = bool(modifiers & QtCore.Qt.ShiftModifier)
    alt = bool(modifiers & QtCore.Qt.AltModifier)

    return Modifiers(ctrl, shift, alt)

