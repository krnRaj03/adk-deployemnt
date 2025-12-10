import asyncio
import json
import logging  # Added logging
import os
from amadeus import Client, ResponseError
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from dotenv import load_dotenv

load_dotenv()

# --- Logging Setup ---
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "amadeus_mcp_server_activity.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode="w"),
    ],
)
# --- End Logging Setup ---

logging.info("Initializing Amadeus MCP Server...")  # Added logging

# Initialize Amadeus client
try:
    amadeus_client = Client(
        client_id='SyHDGe0GU25rjIO27tGorG7kMXrfvTXo',
        client_secret='1Px10g1V8hmoRFfq'
    )
    logging.info("Amadeus client initialized successfully.")  # Added logging
except Exception as e:
    logging.critical(f"Failed to initialize Amadeus client: {e}", exc_info=True)  # Added logging
    raise

# Create MCP Server
logging.info("Creating MCP Server instance for Amadeus Travel APIs...")  # Added logging
app = Server("amadeus-travel-mcp-server")

@app.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    """List available Amadeus tools."""
    logging.info("MCP Server: Received list_tools request.")  # Added logging
    
    tools = [
        mcp_types.Tool(
            name="search_flights",
            description="Search for flight offers between two cities",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin airport code (e.g., MAD)"},
                    "destination": {"type": "string", "description": "Destination airport code (e.g., NYC)"},
                    "departure_date": {"type": "string", "description": "Departure date (YYYY-MM-DD)"},
                    "adults": {"type": "integer", "description": "Number of adults", "default": 1}
                },
                "required": ["origin", "destination", "departure_date"]
            }
        ),
        mcp_types.Tool(
            name="search_hotels",
            description="Search for hotel offers by city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city_code": {"type": "string", "description": "City code (e.g., PAR for Paris)"},
                    "check_in": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                    "check_out": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"}
                },
                "required": ["city_code"]
            }
        ),
        mcp_types.Tool(
            name="get_airport_info",
            description="Get information about airports by keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Search keyword (e.g., LON for London)"}
                },
                "required": ["keyword"]
            }
        )
    ]
    
    # Log each tool being advertised
    for tool in tools:
        logging.info(f"MCP Server: Advertising tool: {tool.name}, InputSchema: {tool.inputSchema}")  # Added logging
    
    return tools

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    """Execute Amadeus API calls."""
    logging.info(f"MCP Server: Received call_tool request for '{name}' with args: {arguments}")  # Added logging
    
    try:
        if name == "search_flights":
            logging.debug(f"Executing flight search: {arguments['origin']} -> {arguments['destination']} on {arguments['departure_date']}")  # Added logging
            
            response = amadeus_client.shopping.flight_offers_search.get(
                originLocationCode=arguments['origin'],
                destinationLocationCode=arguments['destination'],
                departureDate=arguments['departure_date'],
                adults=arguments.get('adults', 1)
            )
            result = json.dumps(response.data, indent=2)
            logging.info(f"MCP Server: Flight search completed successfully. Found {len(response.data)} offers.")  # Added logging
            
        elif name == "search_hotels":
            logging.debug(f"Executing hotel search for city: {arguments['city_code']}")  # Added logging
            
            response = amadeus_client.reference_data.locations.hotels.by_city.get(
                cityCode=arguments['city_code']
            )
            result = json.dumps(response.data, indent=2)
            logging.info(f"MCP Server: Hotel search completed successfully. Found {len(response.data)} hotels.")  # Added logging
            
        elif name == "get_airport_info":
            logging.debug(f"Executing airport info search for keyword: {arguments['keyword']}")  # Added logging
            
            from amadeus import Location
            response = amadeus_client.reference_data.locations.get(
                keyword=arguments['keyword'],
                subType=Location.AIRPORT
            )
            result = json.dumps(response.data, indent=2)
            logging.info(f"MCP Server: Airport search completed successfully. Found {len(response.data)} airports.")  # Added logging
            
        else:
            logging.warning(f"MCP Server: Tool '{name}' not found/exposed by this server.")  # Added logging
            result = json.dumps({"error": f"Unknown tool: {name}"})
        
        logging.info(f"MCP Server: Tool '{name}' executed successfully. Response length: {len(result)} chars")  # Added logging
        return [mcp_types.TextContent(type="text", text=result)]
        
    except ResponseError as error:
        logging.error(f"MCP Server: Amadeus API error in tool '{name}': {error}", exc_info=True)  # Added logging
        error_msg = json.dumps({"error": str(error), "success": False})
        return [mcp_types.TextContent(type="text", text=error_msg)]
        
    except Exception as e:
        logging.error(f"MCP Server: Unexpected error executing tool '{name}': {e}", exc_info=True)  # Added logging
        error_payload = {
            "success": False,
            "message": f"Failed to execute tool '{name}': {str(e)}",
        }
        error_text = json.dumps(error_payload)
        return [mcp_types.TextContent(type="text", text=error_text)]

async def run_server():
    """Run the MCP server over stdio."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logging.info("MCP Stdio Server: Starting handshake with client...")  # Added logging
        
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=app.name,
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
        
        logging.info("MCP Stdio Server: Run loop finished or client disconnected.")  # Added logging

if __name__ == "__main__":
    logging.info("Launching Amadeus Travel MCP Server via stdio...")  # Added logging
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logging.info("\nMCP Server (stdio) stopped by user.")  # Added logging
    except Exception as e:
        logging.critical(f"MCP Server (stdio) encountered an unhandled error: {e}", exc_info=True)  # Added logging
    finally:
        logging.info("MCP Server (stdio) process exiting.")  # Added logging
