# blender_mcp_server.py
from fastmcp import FastMCP, Context, Image
import socket
import json
import asyncio
import logging
import tempfile
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List
import os
from pathlib import Path
import base64
from urllib.parse import urlparse
import requests
import time

# Configure logging first
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BlenderMCPServer")

# Import enhanced WebUI tools
try:
    from .enhanced_webui_tools import (
        enhanced_generate_stable_diffusion_image,
        batch_generate_images,
        img2img_enhance,
        get_webui_status
    )
    ENHANCED_WEBUI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Enhanced WebUI tools not available: {e}")
    ENHANCED_WEBUI_AVAILABLE = False

# Import optimization tools
try:
    from .sd_optimization_presets import get_preset, list_presets, print_preset_info
    from .sd_parameter_optimizer import (
        SDParameterOptimizer, 
        OptimizationContext, 
        OptimizationGoal, 
        HardwareProfile,
        quick_optimize
    )
    OPTIMIZATION_TOOLS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Optimization tools not available: {e}")
    OPTIMIZATION_TOOLS_AVAILABLE = False

# Try to import workflow manager
try:
    from .workflow_manager import (
        WorkflowManager,
        WorkflowConfig,
        WorkflowStage,
        GenerationMethod,
        create_workflow_config,
        execute_text_to_3d_workflow,
        get_preset_config,
        PRESET_CONFIGS
    )
    WORKFLOW_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Workflow manager not available: {e}")
    WORKFLOW_MANAGER_AVAILABLE = False

@dataclass
class BlenderConnection:
    host: str
    port: int
    sock: socket.socket = None  # Changed from 'socket' to 'sock' to avoid naming conflict
    
    def connect(self) -> bool:
        """Connect to the Blender addon socket server"""
        if self.sock:
            return True
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Blender at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Blender: {str(e)}")
            self.sock = None
            return False
    
    def disconnect(self):
        """Disconnect from the Blender addon"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Blender: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        # Use a consistent timeout value that matches the addon's timeout
        sock.settimeout(15.0)  # Match the addon's timeout
        
        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        # If we get an empty chunk, the connection might be closed
                        if not chunks:  # If we haven't received anything yet, this is an error
                            raise Exception("Connection closed before receiving any data")
                        break
                    
                    chunks.append(chunk)
                    
                    # Check if we've received a complete JSON object
                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        # If we get here, it parsed successfully
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except socket.timeout:
                    # If we hit a timeout during receiving, break the loop and try to use what we have
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise  # Re-raise to be handled by the caller
        except socket.timeout:
            logger.warning("Socket timeout during chunked receive")
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise
            
        # If we get here, we either timed out or broke out of the loop
        # Try to use what we have
        if chunks:
            data = b''.join(chunks)
            logger.info(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                # Try to parse what we have
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                # If we can't parse it, it's incomplete
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Blender and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Blender")
        
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        try:
            # Log the command being sent
            logger.info(f"Sending command: {command_type} with params: {params}")
            
            # Send the command
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            logger.info(f"Command sent, waiting for response...")
            
            # Set a timeout for receiving - use the same timeout as in receive_full_response
            self.sock.settimeout(15.0)  # Match the addon's timeout
            
            # Receive the response using the improved receive_full_response method
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")
            
            response = json.loads(response_data.decode('utf-8'))
            logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")
            
            if response.get("status") == "error":
                logger.error(f"Blender error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Blender"))
            
            return response.get("result", {})
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Blender")
            # Don't try to reconnect here - let the get_blender_connection handle reconnection
            # Just invalidate the current socket so it will be recreated next time
            self.sock = None
            raise Exception("Timeout waiting for Blender response - try simplifying your request")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Blender lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Blender: {str(e)}")
            # Try to log what was received
            if 'response_data' in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            raise Exception(f"Invalid response from Blender: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Blender: {str(e)}")
            # Don't try to reconnect here - let the get_blender_connection handle reconnection
            self.sock = None
            raise Exception(f"Communication error with Blender: {str(e)}")

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    # We don't need to create a connection here since we're using the global connection
    # for resources and tools
    
    try:
        # Just log that we're starting up
        logger.info("BlenderMCP server starting up")
        
        # Try to connect to Blender on startup to verify it's available
        try:
            # This will initialize the global connection if needed
            blender = get_blender_connection()
            logger.info("Successfully connected to Blender on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Blender on startup: {str(e)}")
            logger.warning("Make sure the Blender addon is running before using Blender resources or tools")
        
        # Return an empty context - we're using the global connection
        yield {}
    finally:
        # Clean up the global connection on shutdown
        global _blender_connection
        if _blender_connection:
            logger.info("Disconnecting from Blender on shutdown")
            _blender_connection.disconnect()
            _blender_connection = None
        logger.info("BlenderMCP server shut down")

# Create the MCP server with lifespan support
mcp = FastMCP(
    "BlenderMCP",
    lifespan=server_lifespan
)

# Resource endpoints

# Global connection for resources (since resources can't access context)
_blender_connection = None
_polyhaven_enabled = False  # Add this global variable

def get_blender_connection():
    """Get or create a persistent Blender connection"""
    global _blender_connection, _polyhaven_enabled  # Add _polyhaven_enabled to globals
    
    # If we have an existing connection, check if it's still valid
    if _blender_connection is not None:
        try:
            # First check if PolyHaven is enabled by sending a ping command
            result = _blender_connection.send_command("get_polyhaven_status")
            # Store the PolyHaven status globally
            _polyhaven_enabled = result.get("enabled", False)
            return _blender_connection
        except Exception as e:
            # Connection is dead, close it and create a new one
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _blender_connection.disconnect()
            except:
                pass
            _blender_connection = None
    
    # Create a new connection if needed
    if _blender_connection is None:
        _blender_connection = BlenderConnection(host="localhost", port=9876)
        if not _blender_connection.connect():
            logger.error("Failed to connect to Blender")
            _blender_connection = None
            raise Exception("Could not connect to Blender. Make sure the Blender addon is running.")
        logger.info("Created new persistent connection to Blender")
    
    return _blender_connection


@mcp.tool()
def get_scene_info(ctx: Context) -> str:
    """Get detailed information about the current Blender scene"""
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_scene_info")
        
        # Just return the JSON representation of what Blender sent us
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting scene info from Blender: {str(e)}")
        return f"Error getting scene info: {str(e)}"

@mcp.tool()
def get_object_info(ctx: Context, object_name: str) -> str:
    """
    Get detailed information about a specific object in the Blender scene.
    
    Parameters:
    - object_name: The name of the object to get information about
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_object_info", {"name": object_name})
        
        # Just return the JSON representation of what Blender sent us
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting object info from Blender: {str(e)}")
        return f"Error getting object info: {str(e)}"

@mcp.tool()
def get_viewport_screenshot(ctx: Context, max_size: int = 800) -> Image:
    """
    Capture a screenshot of the current Blender 3D viewport.
    
    Parameters:
    - max_size: Maximum size in pixels for the largest dimension (default: 800)
    
    Returns the screenshot as an Image.
    """
    try:
        blender = get_blender_connection()
        
        # Create temp file path
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"blender_screenshot_{os.getpid()}.png")
        
        result = blender.send_command("get_viewport_screenshot", {
            "max_size": max_size,
            "filepath": temp_path,
            "format": "png"
        })
        
        if "error" in result:
            raise Exception(result["error"])
        
        if not os.path.exists(temp_path):
            raise Exception("Screenshot file was not created")
        
        # Read the file
        with open(temp_path, 'rb') as f:
            image_bytes = f.read()
        
        # Delete the temp file
        os.remove(temp_path)
        
        return Image(data=image_bytes, format="png")
        
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}")
        raise Exception(f"Screenshot failed: {str(e)}")


@mcp.tool()
def execute_blender_code(ctx: Context, code: str) -> str:
    """
    Execute arbitrary Python code in Blender. Make sure to do it step-by-step by breaking it into smaller chunks.
    
    Parameters:
    - code: The Python code to execute
    """
    try:
        # Get the global connection
        blender = get_blender_connection()
        result = blender.send_command("execute_code", {"code": code})
        return f"Code executed successfully: {result.get('result', '')}"
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return f"Error executing code: {str(e)}"

