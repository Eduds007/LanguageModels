

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

const sendMessage = async () => {
    if (!userText || !currentChatId) return;

    try {
        // Enviar a mensagem do usuário para o backend
        const response = await fetch(`${API_URL}/chats/${currentChatId}/messages/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ content: userText, user: "User" })
        });

        if (!response.ok) {
            throw new Error("Failed to send message");
        }

        // Adicionar a mensagem do usuário na interface
        const chatElement = createChatElement(userText, "outgoing");
        chatContainer.appendChild(chatElement);
        chatContainer.scrollTo(0, chatContainer.scrollHeight);

        // Esperar pela resposta do chatbot
        await getChatResponse();

    } catch (error) {
        console.error("Error sending message:", error);
    }
};

const getChatResponse2 = async () => {
    try {
        const timeout = 180000; // 3 minutos em milissegundos
        const startTime = Date.now();

        while (Date.now() - startTime < timeout) {
            const response = await fetch(`${API_URL}/chats/${currentChatId}`);
            const chat = await response.json();

            // Encontrar a última mensagem do chatbot
            const chatbotMessage = chat.messages
                .reverse()
                .find(msg => msg.user === "Chatbot");

            if (chatbotMessage) {
                const chatElement = createChatElement(chatbotMessage.content, "incoming");
                chatContainer.appendChild(chatElement);
                chatContainer.scrollTo(0, chatContainer.scrollHeight);
                return;
            }

            await new Promise(resolve => setTimeout(resolve, 1000)); // Esperar 1 segundo antes de tentar novamente
        }

        console.error("Timeout: No response from chatbot within 3 minutes");

    } catch (error) {
        console.error("Error fetching chat response:", error);
    }
};



const createChatElement = (content, className) => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv;
};

const getChatResponse1 = async (incomingChatDiv) => {
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

const handleOutgoingChat = async () => {
    userText = chatInput.value.trim();
    if (!userText) return;

    // Limpa o campo de entrada e ajusta a altura
    chatInput.value = "";
    chatInput.style.height = `${initialInputHeight}px`;

    // Cria e exibe a mensagem do usuário no front-end
    const userMessageHtml = `
        <div class="chat-content">
            <div class="chat-details">
                <img src="images/userIcon.png" alt="user-img">
                <p>${userText}</p>
            </div>
        </div>`;
    const outgoingChatDiv = createChatElement2(userMessageHtml, "outgoing");
    chatContainer.appendChild(outgoingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    // Cria e exibe o elemento de resposta do chatbot com animação de digitação
    const typingChatDiv = document.createElement('div');
    typingChatDiv.className = "chat incoming typing-animation";  // Adiciona uma classe única para a animação
    typingChatDiv.innerHTML = `
        <div class="chat-content">
            <div class="chat-details">
                <img src="images/C4AI.png" alt="chatbot-img">
                <div class="typing-animation">
                    <div class="typing-dot" style="--delay: 0.2s"></div>
                    <div class="typing-dot" style="--delay: 0.3s"></div>
                    <div class="typing-dot" style="--delay: 0.4s"></div>
                </div>
            </div>
        </div>`;
    chatContainer.appendChild(typingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    try {
        // Envia a mensagem do usuário para o backend
        const response = await fetch(`${API_URL}/chats/${currentChatId}/messages/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ content: userText, user: "User" })
        });

        if (!response.ok) {
            throw new Error("Failed to send message");
        }   

        responseData = await response.json();


        updateChatWithResponse(responseData);

    } catch (error) {
        console.error("Error sending message:", error);
        removeTypingAnimation(); // Remove a animação em caso de erro
    }
};

const updateChatWithResponse = (responseData) => {
    // Encontra e remove a animação de digitação
    const typingChatDiv = chatContainer.querySelector(".typing-animation");
    if (typingChatDiv) {
        // Substitui a animação de digitação pela mensagem do chatbot
        typingChatDiv.innerHTML = `
            <div class="chat-content">
                <div class="chat-details">
                    <img src="images/C4AI.png" alt="chatbot-img">
                    <p>${responseData.content}</p>  <!-- Ajuste o acesso ao conteúdo conforme necessário -->
                </div>
            </div>`;
        typingChatDiv.classList.remove("typing-animation"); // Remove a classe de animação
    }
};

const removeTypingAnimation = () => {
    const typingChatDiv = chatContainer.querySelector(".typing-animation");
    if (typingChatDiv) {
        chatContainer.removeChild(typingChatDiv); // Remove o elemento de animação do DOM
    }
};

const createChatElement2 = (html, type) => {
    // Cria um novo elemento de chat e aplica a classe com base no tipo
    const div = document.createElement('div');
    div.className = `chat ${type}`;
    div.innerHTML = html;
    return div;
};


const getChatResponse = async () => {
    try {
        const timeout = 180000; // 3 minutos em milissegundos
        const startTime = Date.now();

        while (Date.now() - startTime < timeout) {
            const response = await fetch(`${API_URL}/chats/${currentChatId}`);
            const chat = await response.json();

            // Encontrar a última mensagem do chatbot
            const chatbotMessage = chat.messages
                .reverse()
                .find(msg => msg.user === "Chatbot");

            if (chatbotMessage) {
                const chatElement = createChatElement(chatbotMessage.content, "incoming");
                chatContainer.appendChild(chatElement);
                chatContainer.scrollTo(0, chatContainer.scrollHeight);
                return;
            }

            await new Promise(resolve => setTimeout(resolve, 1000)); // Esperar 1 segundo antes de tentar novamente
        }

        console.error("Timeout: No response from chatbot within 3 minutes");

    } catch (error) {
        console.error("Error fetching chat response:", error);
    }
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
            chatElement.classList.add("open-chatx");
            chatElement.classList.add("chat-item");
            chatElement.innerHTML = `
                <span class="chat-name">Chat ${chat.id}</span>
                <span class="material-symbols-rounded delete-chat" data-chat-id="${chat.id}">delete</span>
            `;
            
            // Adiciona o event listener para o botão inteiro
            chatElement.addEventListener("click", () => loadChat(chat.id));
            
            chatElement.querySelector(".delete-chat").addEventListener("click", async (event) => {
                event.stopPropagation();  // Impede que o clique no botão delete também carregue o chat
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
