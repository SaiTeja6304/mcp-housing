import sys
import os
from contextlib import asynccontextmanager, AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from utils import extract_text
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

# Load env from current directory first, then fallback/load from server directory as well
load_dotenv()
server_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "mcp-server", "apps", ".env"))
if os.path.exists(server_env_path):
    load_dotenv(server_env_path)

# Global state
mcp_session = None
exit_stack = AsyncExitStack()

server_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "mcp-server", "apps", "src", "housing_server.py"))
server_params = StdioServerParameters(command=sys.executable, args=[server_script])

SYSTEM_PROMPT = (
    "You are a helpful assistant for finding student housing on the Jump Off Campus website.\n"
    "You have access to tools to search, filter, and fetch housing locations, listings, blog posts, and official URLs.\n\n"
    "Here are the rules you must follow to answer queries accurately:\n"
    "1. IF you do not know the slug/subdomain for the university or location requested, you MUST call 'get_house_locations' first to find the correct subdomain (slug).\n"
    "2. When searching for houses or listings, ALWAYS prefer using 'filter_house_information' over 'get_housing_listings' because 'filter_house_information' provides comprehensive house details (amenities, contact, parking, description) and, most importantly, returns the 'listing_path' property.\n"
    "3. If a user asks for a link, URL, or webpage to view a house/listing, you MUST use the 'get_house_link' tool with the correct 'slug' and 'listing_path' (retrieved from 'filter_house_information'). Do NOT invent, hallucinate, or construct listing URLs manually.\n"
    "4. If a user asks questions about housing regulations, tips, moving, damaged apartments, roommate issues, or general guides, search for community posts using 'get_slug_posts' first. If a specific post title is relevant, fetch its full content using 'get_slug_post' to provide an accurate answer.\n"
    "5. Respond in a clean, user-friendly Markdown format with headers, lists, bold text, and clickable hyperlinks (format: [Link Text](URL)) using the URLs returned by the tools."
)

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_session
    try:
        print(f"Connecting to MCP Server at: {server_script}")
        reader, writer = await exit_stack.enter_async_context(stdio_client(server_params))
        mcp_session = await exit_stack.enter_async_context(ClientSession(reader, writer))
        await mcp_session.initialize()

        available_tools = await mcp_session.list_tools()
        print(f"Connected to MCP Server. Available tools: {[t.name for t in available_tools.tools]}")
        yield
    except Exception as e:
        print(f"Failed to connect to MCP Server: {e}", file=sys.stderr)
        raise
    finally:
        await exit_stack.aclose()
        print("MCP session closed.")


app = FastAPI(title="JumpOff Campus MCP Client API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessagePayload(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[MessagePayload]


@app.get("/health")
async def health_endpoint():
    if not mcp_session:
        return {"status": "offline", "reason": "MCP session not initialized"}
    try:
        await mcp_session.list_tools()
        return {"status": "connected"}
    except Exception as e:
        return {"status": "offline", "reason": str(e)}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not mcp_session:
        raise HTTPException(status_code=500, detail="MCP connection is not established")
    if not api_key:
        raise HTTPException(status_code=500, detail="No API Key found. Set GOOGLE_API_KEY or GEMINI_API_KEY in .env")

    # Fetch available tools from the MCP server
    try:
        available_tools = await mcp_session.list_tools()
        tools = [{
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        } for tool in available_tools.tools]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tools from MCP server: {e}")

    # Setup model and bind tools
    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0,
        google_api_key=api_key
    )
    model_with_tools = model.bind_tools(tools) if tools else model

    # Build message history
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for msg in request.history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    messages.append(HumanMessage(content=request.message))

    # Agentic tool-calling loop (max 10 steps to prevent runaway)
    for step in range(1, 11):
        print(f"[Agentic Loop] Step {step}...")

        try:
            response = await model_with_tools.ainvoke(messages)
        except Exception as e:
            print(f"Error during LLM invocation: {e}", file=sys.stderr)
            raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

        messages.append(response)

        # No tool calls means we have the final answer
        if not response.tool_calls:
            return {"response": response.text}

        # Execute each tool call via MCP
        print(f"[Agentic Loop] Tool calls: {[tc['name'] for tc in response.tool_calls]}")
        for tool_call in response.tool_calls:
            print(f"  → {tool_call['name']}({tool_call['args']})")
            try:
                result = await mcp_session.call_tool(tool_call["name"], arguments=tool_call["args"])
                tool_output = extract_text(result.content)
            except Exception as e:
                print(f"  ✗ Error: {e}", file=sys.stderr)
                tool_output = f"Error calling tool: {str(e)}"

            messages.append(ToolMessage(
                content=tool_output,
                tool_call_id=tool_call["id"],
                name=tool_call["name"]
            ))

    raise HTTPException(status_code=500, detail="LLM reached max tool steps without a final answer.")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)