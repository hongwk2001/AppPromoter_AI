import os
import sys
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_marketing_assets(app_key):
    # Load configuration
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    app_config = config["apps"].get(app_key)
    if not app_config:
        print(f"App key '{app_key}' not found in config.json", file=sys.stderr)
        sys.exit(1)
        
    print(f"Generating copywriting assets for: {app_config['name']}")
    
    api_key = GEMINI_API_KEY or "AIzaSyDr5FH2c0HWbTgcRRFhRlX72a5jMyC50CE"
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    # Load Agent configuration (Operational Knowledge)
    config_path = os.path.join("agent_configs", "copywriter_agent.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            agent_config = json.load(f)
    else:
        agent_config = {
            "model": "gemini-2.5-flash",
            "temperature": 0.3,
            "system_instruction": "You are a copywriter.",
            "response_mime_type": "application/json"
        }

    # Load Guidelines (Domain Knowledge)
    guidelines_path = os.path.join("knowledge_base", "marketing_guidelines.md")
    guidelines_content = ""
    if os.path.exists(guidelines_path):
        with open(guidelines_path, "r", encoding="utf-8") as f:
            guidelines_content = f.read()

    # Load Few-Shot Trajectories (Behavioral Knowledge)
    few_shots_path = os.path.join("trajectories", "copywriter_few_shots.jsonl")
    few_shots_str = ""
    if os.path.exists(few_shots_path):
        with open(few_shots_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    few_shots_str += line + "\n"

    system_instruction = agent_config.get("system_instruction", "")
    
    prompt = (
        f"Generate copywriting launch assets for the following application:\n\n"
        f"App Name: {app_config['name']}\n"
        f"App URL: {app_config['url']}\n"
        f"App Description: {app_config['description']}\n"
        f"Target Audience: {app_config['target_audience']}\n\n"
    )

    if guidelines_content:
        prompt += f"Follow these strict design/tone guidelines:\n{guidelines_content}\n\n"

    if few_shots_str:
        prompt += f"Here are examples of correct formatting and trajectories:\n{few_shots_str}\n\n"

    prompt += "Ensure the JSON output complies strictly with the schema requested and matches these inputs."
    
    import time
    attempts = 4
    response = None
    for attempt in range(attempts):
        try:
            response = client.models.generate_content(
                model=agent_config.get("model", "gemini-2.5-flash"),
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=agent_config.get("temperature", 0.3),
                    response_mime_type=agent_config.get("response_mime_type", "application/json"),
                ),
                contents=prompt,
            )
            break
        except Exception as e:
            if "503" in str(e) and attempt < attempts - 1:
                print(f"Gemini servers busy (503). Retrying in 6 seconds (attempt {attempt+1}/{attempts})...")
                time.sleep(6)
            else:
                raise e
    
    output_dir = os.path.join("output", app_key)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        data = json.loads(response.text)
        
        # Save raw JSON
        with open(os.path.join(output_dir, "marketing_assets.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        # Format X Thread as Markdown
        with open(os.path.join(output_dir, "twitter_thread.md"), "w", encoding="utf-8") as f:
            f.write("# Twitter Thread Launch Copy\n\n")
            for i, tweet in enumerate(data.get("twitter_thread", [])):
                f.write(f"### Tweet {i+1}/4\n{tweet}\n\n---\n\n")
                
        # Format LinkedIn Post as Markdown
        with open(os.path.join(output_dir, "linkedin_post.md"), "w", encoding="utf-8") as f:
            f.write("# LinkedIn Launch Copy\n\n")
            f.write(data.get("linkedin_post", ""))
            
        # Format Email Template as Markdown
        with open(os.path.join(output_dir, "email_newsletter.md"), "w", encoding="utf-8") as f:
            f.write("# Email Newsletter outreach copy\n\n")
            f.write(data.get("email_newsletter", ""))
            
        # Format Video Script as Markdown
        with open(os.path.join(output_dir, "video_script.md"), "w", encoding="utf-8") as f:
            f.write("# 60-Second Video Script\n\n")
            f.write("| Time | Visual | Audio (Voiceover) | On-Screen Text |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            for scene in data.get("video_script", []):
                f.write(f"| {scene.get('Time')} | {scene.get('Visual')} | {scene.get('Audio')} | {scene.get('OnScreenText')} |\n")
                
        print(f"Marketing assets successfully generated and saved to: {output_dir}")
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        print(f"Raw response: {response.text}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    app_key_arg = sys.argv[1] if len(sys.argv) > 1 else "npc-aggregator"
    generate_marketing_assets(app_key_arg)