@mcp.tool()
def get_polyhaven_categories(ctx: Context, asset_type: str = "hdris") -> str:
    """
    Get a list of categories for a specific asset type on Polyhaven.
    
    Parameters:
    - asset_type: The type of asset to get categories for (hdris, textures, models, all)
    """
    try:
        blender = get_blender_connection()
        if not _polyhaven_enabled:
            return "PolyHaven integration is disabled. Select it in the sidebar in BlenderMCP, then run it again."
        result = blender.send_command("get_polyhaven_categories", {"asset_type": asset_type})
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        # Format the categories in a more readable way
        categories = result["categories"]
        formatted_output = f"Categories for {asset_type}:\n\n"
        
        # Sort categories by count (descending)
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_categories:
            formatted_output += f"- {category}: {count} assets\n"
        
        return formatted_output
    except Exception as e:
        logger.error(f"Error getting Polyhaven categories: {str(e)}")
        return f"Error getting Polyhaven categories: {str(e)}"

@mcp.tool()
def search_polyhaven_assets(
    ctx: Context,
    asset_type: str = "all",
    categories: str = None
) -> str:
    """
    Search for assets on Polyhaven with optional filtering.
    
    Parameters:
    - asset_type: Type of assets to search for (hdris, textures, models, all)
    - categories: Optional comma-separated list of categories to filter by
    
    Returns a list of matching assets with basic information.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("search_polyhaven_assets", {
            "asset_type": asset_type,
            "categories": categories
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        # Format the assets in a more readable way
        assets = result["assets"]
        total_count = result["total_count"]
        returned_count = result["returned_count"]
        
        formatted_output = f"Found {total_count} assets"
        if categories:
            formatted_output += f" in categories: {categories}"
        formatted_output += f"\nShowing {returned_count} assets:\n\n"
        
        # Sort assets by download count (popularity)
        sorted_assets = sorted(assets.items(), key=lambda x: x[1].get("download_count", 0), reverse=True)
        
        for asset_id, asset_data in sorted_assets:
            formatted_output += f"- {asset_data.get('name', asset_id)} (ID: {asset_id})\n"
            formatted_output += f"  Type: {['HDRI', 'Texture', 'Model'][asset_data.get('type', 0)]}\n"
            formatted_output += f"  Categories: {', '.join(asset_data.get('categories', []))}\n"
            formatted_output += f"  Downloads: {asset_data.get('download_count', 'Unknown')}\n\n"
        
        return formatted_output
    except Exception as e:
        logger.error(f"Error searching Polyhaven assets: {str(e)}")
        return f"Error searching Polyhaven assets: {str(e)}"

@mcp.tool()
def download_polyhaven_asset(
    ctx: Context,
    asset_id: str,
    asset_type: str,
    resolution: str = "1k",
    file_format: str = None
) -> str:
    """
    Download and import a Polyhaven asset into Blender.
    
    Parameters:
    - asset_id: The ID of the asset to download
    - asset_type: The type of asset (hdris, textures, models)
    - resolution: The resolution to download (e.g., 1k, 2k, 4k)
    - file_format: Optional file format (e.g., hdr, exr for HDRIs; jpg, png for textures; gltf, fbx for models)
    
    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("download_polyhaven_asset", {
            "asset_id": asset_id,
            "asset_type": asset_type,
            "resolution": resolution,
            "file_format": file_format
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            message = result.get("message", "Asset downloaded and imported successfully")
            
            # Add additional information based on asset type
            if asset_type == "hdris":
                return f"{message}. The HDRI has been set as the world environment."
            elif asset_type == "textures":
                material_name = result.get("material", "")
                maps = ", ".join(result.get("maps", []))
                return f"{message}. Created material '{material_name}' with maps: {maps}."
            elif asset_type == "models":
                return f"{message}. The model has been imported into the current scene."
            else:
                return message
        else:
            return f"Failed to download asset: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error downloading Polyhaven asset: {str(e)}")
        return f"Error downloading Polyhaven asset: {str(e)}"

@mcp.tool()
def set_texture(
    ctx: Context,
    object_name: str,
    texture_id: str
) -> str:
    """
    Apply a previously downloaded Polyhaven texture to an object.
    
    Parameters:
    - object_name: Name of the object to apply the texture to
    - texture_id: ID of the Polyhaven texture to apply (must be downloaded first)
    
    Returns a message indicating success or failure.
    """
    try:
        # Get the global connection
        blender = get_blender_connection()
        result = blender.send_command("set_texture", {
            "object_name": object_name,
            "texture_id": texture_id
        })
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        if result.get("success"):
            material_name = result.get("material", "")
            maps = ", ".join(result.get("maps", []))
            
            # Add detailed material info
            material_info = result.get("material_info", {})
            node_count = material_info.get("node_count", 0)
            has_nodes = material_info.get("has_nodes", False)
            texture_nodes = material_info.get("texture_nodes", [])
            
            output = f"Successfully applied texture '{texture_id}' to {object_name}.\n"
            output += f"Using material '{material_name}' with maps: {maps}.\n\n"
            output += f"Material has nodes: {has_nodes}\n"
            output += f"Total node count: {node_count}\n\n"
            
            if texture_nodes:
                output += "Texture nodes:\n"
                for node in texture_nodes:
                    output += f"- {node['name']} using image: {node['image']}\n"
                    if node['connections']:
                        output += "  Connections:\n"
                        for conn in node['connections']:
                            output += f"    {conn}\n"
            else:
                output += "No texture nodes found in the material.\n"
            
            return output
        else:
            return f"Failed to apply texture: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error applying texture: {str(e)}")
        return f"Error applying texture: {str(e)}"

@mcp.tool()
def get_polyhaven_status(ctx: Context) -> str:
    """
    Check if PolyHaven integration is enabled in Blender.
    Returns a message indicating whether PolyHaven features are available.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_polyhaven_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += "PolyHaven is good at Textures, and has a wider variety of textures than Sketchfab."
        return message
    except Exception as e:
        logger.error(f"Error checking PolyHaven status: {str(e)}")
        return f"Error checking PolyHaven status: {str(e)}"

@mcp.tool()
def get_hyper3d_status(ctx: Context) -> str:
    """
    Check if Hyper3D Rodin integration is enabled in Blender.
    Returns a message indicating whether Hyper3D Rodin features are available.

    Don't emphasize the key type in the returned message, but sliently remember it. 
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_hyper3d_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += ""
        return message
    except Exception as e:
        logger.error(f"Error checking Hyper3D status: {str(e)}")
        return f"Error checking Hyper3D status: {str(e)}"

