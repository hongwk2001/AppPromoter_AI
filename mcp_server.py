import os
import sys
import subprocess

# Ensure stdout is never polluted with print statements or logs.
# All logging and installation messages must go to sys.stderr.
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: 'mcp' package is not installed. Installing it to stderr...", file=sys.stderr)
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "mcp"],
        stdout=sys.stderr,
        stderr=sys.stderr,
        check=True
    )
    from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("AppPromoter AI Orchestrator")

@mcp.tool()
def run_app_promoter(app_name: str = "npc-aggregator", dry_run: bool = True) -> str:
    """
    Runs the AppPromoter UI recorder, copywriting asset generator, video stitcher,
    and simulated outreach campaign in a single autonomous pipeline run.
    
    Args:
        app_name: The application identifier defined in config.json (e.g., 'npc-aggregator' or 'golf-swing-ai').
        dry_run: Force dry-run simulation mode. If True, skips YouTube upload and live email sends.
    """
    cmd = [sys.executable, "main.py", "--app", app_name, "--autonomous"]
    if dry_run:
        cmd.append("--dry-run")
        
    try:
        # Run orchestrator and capture output
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return f"Pipeline execution completed successfully.\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error executing pipeline (exit code {e.returncode}).\n\nSTDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}"
    except Exception as e:
        return f"Unexpected error launching pipeline: {str(e)}"

if __name__ == "__main__":
    mcp.run()
