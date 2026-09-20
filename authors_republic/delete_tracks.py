import sys
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_deletion():
    cdp_url = "http://127.0.0.1:9222"
    print(f"Connecting to browser on {cdp_url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]
        
        # Find the active page/tab containing authorsrepublic.com
        page = None
        for page_obj in context.pages:
            if "authorsrepublic.com" in page_obj.url:
                page = page_obj
                break
        
        if not page:
            print("⚠️ Could not find an active Authors Republic page. Using the first tab.")
            page = context.pages[0]
            
        print(f"Active Page URL: {page.url}")
        print("Starting deletion loop...")
        
        deleted_count = 0
        while True:
            # Locate all elements that have the exact text "Delete"
            delete_btns = page.get_by_text("Delete", exact=True)
            
            # If no buttons are found, we're done
            if delete_btns.count() == 0:
                print(f"Done! Successfully deleted {deleted_count} tracks.")
                break
            
            # Click the first track's Delete button
            print("Clicking Delete...")
            delete_btns.first.click()
            
            # Wait for the confirmation modal button "Delete Audio"
            confirm_btn = page.get_by_role("button", name="Delete Audio")
            confirm_btn.wait_for(state="visible", timeout=5000)
            
            # Click the confirm button
            confirm_btn.click()
            deleted_count += 1
            
            # Wait for the modal to close and the list to update
            confirm_btn.wait_for(state="hidden", timeout=5000)
            page.wait_for_timeout(1000)

if __name__ == "__main__":
    run_deletion()
