from pydantic import BaseModel, Field
from typing import Dict, Optional
from uuid import UUID

class RegulatoryField(BaseModel):
    """
    A RegulatoryField defines regulatory spacing and setback rules 
    that govern drilling and completion activity within a formation.
    """
    
    regulatory_field_guid: UUID = Field(..., description="GUID that uniquely identifies the regulatory field.")
    name: str = Field(..., description="Name of the regulatory field as defined by the regulator (e.g., 'Barnett Shale Gas Field').")

    lease_line_setback: Optional[float] = Field(
        None, description="Minimum perpendicular setback distance (ft) from a lateral to the lease boundary."
    )
    take_point_setback: Optional[float] = Field(
        None, description="Minimum parallel setback distance (ft) from the first/last take point to the lease boundary."
    )
    well_spacing: Optional[float] = Field(
        None, description="Minimum spacing (ft) required between adjacent laterals within the same formation."
    )
    max_density: Optional[float] = Field(
        None, description="Maximum well density allowed (e.g., wells per section or per acre)."
    )
    other: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Additional regulatory rules or exceptions (key-value pairs)."
    )
