import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Path to your MCP server script
MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "server.py")

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='amadeus_travel_assistant',
    instruction='''You are a travel assistant that helps users search for flights, 
    hotels, and airport information using Amadeus travel APIs. Provide helpful 
    and detailed responses about travel options.''',
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python3',
                    args=[MCP_SERVER_PATH],
                    env={
                        'AMADEUS_CLIENT_ID': 'SyHDGe0GU25rjIO27tGorG7kMXrfvTXo',
                        'AMADEUS_CLIENT_SECRET': '1Px10g1V8hmoRFfq'
                    }
                ),
                timeout=60
            ),
        )
    ],
)
