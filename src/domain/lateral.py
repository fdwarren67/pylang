from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from .types import GeoJSONPoint, GeoJSONLineString

class Lateral(BaseModel):
    """
    A Lateral represents the horizontal portion of a wellbore 
    planned within a block. It is defined by an anchor point, end point (also known as first and last take points), 
    an azimuth, and a length.
    """

    lateral_guid: UUID = Field(..., description="GUID that uniquely identifies the lateral.")
    
    anchor_point: GeoJSONPoint = Field(..., description="Anchor Point (or First Take Point) as a GeoJSON Point.")

    end_point: GeoJSONPoint = Field(..., description="End Point (or Last Take Point) as a GeoJSON Point.")
    
    # formation_guid: UUID = Field(..., description="GUID referencing the formation targeted by this lateral.")
    
    azimuth: Optional[float] = Field(
        None, description="Azimuth (degrees, 0°=north, clockwise) of the lateral orientation."
    )

    length: Optional[float] = Field(
        None, description="Planned lateral length in feet."
    )

    geometry: GeoJSONLineString = Field(..., description="Lateral geometry as a GeoJSON LineString.")
