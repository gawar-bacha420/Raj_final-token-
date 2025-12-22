// Array of beautiful color gradients
const colorThemes = [
    'color-1',  // Purple
    'color-2',  // Pink to Red
    'color-3',  // Cyan to Blue
    'color-4',  // Green to Teal
    'color-5',  // Pink to Yellow
    'color-6',  // Cyan to Dark Purple
    'color-7',  // Mint to Pink
    'color-8',  // Orange to Pink
    'color-9',  // Dark to Purple
    'color-10'  // Light Blue to Dark Blue
];

// Apply random beautiful color on load
function applyRandomColor() {
    const randomColor = colorThemes[Math.floor(Math.random() * colorThemes.length)];
    document.body.className = randomColor;
    localStorage.setItem('selectedColor', randomColor);
}

// Check if cookies exist for Facebook session
async function checkFacebookCookies() {
    try {
        const cookies = await chrome.cookies.getAll({ url: 'https://www.facebook.com' });
        return cookies && cookies.length > 0;
    } catch (e) {
        return false;
    }
}

function showStatus(message, type) {
    const statusEl = document.getElementById('statusMessage');
    statusEl.textContent = message;
    statusEl.className = `status-message ${type}`;
    setTimeout(() => {
        statusEl.className = 'status-message';
    }, 3000);
}

// Initialize page
document.addEventListener('DOMContentLoaded', async function() {
    // Apply random beautiful color
    applyRandomColor();
    
    const hasCookies = await checkFacebookCookies();
    if (!hasCookies) {
        document.getElementById('warningBox').classList.add('show');
    }
});

// Send messages
document.getElementById('sendBtn').addEventListener('click', async function() {
    const messages = document.getElementById('messageText').value.trim().split("\n").filter(msg => msg.trim() !== "");
    const speed = parseInt(document.getElementById('speed').value, 10) * 1000;
    const recipientName = document.getElementById('HatersName').value.trim();

    if (!messages.length) {
        showStatus('❌ Please enter at least one message', 'error');
        return;
    }

    if (!recipientName.trim()) {
        showStatus('❌ Please enter recipient name', 'error');
        return;
    }

    // Disable button during sending
    const sendBtn = document.getElementById('sendBtn');
    const originalText = sendBtn.value;
    sendBtn.disabled = true;

    showStatus('⏳ Starting to send messages...', 'info');

    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        if (!tabs[0]) {
            showStatus('❌ No active tab found', 'error');
            sendBtn.disabled = false;
            return;
        }
        
        // First try to send directly
        chrome.tabs.sendMessage(tabs[0].id, { 
            messages: messages, 
            speed: speed, 
            haterName: recipientName,
            action: 'start'
        }, (response) => {
            if (chrome.runtime.lastError) {
                // If content script not loaded, inject it first
                console.log('Injecting content script...');
                chrome.scripting.executeScript({
                    target: { tabId: tabs[0].id },
                    files: ["content_script.js"]
                }, () => {
                    if (chrome.runtime.lastError) {
                        showStatus('❌ Error: Make sure you\'re on facebook.com/messages/', 'error');
                        sendBtn.disabled = false;
                        return;
                    }
                    
                    // Now send the message
                    setTimeout(() => {
                        chrome.tabs.sendMessage(tabs[0].id, { 
                            messages: messages, 
                            speed: speed, 
                            haterName: recipientName,
                            action: 'start'
                        }, (response) => {
                            if (chrome.runtime.lastError) {
                                showStatus('❌ Error sending messages. Refresh the page and try again.', 'error');
                            } else {
                                showStatus('✅ Messages will be sent! Use Stop button to cancel.', 'success');
                            }
                            sendBtn.disabled = false;
                        });
                    }, 500);
                });
            } else {
                showStatus('✅ Messages will be sent! Use Stop button to cancel.', 'success');
                sendBtn.disabled = false;
            }
        });
    });
});

// Stop sending messages
document.getElementById('stopBtn').addEventListener('click', function() {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        if (tabs[0]) {
            chrome.tabs.sendMessage(tabs[0].id, { action: 'stop' }, (response) => {
                if (!chrome.runtime.lastError) {
                    showStatus('⏹️ Message sending stopped', 'info');
                }
            });
        }
    });
});
