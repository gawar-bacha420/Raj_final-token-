let isRunning = false;
let messageTimeout = null;

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Message received in content script:", request);
    
    if (request.action === 'start') {
        startSending(request.messages, request.speed, request.haterName);
        sendResponse({ status: 'started' });
    } else if (request.action === 'stop') {
        stopSending();
        sendResponse({ status: 'stopped' });
    }
});

function startSending(messages, speed, recipientName) {
    isRunning = true;
    let messageIndex = 0;
    
    console.log(`Starting to send ${messages.length} messages with ${speed}ms delay`);

    function sendNextMessage() {
        if (!isRunning || messageIndex >= messages.length) {
            isRunning = false;
            console.log('✅ All messages sent successfully!');
            return;
        }

        const message = messages[messageIndex];
        const fullMessage = `${recipientName}: ${message}`;
        
        try {
            // Find the message input field - it's a contenteditable div in modern Messenger
            let inputField = findMessageInput();
            
            if (!inputField) {
                console.error('❌ Could not find message input field');
                console.log('Make sure you have a conversation open in Facebook Messenger');
                stopSending();
                return;
            }

            // Clear the input field
            inputField.innerHTML = '';
            inputField.textContent = '';
            
            // Set focus
            inputField.focus();
            
            // Insert the message text using a method that works with React
            insertText(inputField, fullMessage);
            
            // Trigger input/change events for React state update
            triggerEvents(inputField);
            
            // Wait a bit then send
            setTimeout(() => {
                sendMessage(inputField);
                console.log(`✅ Message ${messageIndex + 1}/${messages.length} sent: "${fullMessage}"`);
                
                messageIndex++;
                if (isRunning && messageIndex < messages.length) {
                    messageTimeout = setTimeout(sendNextMessage, speed);
                }
            }, 200);
            
        } catch (error) {
            console.error('Error sending message:', error);
            messageIndex++;
            if (isRunning && messageIndex < messages.length) {
                messageTimeout = setTimeout(sendNextMessage, speed);
            }
        }
    }
    
    sendNextMessage();
}

function findMessageInput() {
    // Look for contenteditable divs in Messenger
    const editables = document.querySelectorAll('[contenteditable="true"]');
    
    if (editables.length === 0) {
        return null;
    }
    
    // Return the last/active contenteditable element (usually the message input)
    let messageInput = null;
    for (let elem of editables) {
        // Skip if it's a search box or other input
        const ariaLabel = elem.getAttribute('aria-label') || '';
        const placeholder = elem.getAttribute('placeholder') || '';
        
        if (!ariaLabel.toLowerCase().includes('search') && 
            !placeholder.toLowerCase().includes('search')) {
            messageInput = elem;
        }
    }
    
    return messageInput || editables[editables.length - 1];
}

function insertText(element, text) {
    // Method 1: Direct text insertion
    element.textContent = text;
    
    // Method 2: Using execCommand for better React integration
    if (document.queryCommandSupported('insertText')) {
        document.execCommand('insertText', false, text);
    }
    
    // Method 3: Simulate paste event (very reliable)
    const pasteEvent = new ClipboardEvent('paste', {
        bubbles: true,
        cancelable: true,
        clipboardData: new DataTransfer()
    });
    pasteEvent.clipboardData.setData('text/plain', text);
    element.dispatchEvent(pasteEvent);
    
    // Ensure the text is there
    if (!element.textContent.includes(text)) {
        element.innerHTML = text;
    }
}

function triggerEvents(element) {
    // Trigger all events that React listens to
    const events = [
        'input',
        'change',
        'keydown',
        'keyup',
        'keypress',
        'textInput'
    ];
    
    events.forEach(eventType => {
        const event = new Event(eventType, { bubbles: true, cancelable: true });
        element.dispatchEvent(event);
    });
    
    // Also trigger composition events
    const compositionStart = new CompositionEvent('compositionstart', { bubbles: true });
    const compositionEnd = new CompositionEvent('compositionend', { bubbles: true });
    element.dispatchEvent(compositionStart);
    element.dispatchEvent(compositionEnd);
}

function sendMessage(inputElement) {
    // Method 1: Try to find and click the send button
    const sendButton = findSendButton();
    if (sendButton) {
        sendButton.click();
        return;
    }
    
    // Method 2: Simulate pressing Enter key
    const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        which: 13,
        bubbles: true,
        cancelable: true
    });
    
    inputElement.dispatchEvent(enterEvent);
    
    const enterUpEvent = new KeyboardEvent('keyup', {
        key: 'Enter',
        code: 'Enter',
        keyCode: 13,
        which: 13,
        bubbles: true,
        cancelable: true
    });
    
    inputElement.dispatchEvent(enterUpEvent);
}

function findSendButton() {
    // Look for the send button in various ways
    
    // Method 1: Look for buttons with send-related aria-label
    const buttons = document.querySelectorAll('button, [role="button"]');
    for (let btn of buttons) {
        const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
        const title = (btn.getAttribute('title') || '').toLowerCase();
        const text = (btn.textContent || '').toLowerCase();
        
        if (ariaLabel.includes('send') || title.includes('send') || text.includes('send')) {
            return btn;
        }
    }
    
    // Method 2: Look by data attributes
    let sendBtn = document.querySelector('[data-testid="send"]');
    if (sendBtn) return sendBtn;
    
    // Method 3: Look for SVG patterns common in send buttons
    const allDivs = document.querySelectorAll('div[role="button"]');
    for (let div of allDivs) {
        const svg = div.querySelector('svg');
        if (svg) {
            // Check if it has send-like appearance
            const parent = div.closest('div[class*="send"], div[class*="composer"]');
            if (parent) return div;
        }
    }
    
    return null;
}

function stopSending() {
    isRunning = false;
    if (messageTimeout) {
        clearTimeout(messageTimeout);
        messageTimeout = null;
    }
    console.log('⏸️  Message sending stopped');
}