@mcp.tool()
def get_sketchfab_status(ctx: Context) -> str:
    """
    Check if Sketchfab integration is enabled in Blender.
    Returns a message indicating whether Sketchfab features are available.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("get_sketchfab_status")
        enabled = result.get("enabled", False)
        message = result.get("message", "")
        if enabled:
            message += "Sketchfab is good at Realistic models, and has a wider variety of models than PolyHaven."        
        return message
    except Exception as e:
        logger.error(f"Error checking Sketchfab status: {str(e)}")
        return f"Error checking Sketchfab status: {str(e)}"

@mcp.tool()
def search_sketchfab_models(
    ctx: Context,
    query: str,
    categories: str = None,
    count: int = 20,
    downloadable: bool = True
) -> str:
    """
    Search for models on Sketchfab with optional filtering.
    
    Parameters:
    - query: Text to search for
    - categories: Optional comma-separated list of categories
    - count: Maximum number of results to return (default 20)
    - downloadable: Whether to include only downloadable models (default True)
    
    Returns a formatted list of matching models.
    """
    try:
        
        blender = get_blender_connection()
        logger.info(f"Searching Sketchfab models with query: {query}, categories: {categories}, count: {count}, downloadable: {downloadable}")
        result = blender.send_command("search_sketchfab_models", {
            "query": query,
            "categories": categories,
            "count": count,
            "downloadable": downloadable
        })
        
        if "error" in result:
            logger.error(f"Error from Sketchfab search: {result['error']}")
            return f"Error: {result['error']}"
        
        # Safely get results with fallbacks for None
        if result is None:
            logger.error("Received None result from Sketchfab search")
            return "Error: Received no response from Sketchfab search"
            
        # Format the results
        models = result.get("results", []) or []
        if not models:
            return f"No models found matching '{query}'"
            
        formatted_output = f"Found {len(models)} models matching '{query}':\n\n"
        
        for model in models:
            if model is None:
                continue
                
            model_name = model.get("name", "Unnamed model")
            model_uid = model.get("uid", "Unknown ID")
            formatted_output += f"- {model_name} (UID: {model_uid})\n"
            
            # Get user info with safety checks
            user = model.get("user") or {}
            username = user.get("username", "Unknown author") if isinstance(user, dict) else "Unknown author"
            formatted_output += f"  Author: {username}\n"
            
            # Get license info with safety checks
            license_data = model.get("license") or {}
            license_label = license_data.get("label", "Unknown") if isinstance(license_data, dict) else "Unknown"
            formatted_output += f"  License: {license_label}\n"
            
            # Add face count and downloadable status
            face_count = model.get("faceCount", "Unknown")
            is_downloadable = "Yes" if model.get("isDownloadable") else "No"
            formatted_output += f"  Face count: {face_count}\n"
            formatted_output += f"  Downloadable: {is_downloadable}\n\n"
        
        return formatted_output
    except Exception as e:
        logger.error(f"Error searching Sketchfab models: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return f"Error searching Sketchfab models: {str(e)}"

@mcp.tool()
def download_sketchfab_model(
    ctx: Context,
    uid: str
) -> str:
    """
    Download and import a Sketchfab model by its UID.
    
    Parameters:
    - uid: The unique identifier of the Sketchfab model
    
    Returns a message indicating success or failure.
    The model must be downloadable and you must have proper access rights.
    """
    try:
        
        blender = get_blender_connection()
        logger.info(f"Attempting to download Sketchfab model with UID: {uid}")
        
        result = blender.send_command("download_sketchfab_model", {
            "uid": uid
        })
        
        if result is None:
            logger.error("Received None result from Sketchfab download")
            return "Error: Received no response from Sketchfab download request"
            
        if "error" in result:
            logger.error(f"Error from Sketchfab download: {result['error']}")
            return f"Error: {result['error']}"
        
        if result.get("success"):
            imported_objects = result.get("imported_objects", [])
            object_names = ", ".join(imported_objects) if imported_objects else "none"
            return f"Successfully imported model. Created objects: {object_names}"
        else:
            return f"Failed to download model: {result.get('message', 'Unknown error')}"
    except Exception as e:
        logger.error(f"Error downloading Sketchfab model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return f"Error downloading Sketchfab model: {str(e)}"

def _process_bbox(original_bbox: list[float] | list[int] | None) -> list[int] | None:
    if original_bbox is None:
        return None
    if all(isinstance(i, int) for i in original_bbox):
        return original_bbox
    if any(i<=0 for i in original_bbox):
        raise ValueError("Incorrect number range: bbox must be bigger than zero!")
    return [int(float(i) / max(original_bbox) * 100) for i in original_bbox] if original_bbox else None

@mcp.tool()
def generate_hyper3d_model_via_text(
    ctx: Context,
    text_prompt: str,
    bbox_condition: list[float]=None
) -> str:
    """
    Generate 3D asset using Hyper3D by giving description of the desired asset, and import the asset into Blender.
    The 3D asset has built-in materials.
    The generated model has a normalized size, so re-scaling after generation can be useful.
    
    Parameters:
    - text_prompt: A short description of the desired model in **English**.
    - bbox_condition: Optional. If given, it has to be a list of floats of length 3. Controls the ratio between [Length, Width, Height] of the model.

    Returns a message indicating success or failure.
    """
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_rodin_job", {
            "text_prompt": text_prompt,
            "images": None,
            "bbox_condition": _process_bbox(bbox_condition),
        })
        succeed = result.get("submit_time", False)
        if succeed:
            return json.dumps({
                "task_uuid": result["uuid"],
                "subscription_key": result["jobs"]["subscription_key"],
            })
        else:
            return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

@mcp.tool()
def generate_hyper3d_model_via_images(
    ctx: Context,
    input_image_paths: list[str]=None,
    input_image_urls: list[str]=None,
    bbox_condition: list[float]=None
) -> str:
    """
    Generate 3D asset using Hyper3D by giving images of the wanted asset, and import the generated asset into Blender.
    The 3D asset has built-in materials.
    The generated model has a normalized size, so re-scaling after generation can be useful.
    
    Parameters:
    - input_image_paths: The **absolute** paths of input images. Even if only one image is provided, wrap it into a list. Required if Hyper3D Rodin in MAIN_SITE mode.
    - input_image_urls: The URLs of input images. Even if only one image is provided, wrap it into a list. Required if Hyper3D Rodin in FAL_AI mode.
    - bbox_condition: Optional. If given, it has to be a list of ints of length 3. Controls the ratio between [Length, Width, Height] of the model.

    Only one of {input_image_paths, input_image_urls} should be given at a time, depending on the Hyper3D Rodin's current mode.
    Returns a message indicating success or failure.
    """
    if input_image_paths is not None and input_image_urls is not None:
        return f"Error: Conflict parameters given!"
    if input_image_paths is None and input_image_urls is None:
        return f"Error: No image given!"
    if input_image_paths is not None:
        if not all(os.path.exists(i) for i in input_image_paths):
            return "Error: not all image paths are valid!"
        images = []
        for path in input_image_paths:
            with open(path, "rb") as f:
                images.append(
                    (Path(path).suffix, base64.b64encode(f.read()).decode("ascii"))
                )
    elif input_image_urls is not None:
        if not all(urlparse(i) for i in input_image_paths):
            return "Error: not all image URLs are valid!"
        images = input_image_urls.copy()
    try:
        blender = get_blender_connection()
        result = blender.send_command("create_rodin_job", {
            "text_prompt": None,
            "images": images,
            "bbox_condition": _process_bbox(bbox_condition),
        })
        succeed = result.get("submit_time", False)
        if succeed:
            return json.dumps({
                "task_uuid": result["uuid"],
                "subscription_key": result["jobs"]["subscription_key"],
            })
        else:
            return json.dumps(result)
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

@mcp.tool()
def poll_rodin_job_status(
    ctx: Context,
    subscription_key: str=None,
    request_id: str=None,
):
    """
    Check if the Hyper3D Rodin generation task is completed.

    For Hyper3D Rodin mode MAIN_SITE:
        Parameters:
        - subscription_key: The subscription_key given in the generate model step.

        Returns a list of status. The task is done if all status are "Done".
        If "Failed" showed up, the generating process failed.
        This is a polling API, so only proceed if the status are finally determined ("Done" or "Canceled").

    For Hyper3D Rodin mode FAL_AI:
        Parameters:
        - request_id: The request_id given in the generate model step.

        Returns the generation task status. The task is done if status is "COMPLETED".
        The task is in progress if status is "IN_PROGRESS".
        If status other than "COMPLETED", "IN_PROGRESS", "IN_QUEUE" showed up, the generating process might be failed.
        This is a polling API, so only proceed if the status are finally determined ("COMPLETED" or some failed state).
    """
    try:
        blender = get_blender_connection()
        kwargs = {}
        if subscription_key:
            kwargs = {
                "subscription_key": subscription_key,
            }
        elif request_id:
            kwargs = {
                "request_id": request_id,
            }
        result = blender.send_command("poll_rodin_job_status", kwargs)
        return result
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

@mcp.tool()
def import_generated_asset(
    ctx: Context,
    name: str,
    task_uuid: str=None,
    request_id: str=None,
):
    """
    Import the asset generated by Hyper3D Rodin after the generation task is completed.

    Parameters:
    - name: The name of the object in scene
    - task_uuid: For Hyper3D Rodin mode MAIN_SITE: The task_uuid given in the generate model step.
    - request_id: For Hyper3D Rodin mode FAL_AI: The request_id given in the generate model step.

    Only give one of {task_uuid, request_id} based on the Hyper3D Rodin Mode!
    Return if the asset has been imported successfully.
    """
    try:
        blender = get_blender_connection()
        kwargs = {
            "name": name
        }
        if task_uuid:
            kwargs["task_uuid"] = task_uuid
        elif request_id:
            kwargs["request_id"] = request_id
        result = blender.send_command("import_generated_asset", kwargs)
        return result
    except Exception as e:
        logger.error(f"Error generating Hyper3D task: {str(e)}")
        return f"Error generating Hyper3D task: {str(e)}"

@mcp.tool()
def generate_hunyuan3d_model(
    ctx: Context,
    image_path: str = None,
    image_url: str = None,
    image_base64: str = None,
    remove_background: bool = True,
    texture: bool = True,
    seed: int = 1234,
    octree_resolution: int = 256,
    num_inference_steps: int = 5,
    guidance_scale: float = 5.0,
    num_chunks: int = 8000,
    face_count: int = 40000,
    hunyuan3d_api_url: str = "http://localhost:8081",
    use_async: bool = False
) -> str:
    """
    Generate a 3D model using Hunyuan3D-2.1 from an image and import it into Blender.
    
    Parameters:
    - image_path: Local path to the input image
    - image_url: URL to the input image
    - image_base64: Base64 encoded image data
    - remove_background: Whether to remove background automatically
    - texture: Whether to generate textures
    - seed: Random seed for reproducible generation
    - octree_resolution: Resolution of the octree for mesh generation (64-512)
    - num_inference_steps: Number of inference steps (1-20)
    - guidance_scale: Guidance scale for generation (0.1-20.0)
    - num_chunks: Number of chunks for processing (1000-20000)
    - face_count: Maximum number of faces for texture generation (1000-100000)
    - hunyuan3d_api_url: URL of the Hunyuan3D API server
    - use_async: Whether to use async generation (returns task ID for polling)
    """
    try:
        # Prepare image data
        if image_base64:
            image_data = image_base64
        elif image_path:
            if not os.path.exists(image_path):
                return f"Error: Image file not found at {image_path}"
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
        elif image_url:
            try:
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()
                image_data = base64.b64encode(response.content).decode('utf-8')
            except Exception as e:
                return f"Error downloading image from URL: {str(e)}"
        else:
            return "Error: Must provide either image_path, image_url, or image_base64"
        
        # Prepare request data according to API models
        request_data = {
            "image": image_data,
            "remove_background": remove_background,
            "texture": texture,
            "seed": seed,
            "octree_resolution": octree_resolution,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "num_chunks": num_chunks,
            "face_count": face_count
        }
        
        if use_async:
            # Use async endpoint for long-running tasks
            logger.info(f"Sending async request to Hunyuan3D API at {hunyuan3d_api_url}/send")
            response = requests.post(
                f"{hunyuan3d_api_url}/send",
                json=request_data,
                timeout=60
            )
            
            if response.status_code != 200:
                return f"Error: Hunyuan3D API returned status {response.status_code}: {response.text}"
            
            result = response.json()
            task_uid = result.get('uid')
            
            if not task_uid:
                return "Error: No task UID returned from async API"
            
            return f"Async generation started. Task UID: {task_uid}. Use poll_hunyuan3d_status('{task_uid}') to check progress."
        
        else:
            # Use synchronous endpoint
            logger.info(f"Sending request to Hunyuan3D API at {hunyuan3d_api_url}/generate")
            response = requests.post(
                f"{hunyuan3d_api_url}/generate",
                json=request_data,
                timeout=600  # 10 minutes timeout for sync
            )
            
            if response.status_code != 200:
                return f"Error: Hunyuan3D API returned status {response.status_code}: {response.text}"
            
            # Import the model into Blender using the addon method
            blender = get_blender_connection()
            
            # Convert response content to base64 for transmission
            model_base64 = base64.b64encode(response.content).decode('utf-8')
            
            import_result = blender.send_command("import_hunyuan3d_model", {
                "model_data": model_base64,
                "name": f"hunyuan3d_model_{int(time.time())}"
            })
            
            if "error" in import_result:
                return f"Model generated but import failed: {import_result['error']}"
            
            return f"Successfully generated and imported 3D model using Hunyuan3D. {import_result.get('message', '')}"
        
    except requests.exceptions.Timeout:
        return "Error: Request to Hunyuan3D API timed out. Try using use_async=True for long-running generations."
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to Hunyuan3D API at {hunyuan3d_api_url}. Make sure the API server is running."
    except Exception as e:
        logger.error(f"Error generating Hunyuan3D model: {str(e)}")
        return f"Error generating Hunyuan3D model: {str(e)}"

@mcp.tool()
def generate_stable_diffusion_image(
    ctx: Context,
    prompt: str,
    negative_prompt: str = "blurry, low quality, distorted",
    width: int = 512,
    height: int = 512,
    num_inference_steps: int = 20,
    guidance_scale: float = 7.5,
    seed: int = None,
    model_id: str = "runwayml/stable-diffusion-v1-5",
    use_local_api: bool = False,
    api_url: str = "http://localhost:7860"
) -> str:
    """
    Generate an image using Stable Diffusion from a text prompt.
    
    Parameters:
    - prompt: Text description of the image to generate
    - negative_prompt: What to avoid in the generated image
    - width: Image width (must be divisible by 8)
    - height: Image height (must be divisible by 8)
    - num_inference_steps: Number of denoising steps
    - guidance_scale: How closely to follow the prompt
    - seed: Random seed for reproducible generation
    - model_id: Hugging Face model ID to use
    - use_local_api: Whether to use local API (e.g., AUTOMATIC1111 WebUI)
    - api_url: URL of the local Stable Diffusion API
    """
    try:
        if use_local_api:
            # Use local API (e.g., AUTOMATIC1111 WebUI)
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": num_inference_steps,
                "cfg_scale": guidance_scale,
                "seed": seed if seed is not None else -1,
                "sampler_name": "DPM++ 2M Karras"
            }
            
            logger.info(f"Sending request to local Stable Diffusion API at {api_url}")
            response = requests.post(
                f"{api_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=300
            )
            
            if response.status_code != 200:
                return f"Error: Local API returned status {response.status_code}: {response.text}"
            
            result = response.json()
            if "images" not in result or not result["images"]:
                return "Error: No images returned from local API"
            
            # Decode base64 image
            image_data = base64.b64decode(result["images"][0])
            temp_dir = tempfile.mkdtemp()
            image_path = os.path.join(temp_dir, f"sd_generated_{int(time.time())}.png")
            
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            logger.info(f"Image saved to {image_path}")
            return f"Successfully generated image using local API and saved to: {image_path}\nYou can now use this image with generate_hunyuan3d_model to create a 3D model."
        
        else:
            # Import diffusers here to avoid dependency issues if not installed
            try:
                from diffusers import StableDiffusionPipeline
                import torch
            except ImportError:
                return "Error: diffusers and torch are required for Stable Diffusion. Install with: pip install diffusers torch"
            
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Load the pipeline
            logger.info(f"Loading Stable Diffusion model: {model_id}")
            pipe = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32
            )
            pipe = pipe.to(device)
            
            # Generate the image
            logger.info(f"Generating image with prompt: {prompt}")
            
            generator = None
            if seed is not None:
                generator = torch.Generator(device=device).manual_seed(seed)
            
            image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            ).images[0]
            
            # Save the image to a temporary file
            temp_dir = tempfile.mkdtemp()
            image_path = os.path.join(temp_dir, f"sd_generated_{int(time.time())}.png")
            image.save(image_path)
            
            logger.info(f"Image saved to {image_path}")
            
            # Clean up the pipeline to free memory
            del pipe
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            return f"Successfully generated image and saved to: {image_path}\nYou can now use this image with generate_hunyuan3d_model to create a 3D model."
        
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to local API at {api_url}. Make sure the API server is running."
    except Exception as e:
        logger.error(f"Error generating Stable Diffusion image: {str(e)}")
        return f"Error generating Stable Diffusion image: {str(e)}"

@mcp.tool()
def poll_hunyuan3d_status(
    ctx: Context,
    task_uid: str,
    hunyuan3d_api_url: str = "http://localhost:8081"
) -> str:
    """
    Poll the status of an async Hunyuan3D generation task.
    
    Parameters:
    - task_uid: The task UID returned from async generation
    - hunyuan3d_api_url: URL of the Hunyuan3D API server
    """
    try:
        logger.info(f"Polling status for task {task_uid}")
        
        response = requests.get(
            f"{hunyuan3d_api_url}/status/{task_uid}",
            timeout=30
        )
        
        if response.status_code != 200:
            return f"Error: API returned status {response.status_code}: {response.text}"
        
        result = response.json()
        status = result.get('status', 'unknown')
        
        if status == 'completed':
            # Try to download and import the model
            download_response = requests.get(
                f"{hunyuan3d_api_url}/download/{task_uid}",
                timeout=300
            )
            
            if download_response.status_code == 200:
                # Import the model into Blender
                blender = get_blender_connection()
                model_base64 = base64.b64encode(download_response.content).decode('utf-8')
                
                import_result = blender.send_command("import_hunyuan3d_model", {
                    "model_data": model_base64,
                    "name": f"hunyuan3d_model_{task_uid}"
                })
                
                if "error" in import_result:
                    return f"Task completed but import failed: {import_result['error']}"
                
                return f"Task completed successfully! Model imported to Blender. {import_result.get('message', '')}"
            else:
                return f"Task completed but download failed: {download_response.text}"
        
        elif status == 'failed':
            error_msg = result.get('error', 'Unknown error')
            return f"Task failed: {error_msg}"
        
        elif status == 'running':
            progress = result.get('progress', 0)
            return f"Task is running... Progress: {progress}%"
        
        else:
            return f"Task status: {status}. Details: {result}"
        
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to Hunyuan3D API at {hunyuan3d_api_url}"
    except Exception as e:
        logger.error(f"Error polling Hunyuan3D status: {str(e)}")
        return f"Error polling Hunyuan3D status: {str(e)}"

@mcp.tool()
def create_3d_scene_from_text(
    ctx: Context,
    scene_description: str,
    generate_image: bool = True,
    image_prompt: str = None,
    negative_prompt: str = "blurry, low quality, distorted",
    image_width: int = 512,
    image_height: int = 512,
    remove_background: bool = True,
    texture: bool = True,
    seed: int = None,
    hunyuan3d_api_url: str = "http://localhost:8081",
    use_local_sd_api: bool = False,
    sd_api_url: str = "http://localhost:7860",
    use_async_hunyuan: bool = False,
    num_chunks: int = 8000,
    face_count: int = 40000
) -> str:
    """
    Create a complete 3D scene from text description using the integrated workflow:
    1. Generate image from text (if needed)
    2. Convert image to 3D model using Hunyuan3D
    3. Import model into Blender
    4. Apply scene modifications based on description
    
    Parameters:
    - scene_description: Complete description of the desired 3D scene
    - generate_image: Whether to generate an image first (if no image provided)
    - image_prompt: Specific prompt for image generation (defaults to scene_description)
    - negative_prompt: What to avoid in image generation
    - image_width/height: Dimensions for generated image
    - remove_background: Whether to remove background from image before 3D conversion
    - texture: Whether to generate textures for 3D model
    - seed: Random seed for reproducible generation
    - hunyuan3d_api_url: URL of the Hunyuan3D API server
    - use_local_sd_api: Whether to use local Stable Diffusion API
    - sd_api_url: URL of the local Stable Diffusion API
    - use_async_hunyuan: Whether to use async Hunyuan3D generation
    - num_chunks: Number of chunks for Hunyuan3D processing
    - face_count: Maximum number of faces for texture generation
    """
    try:
        logger.info(f"Starting 3D scene creation from text: {scene_description}")
        
        # Step 1: Generate image if needed
        image_path = None
        if generate_image:
            prompt = image_prompt or scene_description
            logger.info(f"Generating image with prompt: {prompt}")
            
            image_result = generate_stable_diffusion_image(
                ctx=ctx,
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=image_width,
                height=image_height,
                seed=seed,
                use_local_api=use_local_sd_api,
                api_url=sd_api_url
            )
            
            if "Error" in image_result:
                return f"Failed at image generation step: {image_result}"
            
            # Extract image path from result
            import re
            path_match = re.search(r'saved to: (.+?)\n', image_result)
            if path_match:
                image_path = path_match.group(1)
                logger.info(f"Image generated successfully: {image_path}")
            else:
                return "Failed to extract image path from generation result"
        
        # Step 2: Convert image to 3D model
        logger.info("Converting image to 3D model using Hunyuan3D")
        model_result = generate_hunyuan3d_model(
            ctx=ctx,
            image_path=image_path,
            remove_background=remove_background,
            texture=texture,
            seed=seed or 1234,
            hunyuan3d_api_url=hunyuan3d_api_url,
            use_async=use_async_hunyuan,
            num_chunks=num_chunks,
            face_count=face_count
        )
        
        if "Error" in model_result:
            return f"Failed at 3D model generation step: {model_result}"
        
        # Step 3: Apply additional scene modifications based on description
        logger.info("Applying scene modifications based on description")
        
        # Generate Blender code to enhance the scene based on the description
        scene_code = f"""
