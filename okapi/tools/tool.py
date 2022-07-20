from okapi.bezier import Point
from okapi.frame import Frame
from okapi.ui import Modifiers


class Tool:
    # TODO: Figure out the right input.
    def __init__(self, frame: Frame):
        self.frame = frame

    def onMousePress(self, point: Point, modifiers: Modifiers):
        pass

    def onMouseRelease(self, point: Point, modifiers: Modifiers):
        pass

    def onMouseMove(self, point: Point, modifiers: Modifiers):
        pass

    # FIXME: Handle these events:
    #   Mouse double click
    #   Key press
    #   Key release
    #   Wheel events (Does any tool need these?)
    #   Keypress
