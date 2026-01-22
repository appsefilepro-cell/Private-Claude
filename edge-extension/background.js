// AgentX5 Edge Extension - Background Service Worker

chrome.runtime.onInstalled.addListener(() => {
    console.log('AgentX5 installed!');
    
    // Show welcome notification
    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon48.png',
        title: 'AgentX5 Installed!',
        message: 'Press Ctrl+Shift+A to open AgentX5. Your $313K fraud dispute is ready to file!',
        priority: 2
    });
});

// Listen for command (keyboard shortcut)
chrome.commands.onCommand.addListener((command) => {
    if (command === '_execute_action') {
        chrome.action.openPopup();
    }
});

// Context menu
chrome.contextMenus.create({
    id: 'agentx5-help',
    title: 'Ask AgentX5: "%s"',
    contexts: ['selection']
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'agentx5-help') {
        // Store the query and open popup
        chrome.storage.local.set({ pendingQuery: info.selectionText });
        chrome.action.openPopup();
    }
});
