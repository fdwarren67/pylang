from pydantic import BaseModel, Field, conint
from typing import List, Literal, Optional
from uuid import UUID
from .types import GeoJSONPolygon
from .lateral import Lateral

class BlockReference(BaseModel):
    """
    A normalized description of a block feature the user referenced.
    """
    relation: Literal["edge"] = Field(..., description="Currently only edges are supported.")
    orientation: Literal[
        "north", "northeast", "east", "southeast",
        "south", "southwest", "west", "northwest"
    ] = Field(..., description="Cardinal orientation of the edge.")


class BlockFormation(BaseModel):
    """
    A BlockFormation links a Block to a specific Formation, 
    with associated regulatory rules and planned laterals.
    """

    # block_formation_guid: UUID = Field(..., description="GUID that uniquely identifies the block–formation relationship.")
    # formation_guid: UUID = Field(..., description="GUID referencing the formation developed in this block.")
    regulatory_field_guid: UUID = Field(..., description="GUID referencing the regulatory field that governs this block–formation.")
    
    drillable_area: Optional[GeoJSONPolygon] = Field(
        None, description="Drillable area polygon after applying regulatory rules (GeoJSON)."
    )
    laterals: List[Lateral] = Field(
        default_factory=list, description="List of laterals within this block–formation."
    )

class Block(BaseModel):
    """
    A Block is a legally defined parcel of land for oil and gas development.
    It contains a boundary polygon, regulatory context, and multiple formations
    that may host laterals.
    """
     
    # block_guid: UUID = Field(..., description="GUID that uniquely identifies the block.")
    name: Optional[str] = Field(None, description="Optional human-readable block name or label.")

    geometry: GeoJSONPolygon = Field(..., description="Block boundary as a GeoJSON Polygon (coordinates in EPSG projection).")
    azimuth: float = Field(
        ..., description="Default azimuth in degrees (0°=north, clockwise, range 0–359)."
    )

    epsg_code: int = Field(..., description="EPSG code (integer) defining the projected coordinate system (e.g., 32038).")
    epsg_name: str = Field(..., description="Human-readable name of the EPSG projection (e.g., 'NAD27 / Texas North Central').")

    total_acreage: Optional[float] = Field(
        None, description="Total surface acreage of the block (acres)."
    )

    block_formations: List[BlockFormation] = Field(
        default_factory=list, description="Block–formation combinations regulated and developed within this block."
    )
