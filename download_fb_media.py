import os
import time
import requests
from playwright.sync_api import sync_playwright

# Configuration
# Group name = "https://www.facebook.com/groups/YOUR_GROUP_ID/media"

GROUP_MEDIA_URL = "https://www.facebook.com/groups/YOUR_GROUP_ID/media"
DOWNLOAD_DIR = "facebook_group_photos"
SCROLL_PAUSE_TIME = 2.5
MAX_SCROLLS = 40  # Increase or decrease depending on how large the media gallery is

def main():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    with sync_playwright() as p:
        # Launch browser in non-headless mode so you can log in manually
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        print("Navigating to Facebook...")
        page.goto("https://www.facebook.com")
        
        print("\n" + "="*50)
        print("ACTION REQUIRED:")
        print("1. Log into your Facebook account in the opened browser window.")
        print("2. Complete any 2FA or security prompts if necessary.")
        print("3. Once you are fully logged in, return here and press ENTER.")
        print("="*50 + "\n")
        input("Press Enter to continue after logging in...")

        print(f"Navigating to group media: {GROUP_MEDIA_URL}")
        page.goto(GROUP_MEDIA_URL)
        time.sleep(5)

        print("Starting automated scrolling to load all photos...")
        image_urls = set()
        
        for i in range(MAX_SCROLLS):
            # Scroll down to trigger lazy loading of media
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            
            # Extract image source URLs from the page
            images = page.locator("img")
            count = images.count()
            
            for j in range(count):
                img = images.nth(j)
                src = img.get_attribute("src")
                # Facebook image CDN links typically contain 'scontent'
                if src and "scontent" in src:
                    image_urls.add(src)
            
            print(f"Scroll {i+1}/{MAX_SCROLLS}: Collected {len(image_urls)} unique image URLs...")

        print(f"\nFound {len(image_urls)} unique images. Starting download...")
        
        for idx, url in enumerate(image_urls):
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    file_path = os.path.join(DOWNLOAD_DIR, f"photo_{idx+1}.jpg")
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    print(f"Downloaded [{idx+1}/{len(image_urls)}]")
                else:
                    print(f"Failed to download image {idx+1}: Status code {response.status_code}")
            except Exception as e:
                print(f"Error downloading image {idx+1}: {e}")

        print(f"\nDone! All available photos have been saved to the '{DOWNLOAD_DIR}' folder.")
        browser.close()

if __name__ == "__main__":
    main()