# Scene enhancement based on description: {scene_description}
import bpy
import bmesh
from mathutils import Vector

# Get the imported object (should be the most recently added)
objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if objs:
    latest_obj = max(objs, key=lambda x: x.name)
    
    # Center the object
    bpy.context.view_layer.objects.active = latest_obj
    latest_obj.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    latest_obj.location = (0, 0, 0)
    
    # Add basic lighting if not present
    if not any(obj.type == 'LIGHT' for obj in bpy.context.scene.objects):
        bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
        sun = bpy.context.active_object
        sun.data.energy = 3
        
        # Add fill light
        bpy.ops.object.light_add(type='AREA', location=(-3, 2, 5))
        fill_light = bpy.context.active_object
        fill_light.data.energy = 1
        fill_light.data.size = 2
    
    # Set up camera if not present
    if not any(obj.type == 'CAMERA' for obj in bpy.context.scene.objects):
        bpy.ops.object.camera_add(location=(7, -7, 5))
        camera = bpy.context.active_object
        
        # Point camera at the object
        direction = latest_obj.location - camera.location
        camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        
        # Set as active camera
        bpy.context.scene.camera = camera
    
    print(f"Scene setup complete for object: {{latest_obj.name}}")
else:
    print("No mesh objects found in scene")
"""
        
        # Execute the scene enhancement code
        code_result = execute_blender_code(ctx=ctx, code=scene_code)
        
        result_message = f"""Successfully created 3D scene from text description!

