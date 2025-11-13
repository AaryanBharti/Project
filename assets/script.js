const chatContainer = document.querySelector(".chats-container");
const promptForm = document.querySelector(".prompt-form");
const promptInput = document.querySelector(".prompt-input");
const fileInput = document.querySelector("#file-input");
const filePreview = document.querySelector(".file-preview");
const cancelFileBtn = document.querySelector("#cancel-file-btn");
const addFileBtn = document.querySelector("#add-file-btn");
const stopResponseBtn = document.querySelector("#stop-response-btn");
const themeToggleBtn = document.querySelector("#theme-toggle-btn");
const deleteChatsBtn = document.querySelector("#delete-chats-btn");
const suggestionsContainer = document.querySelector(".suggestions");

let controller = null;
let filesArray = [];

const removeSuggestions = () => suggestionsContainer.classList.add("hidden");

const handleFormSubmission = async (userMessage, filesData = []) => {
    const formData = {
        query: userMessage,  // Changed from message to query to match backend
        files: filesData,
    };
    
    try {
        controller = new AbortController();
        const response = await fetch("http://127.0.0.1:8502/api/research", {  // Use full URL
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(formData),
            signal: controller.signal,
        });

        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        return data;
    } catch (error) {
        if (error.name === "AbortError") {
            throw new Error("Request aborted.");
        }
        throw new Error("Something went wrong. Please try again.");
    }
};

const createChatElement = (content, className) => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = `
        <div class="chat-content">
            <div class="chat-details">
                <img src="${className === "outgoing" ? "assets/user.jpg" : "assets/chatbot.jpg"}" alt="chat-avatar">
                <p>${content}</p>
            </div>
        </div>
    `;
    return chatDiv;
};

const getChatResponse = async (incomingChatDiv, userMessage) => {
    try {
        const response = await handleFormSubmission(userMessage, filesArray);
        incomingChatDiv.querySelector(".typing-animation")?.remove();
        
        // Create response content
        const contentDiv = document.createElement("div");
        contentDiv.className = "chat-response";
        
        // Add main response
        if (response.summary) {
            const mainResponse = document.createElement("div");
            mainResponse.className = "main-response";
            mainResponse.textContent = response.summary;
            contentDiv.appendChild(mainResponse);
        }
        
        // Add sources if available
        if (response.sources && response.sources.length > 0) {
            const sourcesDiv = document.createElement("div");
            sourcesDiv.className = "sources";
            
            response.sources.forEach(source => {
                const sourceCard = document.createElement("a");
                sourceCard.href = source.url;
                sourceCard.target = "_blank";
                sourceCard.className = "source-card";
                
                // Add thumbnail if available
                if (source.thumbnail) {
                    const img = document.createElement("img");
                    img.src = source.thumbnail;
                    img.alt = source.title;
                    sourceCard.appendChild(img);
                }
                
                const sourceInfo = document.createElement("div");
                sourceInfo.className = "source-info";
                sourceInfo.innerHTML = `
                    <div class="source-title">${source.title || 'Source'}</div>
                    <div class="source-text">${source.text.substring(0, 150)}...</div>
                    <div class="source-domain">${source.source}</div>
                `;
                sourceCard.appendChild(sourceInfo);
                sourcesDiv.appendChild(sourceCard);
            });
            
            contentDiv.appendChild(sourcesDiv);
        }
        
        // Add suggestions if available
        if (response.suggestions && response.suggestions.length > 0) {
            const suggestionsDiv = document.createElement("div");
            suggestionsDiv.className = "response-suggestions";
            
            response.suggestions.forEach(suggestion => {
                const suggestionBtn = document.createElement("button");
                suggestionBtn.className = "suggestion-btn";
                suggestionBtn.textContent = suggestion.text;
                suggestionBtn.onclick = () => {
                    promptInput.value = suggestion.text;
                    promptForm.dispatchEvent(new Event("submit"));
                };
                suggestionsDiv.appendChild(suggestionBtn);
            });
            
            contentDiv.appendChild(suggestionsDiv);
        }
        
        const chatDetails = incomingChatDiv.querySelector(".chat-details");
        chatDetails.innerHTML = ""; // Clear existing content
        chatDetails.appendChild(contentDiv);
        
    } catch (error) {
        incomingChatDiv.querySelector(".typing-animation")?.remove();
        incomingChatDiv.querySelector(".chat-details").innerHTML = 
            '<p class="error-message">Oops! Something went wrong. Please try again.</p>';
    } finally {
        filesArray = [];
        stopResponseBtn.style.display = "none";
        promptForm.reset();
    }
};

const handleChat = async (e) => {
    e.preventDefault();
    const userMessage = promptInput.value.trim();
    if(!userMessage) return;

    removeSuggestions();
    stopResponseBtn.style.display = "block";

    // Append the user's message to the chat
    chatContainer.appendChild(createChatElement(userMessage, "outgoing"));
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    // Create and append the incoming chat div
    const incomingChatDiv = createChatElement("Thinking...", "incoming");
    chatContainer.appendChild(incomingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    await getChatResponse(incomingChatDiv, userMessage);
};

const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if(!file) return;

    filesArray.push(file);
    filePreview.src = URL.createObjectURL(file);
    filePreview.style.display = "block";
    cancelFileBtn.style.display = "block";
    addFileBtn.style.display = "none";
};

const handleFileCancel = () => {
    filesArray = [];
    filePreview.src = "";
    filePreview.style.display = "none";
    cancelFileBtn.style.display = "none";
    addFileBtn.style.display = "block";
    fileInput.value = "";
};

const handleThemeToggle = () => {
    document.body.classList.toggle("dark-mode");
    localStorage.setItem("theme", document.body.classList.contains("dark-mode") ? "dark" : "light");
    themeToggleBtn.innerText = document.body.classList.contains("dark-mode") ? "light_mode" : "dark_mode";
};

const handleDeleteChats = () => {
    if(confirm("Are you sure you want to delete all chats?")) {
        chatContainer.innerHTML = "";
        localStorage.removeItem("all-chats");
    }
};

const handleSuggestionClick = (e) => {
    const clickedSuggestion = e.target.closest(".suggestions-item");
    if(clickedSuggestion) {
        const suggestionText = clickedSuggestion.querySelector(".text").textContent;
        promptInput.value = suggestionText;
        promptForm.dispatchEvent(new Event("submit"));
    }
};

promptForm.addEventListener("submit", handleChat);
fileInput.addEventListener("change", handleFileUpload);
cancelFileBtn.addEventListener("click", handleFileCancel);
addFileBtn.addEventListener("click", () => fileInput.click());
stopResponseBtn.addEventListener("click", () => controller?.abort());
themeToggleBtn.addEventListener("click", handleThemeToggle);
deleteChatsBtn.addEventListener("click", handleDeleteChats);
suggestionsContainer.addEventListener("click", handleSuggestionClick);

// Load saved theme from localStorage
if(localStorage.getItem("theme") === "dark") {
    handleThemeToggle();
}