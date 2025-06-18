let ws = null;
let userId = null;
let username = null;
let email = null;
let role = null;

function connectWebSocket() {
    const chatData = document.getElementById("chat-data");
    if (!chatData) {
        console.error("chat-data element not found");
        return;
    }

    // Получаем данные пользователя из DOM
    userId = chatData.dataset.userId;
    username = chatData.dataset.username;
    email = chatData.dataset.email;
    role = chatData.dataset.role;

    const roomId = chatData.dataset.roomId;
    const wsUrl = `ws://${window.location.host}/ws/v1/chat/${roomId}/${userId}?username=${encodeURIComponent(username)}&email=${encodeURIComponent(email)}&role=${encodeURIComponent(role)}`;

    ws = new WebSocket(wsUrl);

    // Отправляем данные аутентификации
    ws.onopen = () => {
        console.log("WebSocket connected");
        ws.send(JSON.stringify({
            type: "auth",
            userId: userId,
            username: username,
            email: email,
            role: role
        }));
        ws.send(JSON.stringify({ command: "get_history" }));

        if (role === "admin") {
            loadAllRooms();
            loadAllUsers();
            document.getElementById("createRoomBtn")?.addEventListener("click", createRoom);
            document.getElementById("deleteRoomBtn")?.addEventListener("click", deleteRoom);
            document.getElementById("addUserBtn")?.addEventListener("click", addUserToRoom);
            document.getElementById("removeUserBtn")?.addEventListener("click", removeUserFromRoom);
        }
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === "history") {
                data.messages.forEach((msg) => {
                    displayMessage(msg, msg.username === username);
                });
            } else if (data.type === "message") {
                displayMessage(data, data.is_self);
            } else if (data.type === "system") {
                displaySystemMessage(data);
            } else if (data.type === "users_update") {
                updateUsersList(data.users);
            }
        } catch (e) {
            console.error("Ошибка обработки сообщения:", e);
        }
    };

    ws.onclose = () => {
        console.log("WebSocket отключён, повторное подключение через 3 сек.");
        setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        const messages = document.getElementById("messages");
        if (messages) {
            const errorDiv = document.createElement("div");
            errorDiv.className = "flex justify-center my-2 text-red-600";
            errorDiv.innerHTML = `<span>Ошибка соединения. Переподключение...</span>`;
            messages.appendChild(errorDiv);
        }
    };
}

// Send message
function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input ? input.value.trim() : "";

    if (!input || !ws || ws.readyState !== WebSocket.OPEN || !message) {
        console.warn("Сообщение не отправлено: WebSocket не готов или поле пустое");
        return;
    }

    try {
        const messageObj = {
            text: message,
            timestamp: Date.now()
        };
        ws.send(JSON.stringify(messageObj));
        input.value = "";
        input.focus();
    } catch (e) {
        console.error("Ошибка при отправке сообщения:", e);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initChatPage().catch(err => console.error("initChatPage failed", err));

    const sendButton = document.getElementById("sendButton");
    const messageInput = document.getElementById("messageInput");

    if (sendButton) {
        sendButton.addEventListener("click", sendMessage);
    }

    if (messageInput) {
        messageInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

});

async function initChatPage() {
    connectWebSocket();
}

