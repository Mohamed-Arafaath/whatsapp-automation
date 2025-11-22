import pandas as pd
import time
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

# Configuration
EXCEL_FILE = 'whatsapp_cold_messaging/whatsapp.xlsx'
SESSION_DIR = './whatsapp_session'

def setup_driver():
    """Initialize Chrome driver with existing session."""
    print("Initializing WhatsApp Web...")
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={SESSION_DIR}")
    
    # Check if session dir exists to warn user
    if not os.path.exists(SESSION_DIR):
        print(f"WARNING: Session directory '{SESSION_DIR}' not found. You will need to scan QR code.")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get("https://web.whatsapp.com")
    return driver

def wait_for_login(driver):
    """Wait for the user to log in (scan QR code if needed)."""
    print("\nPlease scan the QR code if not logged in...")
    try:
        # Wait for the chat list pane to appear
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="pane-side"]'))
        )
        print("✅ WhatsApp Web connected!")
        return True
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False

def send_message(driver, phone, name, message_template):
    """Send a message to a specific phone number."""
    try:
        # Clean phone number (remove non-digits)
        phone = str(phone).replace('.0', '') # Handle float conversion
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        if not clean_phone:
            print(f"Skipping invalid phone number: {phone}")
            return False

        print(f"Sending to {name} ({clean_phone})...")
        
        # Encode message
        encoded_message = urllib.parse.quote(message_template)
        
        # Navigate to send url
        url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"
        driver.get(url)
        
        # Wait for the page to load
        try:
            # First, wait for the chat to load (either input box or invalid number message)
            time.sleep(3)  # Give page time to load
            
            # Check for invalid number
            try:
                invalid_msg = driver.find_element(By.XPATH, '//div[contains(text(), "Phone number shared via url is invalid")]')
                print(f"⚠️ Invalid number detected by WhatsApp: {clean_phone}")
                return False
            except:
                pass  # No invalid message, continue
            
            # Wait for the input box to appear (message is pre-filled)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            
            print(f"  Message loaded, looking for send button...")
            
            # Strategy 1: Try the send icon
            try:
                send_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                )
                print(f"  Found send button (icon), clicking...")
                send_button.click()
                time.sleep(2)
                print(f"✅ Sent to {name}")
                return True
            except Exception as e1:
                print(f"  Strategy 1 failed: {e1}")
            
            # Strategy 2: Try button with aria-label
            try:
                send_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Send"]'))
                )
                print(f"  Found send button (aria-label), clicking...")
                send_button.click()
                time.sleep(2)
                print(f"✅ Sent to {name}")
                return True
            except Exception as e2:
                print(f"  Strategy 2 failed: {e2}")
            
            # Strategy 3: Try finding any button with send icon as child
            try:
                send_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[.//span[@data-icon="send"]]'))
                )
                print(f"  Found send button (parent), clicking...")
                send_button.click()
                time.sleep(2)
                print(f"✅ Sent to {name}")
                return True
            except Exception as e3:
                print(f"  Strategy 3 failed: {e3}")
            
            # Strategy 4: Press Enter key in the input box
            try:
                input_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                print(f"  Trying Enter key...")
                input_box.send_keys(Keys.RETURN)
                time.sleep(2)
                print(f"✅ Sent to {name}")
                return True
            except Exception as e4:
                print(f"  Strategy 4 failed: {e4}")
            
            print(f"❌ All strategies failed for {name}")
            return False
            
        except Exception as e:
            print(f"❌ Failed to send to {name}: Page load error. ({e})")
            return False

    except Exception as e:
        print(f"❌ Error processing {name}: {e}")
        return False

def get_user_input():
    """Get message template and contact count from user."""
    print("\n" + "="*60)
    print("WhatsApp Cold Messaging Agent")
    print("="*60)
    
    # Get message template
    print("\nEnter the message you want to send:")
    message = input("> ").strip()
    
    if not message:
        print("❌ Message cannot be empty!")
        return None, None
    
    # Get number of contacts
    print("\nHow many contacts do you want to message? (top X from Excel)")
    while True:
        try:
            count = int(input("> ").strip())
            if count <= 0:
                print("❌ Please enter a positive number!")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid number!")
    
    return message, count

def main():
    # 1. Get user input
    message_template, contact_count = get_user_input()
    
    if message_template is None:
        return
    
    # 2. Load Contacts
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: File '{EXCEL_FILE}' not found.")
        return

    try:
        df = pd.read_excel(EXCEL_FILE)
        total_contacts = len(df)
        print(f"\n📊 Loaded {total_contacts} total contacts from Excel.")
        
        # Limit to top X contacts
        if contact_count < total_contacts:
            df = df.head(contact_count)
            print(f"📌 Will message the top {contact_count} contacts.")
        else:
            print(f"📌 Will message all {total_contacts} contacts.")
            
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    # 3. Confirm with user
    print(f"\n⚠️  CONFIRMATION:")
    print(f"   Message: \"{message_template}\"")
    print(f"   Contacts: {len(df)}")
    print(f"\nType 'yes' to proceed or 'no' to cancel:")
    
    confirmation = input("> ").strip().lower()
    if confirmation != 'yes':
        print("❌ Cancelled by user.")
        return

    # 4. Setup Browser
    driver = setup_driver()
    
    if not wait_for_login(driver):
        driver.quit()
        return

    # 5. Iterate and Send
    total_sent = 0
    
    print("\n🚀 Starting cold messaging in 5 seconds...")
    print("Press Ctrl+C to stop safely.")
    time.sleep(5)

    try:
        for index, row in df.iterrows():
            name = row.get("Contact's Public Display Name", "Unknown")
            phone = row.get("Phone Number", "")
            
            if pd.isna(phone):
                continue
                
            success = send_message(driver, phone, name, message_template)
            
            if success:
                total_sent += 1
                # Random delay to avoid ban
                delay = random.uniform(10, 20)
                print(f"Waiting {delay:.1f}s... ({total_sent}/{len(df)} sent)")
                time.sleep(delay)
            else:
                print("Skipping delay due to failure.")
                time.sleep(2) # Short delay even on fail

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        print(f"\n{'='*60}")
        print(f"✅ Done! Total messages sent: {total_sent}/{len(df)}")
        print(f"{'='*60}")
        print("Keeping browser open for 10 seconds to ensure last message sends...")
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    main()
