# identify_edge.py
from pydantic import BaseModel, Field
from typing import Literal, Optional, Tuple
from shapely.geometry import shape, Polygon, LineString, mapping
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
import json, math

from domain.block import BlockReference

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
        angle = segment_angle(p1, p2) - 90
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


parser = PydanticOutputParser(pydantic_object=BlockReference)

prompt = ChatPromptTemplate.from_template(
    """
    You are an assistant that determines user intent by converting oil and gas lease language into compass directions.

    Schema:
    {format_instructions}

    - Normalize user instructions to one of:
      north, northeast, east, southeast, south, southwest, west, northwest.
    - Always set relation = "edge".

    Example:

    User input: "south of the northern boundary"  
    Reasoning: The intended boundary is north. The expression "south of" indicates a location relative to that boundary, but the boundary itself is still the northern edge of the block.
    Output: {{ "relation": "edge", "orientation": "north" }}
    
    User input: {user_input}
    """
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
translator_chain = prompt | llm | parser

# ---- Node ----

class IdentifyEdgeInput(BaseModel):
    user_input: str = Field(..., description="Natural language reference to an edge (e.g., 'north lease line').")
    block_geometry: dict = Field(..., description="Block polygon in GeoJSON format.")

# --- Tool function ---
def identify_edge_tool_func(user_input: str, block_geometry: dict):
    ref = translator_chain.invoke({
        "user_input": user_input,
        "format_instructions": parser.get_format_instructions()
    })

    edge_geom = resolve_edge(block_geometry, ref.orientation)

    edge_line = shape(edge_geom)
    midpoint = edge_line.interpolate(0.5, normalized=True)

    return {
        "reference": ref.model_dump(),
        "edge": edge_geom,
        "edge_midpoint": [midpoint.x, midpoint.y]
    }

# --- Tool wrapper ---
IdentifyEdgeTool = StructuredTool.from_function(
    func=identify_edge_tool_func,
    name="IdentifyEdge",
    description="Identify which edge of a block a user refers to and return the edge geometry.",
    args_schema=IdentifyEdgeInput
)