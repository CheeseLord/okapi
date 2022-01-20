from okapi.bezier import Point
from okapi.frame import Frame


class Tool:
    # TODO: Figure out the right input.
    def __init__(self, frame: Frame):
        self.frame = frame

    # TODO: Figure out the right events.
    def onPress(self, point: Point):
        pass

    def onRelease(self, point: Point):
        pass

