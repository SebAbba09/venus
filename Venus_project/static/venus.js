document.addEventListener("DOMContentLoaded", function() {
    // Fonction pour obtenir les cookies nécessaires pour les requêtes CSRF
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

    const csrftoken = getCookie('csrftoken');

    // Fonction pour afficher les rappels
    function loadReminders() {
        fetch('view_reminders/')
            .then(response => response.json())
            .then(data => {
                const remindersList = document.getElementById("reminders-list");
                remindersList.innerHTML = '';
                data.reminders.forEach(reminder => {
                    const reminderDiv = document.createElement('div');
                    reminderDiv.className = 'reminder-item';
                    reminderDiv.textContent = `${reminder.title}: ${reminder.message} (Due: ${new Date(reminder.time).toLocaleString()})`;

                    const editBtn = document.createElement('button');
                    editBtn.textContent = 'Edit';
                    editBtn.className = 'btn btn-primary btn-sm';
                    editBtn.addEventListener('click', function() {
                        editReminder(reminder.id);
                    });

                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = 'Delete';
                    deleteBtn.className = 'btn btn-danger btn-sm';
                    deleteBtn.addEventListener('click', function() {
                        deleteReminder(reminder.id);
                    });

                    reminderDiv.appendChild(editBtn);
                    reminderDiv.appendChild(deleteBtn);
                    remindersList.appendChild(reminderDiv);
                });
            });
    }

    // Fonction pour ajouter un rappel
    function addReminder() {
        const reminderForm = document.getElementById('reminder-form');
        const formData = new FormData(reminderForm);
        fetch('reminder/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                reminderForm.reset();
                loadReminders();
            } else {
                alert(data.message);
            }
        });
    }

    // Fonction pour éditer un rappel
    function editReminder(id) {
        // Fonctionnalité pour éditer un rappel (peut être implémentée selon les besoins spécifiques)
    }

    // Fonction pour supprimer un rappel
    function deleteReminder(id) {
        fetch('reminder/<int:pk>/delete/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: new URLSearchParams({ 'id': id })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadReminders();
            } else {
                alert(data.message);
            }
        });
    }

    // Fonction pour afficher les notifications
    function loadNotifications() {
        fetch('notifications/')
            .then(response => response.json())
            .then(data => {
                const notificationsList = document.getElementById("notifications-list");
                notificationsList.innerHTML = '';
                data.notifications.forEach(notification => {
                    const notificationDiv = document.createElement('div');
                    notificationDiv.className = 'notification-item';
                    notificationDiv.textContent = notification.message;

                    const markReadBtn = document.createElement('button');
                    markReadBtn.textContent = 'Mark as Read';
                    markReadBtn.className = 'btn btn-success btn-sm';
                    markReadBtn.addEventListener('click', function() {
                        markAsRead(notification.id);
                    });

                    notificationDiv.appendChild(markReadBtn);
                    notificationsList.appendChild(notificationDiv);
                });
            });
    }

    // Fonction pour marquer une notification comme lue






    // Chat view handler
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const userMessage = document.getElementById('message').value;
            fetch('chat_view/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ message: userMessage })
            })
                .then(response => response.json())
                .then(data => {
                    displayResponse(data.response);
                })
                .catch(error => console.error('Error:', error));
        });
    }

    // Chat view with context handler
    const chatContextForm = document.getElementById('chat-context-form');
    if (chatContextForm) {
        chatContextForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const userMessage = document.getElementById('context-message').value;
            fetch('chat_with_context/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ message: userMessage })
            })
                .then(response => response.json())
                .then(data => {
                    displayResponse(data.response);
                    displayRecommendations(data.recommendations);
                })
                .catch(error => console.error('Error:', error));
        });
    }

    // Notification view handler
    const notificationButton = document.getElementById('notification-button');
    if (notificationButton) {
        notificationButton.addEventListener('click', function () {
            fetch('notifications/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                }
            })
                .then(response => response.json())
                .then(data => {
                    displayNotifications(data);
                })
                .catch(error => console.error('Error:', error));
        });
    }

    // Mark as read handler
    const notificationsContainer = document.getElementById('notifications-container');
    if (notificationsContainer) {
        notificationsContainer.addEventListener('click', function (event) {
            if (event.target.classList.contains('mark-as-read')) {
                const notificationId = event.target.dataset.id;
                fetch(`/notifications/read/${notificationId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken(),
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            event.target.parentElement.remove();
                        }
                    })
                    .catch(error => console.error('Error:', error));
            }
        });
    }


});