// Загрузка текущих комнат
async function loadAllUsers() {
    try {
        const response = await fetch("/ws/v1/chat/users");
        const users = await response.json();

        const addUserSelect = document.getElementById("addUserEmail");
        const removeUserSelect = document.getElementById("removeUserEmail");

        if (!users || users.length === 0) {
            console.warn("Список пользователей пуст");
            if (addUserSelect) addUserSelect.innerHTML = "<option value=''>Нет доступных пользователей</option>";
            if (removeUserSelect) removeUserSelect.innerHTML = "<option value=''>Нет доступных пользователей</option>";
            return;
        }

        // Очистка текущих опций
        if (addUserSelect) {
            addUserSelect.innerHTML = "<option value=''>Выберите пользователя</option>";
            users.forEach(user => {
                const option = document.createElement("option");
                option.value = user.email;
                option.textContent = `${user.name} (${user.email})`;
                addUserSelect.appendChild(option);
            });
        }

        if (removeUserSelect) {
            removeUserSelect.innerHTML = "<option value=''>Выберите пользователя</option>";
            users.forEach(user => {
                const option = document.createElement("option");
                option.value = user.email;
                option.textContent = `${user.name} (${user.email})`;
                removeUserSelect.appendChild(option);
            });
        }

    } catch (e) {
        console.error("Ошибка загрузки пользователей:", e);
        if (document.getElementById("addUserEmail")) {
            document.getElementById("addUserEmail").innerHTML = "<option value=''>Ошибка загрузки</option>";
        }
        if (document.getElementById("removeUserEmail")) {
            document.getElementById("removeUserEmail").innerHTML = "<option value=''>Ошибка загрузки</option>";
        }
    }
}
// Загрузка текущих пользователей
async function loadAllRooms() {
    try {
        const response = await fetch("/ws/v1/chat/rooms");
        const rooms = await response.json();

        const addUserRoomSelect = document.getElementById("addUserRoomId");
        const removeUserRoomSelect = document.getElementById("removeUserRoomId");
        const switchRoomSelect = document.getElementById("switchRoomSelect");
        const roomToDeleteSelect = document.getElementById("roomToDeleteSelect");

        if (!rooms || rooms.length === 0) {
            [addUserRoomSelect, removeUserRoomSelect, switchRoomSelect, roomToDeleteSelect].forEach(select => {
                if (select) select.innerHTML = "<option value=''>Нет доступных комнат</option>";
            });
            return;
        }

        const currentRoomId = document.getElementById("chat-data")?.dataset?.roomId;

        // Для добавления
        if (addUserRoomSelect) {
            addUserRoomSelect.innerHTML = "<option value=''>Выберите комнату</option>";
            rooms.forEach(room => {
                const option = document.createElement("option");
                option.value = room.id;
                option.textContent = room.name;
                addUserRoomSelect.appendChild(option);
            });
        }

        // Для удаления
        if (removeUserRoomSelect) {
            removeUserRoomSelect.innerHTML = "<option value=''>Выберите комнату</option>";
            rooms.forEach(room => {
                const option = document.createElement("option");
                option.value = room.id;
                option.textContent = room.name;
                removeUserRoomSelect.appendChild(option);
            });
        }

        // Для переключения
        if (switchRoomSelect) {
            switchRoomSelect.innerHTML = "";
            const currentRoomId = document.getElementById("chat-data").dataset.roomId;
            const selectDiv = document.createElement("div");
            selectDiv.className = "flex items-center gap-2";

            const select = document.createElement("select");
            select.id = "switchRoomSelect";
            select.className = "w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 bg-white";
            select.innerHTML = "<option value=''>Выберите комнату</option>";

            rooms.forEach(room => {
                if (room.id !== currentRoomId) {
                    const option = document.createElement("option");
                    option.value = room.id;
                    option.textContent = room.name;
                    select.appendChild(option);
                }
            });

            const button = document.createElement("button");
            button.type = "button";
            button.className = "p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600";
            button.textContent = "Переключиться";
            button.onclick = async () => {
                const newRoomId = select.value;
                if (!newRoomId) return alert("Выберите комнату для переключения");

                const response = await fetch("/ws/v1/chat/switch_room", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: `user_id=${encodeURIComponent(userId)}&new_room_id=${encodeURIComponent(newRoomId)}&username=${encodeURIComponent(username)}&email=${encodeURIComponent(email)}&role=${encodeURIComponent(role)}`
                });

                const data = await response.json();
                if (data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    alert(data.error || "Ошибка переключения комнаты");
                }
            };

            selectDiv.appendChild(select);
            selectDiv.appendChild(button);
            switchRoomSelect.appendChild(selectDiv);
        }

        // Для удаления комнаты
        if (roomToDeleteSelect) {
            roomToDeleteSelect.innerHTML = "<option value=''>Выберите комнату</option>";
            rooms.forEach(room => {
                const option = document.createElement("option");
                option.value = room.id;
                option.textContent = `${room.name} (ID: ${room.id})`;
                roomToDeleteSelect.appendChild(option);
            });
        }

    } catch (e) {
        console.error("Ошибка загрузки комнат:", e);
        [addUserRoomSelect, removeUserRoomSelect, switchRoomSelect, roomToDeleteSelect].forEach(select => {
            if (select) select.innerHTML = "<option value=''>Ошибка загрузки</option>";
        });
    }
}

