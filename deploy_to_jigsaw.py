import os
import ftplib
import glob

def deploy():
    host = "jigsawpuzzlehelper.com"
    user = "zub1wu7sfht0"
    passwd = "vRhej%7uP3$LKuVv"
    
    local_dir = r"d:\git_repo\AppPromoter_AI\output\kb_html"
    
    print(f"Connecting to FTP server: {host}...")
    try:
        ftp = ftplib.FTP(host)
        ftp.login(user, passwd)
        print("Login successful.")
        
        # 1. Clean up old root files
        ftp.cwd("public_html")
        print("Cleaning up old files from root...")
        old_root_files = ["dev_journey_reddit_replier.html", "cli_menu.png", "error_403.png", "editor_popup.png", "reddit_review_screenshot.png"]
        for f_name in old_root_files:
            try:
                ftp.delete(f_name)
                print(f"[CLEANUP] Deleted old root file: {f_name}")
            except Exception:
                pass
                
        # 2. Create and navigate to reddit_replier directory
        dir_name = "reddit_replier"
        try:
            ftp.mkd(dir_name)
            print(f"Created remote directory: /{dir_name}")
        except Exception:
            # Directory already exists
            pass
            
        # 3. Deploy KB articles to Root
        print("\nDeploying KB articles to root public_html...")
        root_articles = ["kb_golf.html", "kb_npc.html"]
        for art in root_articles:
            local_path = os.path.join(local_dir, art)
            if os.path.exists(local_path):
                print(f"Uploading '{art}' to root...")
                with open(local_path, "rb") as f:
                    ftp.storbinary(f"STOR {art}", f)
                print(f"[OK] Uploaded to root: {art}")
                
        # 4. Deploy Dev Journey & Images to reddit_replier folder
        ftp.cwd(dir_name)
        print(f"\nDeploying dev journey and images to /{dir_name}...")
        
        # Files to upload to subfolder
        sub_files = ["dev_journey_reddit_replier.html", "cli_menu.png", "error_403.png", "editor_popup.png", "reddit_review_screenshot.png", "gemini_token_limit.png", "reddit_replier_launch.mp4"]
        for sub_file in sub_files:
            local_path = os.path.join(local_dir, sub_file)
            if os.path.exists(local_path):
                print(f"Uploading '{sub_file}' to /{dir_name}...")
                with open(local_path, "rb") as f:
                    ftp.storbinary(f"STOR {sub_file}", f)
                print(f"[OK] Uploaded to /{dir_name}: {sub_file}")
                
        ftp.quit()
        print("\nDeployment completed successfully! Files are organized and live on jigsawpuzzlehelper.com.")
    except Exception as e:
        print(f"Deployment failed with error: {e}")

if __name__ == "__main__":
    deploy()
