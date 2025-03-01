

// Toggle the visibility of the chatbot
chatToggleButton.onclick = function () {
    aiChatbot.classList.toggle("hidden");
}

// Close the chatbot when the close button is clicked
closeChatButton.onclick = function () {
    aiChatbot.classList.add("hidden");
}

// Handle form submission (for adding a message to the chat)
chatForm.onsubmit = function (event) {
    event.preventDefault(); // Prevent form from refreshing the page

    const userMessage = chatInput.value.trim();
    if (userMessage !== "") {
        // Add the user message to the chat
        const userMessageElement = document.createElement("div");
        userMessageElement.classList.add("bg-indigo-100", "p-2", "rounded-lg", "text-gray-700");
        userMessageElement.textContent = userMessage;
        chatMessages.appendChild(userMessageElement);

        // Clear the input field
        chatInput.value = "";

        // Scroll to the bottom of the messages
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Optionally, add an AI response (for demonstration)
        setTimeout(() => {
            const aiMessageElement = document.createElement("div");
            aiMessageElement.classList.add("bg-gray-100", "p-2", "rounded-lg", "text-gray-700");
            aiMessageElement.textContent = "";
            chatMessages.appendChild(aiMessageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 1000); // Simulate a response after 1 second
    }
};

const ctx = document.getElementById('spendingChart').getContext('2d');
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Groceries', 'Entertainment', 'Coffee'],
        datasets: [{
            label: 'Spending ($)',
            data: [150, 80, 50],
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    },
    options: { scales: { y: { beginAtZero: true } } }
});

// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    // Select all the words in the welcome overlay
    const words = document.querySelectorAll('.word');

    // Set each word's animation delay dynamically
    words.forEach((word, index) => {
        word.style.setProperty('--word-index', index);
    });

    // After the animation finishes (about 4 seconds), fade out the welcome overlay and show the main content
    setTimeout(function () {
        document.querySelector('.welcome-overlay').classList.add('fade-out');
        document.querySelector('.hero').style.display = 'block'; // Show the main content
    }, 4000); // Timing matches the fade-in duration
});

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function askGemini() {
    const query = document.getElementById("userQuery").value;
    const responseDiv = document.getElementById("response");

    responseDiv.innerText = "Loading...";
    
    const response = await fetch("/ask_gemini", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ query })
    });

    const data = await response.json();
    responseDiv.innerText = data.response || "Error: " + data.error;
}





