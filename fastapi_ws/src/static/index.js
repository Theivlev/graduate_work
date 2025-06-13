function escapeHtml(unsafe) {
  return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
}

function initChatPage() {
  const chatData = document.getElementById("chat-data");
  if (!chatData) return;

  const roomId = chatData.dataset.roomId;
  const userId = chatData.dataset.userId;
  const username = chatData.dataset.username;
  const role = chatData.dataset.role;
  const wsUrl = chatData.dataset.websocketUrl;
  console.log('Connecting to:', `ws://${window.location.host}${wsUrl}`);
  const fullWsUrl = `ws://${window.location.host}${wsUrl}?username=${encodeURIComponent(username)}&role=${role}`;

  let ws;

  function connectWebSocket() {
      ws = new WebSocket(fullWsUrl);

      ws.onopen = () => {
          console.log("WebSocket подключён");
          ws.send(JSON.stringify({ command: "get_history" }));
          if (role === "admin") {
              loadRooms();
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
            errorDiv.className = "flex justify-center my-2";
            errorDiv.innerHTML = `
                <div class="text-xs text-red-500 italic px-2 py-1 bg-gray-100 rounded">
                    Ошибка соединения с чатом
                </div>
            `;
            messages.appendChild(errorDiv);
        }
    };

  }

  function displayMessage(data, isSelf) {
      const messages = document.getElementById("messages");
      const messageDiv = document.createElement("div");
      messageDiv.className = isSelf ? "flex justify-end" : "flex justify-start";

      messageDiv.innerHTML = `
          <div class="max-w-xs lg:max-w-md">
              <div class="${isSelf ? "flex justify-end items-center" : "flex items-center"} mb-1">
                  ${!isSelf ? `<span class="text-sm font-medium mr-2">${escapeHtml(data.username)}</span>` : ""}
                  <span class="text-xs text-gray-500">${new Date(data.timestamp * 1000).toLocaleTimeString()}</span>
                  ${isSelf ? '<span class="text-sm font-medium ml-2">Вы</span>' : ""}
              </div>
              <div class="px-4 py-2 rounded-lg ${isSelf ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"}">
                  ${escapeHtml(data.text)}
              </div>
          </div>
      `;
      messages.appendChild(messageDiv);
      messages.scrollTop = messages.scrollHeight;
  }

  function displaySystemMessage(data) {
      const messages = document.getElementById("messages");
      const messageDiv = document.createElement("div");
      messageDiv.className = "flex justify-center my-2";
      messageDiv.innerHTML = `
          <div class="text-xs text-gray-500 italic px-2 py-1 bg-gray-100 rounded">
              ${escapeHtml(data.text)}
          </div>
      `;
      messages.appendChild(messageDiv);
      messages.scrollTop = messages.scrollHeight;
  }

  function updateUsersList(users) {
      const onlineCount = document.getElementById("onlineCount");
      if (onlineCount) {
          onlineCount.textContent = `${users.length} онлайн`;
      }
  }

  async function loadRooms() {
    try {
        const response = await fetch("/ws/v1/chat/get_rooms");

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(
                errorData.error || `HTTP error! status: ${response.status}`
            );
        }

        const data = await response.json();

        if (data.success && data.rooms) {
            const roomsList = document.getElementById("roomsList");
            if (roomsList) {
                roomsList.innerHTML = data.rooms
                    .map(room => `
                        <div class="flex justify-between items-center p-2 border rounded-lg ${
                            room.id === roomId ? "bg-blue-50" : ""
                        }">
                            <span>${escapeHtml(room.name)} (${room.users_count || 0} пользователей)</span>
                            ${
                                room.id !== roomId
                                    ? `<button onclick="switchRoom('${room.id}')"
                                       class="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
                                        Перейти
                                      </button>`
                                    : ""
                            }
                        </div>
                    `)
                    .join("");
            }
        } else {
            console.error("Server returned unsuccessful response:", data);
            showError("Не удалось загрузить список комнат");
        }
    } catch (error) {
        console.error("Ошибка загрузки комнат:", error);
        showError(`Ошибка: ${error.message}`);
    }
}


function sendMessage() {
  const input = document.getElementById("messageInput");
  const message = input.value.trim();
  if (ws && ws.readyState === WebSocket.OPEN && message) {
      try {
          const messageObj = {
              text: message,
              timestamp: Date.now()
          };
          ws.send(JSON.stringify(messageObj));
          input.value = "";
          input.focus();
      } catch (e) {
          console.error("Error sending message:", e);
      }
  }
}

  document.getElementById("sendButton").addEventListener("click", sendMessage);
  document.getElementById("messageInput").addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
          sendMessage();
      }
  });

  if (role === "admin") {
      document.getElementById("createRoomBtn").addEventListener("click", createRoom);
  }

  window.switchRoom = async (newRoomId) => {
      const response = await fetch("/ws/v1/chat/switch_room", {
          method: "POST",
          headers: {
              "Content-Type": "application/x-www-form-urlencoded"
          },
          body: `user_id=${userId}&old_room_id=${roomId}&new_room_id=${newRoomId}&username=${encodeURIComponent(
              username
          )}&role=${role}`
      });
      const data = await response.json();
      if (data.success) {
          window.location.href = data.redirect_url;
      }
  };

  function createRoom() {
      const roomName = document.getElementById("newRoomName").value.trim();
      if (!roomName) return;
      fetch("/ws/v1/chat/create_room_api", {
          method: "POST",
          headers: {
              "Content-Type": "application/x-www-form-urlencoded"
          },
          body: `name=${encodeURIComponent(roomName)}&username=${encodeURIComponent(username)}`
      })
          .then((res) => res.json())
          .then((data) => {
              if (data.success) {
                  window.location.href = data.redirect_url;
              }
          })
          .catch((err) => console.error("Ошибка создания комнаты:", err));
  }

  connectWebSocket();
}

function initHomePage() {
  document.getElementById("createRoomForm").addEventListener("submit", function(e) {
      e.preventDefault();
      const adminName = document.getElementById("adminName").value.trim();
      const roomName = document.getElementById("roomName").value.trim();

      if (!adminName || !roomName) {
          showError("Заполните все поля");
          return;
      }

      fetch("/ws/v1/chat/create_room_api", {
          method: "POST",
          headers: {
              "Content-Type": "application/x-www-form-urlencoded",
          },
          body: `username=${encodeURIComponent(adminName)}&name=${encodeURIComponent(roomName)}`
      })
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              window.location.href = data.redirect_url;
          } else {
              showError(data.error || "Ошибка создания комнаты");
          }
      })
      .catch(error => showError("Ошибка сети"));
  });

  document.getElementById("joinRoomForm").addEventListener("submit", function(e) {
      e.preventDefault();
      const username = document.getElementById("username").value.trim();
      const roomId = document.getElementById("roomId").value.trim();

      if (!username || !roomId) {
          showError("Заполните все поля");
          return;
      }

      fetch("/ws/v1/chat/join_chat_api", {
          method: "POST",
          headers: {
              "Content-Type": "application/x-www-form-urlencoded",
          },
          body: `username=${encodeURIComponent(username)}&room_id=${encodeURIComponent(roomId)}`
      })
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              window.location.href = data.redirect_url;
          } else {
              showError(data.error || "Ошибка входа в комнату");
          }
      })
      .catch(error => showError("Ошибка сети"));
  });

  function showError(message) {
      const errorDiv = document.getElementById("error");
      errorDiv.textContent = message;
      setTimeout(() => errorDiv.textContent = '', 3000);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("chat-data")) {
      initChatPage();
  } else {
      initHomePage();
  }
});
