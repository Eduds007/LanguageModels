

const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");
const chatsList = document.getElementById("chats-list");
const newChatBtn = document.getElementById("new-chat-btn");


let currentChatId = null;
let userText = null;
const API_URL = "http://127.0.0.1:8000"; // Backend URL



const createChatElement = (content, className) => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv;
};

const getChatResponse = async (incomingChatDiv) => {
    try {
        const response = await fetch(`${API_URL}/chats/${currentChatId}/messages/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ content: userText, user: "User" })
        }).then(res => res.json());

        const chatbotMessage = await fetch(`${API_URL}/chats/${currentChatId}`)
            .then(res => res.json())
            .then(chat => chat.messages.find(msg => msg.user === "Chatbot" && msg.content.startsWith("Echo: ")));

        const pElement = document.createElement("p");
        pElement.textContent = chatbotMessage.content;

        setTimeout(() => {
            incomingChatDiv.querySelector(".typing-animation").remove();
            incomingChatDiv.querySelector(".chat-details").appendChild(pElement);
            chatContainer.scrollTo(0, chatContainer.scrollHeight);
        }, 3000);

    } catch (error) {
        console.error("Error fetching chat response:", error);
    }
};

const showTypingAnimation = () => {
    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="/images/C4AI.png" alt="chatbot-img">
                        <div class="typing-animation">
                            <div class="typing-dot" style="--delay: 0.2s"></div>
                            <div class="typing-dot" style="--delay: 0.3s"></div>
                            <div class="typing-dot" style="--delay: 0.4s"></div>
                        </div>
                    </div>
                    <span class="material-symbols-rounded">content_copy</span>
                </div>`;
    const incomingChatDiv = createChatElement(html, "incoming");
    chatContainer.appendChild(incomingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    getChatResponse(incomingChatDiv);
};

const handleOutgoingChat = () => {
    userText = chatInput.value.trim();
    if (!userText) return;

    chatInput.value = "";
    chatInput.style.height = `${initialInputHeight}px`;

    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="images/userIcon.png" alt="user-img">
                        <p>${userText}</p>
                    </div>
                </div>`;

    const outgoingChatDiv = createChatElement(html, "outgoing");
    chatContainer.appendChild(outgoingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
    setTimeout(showTypingAnimation, 500);
};


newChatBtn.addEventListener("click", async () => {
    try {
        const response = await fetch(`${API_URL}/chats/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name: "New Chat" })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const chat = await response.json();

        currentChatId = chat.id;
        const chatElement = document.createElement("button");
        chatElement.classList.add("open-chatx")
        chatElement.classList.add("chat-item");
        chatElement.innerHTML = `
            <span class="chat-name">Chat ${chat.id}</span>
            <span class="material-symbols-rounded delete-chat" data-chat-id="${chat.id}">delete</span>
        `;
        chatElement.querySelector(".chat-name").addEventListener("click", () => loadChat(chat.id));
        chatElement.querySelector(".delete-chat").addEventListener("click", async (event) => {
            event.stopPropagation();
            await deleteChat(chat.id);
            loadChatsList();
        });
        chatsList.appendChild(chatElement);

        chatContainer.innerHTML = "";
    } catch (error) {
        console.error("Error creating new chat:", error);
    }
});

const loadChat = async (chatId) => {
    try {
        currentChatId = chatId;
        const chat = await fetch(`${API_URL}/chats/${chatId}`).then(res => res.json());
        chatContainer.innerHTML = chat.messages.map(msg => `
            <div class="chat ${msg.user === "User" ? "outgoing" : "incoming"}">
                <div class="chat-content">
                    <div class="chat-details">
                        <img src="${msg.user === "User" ? "images/userIcon.png" : "images/C4AI.png"}" alt="${msg.user}">
                        <p>${msg.content}</p>
                    </div>
                </div>
            </div>
        `).join("");
        chatContainer.scrollTo(0, chatContainer.scrollHeight);
    } catch (error) {
        console.error("Error loading chat:", error);
    }
};

const loadChatsList = async () => {
    try {
        const chats = await fetch(`${API_URL}/chats/`).then(res => res.json());
        chatsList.innerHTML = "";
        chats.forEach(chat => {
            const chatElement = document.createElement("button");
            chatElement.classList.add("open-chatx")
            chatElement.classList.add("chat-item");
            chatElement.innerHTML = `
                <span class="chat-name">Chat ${chat.id}</span>
                <span class="material-symbols-rounded delete-chat" data-chat-id="${chat.id}">delete</span>
            `;
            chatElement.querySelector(".chat-name").addEventListener("click", () => loadChat(chat.id));
            chatElement.querySelector(".delete-chat").addEventListener("click", async (event) => {
                event.stopPropagation();
                await deleteChat(chat.id);
                loadChatsList();
            });
            chatsList.appendChild(chatElement);
        });

        if (chats.length > 0) {
            loadChat(chats[0].id);
        }
    } catch (error) {
        console.error("Error loading chats list:", error);
    }
};

const deleteMessages = async () => {
    if (!currentChatId) {
        console.error("No chat selected to delete messages from.");
        return;
    }

    try {
        await fetch(`${API_URL}/chats/${currentChatId}/messages/`, {
            method: 'DELETE',
        });
        chatContainer.innerHTML = "";  // Clear the chat container in the UI
        console.log("Messages deleted successfully");
    } catch (error) {
        console.error("Error deleting messages:", error);
    }
};

const deleteChat = async (chatId) => {
    try {
        await fetch(`${API_URL}/chats/${chatId}/`, {
            method: 'DELETE',
        });
        console.log("Chat deleted successfully");
    } catch (error) {
        console.error("Error deleting chat:", error);
    }
};

themeButton.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");
    localStorage.setItem("themeColor", themeButton.innerText);
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
});

const initialInputHeight = chatInput.scrollHeight;

chatInput.addEventListener("input", () => {
    chatInput.style.height = `${initialInputHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

sendButton.addEventListener("click", handleOutgoingChat);

document.addEventListener("DOMContentLoaded", loadChatsList);
deleteButton.addEventListener("click", deleteMessages);
