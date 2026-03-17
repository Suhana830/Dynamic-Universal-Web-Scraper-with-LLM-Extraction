from langgraph.graph import START, END, StateGraph
from langchain_core.tools import tool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from ai_scrapperAi import fetch_pages
import asyncio
from pydantic import BaseModel, Field
from typing import TypedDict
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import BaseMessage
load_dotenv()

# AI model
llm = ChatOpenAI()

@tool
async def website_text_extraction(url:str):
    """This tool perform the text extraction from the website url"""
    if not url:
        return "No url provided"
    else:
        response = await fetch_pages(url)
        return response
    
# Bind tools with llm
llm_with_tools = llm.bind_tools([website_text_extraction])

#-----------State---------------
class InfoState(BaseModel):
    url: str | None = None
    query: str
    messages: list[BaseMessage] | None = None
    extraction_schema: str | None = None
    response: str | None = None

tool_nodes = ToolNode([website_text_extraction])


#----------------- LangGraph Node functions-----------
#Create Dynamic Schema
def dynamic_schema(state: InfoState):

    prompt = PromptTemplate(
        template="""
You are a data extraction AI.

Create a Pydantic schema for extracting structured data
based on the user request.

User request:
{query}

Return only the Pydantic model.
""",
        input_variables=["query"]
    )

    schema = llm.invoke(prompt.format(query=state.query))

    return {"extraction_schema": schema.content} 


#Agent Node decide -> use tool or can answer directly
async def agent_node(state: InfoState):

    prompt = f"""
You are an AI web scraping agent & Ai assistant.

User request:
{state.query}

If a website URL is present, call the crawl_page tool
to fetch the webpage content.
"""

    response = await llm_with_tools.ainvoke(prompt)
    print(response)
    print("0----------------------------------")

    return {"messages": [response]}

#extracting text from site
async def get_Info_From_Site(state: InfoState):

    query = state.query
    schema = state.extraction_schema

    content = ""

    if state.messages:
        last_msg = state.messages[-1]

        if hasattr(last_msg, "content"):
            content = last_msg.content
        else:
            content = str(last_msg)

    prompt = f"""
You are a smart AI assistant.

User request:
{query}

Website content:
{content}

Extract structured data using this schema:
{schema}

Return ONLY JSON.
If data not found return null values.
"""

    response = await llm.ainvoke(prompt)
    print(response)
    print("0----------------------------------")

    return {"response": response.content}

    
#-------------Graph creation----------
graph = StateGraph(InfoState)
graph.add_node("schema_node", dynamic_schema)
graph.add_node("agent_node", agent_node)
graph.add_node("tools", tool_nodes)
graph.add_node("crwaler_node", get_Info_From_Site)


graph.add_edge(START, "schema_node")
graph.add_edge("schema_node", "agent_node")
graph.add_conditional_edges("agent_node", tools_condition)
graph.add_edge("tools", "crwaler_node")
graph.add_edge("crwaler_node",END)
graph.add_edge("agent_node", END)

app = graph.compile()
# app.get_graph().print_ascii()

# async def run():
#     result = await app.ainvoke({
#         "query": "Extract product name and price from https://www.flipkart.com/vivo-v70-passion-red-256-gb/p/itmecfa7a31699de?pid=MOBHK7E7J3VFYHNQ&param=2357&BU=Mobile&pageUID=1773685935427"
#     })
#     print(result["response"])

# asyncio.run(run())
