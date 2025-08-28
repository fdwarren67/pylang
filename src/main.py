from dotenv import load_dotenv
load_dotenv()

from typing import Optional, Tuple
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_openai import ChatOpenAI
from uuid import UUID

from pydantic import BaseModel
from domain.block import Block
from domain.lateral import Lateral
from identify_edge import IdentifyEdgeTool

class State(BaseModel):
    user_input: str
    block_context: dict
    block_guid: Optional[UUID] = None
    azimuth: Optional[float] = None
    length: Optional[float] = None
    reference: Optional[dict] = None
    edge: Optional[dict] = None
    edge_midpoint: Optional[Tuple[float, float]] = None
    # intent: Optional[CreateLateralIntent] = None

graph = StateGraph(State)

def identify_edge_node(state: State):
    output = IdentifyEdgeTool.invoke({
        "user_input": state.user_input,
        "block_geometry": state.block_context["geometry"]
    })
    return {
        "reference": output["reference"],
        "edge": output["edge"],
        "edge_midpoint": output["edge_midpoint"]
    }


graph.add_node("identify_edge", identify_edge_node)
graph.set_entry_point("identify_edge")
graph.add_edge("identify_edge", END)

app = graph.compile()


def main():
    block = Block(
        # block_guid="550e8400-e29b-41d4-a716-446655440000",
        name="North Unit 12",
        geometry={"type": "Polygon", "coordinates": [[
            [
          1302884.0727000097,
          495868.2017720627
        ],
        [
          1302477.476373858,
          501620.4734356067
        ],
        [
          1306295.3290577002,
          501890.3363638263
        ],
        [
          1306701.9253838519,
          496138.06470028235
        ],
        [
          1302884.0727000097,
          495868.2017720627
        ]
        ]]},
        azimuth=166.101,
        epsg_code=32039,
        epsg_name="NAD27 / Texas Central",
        total_acreage=640,
        block_formations=[]
    )

    result = app.invoke({
        "user_input": "Create three wellbores just north of the lower left lease line.",
        "block_context": block.model_dump(),
        "block_guid": UUID("550e8400-e29b-41d4-a716-446655440000"),
        # "azimuth": block.azimuth,
        # "length": 3000
    })

    print("\n-----------------")
    print(result["user_input"])
    print(result["reference"])
    
    lst = [list(x) for x in result["edge"]["coordinates"]]

    print(lst)


if __name__ == "__main__":
    main()