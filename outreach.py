import os
import sys
import csv
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()

# Load SMTP configurations from .env
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

def parse_email_template(filepath):
    """Parses email_newsletter.md to extract Subject and Body content."""
    if not os.path.exists(filepath):
        print(f"Error: Email template not found at '{filepath}'", file=sys.stderr)
        sys.exit(1)
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split("\n")
    subject = "Product Launch Announcement"
    body_lines = []
    subject_found = False
    
    for line in lines:
        stripped = line.strip()
        # Skip markdown headers
        if stripped.startswith("#"):
            continue
        if stripped.lower().startswith("subject:"):
            subject = stripped[len("subject:"):].strip()
            subject_found = True
            continue
        # Collect body text
        if not subject_found and not stripped:
            continue
        body_lines.append(line)
        
    body = "\n".join(body_lines).strip()
    return subject, body

def personalize_text(text, name, organization):
    """Replaces common placeholders and renders Jinja2 formatting in text."""
    # Run Jinja2 render first
    try:
        template = Template(text)
        rendered = template.render(name=name, organization=organization)
    except Exception:
        rendered = text
        
    # Standard replacement dictionary for other placeholder styles
    replacements = {
        "{{name}}": name,
        "{{Name}}": name,
        "[Name]": name,
        "[Contact Name]": name,
        "{{organization}}": organization,
        "{{Organization}}": organization,
        "[Organization]": organization,
        "[School]": organization
    }
    for placeholder, val in replacements.items():
        if val:
            rendered = rendered.replace(placeholder, val)
            
    # Fallback greeting replacement if the template starts with a generic greeting
    if rendered.startswith("Dear Future College Student / Parent,"):
        rendered = rendered.replace(
            "Dear Future College Student / Parent,",
            f"Dear {name},"
        )
    elif rendered.startswith("Dear Golfer,"):
        rendered = rendered.replace(
            "Dear Golfer,",
            f"Dear {name},"
        )
        
    return rendered

def run_outreach(app_key, dry_run=False):
    # Load app configurations
    if not os.path.exists("config.json"):
        print("Error: config.json not found.", file=sys.stderr)
        sys.exit(1)
        
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        
    app_config = config["apps"].get(app_key)
    if not app_config:
        print(f"Error: App key '{app_key}' not found in config.json.", file=sys.stderr)
        sys.exit(1)
        
    csv_filename = app_config.get("outreach_list")
    if not csv_filename:
        print(f"Error: No outreach_list CSV file configured for '{app_key}'.", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(csv_filename):
        print(f"Error: Contact CSV file '{csv_filename}' not found.", file=sys.stderr)
        sys.exit(1)
        
    output_dir = os.path.join("output", app_key)
    template_path = os.path.join(output_dir, "email_newsletter.md")
    
    # Parse template
    subject_template, body_template = parse_email_template(template_path)
    
    # Read contacts
    contacts = []
    with open(csv_filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)
            
    if not contacts:
        print(f"Warning: No contacts found in CSV file '{csv_filename}'. Exiting.")
        return
        
    # Check execution mode
    is_smtp_available = all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD]) and not dry_run
    
    drafts_dir = os.path.join(output_dir, "outreach_drafts")
    os.makedirs(drafts_dir, exist_ok=True)
    
    log_path = os.path.join(output_dir, "outreach_log.csv")
    log_file_exists = os.path.exists(log_path)
    
    outreach_results = []
    
    print("\n=== Stage 1: Initiating Outreach Campaign ===")
    if is_smtp_available:
        print(f"SMTP Configuration detected. Dispatching real emails via {SMTP_HOST}...")
    else:
        print("SMTP Credentials not fully provided. Running in SIMULATION MODE.")
        print(f"Personalized drafts will be saved to: '{drafts_dir}'")
        
    for contact in contacts:
        name = contact.get("name", "").strip()
        email = contact.get("email", "").strip()
        org = contact.get("organization", contact.get("company", "")).strip()
        
        if not email:
            print(f"Skipping contact '{name}' because email is missing.")
            continue
            
        # Personalize subject & body
        subject = personalize_text(subject_template, name, org)
        body = personalize_text(body_template, name, org)
        
        status = "SIMULATED"
        err_msg = ""
        
        if is_smtp_available:
            try:
                # Setup email message
                msg = MIMEMultipart()
                msg['From'] = SMTP_USER
                msg['To'] = email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
                
                # Send
                server = smtplib.SMTP(SMTP_HOST, int(SMTP_PORT))
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, email, msg.as_string())
                server.quit()
                
                status = "SENT"
                print(f"Email successfully sent to: {email} ({name})")
            except Exception as e:
                status = "FAILED"
                err_msg = str(e)
                print(f"Failed to send email to {email}: {err_msg}", file=sys.stderr)
        else:
            # Simulation mode: Save personalized drafts to text files
            draft_path = os.path.join(drafts_dir, f"{email}.txt")
            with open(draft_path, "w", encoding="utf-8") as df:
                df.write(f"To: {email}\n")
                df.write(f"Subject: {subject}\n")
                df.write("="*60 + "\n\n")
                df.write(body)
            print(f"Draft generated: '{draft_path}'")
            
        outreach_results.append({
            "name": name,
            "email": email,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "error": err_msg
        })
        
    # Write outreach history log
    with open(log_path, "a", newline="", encoding="utf-8") as lf:
        writer = csv.DictWriter(lf, fieldnames=["name", "email", "status", "timestamp", "error"])
        if not log_file_exists:
            writer.writeheader()
        writer.writerows(outreach_results)
        
    # Print campaign summary
    sent_count = sum(1 for r in outreach_results if r["status"] == "SENT")
    failed_count = sum(1 for r in outreach_results if r["status"] == "FAILED")
    simulated_count = sum(1 for r in outreach_results if r["status"] == "SIMULATED")
    
    print("\n=== Outreach Campaign Summary ===")
    print(f"Total Contacts Processed: {len(contacts)}")
    if is_smtp_available:
        print(f"Successfully Sent: {sent_count}")
        print(f"Failed Dispatches: {failed_count}")
    else:
        print(f"Simulated Drafts Saved: {simulated_count}")
    print(f"Outreach log updated at: '{log_path}'")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AppPromoter AI Outreach")
    parser.add_argument("app", nargs="?", default="npc-aggregator", help="Application key")
    parser.add_argument("--dry-run", action="store_true", help="Force dry-run simulation mode")
    args = parser.parse_args()
    
    run_outreach(args.app, dry_run=args.dry_run)
