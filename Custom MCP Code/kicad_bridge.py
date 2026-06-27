import os
import re
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("KiCad-Direct")

PROJECT_DIR = "/Users/aryanruia/Documents/Rocketry/ARC27/Flight Computer/FlightComputer"

def _find_pcb_file(explicit_name: str) -> str:
    """Helper to find the real pcb filename if the default isn't quite right."""
    if explicit_name and os.path.exists(os.path.join(PROJECT_DIR, explicit_name)):
        return explicit_name
    # Fallback search if the default filename doesn't exist
    for f in os.listdir(PROJECT_DIR):
        if f.endswith(".kicad_pcb"):
            return f
    return explicit_name

@mcp.tool()
def list_my_files() -> str:
    """Lists all files in the flight computer project directory."""
    try:
        files = os.listdir(PROJECT_DIR)
        return "\n".join(files)
    except Exception as e:
        return f"Error reading directory: {str(e)}"

@mcp.tool()
def read_project_file(filename: str) -> str:
    """Reads small project files entirely (like schematics, reports, or logs)."""
    safe_name = os.path.basename(filename)
    target_path = os.path.join(PROJECT_DIR, safe_name)
    
    if os.path.exists(target_path) and os.path.getsize(target_path) > 2 * 1024 * 1024:
        return "Error: This file is larger than 2MB. Please use 'search_pcb_file' or 'get_pcb_component' to inspect it safely."

    try:
        with open(target_path, "r", errors="ignore") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def search_pcb_file(keyword: str, file_name: str = "flight_computer.kicad_pcb") -> str:
    """Searches a large PCB file for a specific keyword (like a Net name, Pin, or Component ref) and returns matching lines."""
    real_file = _find_pcb_file(file_name)
    target_path = os.path.join(PROJECT_DIR, real_file)
    if not os.path.exists(target_path):
        return f"Error: PCB file '{real_file}' not found in directory."
    
    matches = []
    try:
        with open(target_path, "r", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                if keyword.lower() in line.lower():
                    matches.append(f"Line {i}: {line.strip()}")
                if len(matches) > 100:
                    matches.append("... [Truncated: Too many matches. Be more specific] ...")
                    break
        return "\n".join(matches) if matches else f"No matches found for '{keyword}'."
    except Exception as e:
        return f"Error scanning PCB: {str(e)}"

@mcp.tool()
def get_pcb_component(reference: str, file_name: str = "flight_computer.kicad_pcb") -> str:
    """Extracts the entire block configuration for a specific component (e.g., 'U1', 'C5') from the PCB layout file."""
    real_file = _find_pcb_file(file_name)
    target_path = os.path.join(PROJECT_DIR, real_file)
    if not os.path.exists(target_path):
        return f"Error: PCB file '{real_file}' not found."

    try:
        with open(target_path, "r", errors="ignore") as f:
            content = f.read()
        
        pattern = r"\(footprint\s+\"[^\"]*\"[^{}]*?\(uuid\s+\"[^\"]*\"\)[^{}]*?\(at\s+[^{}]*?\)[^{}]*?\(descr\s+\"[^\"]*\"\)[^{}]*?\(property\s+\"Reference\"\s+\"" + re.escape(reference) + r"\".*?\n\s*\)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(0)
        
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if f'"{reference}"' in line or f' {reference} ' in line:
                start = max(0, i - 5)
                end = min(len(lines), i + 25)
                return "\n".join(lines[start:end])
                
        return f"Component {reference} block not cleanly isolated."
    except Exception as e:
        return f"Error extracting component: {str(e)}"

# CRITICAL ENTRYPOINT: This runs the actual STDIO server pipe for Claude
if __name__ == "__main__":
    mcp.run(transport="stdio")