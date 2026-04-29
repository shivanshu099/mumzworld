import sqlite3
from typing import TypedDict, Annotated, Sequence, operator, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode
import os
from dotenv import load_dotenv

load_dotenv()

# Define the State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Define the tool
@tool
def search_gifts(query: str = "", max_price: Optional[float] = None, age_group: str = "") -> str:
    """
    Search the gifts database for suitable items.
    query: optional search term (e.g. 'monitor', 'toy')
    max_price: optional maximum price in AED
    age_group: optional age group (e.g. '0-6 months', '1-3 years')
    """
    conn = sqlite3.connect('gifts.db')
    cursor = conn.cursor()
    
    sql = "SELECT name, description, category, price_aed, age_group, rating FROM gifts WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (name LIKE ? OR description LIKE ? OR category LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
    
    if max_price is not None:
        sql += " AND price_aed <= ?"
        params.append(max_price)
        
    if age_group:
        sql += " AND age_group LIKE ?"
        params.append(f"%{age_group}%")
        
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return "No gifts found matching the criteria."
        
    formatted_results = []
    for r in results:
        formatted_results.append(f"- {r[0]}: {r[1]} (Category: {r[2]}, Price: {r[3]} AED, Age: {r[4]}, Rating: {r[5]})")
        
    return "\n".join(formatted_results)

tools = [search_gifts]

# Set up the LLM
# Using Groq
llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
llm_with_tools = llm.bind_tools(tools)

# Define nodes
def chatbot_node(state: AgentState):
    system_prompt = SystemMessage(content='''You are an expert gift finder for moms and babies at Mumzworld.
Your goal is to help users find the perfect gift based on their requirements.
Always use the search_gifts tool to query the database for options.
Once you have the options, provide a curated shortlist of the best items with reasoning.
Crucially, you MUST provide the final response in BOTH English and Arabic.
If the user mentions a budget, ensure you use the max_price parameter in the tool.
''')
    # Filter messages to ensure we only have supported message types
    messages = [system_prompt] + list(state["messages"])
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("chatbot", chatbot_node)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("chatbot")

# Define routing function
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow.add_conditional_edges("chatbot", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "chatbot")

app = workflow.compile()

def process_query(user_text: str, history: list = None):
    messages = []
    if history:
        messages.extend(history)
    messages.append(HumanMessage(content=user_text))
    
    response = app.invoke({"messages": messages})
    return response["messages"][-1].content
