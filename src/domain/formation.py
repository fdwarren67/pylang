from pydantic import BaseModel, Field
from uuid import UUID

class Formation(BaseModel):
    """
    A Formation is a geologic reservoir target that laterals are drilled into.
    Defined by its name and vertical boundaries relative to sea level.
    """
    
    formation_guid: UUID = Field(..., description="GUID that uniquely identifies the formation.")
    name: str = Field(..., description="Name of the geologic formation (e.g., 'Wolfcamp A', 'Eagle Ford').")
    top_sstvd: float = Field(..., description="Top depth of the formation relative to sea level (ft).")
    base_sstvd: float = Field(..., description="Base depth of the formation relative to sea level (ft).")
