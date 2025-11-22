# WhatsApp Automation App 🚀

A powerful, user-friendly tool to automate WhatsApp messages using Selenium and Python.

## 📂 Project Structure

- **`Cloud/`**: Contains everything needed for Render deployment.
- **`Local/`**:
    - **`Windows/`**: Contains the App + Run scripts for Windows.
    - **`Mac/`**: Contains the App + Run scripts for Mac.

## 🚀 How to Run

### Option 1: Run Locally (Your Computer)

## 🚀 How to Run

### Option 1: Run Locally (Your Computer)

**Windows:**
1. Download the `Local/Windows` folder.
2. Double‑click `SETUP_WINDOWS.bat` (first time only). This will install Python, Chrome, and required Python packages.
3. After the setup completes, double‑click `RUN_WINDOWS.bat` to start the Flask app.
4. Open your browser and navigate to `http://localhost:5001`.

**Mac:**
1. Download the `Local/Mac` folder.
2. Run `./SETUP_MAC.sh` (first time only).
3. Run `./RUN_MAC.sh` to start the app.
4. Open your browser and go to `http://localhost:5001`.

### Option 2: Deploy to Cloud (Render)

See `DEPLOYMENT_GUIDE.md` for full instructions. **Important**: Set the Dockerfile path to `Cloud/Dockerfile` in Render settings.

**Mac:**
1. Download the `Local/Mac` folder.
2. Run `./SETUP_MAC.sh` (First time only).
3. Run `./RUN_MAC.sh`.

### Option 2: Deploy to Cloud (Render)

See `DEPLOYMENT_GUIDE.md` for full instructions.
**Important**: Set "Dockerfile Path" to `Cloud/Dockerfile` in Render settings.

## ✨ Features

- **Bulk Messaging**: Send messages to hundreds of contacts from an Excel file.
- **Smart Delays**: Random delays between messages to avoid blocking.
- **Session Saving**: Scan QR code once, and it stays connected.
- **Modern UI**: Beautiful web interface to control everything.
