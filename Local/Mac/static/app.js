// State
let isConnected = false;
let isRunning = false;
let statusInterval = null;

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const fileStatus = document.getElementById('fileStatus');
const clearFileBtn = document.getElementById('clearFileBtn');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');
const connectionStatus = document.getElementById('connectionStatus');
const qrContainer = document.getElementById('qrContainer');
const qrCode = document.getElementById('qrCode');
const messageInput = document.getElementById('messageInput');
const countInput = document.getElementById('countInput');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const sentCount = document.getElementById('sentCount');
const totalCount = document.getElementById('totalCount');
const currentContact = document.getElementById('currentContact');
const progressBar = document.getElementById('progressBar');
const logs = document.getElementById('logs');

// File Upload
uploadZone.addEventListener('click', () => fileInput.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragover');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    showStatus(fileStatus, 'Uploading...', 'info');

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showStatus(fileStatus, `✅ Loaded ${data.total_contacts} contacts`, 'success');
            countInput.max = data.total_contacts;
            countInput.value = Math.min(10, data.total_contacts);
            clearFileBtn.style.display = 'block';
            uploadZone.style.display = 'none';
        } else {
            showStatus(fileStatus, `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus(fileStatus, `❌ Upload failed: ${error.message}`, 'error');
    }
}

// Clear file and allow new upload
clearFileBtn.addEventListener('click', () => {
    fileInput.value = '';
    fileStatus.textContent = '';
    fileStatus.className = 'status-message';
    clearFileBtn.style.display = 'none';
    uploadZone.style.display = 'block';
    countInput.value = 10;
});

// WhatsApp Connection
connectBtn.addEventListener('click', async () => {
    connectBtn.disabled = true;
    connectBtn.textContent = 'Connecting...';
    showStatus(connectionStatus, 'Initializing WhatsApp Web...', 'info');

    try {
        const response = await fetch('/connect', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showStatus(connectionStatus, 'Waiting for QR code scan...', 'info');
            startQRPolling();
        } else {
            showStatus(connectionStatus, `❌ ${data.error}`, 'error');
            connectBtn.disabled = false;
            connectBtn.textContent = 'Connect WhatsApp';
        }
    } catch (error) {
        showStatus(connectionStatus, `❌ Connection failed: ${error.message}`, 'error');
        connectBtn.disabled = false;
        connectBtn.textContent = 'Connect WhatsApp';
    }
});

async function startQRPolling() {
    const pollQR = async () => {
        try {
            // Check connection first
            const connResponse = await fetch('/check_connection');
            const connData = await connResponse.json();

            if (connData.success && connData.connected) {
                isConnected = true;
                qrContainer.style.display = 'none';
                showStatus(connectionStatus, '✅ WhatsApp connected!', 'success');
                connectBtn.style.display = 'none';
                disconnectBtn.style.display = 'block';
                startBtn.disabled = false;
                startStatusPolling();
                return;
            }

            // Get QR code
            const qrResponse = await fetch('/qr');
            const qrData = await qrResponse.json();

            if (qrData.success && qrData.qr_code) {
                qrCode.src = qrData.qr_code;
                qrContainer.style.display = 'block';
            }

            // Poll again
            setTimeout(pollQR, 2000);
        } catch (error) {
            console.error('QR polling error:', error);
            setTimeout(pollQR, 2000);
        }
    };

    pollQR();
}

// Disconnect WhatsApp
disconnectBtn.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to disconnect WhatsApp?')) {
        return;
    }

    disconnectBtn.disabled = true;
    disconnectBtn.textContent = 'Disconnecting...';

    try {
        const response = await fetch('/disconnect', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            isConnected = false;
            disconnectBtn.style.display = 'none';
            connectBtn.style.display = 'block';
            connectBtn.disabled = false;
            connectBtn.textContent = 'Connect WhatsApp';
            showStatus(connectionStatus, 'Disconnected', 'info');
            startBtn.disabled = true;

            if (statusInterval) {
                clearInterval(statusInterval);
                statusInterval = null;
            }
        } else {
            showStatus(connectionStatus, `❌ ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus(connectionStatus, `❌ Disconnect failed: ${error.message}`, 'error');
    } finally {
        disconnectBtn.disabled = false;
        disconnectBtn.textContent = 'Disconnect';
    }
});

// Start/Stop
startBtn.addEventListener('click', async () => {
    const message = messageInput.value.trim();
    const count = parseInt(countInput.value);

    if (!message) {
        alert('Please enter a message');
        return;
    }

    if (count <= 0) {
        alert('Please enter a valid contact count');
        return;
    }

    if (!confirm(`Send "${message}" to ${count} contacts?`)) {
        return;
    }

    try {
        const response = await fetch('/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message, count })
        });

        const data = await response.json();

        if (data.success) {
            isRunning = true;
            startBtn.disabled = true;
            stopBtn.disabled = false;
            messageInput.disabled = true;
            countInput.disabled = true;
        } else {
            alert(`Failed to start: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
});

stopBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/stop', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            isRunning = false;
            startBtn.disabled = false;
            stopBtn.disabled = true;
            messageInput.disabled = false;
            countInput.disabled = false;
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
});

// Status Polling
function startStatusPolling() {
    if (statusInterval) {
        clearInterval(statusInterval);
    }

    statusInterval = setInterval(async () => {
        try {
            const response = await fetch('/status');
            const data = await response.json();

            if (data.success) {
                updateStatus(data.status);
            }
        } catch (error) {
            console.error('Status polling error:', error);
        }
    }, 1000);
}

function updateStatus(status) {
    // Update connection status
    isConnected = status.connected;
    isRunning = status.running;

    // Update progress
    const progress = status.progress;
    sentCount.textContent = progress.sent;
    totalCount.textContent = progress.total;
    currentContact.textContent = progress.current || '-';

    // Update progress bar
    if (progress.total > 0) {
        const percentage = (progress.sent / progress.total) * 100;
        progressBar.style.width = `${percentage}%`;
    }

    // Update logs
    if (status.logs && status.logs.length > 0) {
        logs.innerHTML = status.logs.map(log =>
            `<div class="log-entry">${escapeHtml(log)}</div>`
        ).join('');
        logs.scrollTop = logs.scrollHeight;
    }

    // Update button states
    if (!isRunning && startBtn.disabled && isConnected) {
        startBtn.disabled = false;
        stopBtn.disabled = true;
        messageInput.disabled = false;
        countInput.disabled = false;
    }
}

// Utility Functions
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message ${type}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
console.log('WhatsApp Cold Messaging App loaded');
