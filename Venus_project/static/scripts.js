// scripts.js

function showSection(sectionId) {
    const sections = document.querySelectorAll('main section');
    sections.forEach(section => {
        if (section.id === sectionId) {
            section.classList.remove('hidden');
        } else {
            section.classList.add('hidden');
        }
    });
}

function sendMessage() {
    const userMessage = document.getElementById('userMessage').value;
    // Logic for sending message to the chatbot and displaying response
    document.getElementById('chatResponse').innerHTML += `<p>${userMessage}</p>`;
    document.getElementById('userMessage').value = '';
}

function startRiddleGame() {
    // Logic to start the riddle game
    fetch('/start_riddle_game/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('riddleGame').innerHTML = `
                <p>${data.question}</p>
                <input type="hidden" id="riddle_id" value="${data.id}">
                <input type="text" id="answer" placeholder="Your answer">
                <button onclick="submitRiddleAnswer()">Submit</button>
            `;
        });
}

function submitRiddleAnswer() {
    const riddleId = document.getElementById('riddle_id').value;
    const userAnswer = document.getElementById('answer').value;
    fetch('/submit_riddle_answer/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            riddle_id: riddleId,
            answer: userAnswer
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.is_correct) {
            document.getElementById('riddleGame').innerHTML += `<p>Correct!</p>`;
        } else {
            document.getElementById('riddleGame').innerHTML += `<p>Incorrect. The correct answer is ${data.correct_answer}</p>`;
        }
    });
}

function fetchNotifications() {
    fetch('/fetch_notifications/')
        .then(response => response.json())
        .then(data => {
            const notificationsList = document.getElementById('notificationsList');
            notificationsList.innerHTML = '';
            data.notifications.forEach(notification => {
                notificationsList.innerHTML += `<p>${notification.message}</p>`;
            });
        });
}

function viewReminders() {
    fetch('/view_reminders/')
        .then(response => response.json())
        .then(data => {
            const remindersList = document.getElementById('remindersList');
            remindersList.innerHTML = '';
            data.reminders.forEach(reminder => {
                remindersList.innerHTML += `<p>${reminder.message} at ${reminder.time}</p>`;
            });
        });
}

function fetchRecommendations() {
    fetch('/fetch_recommendations/')
        .then(response => response.json())
        .then(data => {
            const recommendationsList = document.getElementById('recommendationsList');
            recommendationsList.innerHTML = '';
            data.recommendations.forEach(recommendation => {
                recommendationsList.innerHTML += `<p>${recommendation}</p>`;
            });
        });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
