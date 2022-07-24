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

        # FIXME: Handle intersections and self-intersections.
        self.curves += self.active
        self.active = []

