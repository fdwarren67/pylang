from dotenv import load_dotenv
load_dotenv()

from calcs import resolve_edge

from typing import Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_openai import ChatOpenAI
from uuid import UUID

from pydantic import BaseModel
# from domain.intent import CreateLateralIntent, Point
from domain.block import Block
from domain.lateral import Lateral


class State(BaseModel):
    user_input: str
    block_context: dict
    # intent: Optional[CreateLateralIntent] = None


schemas = {
    "Block": Block.model_json_schema(),
    "Lateral": Lateral.model_json_schema()
}

schema_text = "\n\n".join(
    [f"### {name} Schema\n{schema}" for name, schema in schemas.items()]
)


parser = PydanticOutputParser(pydantic_object=CreateLateralIntent)

prompt = ChatPromptTemplate.from_template(
    """
    You are an assistant that converts user requests into block references.

    Schema:
    {format_instructions}

    - Normalize edge references to one of: 
      north, northeast, east, southeast, south, southwest, west, northwest.
    - Always set relation = "edge".

    User input: {user_input}
    """
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
translator_chain = prompt | llm | parser
    
def identify_edge_node(state: State):
    # Step 1. Normalize user input → BlockReference
    ref = translator_chain.invoke({
        "user_input": state.user_input,
        "format_instructions": parser.get_format_instructions()
    })
    
    # Step 2. Resolve actual edge geometry
    edge_geom = resolve_edge(state.block_context, ref.orientation)
    
    # Pick a reference point (e.g., midpoint of the edge)
    from shapely.geometry import shape
    edge_line = shape(edge_geom)
    midpoint = edge_line.interpolate(0.5, normalized=True)
    
    return {
        "reference": ref,
        "edge": edge_geom,
        "edge_midpoint": (midpoint.x, midpoint.y)
    }

# def create_lateral_intent_node(state: State):
#     # Build intent using the reference point found by edge detector
#     intent = CreateLateralIntent(
#         # block_guid=state["block_guid"],
#         points=[
#             Point(coordinates=state.edge_midpoint, point_type="reference")
#         ],
#         azimuth=state.azimuth,
#         length=state.length
#     )
#     return {"lateral_intent": intent}


graph = StateGraph(State)
graph.add_node("identify_edge", identify_edge_node)
# graph.add_node("create_lateral_intent", create_lateral_intent_node)

graph.set_entry_point("identify_edge")
# graph.add_edge("identify_edge", "create_lateral_intent")
graph.add_edge("identify_edge", END)

# graph.add_edge("create_lateral_intent", END)

app = graph.compile()

def main():
    block = Block(
        # block_guid="550e8400-e29b-41d4-a716-446655440000",
        name="North Unit 12",
        geometry={"type": "Polygon", "coordinates": [[[
          1303855.8553287212,
          496081.36024564353
        ],
        [
          1302546.52437828,
          501372.4894525196
        ],
        [
          1305950.7211166995,
          502214.8843320876
        ],
        [
          1307260.0520671408,
          496923.7551252115
        ],
        [
          1303855.8553287212,
          496081.36024564353
        ]]]},
        azimuth=166.101,
        epsg_code=32039,
        epsg_name="NAD27 / Texas Central",
        total_acreage=640,
        block_formations=[]
    )

    result = app.invoke({
        "user_input": "Draw a lateral along the northern boundary.",
        "block_context": block.model_dump()
    })

    print(result["intent"].model_dump_json(indent=2))


if __name__ == "__main__":
    main()