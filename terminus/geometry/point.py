import shapely.geometry
from monkeypatch import monkeypatch_method

Point = shapely.geometry.Point


@monkeypatch_method(Point)
def __hash__(self):
    if self._ndim == 3:
        return hash((self.x, self.y, self.z))
    else:
        return hash((self.x, self.y))
