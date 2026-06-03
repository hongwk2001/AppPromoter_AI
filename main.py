import os
import sys
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="AppPromoter AI Orchestrator")
    parser.add_argument("--app", default="npc-aggregator", help="Application key (defined in config.json)")
    parser.add_argument("--actions", default=None, help="Comma-separated actions: record, write, stitch, outreach, upload")
    parser.add_argument("--autonomous", action="store_true", help="Run full pipeline autonomously (record, write, stitch, outreach)")
    parser.add_argument("--dry-run", action="store_true", help="Force dry-run simulation mode (skips upload, runs simulated outreach)")
    
    args = parser.parse_args()
    
    if args.autonomous:
        # Autonomous mode runs all generation steps, skipping dangerous upload step
        actions = ["record", "write", "stitch", "outreach"]
    elif args.actions:
        actions = [a.strip() for a in args.actions.split(",")]
    else:
        # Default fallback
        actions = ["write"]
        
    if "record" in actions:
        print("\n=== Action: Recording App UI via Playwright ===")
        try:
            subprocess.run(["node", "recorder.js", args.app], check=True)
        except Exception as e:
            print(f"Error running Playwright recorder: {e}", file=sys.stderr)
            
    if "write" in actions:
        print("\n=== Action: Generating Copywriting Assets via Gemini ===")
        try:
            subprocess.run([sys.executable, "copywriter.py", args.app], check=True)
        except Exception as e:
            print(f"Error running Gemini copywriter: {e}", file=sys.stderr)
            
    if "stitch" in actions:
        print("\n=== Action: Stitching Video, Audio & Captions ===")
        try:
            subprocess.run([sys.executable, "stitcher.py", args.app], check=True)
        except Exception as e:
            print(f"Error running stitcher: {e}", file=sys.stderr)
            
    if "outreach" in actions:
        print("\n=== Action: Sending Personalized Outreach Emails ===")
        try:
            cmd = [sys.executable, "outreach.py", args.app]
            if args.dry_run:
                cmd.append("--dry-run")
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"Error running outreach engine: {e}", file=sys.stderr)
            
    if "upload" in actions:
        if args.dry_run:
            print("\n=== Action: Uploading Stitched Video to YouTube [SKIPPED - DRY RUN ACTIVE] ===")
        else:
            print("\n=== Action: Uploading Stitched Video to YouTube ===")
            try:
                subprocess.run([sys.executable, "upload_youtube.py", args.app], check=True)
            except Exception as e:
                print(f"Error running YouTube uploader: {e}", file=sys.stderr)
                
    if "instagram" in actions:
        print("\n=== Action: Publishing Video to Instagram via Playwright ===")
        try:
            subprocess.run(["node", "publish_instagram.js", args.app], check=True)
        except Exception as e:
            print(f"Error publishing to Instagram: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
