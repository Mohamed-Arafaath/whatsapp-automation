# WhatsApp Automation App 🚀

A powerful, user-friendly tool to automate WhatsApp messages using Selenium and Python.

## 📂 Project Structure

- **`Cloud/`**: Configuration files for deploying to the cloud (Render.com).
- **`Local/`**: Scripts to run the app on your own computer.
    - **`Windows/`**: Double-click scripts for Windows.
    - **`Mac/`**: Terminal scripts for Mac/Linux.
- **`src/`**: The source code of the application.

## 🚀 How to Run

### Option 1: Run Locally (Your Computer)

**Windows:**
1. Go to `Local/Windows`.
2. Run `SETUP_WINDOWS.bat` (First time only).
3. Run `RUN_WINDOWS.bat`.

**Mac:**
1. Go to `Local/Mac`.
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
