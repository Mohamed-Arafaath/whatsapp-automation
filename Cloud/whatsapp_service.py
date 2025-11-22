import pandas as pd
import time
import random
import urllib.parse
import threading
import io
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

class WhatsAppService:
    def __init__(self, session_id):
        self.session_id = session_id
        self.driver = None
        self.is_connected = False
        self.is_running = False
        self.should_stop = False
        self.progress = {"sent": 0, "total": 0, "current": ""}
        self.logs = []
        self.contacts_df = None
        self.message_template = ""
        self.contact_count = 0
        self.media_path = None  # Store media file path
        
    def log(self, message):
        """Add a log message."""
        self.logs.append(message)
        print(message)
    
    def setup_driver(self):
        """Initialize Chrome driver with session."""
        self.log("Initializing WhatsApp Web...")
        options = webdriver.ChromeOptions()
        session_dir = f"./whatsapp_sessions/session_{self.session_id}"
        options.add_argument(f"--user-data-dir={session_dir}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--blink-settings=imagesEnabled=false") # Disable images to save memory
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Check if running on Render
        if os.environ.get('RENDER'):
            options.binary_location = "/usr/bin/google-chrome"
            options.add_argument("--headless=new")  # Headless mode is required on Render
        
        os.makedirs(session_dir, exist_ok=True)
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            self.driver.get("https://web.whatsapp.com")
        except Exception as e:
            self.log(f"Failed to start driver: {str(e)}")
            raise e
        
    def check_connection(self):
        """Check if WhatsApp Web is connected."""
        try:
            if not self.driver:
                return False
                
            # Check for multiple possible elements that indicate login
            selectors = [
                '//div[@id="pane-side"]',  # Chat list
                '//header//img',           # Profile picture
                '//div[@contenteditable="true"][@data-tab="3"]', # Search box
                '//span[@data-icon="chat"]', # New chat icon
                '//div[@id="side"]'        # Side panel
            ]
            
            for selector in selectors:
                try:
                    self.driver.find_element(By.XPATH, selector)
                    self.is_connected = True
                    self.log("✅ Connection detected!")
                    return True
                except:
                    continue
            
            self.is_connected = False
            return False
        except Exception as e:
            self.log(f"Connection check error: {e}")
            self.is_connected = False
            return False
    
    def get_qr_code(self):
        """Get QR code as base64 image."""
        try:
            if not self.driver:
                return None
            # Find QR code canvas
            qr_element = self.driver.find_element(By.XPATH, '//canvas[@aria-label="Scan this QR code to link a device!"]')
            # Take screenshot of QR code
            qr_png = qr_element.screenshot_as_png
            qr_base64 = base64.b64encode(qr_png).decode('utf-8')
            return f"data:image/png;base64,{qr_base64}"
        except:
            return None
    
    def load_contacts(self, file_content):
        """Load contacts from Excel file content."""
        try:
            self.contacts_df = pd.read_excel(io.BytesIO(file_content))
            self.log(f"Loaded {len(self.contacts_df)} contacts from Excel")
            return True
        except Exception as e:
            self.log(f"Error loading Excel: {e}")
            return False
    
    
    def send_message(self, phone, name):
        """Send a message (with optional media) to a specific phone number."""
        try:
            # Clean phone number
            phone = str(phone).replace('.0', '')
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            if not clean_phone:
                self.log(f"Skipping invalid phone number: {phone}")
                return False

            self.log(f"Sending to {name} ({clean_phone})...")
            self.progress["current"] = f"{name} ({clean_phone})"
            
            # Navigate to chat (without message in URL for media support)
            url = f"https://web.whatsapp.com/send?phone={clean_phone}"
            self.driver.get(url)
            time.sleep(1)  # Optimized page load wait
            
            # Check for invalid number
            try:
                self.driver.find_element(By.XPATH, '//div[contains(text(), "Phone number shared via url is invalid")]')
                self.log(f"⚠️ Invalid number: {clean_phone}")
                return False
            except:
                pass
            
            # Wait for input box to be ready
            input_box = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            
            # Case 1: Media attachment
            if self.media_path and os.path.exists(self.media_path):
                try:
                    self.log(f"Attaching media: {os.path.basename(self.media_path)}")
                    
                    # Click attach button (paperclip icon)
                    attach_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@title="Attach" or @aria-label="Attach"]'))
                    )
                    attach_btn.click()
                    time.sleep(0.5)
                    
                    # Find and send file path to the hidden file input
                    media_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
                    )
                    media_input.send_keys(os.path.abspath(self.media_path))
                    time.sleep(2)  # Wait for media preview to load
                    
                    # Add caption (message text) if provided
                    if self.message_template:
                        try:
                            caption_box = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                            )
                            caption_box.send_keys(self.message_template)
                            time.sleep(0.3)
                        except Exception as e:
                            self.log(f"Warning: Could not add caption: {e}")
                    
                    # Click send button
                    send_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                    )
                    send_btn.click()
                    
                    time.sleep(0.5)
                    self.log(f"✅ Sent media + message to {name}")
                    return True
                    
                except Exception as e:
                    self.log(f"❌ Failed to send media: {e}")
                    return False
            
            # Case 2: Text-only message
            else:
                try:
                    # Type message in input box
                    input_box.send_keys(self.message_template)
                    time.sleep(0.3)
                    
                    # Try to send message
                    sent = False
                    
                    # Strategy 1: Click send icon
                    try:
                        send_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                        )
                        send_button.click()
                        sent = True
                    except:
                        pass
                    
                    # Strategy 2: Press Enter key
                    if not sent:
                        try:
                            input_box.send_keys(Keys.RETURN)
                            sent = True
                        except:
                            pass
                    
                    if sent:
                        time.sleep(0.5)
                        self.log(f"✅ Sent to {name}")
                        return True
                    else:
                        self.log(f"❌ Failed to send to {name}")
                        return False
                        
                except Exception as e:
                    self.log(f"❌ Error sending text: {e}")
                    return False
                
        except Exception as e:
            self.log(f"❌ Error: {e}")
            return False
    
    def start_sending(self, message, count, media_path=None):
        """Start sending messages in a background thread."""
        self.message_template = message
        self.contact_count = count
        self.media_path = media_path  # Store media path
        self.should_stop = False
        self.is_running = True
        
        thread = threading.Thread(target=self._send_loop)
        thread.daemon = True
        thread.start()
    
    def _send_loop(self):
        """Main sending loop (runs in background thread)."""
        try:
            if self.contacts_df is None:
                self.log("❌ No contacts loaded")
                self.is_running = False
                return
            
            # Limit to top X contacts
            df = self.contacts_df.head(self.contact_count)
            self.progress["total"] = len(df)
            self.progress["sent"] = 0
            
            self.log(f"🚀 Starting to send to {len(df)} contacts...")
            
            for index, row in df.iterrows():
                if self.should_stop:
                    self.log("🛑 Stopped by user")
                    break
                
                name = row.get("Contact's Public Display Name", "Unknown")
                phone = row.get("Phone Number", "")
                
                if pd.isna(phone):
                    continue
                
                success = self.send_message(phone, name)
                
                if success:
                    self.progress["sent"] += 1
                    # Random delay
                    delay = random.uniform(2, 5)  # Optimized: reduced from 10-20s to 2-5s for faster sending
                    self.log(f"Waiting {delay:.1f}s... ({self.progress['sent']}/{self.progress['total']})")
                    
                    # Sleep in small chunks to allow stopping
                    for _ in range(int(delay * 10)):
                        if self.should_stop:
                            break
                        time.sleep(0.1)
                else:
                    time.sleep(2)
            
            self.log(f"✅ Done! Sent {self.progress['sent']}/{self.progress['total']} messages")
            
        except Exception as e:
            self.log(f"❌ Error in send loop: {e}")
        finally:
            self.is_running = False
    
    def stop_sending(self):
        """Stop the sending process."""
        self.should_stop = True
        self.log("Stopping...")
    
    def get_status(self):
        """Get current status."""
        return {
            "connected": self.is_connected,
            "running": self.is_running,
            "progress": self.progress,
            "logs": self.logs[-20:]  # Last 20 logs
        }
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None
