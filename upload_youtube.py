import os
import sys
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    """Initializes and returns the authenticated YouTube Data API v3 service client."""
    creds = None
    # token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
                
        if not creds:
            if not os.path.exists("client_secrets.json"):
                print("\n" + "="*80, file=sys.stderr)
                print("ERROR: Google API credentials file 'client_secrets.json' is missing.", file=sys.stderr)
                print("To run the YouTube uploader, please follow these steps:", file=sys.stderr)
                print("1. Go to Google Cloud Console (https://console.cloud.google.com/)", file=sys.stderr)
                print("2. Enable the 'YouTube Data API v3' for your project.", file=sys.stderr)
                print("3. Configure the OAuth Consent Screen (add your email as a Test User!).", file=sys.stderr)
                print("4. Create 'OAuth client ID' credentials of type 'Desktop app'.", file=sys.stderr)
                print("5. Download the credentials JSON, rename it to 'client_secrets.json',", file=sys.stderr)
                print("   and place it in the root folder of this project.", file=sys.stderr)
                print("="*80 + "\n", file=sys.stderr)
                sys.exit(1)
                
            flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            
    return build("youtube", "v3", credentials=creds)

def main_upload(app_key, video_file_override=None, title_override=None, desc_override=None):
    # Load configuration
    if not os.path.exists("config.json"):
        print("Error: config.json not found.", file=sys.stderr)
        sys.exit(1)
        
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        
    app_config = config["apps"].get(app_key)
    if not app_config:
        print(f"Error: App key '{app_key}' not found in config.json.", file=sys.stderr)
        sys.exit(1)
        
    if video_file_override:
        video_file = video_file_override
    else:
        output_dir = os.path.join("output", app_key)
        video_file = os.path.join(output_dir, "final_shorts.mp4")
    
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found.", file=sys.stderr)
        sys.exit(1)
        
    # Get authenticated client (this will prompt in browser if client_secrets.json is present)
    youtube = get_authenticated_service()
    
    # Configure metadata
    app_name = app_config.get("name", app_key)
    app_desc = app_config.get("description", "")
    app_url = app_config.get("url", "")
    
    if title_override:
        title = title_override
    else:
        title = f"{app_name} - AI App Showcase"
    if len(title) > 100:
        title = title[:95] + "..."
        
    if desc_override:
        description = desc_override
    else:
        description = (
            f"{app_desc}\n\n"
            f"Try out the application here: {app_url}\n\n"
            f"Automated launch demo generated using AppPromoter AI.\n\n"
            f"#Shorts #AppDemo #Software #AI #Launch"
        )
    
    # Resumable upload media setup
    media = MediaFileUpload(
        video_file,
        chunksize=1024 * 1024,  # 1MB chunk size
        mimetype="video/mp4",
        resumable=True
    )
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [app_key, "AI Showcase", "App Demo", "Shorts"],
            "categoryId": "27"  # Education category
        },
        "status": {
            "privacyStatus": "private"  # Default to Private for user safety and review
        }
    }
    
    print(f"\n=== Uploading Video to YouTube ===")
    print(f"Target file: '{video_file}'")
    print(f"Title: '{title}'")
    
    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%...")
                
        video_id = response.get("id")
        print("\n=== Video Upload Completed Successfully! ===")
        print(f"Video ID: {video_id}")
        print(f"Watch link (Private): https://www.youtube.com/watch?v={video_id}")
        print(f"Manage in YouTube Studio: https://studio.youtube.com/video/{video_id}/edit")
        
    except Exception as e:
        print(f"Error during video upload: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    app_key_arg = sys.argv[1] if len(sys.argv) > 1 else "npc-aggregator"
    if app_key_arg == "devlog":
        video_path = r"d:\git_repo\AppPromoter_AI\output\kb_html\reddit_replier_launch.mp4"
        title = "Building a KB-Driven Reddit Outreach Dashboard (Dev Log)"
        description = (
            "A 2-minute progress dev log detailing our journey building a local Reddit outreach dashboard.\n\n"
            "We cover:\n"
            "- Bypassing Reddit 403 blocks with public RSS search feeds\n"
            "- Handling Gemini token limit exhaustions\n"
            "- Running Gemma 2 locally using Ollama\n"
            "- Creating a custom dual-panel review GUI popup in Tkinter\n\n"
            "Live Web article: https://jigsawpuzzlehelper.com/reddit_replier/dev_journey_reddit_replier.html\n\n"
            "#developer #devlog #localLLM #ollama #gemma2 #tkinter #buildinpublic"
        )
        main_upload("npc-aggregator", video_file_override=video_path, title_override=title, desc_override=description)
    else:
        main_upload(app_key_arg)
