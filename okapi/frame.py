import itertools

from okapi.bezier import intersect


class Frame:
    def __init__(self):
        self.curves = []
        self.active = []

        # TODO: Handle fill.
        # TODO: Multiple layers.
        # TODO: Spatial partitioning.

    def deactivateAll(self):
        """
        Deactivate all selections and update the geometry accordingly.
        """

        # Find the t values where curves intersect.
        # FIXME: Handle self-intersections and overlaps.
        curvesInts = [[] for _ in self.curves]
        activeInts = [[] for _ in self.active]
        for i, curve in enumerate(self.curves):
            for j, active_ in enumerate(self.active):
                points = intersect(curve, active_)
                # TODO: Handle t values close together.
                curvesInts[i] += [curve.getT(p) for p in points]
                activeInts[j] += [active_.getT(p) for p in points]
        for i, j in itertools.combinations(range(len(self.active)), 2):
            points = intersect(self.active[i], self.active[j])
            activeInts[i] += [self.active[i].getT(p) for p in points]
            activeInts[j] += [self.active[j].getT(p) for p in points]

        # Split the curves appropriately.
        newCurves = []
        for curve, ints in zip(self.curves, curvesInts):
            newCurves += curve.split(ints)
        for curve, ints in zip(self.active, activeInts):
            newCurves += curve.split(ints)
        self.curves = newCurves
        self.active = []

