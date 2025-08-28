import json
from shapely.geometry import Polygon, LineString, mapping
import math

TARGET_ANGLES = {
    "north": 0,
    "northeast": 45,
    "east": 90,
    "southeast": 135,
    "south": 180,
    "southwest": 225,
    "west": 270,
    "northwest": 315,
}

def segment_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = math.degrees(math.atan2(dx, dy))  # 0°=north, clockwise
    return angle + 360 if angle < 0 else angle


def resolve_edge(block_geometry: dict, orientation: str):
    if isinstance(block_geometry, str):
        block_geometry = json.loads(block_geometry)
        
    poly = Polygon(block_geometry["coordinates"][0])

    coords = list(poly.exterior.coords)

    segments = []
    for i in range(len(coords) - 1):
        p1, p2 = coords[i], coords[i+1]
        angle = segment_angle(p1, p2)
        segments.append((LineString([p1, p2]), angle, p1, p2))

    target = TARGET_ANGLES[orientation.lower()]

    candidates = []
    for seg, ang, p1, p2 in segments:
        diff = min(abs(ang - target), 360 - abs(ang - target))  # circular difference
        candidates.append((diff, seg, p1, p2))

    candidates.sort(key=lambda x: x[0])
    best_diff = candidates[0][0]
    best_segs = [c for c in candidates if abs(c[0] - best_diff) < 1e-6]

    if orientation in ["north", "northeast", "northwest"]:
        best = max(best_segs, key=lambda c: max(c[2][1], c[3][1]))  # highest Y
    elif orientation in ["south", "southeast", "southwest"]:
        best = min(best_segs, key=lambda c: min(c[2][1], c[3][1]))  # lowest Y
    elif orientation == "east":
        best = max(best_segs, key=lambda c: max(c[2][0], c[3][0]))  # highest X
    elif orientation == "west":
        best = min(best_segs, key=lambda c: min(c[2][0], c[3][0]))  # lowest X
    else:
        raise ValueError(f"Unsupported orientation: {orientation}")

    return mapping(best[1])

