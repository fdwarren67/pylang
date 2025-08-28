from typing import Tuple, List, TypedDict

class GeoJSONPoint(TypedDict):
    """A GeoJSON Point representing a single location as [x, y] or [x, y, z]."""
    type: str
    coordinates: Tuple[float, float]

class GeoJSONLineString(TypedDict):
    """A GeoJSON LineString representing a connected series of coordinates."""
    type: str
    coordinates: List[Tuple[float, float]]

class GeoJSONPolygon(TypedDict):
    """A GeoJSON Polygon representing a closed shape defined by one or more linear rings."""
    type: str
    coordinates: List[List[Tuple[float, float]]]
