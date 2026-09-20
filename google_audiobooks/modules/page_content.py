import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def upload_content_page(page, cf):
    print("\n--- [Module: Content & Cover Page] ---")
    cover_path = cf.get("cover_image_path")
    audio_files = cf.get("audio_files", [])

    # Dismiss dialog if open
    cancel_btn = page.locator('mat-dialog-container button:has-text("Cancel")').first
    if cancel_btn.count() > 0 and cancel_btn.is_visible():
        cancel_btn.click(force=True)
        time.sleep(1)

    # 1. Upload Cover via expect_file_chooser
    if cover_path and os.path.exists(cover_path):
        cov_btn = page.locator('button:has-text("Upload a cover"), [role="button"]:has-text("Upload a cover")').first
        if cov_btn.count() > 0 and cov_btn.is_visible():
            print(f"➡️ Uploading Cover Image: {os.path.basename(cover_path)}")
            cov_btn.click(force=True)
            time.sleep(1.5)

            browse_btn = page.locator('mat-dialog-container button:has-text("Browse"), mat-dialog-container [role="button"]:has-text("Browse")').first
            if browse_btn.count() > 0 and browse_btn.is_visible():
                try:
                    with page.expect_file_chooser(timeout=5000) as fc_info:
                        browse_btn.click(force=True)
                    fc = fc_info.value
                    fc.set_files(cover_path)
                    time.sleep(3)
                    print("  ✓ Cover uploaded via expect_file_chooser successfully!")
                except Exception as e:
                    print(f"  Cover upload note: {e}")

            close_btn = page.locator('mat-dialog-container button:has-text("Close"), mat-dialog-container button:has-text("Cancel")').first
            if close_btn.count() > 0 and close_btn.is_visible():
                close_btn.click(force=True)
                time.sleep(1)

    # 2. Upload Audio Files via native CDP flattened DOM (bypassing Playwright 50MB limit)
    if audio_files:
        audio_btn = page.locator('button:has-text("Upload audio file"), [role="button"]:has-text("Upload audio file")').first
        if audio_btn.count() > 0 and audio_btn.is_visible():
            print(f"\n➡️ Uploading {len(audio_files)} Audio Tracks via CDP...")
            audio_btn.click(force=True)
            time.sleep(1.5)

            browse_btn = page.locator('mat-dialog-container button:has-text("Browse"), mat-dialog-container [role="button"]:has-text("Browse")').first
            if browse_btn.count() > 0 and browse_btn.is_visible():
                browse_btn.click(force=True)
                time.sleep(1)

            client = page.context.new_cdp_session(page)
            client.send("DOM.enable")
            doc = client.send("DOM.getFlattenedDocument", {"depth": -1, "pierce": True})

            file_nodes = []
            for n in doc.get("nodes", []):
                attrs = n.get("attributes", [])
                if n.get("nodeName") == "INPUT" and "type" in attrs and "file" in attrs:
                    file_nodes.append(n.get("nodeId"))

            if file_nodes:
                client.send("DOM.setFileInputFiles", {
                    "files": audio_files,
                    "nodeId": file_nodes[-1]
                })
                time.sleep(3)
                print(f"  ✓ All {len(audio_files)} audio tracks injected via CDP successfully!")

            sub_btn = page.locator('mat-dialog-container button:has-text("Submit")').first
            if sub_btn.count() > 0 and sub_btn.is_visible():
                sub_btn.click(force=True)
                time.sleep(2)

    print("✨ Content & Cover Page upload complete!")