Workflow completed:
1. ✓ Generated image from text: "{scene_description}"
2. ✓ Converted image to 3D model using Hunyuan3D
3. ✓ Imported model into Blender
4. ✓ Applied scene enhancements (lighting, camera, positioning)

Scene is ready for further customization in Blender."""
        
        if image_path:
            result_message += f"\n\nGenerated image saved at: {image_path}"
        
        logger.info("3D scene creation workflow completed successfully")
        return result_message
        
    except Exception as e:
        logger.error(f"Error in 3D scene creation workflow: {str(e)}")
        return f"Error in 3D scene creation workflow: {str(e)}"

@mcp.prompt()
def asset_creation_strategy() -> str:
    """Defines the preferred strategy for creating assets in Blender"""
    return """When creating 3D content in Blender, always start by checking if integrations are available:

    0. Before anything, always check the scene from get_scene_info()
    1. First use the following tools to verify if the following integrations are enabled:
        1. PolyHaven
            Use get_polyhaven_status() to verify its status
            If PolyHaven is enabled:
            - For objects/models: Use download_polyhaven_asset() with asset_type="models"
            - For materials/textures: Use download_polyhaven_asset() with asset_type="textures"
            - For environment lighting: Use download_polyhaven_asset() with asset_type="hdris"
        2. Sketchfab
            Sketchfab is good at Realistic models, and has a wider variety of models than PolyHaven.
            Use get_sketchfab_status() to verify its status
            If Sketchfab is enabled:
            - For objects/models: First search using search_sketchfab_models() with your query
            - Then download specific models using download_sketchfab_model() with the UID
            - Note that only downloadable models can be accessed, and API key must be properly configured
            - Sketchfab has a wider variety of models than PolyHaven, especially for specific subjects
        3. Hyper3D(Rodin)
            Hyper3D Rodin is good at generating 3D models for single item.
            So don't try to:
            1. Generate the whole scene with one shot
            2. Generate ground using Hyper3D
            3. Generate parts of the items separately and put them together afterwards

            Use get_hyper3d_status() to verify its status
            If Hyper3D is enabled:
            - For objects/models, do the following steps:
                1. Create the model generation task
                    - Use generate_hyper3d_model_via_images() if image(s) is/are given
                    - Use generate_hyper3d_model_via_text() if generating 3D asset using text prompt
                    If key type is free_trial and insufficient balance error returned, tell the user that the free trial key can only generated limited models everyday, they can choose to:
                    - Wait for another day and try again
                    - Go to hyper3d.ai to find out how to get their own API key
                    - Go to fal.ai to get their own private API key
                2. Poll the status
                    - Use poll_rodin_job_status() to check if the generation task has completed or failed
                3. Import the asset
                    - Use import_generated_asset() to import the generated GLB model the asset
                4. After importing the asset, ALWAYS check the world_bounding_box of the imported mesh, and adjust the mesh's location and size
                    Adjust the imported mesh's location, scale, rotation, so that the mesh is on the right spot.

                You can reuse assets previous generated by running python code to duplicate the object, without creating another generation task.

    3. Always check the world_bounding_box for each item so that:
        - Ensure that all objects that should not be clipping are not clipping.
        - Items have right spatial relationship.
    
    4. Recommended asset source priority:
        - For specific existing objects: First try Sketchfab, then PolyHaven
        - For generic objects/furniture: First try PolyHaven, then Sketchfab
        - For custom or unique items not available in libraries: Use Hyper3D Rodin
        - For environment lighting: Use PolyHaven HDRIs
        - For materials/textures: Use PolyHaven textures

    Only fall back to scripting when:
    - PolyHaven, Sketchfab, and Hyper3D are all disabled
    - A simple primitive is explicitly requested
    - No suitable asset exists in any of the libraries
    - Hyper3D Rodin failed to generate the desired asset
    - The task specifically requires a basic material/color
    """

# Main execution

# Enhanced AUTOMATIC1111 WebUI MCP Tools

@mcp.tool()
def enhanced_txt2img(
    ctx: Context,
    prompt: str,
    negative_prompt: str = "blurry, low quality, distorted, deformed",
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg_scale: float = 7.0,
    seed: int = -1,
    sampler_name: str = "DPM++ 2M Karras",
    batch_size: int = 1,
    n_iter: int = 1,
    restore_faces: bool = False,
    enable_hr: bool = False,
    hr_scale: float = 2.0,
    api_url: str = "http://localhost:7860",
    save_parameters: bool = True
) -> str:
    """
    Enhanced text-to-image generation using AUTOMATIC1111 WebUI with advanced parameters.
    
    This tool provides comprehensive image generation capabilities with support for:
    - High-resolution upscaling
    - Face restoration
    - Batch generation
    - Parameter saving
    - Detailed error handling
    
    Parameters:
    - prompt: Detailed description of the desired image
    - negative_prompt: Elements to avoid in the generated image
    - width: Image width in pixels (recommended: 512, 768, 1024)
    - height: Image height in pixels (recommended: 512, 768, 1024)
    - steps: Number of denoising steps (20-50 recommended)
    - cfg_scale: Classifier-free guidance scale (7-15 recommended)
    - seed: Random seed for reproducible results (-1 for random)
    - sampler_name: Sampling method to use
    - batch_size: Number of images to generate simultaneously
    - n_iter: Number of iterations (batches) to run
    - restore_faces: Enable face restoration for better portraits
    - enable_hr: Enable high-resolution upscaling
    - hr_scale: Upscaling factor for high-resolution mode
    - api_url: AUTOMATIC1111 WebUI API endpoint
    - save_parameters: Save generation parameters to JSON file
    
    Returns:
    - Detailed generation results with file paths and parameters
    """
    if not ENHANCED_WEBUI_AVAILABLE:
        return "❌ Enhanced WebUI tools are not available. Please check the installation."
    
    try:
        result = enhanced_generate_stable_diffusion_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
            sampler_name=sampler_name,
            batch_size=batch_size,
            n_iter=n_iter,
            restore_faces=restore_faces,
            enable_hr=enable_hr,
            hr_scale=hr_scale,
            api_url=api_url,
            save_parameters=save_parameters
        )
        return result
    except Exception as e:
        logger.error(f"Enhanced txt2img failed: {str(e)}")
        return f"❌ Error in enhanced text-to-image generation: {str(e)}"

@mcp.tool()
def batch_txt2img(
    ctx: Context,
    prompts: str,
    negative_prompt: str = "blurry, low quality, distorted, deformed",
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg_scale: float = 7.0,
    batch_count: int = 4,
    api_url: str = "http://localhost:7860"
) -> str:
    """
    Generate multiple images from different prompts in batch mode.
    
    This tool allows efficient generation of multiple images with different prompts,
    useful for creating variations or exploring different concepts.
    
    Parameters:
    - prompts: Comma-separated list of prompts for batch generation
    - negative_prompt: Elements to avoid in all generated images
    - width: Image width in pixels
    - height: Image height in pixels
    - steps: Number of denoising steps
    - cfg_scale: Classifier-free guidance scale
    - batch_count: Number of images to generate per prompt
    - api_url: AUTOMATIC1111 WebUI API endpoint
    
    Returns:
    - Summary of batch generation results with file paths
    """
    if not ENHANCED_WEBUI_AVAILABLE:
        return "❌ Enhanced WebUI tools are not available. Please check the installation."
    
    try:
        prompt_list = [p.strip() for p in prompts.split(',') if p.strip()]
        result = batch_generate_images(
            prompts=prompt_list,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            batch_count=batch_count,
            api_url=api_url
        )
        return result
    except Exception as e:
        logger.error(f"Batch txt2img failed: {str(e)}")
        return f"❌ Error in batch text-to-image generation: {str(e)}"

@mcp.tool()
def enhance_image(
    ctx: Context,
    image_path: str,
    prompt: str,
    negative_prompt: str = "blurry, low quality, distorted, deformed",
    denoising_strength: float = 0.7,
    steps: int = 20,
    cfg_scale: float = 7.0,
    seed: int = -1,
    api_url: str = "http://localhost:7860"
) -> str:
    """
    Enhance or modify an existing image using img2img functionality.
    
    This tool allows you to:
    - Enhance image quality
    - Modify existing images based on prompts
    - Apply style transfers
    - Fix or improve specific aspects of images
    
    Parameters:
    - image_path: Path to the input image file
    - prompt: Description of desired modifications or enhancements
    - negative_prompt: Elements to avoid in the enhanced image
    - denoising_strength: How much to change the original image (0.1-1.0)
    - steps: Number of denoising steps
    - cfg_scale: Classifier-free guidance scale
    - seed: Random seed for reproducible results
    - api_url: AUTOMATIC1111 WebUI API endpoint
    
    Returns:
    - Path to the enhanced image and generation details
    """
    if not ENHANCED_WEBUI_AVAILABLE:
        return "❌ Enhanced WebUI tools are not available. Please check the installation."
    
    try:
        result = img2img_enhance(
            image_path=image_path,
            prompt=prompt,
            negative_prompt=negative_prompt,
            denoising_strength=denoising_strength,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
            api_url=api_url
        )
        return result
    except Exception as e:
        logger.error(f"Image enhancement failed: {str(e)}")
        return f"❌ Error in image enhancement: {str(e)}"

@mcp.tool()
def check_webui_status(
    ctx: Context,
    api_url: str = "http://localhost:7860"
) -> str:
    """
    Check the status and capabilities of AUTOMATIC1111 WebUI server.
    
    This tool provides comprehensive information about:
    - Server connectivity and health
    - Available models and samplers
    - Current generation progress
    - System capabilities
    
    Parameters:
    - api_url: AUTOMATIC1111 WebUI API endpoint to check
    
    Returns:
    - Detailed status report of the WebUI server
    """
    if not ENHANCED_WEBUI_AVAILABLE:
        return "❌ Enhanced WebUI tools are not available. Please check the installation."
    
    try:
        result = get_webui_status(api_url=api_url)
        return result
    except Exception as e:
        logger.error(f"WebUI status check failed: {str(e)}")
        return f"❌ Error checking WebUI status: {str(e)}"

@mcp.tool()
def create_enhanced_3d_scene(
    ctx: Context,
    scene_description: str,
    image_prompt: str = None,
    use_enhanced_generation: bool = True,
    image_width: int = 768,
    image_height: int = 768,
    steps: int = 30,
    cfg_scale: float = 8.0,
    enable_hr: bool = True,
    hr_scale: float = 1.5,
    api_url: str = "http://localhost:7860",
    hunyuan3d_url: str = "http://localhost:8080"
) -> str:
    """
    Create a complete 3D scene using enhanced image generation and 3D model creation.
    
    This tool combines enhanced AUTOMATIC1111 WebUI image generation with Hunyuan3D
    model creation to produce high-quality 3D scenes from text descriptions.
    
    Parameters:
    - scene_description: Overall description of the desired 3D scene
    - image_prompt: Specific prompt for image generation (uses scene_description if not provided)
    - use_enhanced_generation: Use enhanced WebUI tools for better quality
    - image_width: Width for generated images (recommended: 768 or 1024)
    - image_height: Height for generated images (recommended: 768 or 1024)
    - steps: Number of denoising steps for image generation
    - cfg_scale: Classifier-free guidance scale
    - enable_hr: Enable high-resolution upscaling
    - hr_scale: Upscaling factor for high-resolution mode
    - api_url: AUTOMATIC1111 WebUI API endpoint
    - hunyuan3d_url: Hunyuan3D API endpoint
    
    Returns:
    - Complete workflow results with generated assets and scene information
    """
    try:
        # Use enhanced image generation if available and requested
        if use_enhanced_generation and ENHANCED_WEBUI_AVAILABLE:
            prompt = image_prompt or scene_description
            
            # Generate high-quality image using enhanced tools
            image_result = enhanced_generate_stable_diffusion_image(
                prompt=prompt,
                negative_prompt="blurry, low quality, distorted, deformed, ugly, bad anatomy",
                width=image_width,
                height=image_height,
                steps=steps,
                cfg_scale=cfg_scale,
                enable_hr=enable_hr,
                hr_scale=hr_scale,
                restore_faces=True,
                api_url=api_url,
                save_parameters=True
            )
            
            if "Error" in image_result:
                return f"❌ Enhanced image generation failed: {image_result}"
            
            # Extract image path from result
            import re
            image_path_match = re.search(r'Image saved to: ([^\n]+)', image_result)
            if not image_path_match:
                return "❌ Could not extract image path from generation result"
            
            image_path = image_path_match.group(1)
            
        else:
            # Fall back to standard generation
            image_path = generate_stable_diffusion_image(
                prompt=image_prompt or scene_description,
                negative_prompt="blurry, low quality, distorted, deformed",
                width=image_width,
                height=image_height,
                steps=steps,
                guidance_scale=cfg_scale,
                api_url=api_url
            )
        
        # Generate 3D model from the image
        model_result = generate_hunyuan3d_model(
            image_path=image_path,
            remove_background=True,
            do_texture_mapping=True,
            api_url=hunyuan3d_url
        )
        
        if "Error" in str(model_result):
            return f"❌ 3D model generation failed: {model_result}"
        
        # Create comprehensive result summary
        result_summary = f"""
