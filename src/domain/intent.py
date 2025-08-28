from pydantic import BaseModel, Field
from typing import Optional, Tuple, List, Literal
from uuid import UUID

class Point(BaseModel):
    """
    A point associated with a lateral.
    """
    coordinates: Tuple[float, float] = Field(
        ..., description="Coordinates of the point [x, y]."
    )
    point_type: Literal["anchor_point", "end_point", "reference"] = Field(
        ..., description=(
            "Role of the point in the lateral. "
            "'anchor_point' = starting location of the lateral, "
            "'end_point' = ending location of the lateral, "
            "'reference' = any arbitrary point along the lateral."
        )
    )

class CreateLateralIntent(BaseModel):
    """
    User intent to create a lateral in relation to a block.
    Valid inputs:
    - Two points (anchor + end), OR
    - One point (anchor/end/reference) + azimuth + length, OR
    - One point (anchor/end/reference) + azimuth + no length (max length in block).
    """
    action: Literal["create"] = "create"
    # block_guid: UUID = Field(..., description="The block in which the lateral will be created.")

    points: List[Point] = Field(
        default_factory=list,
        description="List of points defining the lateral (anchor, end, or reference)."
    )

    azimuth: Optional[float] = Field(
        None, description="Azimuth (degrees, 0°=north, clockwise)."
    )
    length: Optional[float] = Field(
        None, description="Planned lateral length in feet. If omitted and only one point is given, assume max length."
    )