// Switch room
window.switchRoom = async (newRoomId) => {
    try {
        const response = await fetch("/ws/v1/chat/switch_room", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `user_id=${encodeURIComponent(userId)}&new_room_id=${encodeURIComponent(newRoomId)}&username=${encodeURIComponent(username)}&email=${encodeURIComponent(email)}&role=${encodeURIComponent(role)}`
        });

        const data = await response.json();
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            alert(data.error || "Ошибка переключения комнаты");
        }
    } catch (error) {
        console.error("Ошибка переключения комнаты:", error);
        alert("Ошибка сети при переключении комнаты");
    }
};

// Показ сообщений в чате
function displayMessage(message, isSelf) {
    const messages = document.getElementById("messages");
    if (!messages) return;

    const messageDiv = document.createElement("div");
    messageDiv.className = `flex ${isSelf ? "justify-end" : "justify-start"}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = `max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${isSelf ? "bg-blue-100" : "bg-gray-100"}`;

    const usernameSpan = document.createElement("span");
    usernameSpan.className = "text-sm font-semibold";
    usernameSpan.textContent = message.username || "Unknown";

    const textDiv = document.createElement("div");
    textDiv.className = "mt-1";
    textDiv.textContent = message.text;

    contentDiv.appendChild(usernameSpan);
    contentDiv.appendChild(textDiv);
    messageDiv.appendChild(contentDiv);
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

// Сообщения системы
function displaySystemMessage(message) {
    const messages = document.getElementById("messages");
    if (!messages) return;

    const systemDiv = document.createElement("div");
    systemDiv.className = "flex justify-center my-2";

    const contentDiv = document.createElement("div");
    contentDiv.className = "bg-gray-200 px-3 py-1 rounded-full text-sm text-gray-600";
    contentDiv.textContent = message.text;

    systemDiv.appendChild(contentDiv);
    messages.appendChild(systemDiv);
    messages.scrollTop = messages.scrollHeight;
}

// Обновление пользователей онлайн
function updateUsersList(users) {
    const onlineCount = document.getElementById("onlineCount");
    if (onlineCount) {
        onlineCount.textContent = `${users.length} онлайн`;
    }
}

// Функции администратора
async function createRoom() {
    const roomName = document.getElementById("newRoomName").value.trim();
    if (!roomName) return alert("Введите название комнаты");

    const response = await fetch("/ws/v1/chat/create_room", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name: roomName })
    });

    const data = await response.json();
    if (data.success) {
        alert("Комната создана!");
        loadAllRooms();
        loadAllUsers();
    } else {
        alert(data.error || "Ошибка создания комнаты");
    }
}

async function deleteRoom() {
    const selectedRoomId = document.getElementById("roomToDeleteSelect").value;
    if (!selectedRoomId) return alert("Выберите комнату для удаления");

    const response = await fetch(`/ws/v1/chat/delete_room`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `room_id=${encodeURIComponent(selectedRoomId)}`
    });

    const data = await response.json();
    if (data.success) {
        alert("Комната удалена!");
        loadAllRooms();
        loadAllUsers();
    } else {
        alert(data.error || "Ошибка удаления комнаты");
    }
}

async function addUserToRoom() {
    const selectedEmail = document.getElementById("addUserEmail").value.trim();
    const selectedRoomId = document.getElementById("addUserRoomId").value;

    if (!selectedEmail || !selectedRoomId) {
        alert("Выберите пользователя и комнату");
        return;
    }

    const response = await fetch("/ws/v1/chat/add_user_to_room", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `email=${encodeURIComponent(selectedEmail)}&room_id=${encodeURIComponent(selectedRoomId)}`
    });

    const data = await response.json();
    if (data.success) {
        alert("Пользователь добавлен в комнату");
        loadAllUsers();
        loadAllRooms();
    } else {
        alert(data.error || "Ошибка добавления пользователя");
    }
}

async function removeUserFromRoom() {
    const selectedEmail = document.getElementById("removeUserEmail").value.trim();
    const selectedRoomId = document.getElementById("removeUserRoomId").value;

    if (!selectedEmail || !selectedRoomId) {
        alert("Выберите пользователя и комнату");
        return;
    }

    const response = await fetch("/ws/v1/chat/remove_user_from_room", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `email=${encodeURIComponent(selectedEmail)}&room_id=${encodeURIComponent(selectedRoomId)}`
    });

    const data = await response.json();
    if (data.success) {
        alert("Пользователь удален из комнаты");
        loadAllUsers();
        loadAllRooms();
    } else {
        alert(data.error || "Ошибка удаления пользователя");
    }
}