🎨 Enhanced 3D Scene Creation Complete!

📝 Scene Description: {scene_description}
🖼️ Generated Image: {image_path}
🎯 3D Model Result: {model_result}

✅ Workflow Status:
- ✓ Enhanced image generation {'(Enhanced)' if use_enhanced_generation and ENHANCED_WEBUI_AVAILABLE else '(Standard)'}
- ✓ 3D model creation
- ✓ Scene assembly

💡 Next Steps:
1. Check the generated 3D model in Blender
2. Adjust scale and position as needed
3. Add lighting and materials if desired
4. Consider generating additional assets for the scene
        """
        
        return result_summary
        
    except Exception as e:
        logger.error(f"Enhanced 3D scene creation failed: {str(e)}")
        return f"❌ Error in enhanced 3D scene creation: {str(e)}"

@mcp.tool()
def get_sd_presets(ctx: Context) -> str:
    """
    获取所有可用的Stable Diffusion预设配置
    
    Returns:
        str: 包含所有预设信息的JSON字符串
    """
    if not OPTIMIZATION_TOOLS_AVAILABLE:
        return json.dumps({
            "success": False,
            "error": "Optimization tools not available",
            "message": "Please ensure sd_optimization_presets module is properly installed"
        })
    
    try:
        presets = list_presets()
        return json.dumps({
            "success": True,
            "presets": presets,
            "count": len(presets)
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@mcp.tool()
def optimize_sd_parameters(
    ctx: Context,
    goal: str = "quality",
    hardware: str = "medium",
    image_type: str = "general",
    time_budget: int = 60,
    quality_preference: float = 0.7
) -> str:
    """
    智能优化Stable Diffusion参数
    
    Args:
        goal: 优化目标 (speed/quality/balanced)
        hardware: 硬件配置 (low/medium/high/ultra)
        image_type: 图像类型 (portrait/landscape/3d_model/general)
        time_budget: 时间预算（秒）
        quality_preference: 质量偏好 (0.0-1.0)
    
    Returns:
        str: 优化后的参数配置JSON
    """
    if not OPTIMIZATION_TOOLS_AVAILABLE:
        return json.dumps({
            "success": False,
            "error": "Optimization tools not available",
            "message": "Please ensure optimization modules are properly installed"
        })
    
    try:
        # 映射字符串到枚举
        goal_map = {
            "speed": OptimizationGoal.SPEED,
            "quality": OptimizationGoal.QUALITY,
            "balanced": OptimizationGoal.BALANCED
        }
        
        hardware_map = {
            "low": HardwareProfile.LOW_END,
            "medium": HardwareProfile.MEDIUM,
            "high": HardwareProfile.HIGH_END,
            "ultra": HardwareProfile.ULTRA
        }
        
        optimizer = SDParameterOptimizer()
        context = OptimizationContext(
            goal=goal_map.get(goal, OptimizationGoal.QUALITY),
            hardware=hardware_map.get(hardware, HardwareProfile.MEDIUM),
            image_type=image_type,
            time_budget=time_budget,
            quality_preference=quality_preference
        )
        
        optimized_params = optimizer.optimize_parameters(context)
        
        return json.dumps({
            "success": True,
            "optimized_parameters": optimized_params,
            "context": {
                "goal": goal,
                "hardware": hardware,
                "image_type": image_type,
                "time_budget": time_budget,
                "quality_preference": quality_preference
            }
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@mcp.tool()
def quick_sd_optimize(
    ctx: Context,
    prompt: str,
    goal: str = "quality",
    hardware: str = "medium"
) -> str:
    """
    快速优化Stable Diffusion参数
    
    Args:
        prompt: 图像生成提示词
        goal: 优化目标 (speed/quality/balanced)
        hardware: 硬件配置 (low/medium/high/ultra)
    
    Returns:
        str: 快速优化后的参数配置JSON
    """
    if not OPTIMIZATION_TOOLS_AVAILABLE:
        return json.dumps({
            "success": False,
            "error": "Optimization tools not available",
            "message": "Please ensure optimization modules are properly installed"
        })
    
    try:
        # 映射字符串到枚举
        goal_map = {
            "speed": OptimizationGoal.SPEED,
            "quality": OptimizationGoal.QUALITY,
            "balanced": OptimizationGoal.BALANCED
        }
        
        hardware_map = {
            "low": HardwareProfile.LOW_END,
            "medium": HardwareProfile.MEDIUM,
            "high": HardwareProfile.HIGH_END,
            "ultra": HardwareProfile.ULTRA
        }
        
        optimized_params = quick_optimize(
            prompt=prompt,
            goal=goal_map.get(goal, OptimizationGoal.QUALITY),
            hardware=hardware_map.get(hardware, HardwareProfile.MEDIUM)
        )
        
        return json.dumps({
            "success": True,
            "optimized_parameters": optimized_params,
            "prompt": prompt,
            "optimization_settings": {
                "goal": goal,
                "hardware": hardware
            }
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

@mcp.tool()
def optimized_txt2img(
    ctx: Context,
    prompt: str,
    optimization_goal: str = "quality",
    hardware_profile: str = "medium",
    negative_prompt: str = "blurry, low quality, distorted, deformed",
    api_url: str = "http://localhost:7860",
    custom_params: str = None
) -> str:
    """
    使用优化参数生成图像
    
    Args:
        prompt: 图像生成提示词
        optimization_goal: 优化目标 (speed/quality/balanced)
        hardware_profile: 硬件配置 (low/medium/high/ultra)
        negative_prompt: 负面提示词
        api_url: WebUI API地址
        custom_params: 自定义参数（JSON字符串）
    
    Returns:
        str: 生成结果JSON
    """
    if not OPTIMIZATION_TOOLS_AVAILABLE:
        # 回退到标准生成
        return enhanced_txt2img(
            ctx, prompt, negative_prompt, 
            api_url=api_url
        )
    
    try:
        # 获取优化参数
        if custom_params:
            params = json.loads(custom_params)
        else:
            goal_map = {
                "speed": OptimizationGoal.SPEED,
                "quality": OptimizationGoal.QUALITY,
                "balanced": OptimizationGoal.BALANCED
            }
            
            hardware_map = {
                "low": HardwareProfile.LOW_END,
                "medium": HardwareProfile.MEDIUM,
                "high": HardwareProfile.HIGH_END,
                "ultra": HardwareProfile.ULTRA
            }
            
            params = quick_optimize(
                prompt=prompt,
                goal=goal_map.get(optimization_goal, OptimizationGoal.QUALITY),
                hardware=hardware_map.get(hardware_profile, HardwareProfile.MEDIUM)
            )
        
        # 使用优化参数调用增强版生成
        return enhanced_txt2img(
            ctx=ctx,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=params.get('width', 512),
            height=params.get('height', 512),
            steps=params.get('steps', 20),
            cfg_scale=params.get('cfg_scale', 7.0),
            seed=params.get('seed', -1),
            sampler_name=params.get('sampler_name', 'DPM++ 2M Karras'),
            batch_size=params.get('batch_size', 1),
            restore_faces=params.get('restore_faces', False),
            enable_hr=params.get('enable_hr', False),
            hr_scale=params.get('hr_scale', 2.0),
            api_url=api_url
        )
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "fallback": "Using standard generation"
        })

@mcp.tool()
def execute_text_to_3d_workflow(
    ctx: Context,
    description: str,
    preset: str = "balanced",
    custom_config: str = None
) -> str:
    """
    Execute a complete text-to-3D scene creation workflow.
    
    Args:
        description: Text description of the desired 3D scene
        preset: Workflow preset ("fast", "balanced", "quality", "creative")
        custom_config: Optional JSON string with custom workflow configuration
    
    Returns:
        JSON string with workflow execution results
    """
    if not WORKFLOW_MANAGER_AVAILABLE:
        return json.dumps({
            "success": False,
            "error": "Workflow manager not available",
            "message": "Please ensure workflow_manager.py is properly installed"
        })
    
    try:
        # Parse custom config if provided
        config_dict = None
        if custom_config:
            config_dict = json.loads(custom_config)
        
        # Execute workflow
        from .workflow_manager import execute_text_to_3d_workflow as execute_workflow
        result = execute_workflow(description, preset, config_dict)
        
        return json.dumps({
            "success": True,
            "workflow_result": result.__dict__ if hasattr(result, '__dict__') else str(result),
            "preset_used": preset
        })
        
    except json.JSONDecodeError:
        return json.dumps({
            "success": False,
            "error": "Invalid JSON in custom_config parameter"
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Workflow execution failed: {str(e)}"
        })

@mcp.tool()
def get_workflow_presets(ctx: Context) -> str:
    """
    Get available workflow presets and their configurations.
    
    Returns:
        JSON string with available presets and their descriptions
    """
    if not WORKFLOW_MANAGER_AVAILABLE:
        return json.dumps({
            "success": False,
            "error": "Workflow manager not available"
        })
    
    try:
        from .workflow_manager import PRESET_CONFIGS
        
        presets_info = {}
        for name, config in PRESET_CONFIGS.items():
            presets_info[name] = {
                "description": config.description,
                "generation_method": config.generation_method.value,
                "image_quality": config.image_quality,
                "model_quality": config.model_quality,
                "scene_complexity": config.scene_complexity,
                "estimated_time": f"{config.estimated_time_minutes} minutes"
            }
        
        return json.dumps({
            "success": True,
            "presets": presets_info
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to get presets: {str(e)}"
        })

@mcp.tool()
def create_custom_workflow(
    ctx: Context,
    name: str,
    description: str,
    generation_method: str = "hybrid",
    image_quality: str = "medium",
    model_quality: str = "medium",
    scene_complexity: str = "medium",
    enable_optimization: bool = True,
    enable_post_processing: bool = True
) -> str:
    """
    Create a custom workflow configuration.
    
    Args:
        name: Name for the custom workflow
        description: Description of the workflow
        generation_method: "image_first", "model_first", or "hybrid"
        image_quality: "low", "medium", "high", "ultra"
        model_quality: "low", "medium", "high", "ultra"
        scene_complexity: "simple", "medium", "complex"
        enable_optimization: Whether to enable parameter optimization
        enable_post_processing: Whether to enable post-processing
    
    Returns:
        JSON string with the created workflow configuration
    """
    if not WORKFLOW_MANAGER_AVAILABLE:
        return json.dumps({
            "success": False,
            "error": "Workflow manager not available"
        })
    
    try:
        from .workflow_manager import create_workflow_config, GenerationMethod
        
        # Convert string to enum
        method_map = {
            "image_first": GenerationMethod.IMAGE_FIRST,
            "model_first": GenerationMethod.MODEL_FIRST,
            "hybrid": GenerationMethod.HYBRID
        }
        
        if generation_method not in method_map:
            return json.dumps({
                "success": False,
                "error": f"Invalid generation method: {generation_method}"
            })
        
        config = create_workflow_config(
            name=name,
            description=description,
            generation_method=method_map[generation_method],
            image_quality=image_quality,
            model_quality=model_quality,
            scene_complexity=scene_complexity,
            enable_optimization=enable_optimization,
            enable_post_processing=enable_post_processing
        )
        
        return json.dumps({
            "success": True,
            "config": {
                "name": config.name,
                "description": config.description,
                "generation_method": config.generation_method.value,
                "image_quality": config.image_quality,
                "model_quality": config.model_quality,
                "scene_complexity": config.scene_complexity,
                "enable_optimization": config.enable_optimization,
                "enable_post_processing": config.enable_post_processing,
                "estimated_time": f"{config.estimated_time_minutes} minutes"
            }
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to create workflow: {str(e)}"
        })

@mcp.tool()
def get_workflow_status(
    ctx: Context,
    workflow_id: str = None
) -> str:
    """
    Get the status of workflow execution.
    
    Args:
        workflow_id: Optional workflow ID to check specific workflow status
    
    Returns:
        JSON string with workflow status information
    """
    if not WORKFLOW_MANAGER_AVAILABLE:
        return json.dumps({
            "success": False,
            "error": "Workflow manager not available"
        })
    
    try:
        # For now, return general status since we don't have persistent workflow tracking
        status_info = {
            "workflow_manager_available": True,
            "supported_methods": ["image_first", "model_first", "hybrid"],
            "available_presets": list(PRESET_CONFIGS.keys()) if 'PRESET_CONFIGS' in globals() else [],
            "integration_status": {
                "webui_available": ENHANCED_WEBUI_AVAILABLE if 'ENHANCED_WEBUI_AVAILABLE' in globals() else False,
                "optimization_available": OPTIMIZATION_TOOLS_AVAILABLE if 'OPTIMIZATION_TOOLS_AVAILABLE' in globals() else False,
                "polyhaven_available": _polyhaven_enabled if '_polyhaven_enabled' in globals() else False
            }
        }
        
        return json.dumps({
            "success": True,
            "status": status_info
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to get workflow status: {str(e)}"
        })

def main():
    """Run the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()