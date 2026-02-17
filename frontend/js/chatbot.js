document.addEventListener("DOMContentLoaded", () => {
    // Inject HTML Structure
    const chatHTML = `
        <div class="chat-widget-btn" onclick="toggleChat()">
            <svg class="chat-icon" viewBox="0 0 24 24">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
            </svg>
        </div>
        <div class="chat-window" id="chatWindow">
            <div class="chat-header">
                <span>AI Assistant</span>
                <span class="chat-close" onclick="toggleChat()">&times;</span>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="message bot">Hello! I'm your AI tutor. Ask me anything about this course!</div>
            </div>
            <div class="typing" id="typingIndicator">AI is thinking...</div>
            <div class="chat-input-area">
                <input type="text" class="chat-input" id="chatInput" placeholder="Type a message..." onkeypress="handleKeyPress(event)">
                <button class="chat-send-btn" onclick="sendMessage()">Send</button>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML("beforeend", chatHTML);
});

function toggleChat() {
    document.getElementById("chatWindow").classList.toggle("open");
}

function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}

function addUserMessage(text) {
    const chatMessages = document.getElementById("chatMessages");
    const msgDiv = document.createElement("div");
    msgDiv.className = "message user";
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addBotMessage(text) {
    const chatMessages = document.getElementById("chatMessages");
    const msgDiv = document.createElement("div");
    msgDiv.className = "message bot";
    msgDiv.textContent = text; // Ideally parse markdown here but keeping simple text for now
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById("chatInput");
    const message = input.value.trim();
    if (!message) return;

    input.value = "";
    addUserMessage(message);

    const typing = document.getElementById("typingIndicator");
    typing.style.display = "block";

    try {
        // Use API_BASE from api.js
        if (typeof API_BASE === 'undefined') {
            console.error("API_BASE is undefined. Make sure api.js is loaded.");
            return;
        }

        const response = await fetch(`${API_BASE}/ai/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) throw new Error("Network response was not ok");

        const data = await response.json();
        typing.style.display = "none";
        addBotMessage(data.reply);

    } catch (error) {
        console.error("Chat Error:", error);
        typing.style.display = "none";
        addBotMessage("Sorry, I encountered an error. Please try again later.");
    }
}
