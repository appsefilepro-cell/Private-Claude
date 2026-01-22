// AgentX5 Edge Extension - Content Script

// This script runs on all web pages
console.log('AgentX5 content script loaded');

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getPageInfo') {
        sendResponse({
            title: document.title,
            url: window.location.href
        });
    }
});
