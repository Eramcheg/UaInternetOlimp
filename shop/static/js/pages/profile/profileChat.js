import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.10/firebase-app.js";
import { getFirestore, collection, query, onSnapshot, doc, getDoc, setDoc, serverTimestamp, addDoc,updateDoc, where, orderBy } from "https://www.gstatic.com/firebasejs/9.6.10/firebase-firestore.js";
import { getStorage, ref as storageRef, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/9.6.10/firebase-storage.js";
const firebaseConfig = {
    apiKey: "AIzaSyAzV7CPVJJbgteozTbjdlIcyt85Kbuxd90",
    authDomain: "uainternetolimp-41dd1.firebaseapp.com",
    projectId: "uainternetolimp-41dd1",
    storageBucket: "uainternetolimp-41dd1.appspot.com",
    messagingSenderId: "545486624571",
    appId: "1:545486624571:web:4a543063a04b43e5bb091e",
    measurementId: "G-MJBJXCE1SJ"};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const storage = getStorage(app);
let currentChatId = null;
let userId = window.config.userId;
let user_class = window.config.userClass;
let role = window.config.userRole;
let tour = window.config.currentTour;
let year = window.config.currentYear;
let tasks = window.config.tasks_chat || {};
let username = window.config.username;
const chatMessagesRef = collection(db, "messages");
const q = query(chatMessagesRef, where("chat_id", "==", currentChatId), orderBy("timestamp"));
const chatMessagesRef2 = collection(db, "messages");
const q2 = query(chatMessagesRef2, orderBy("activity"));

document.addEventListener("DOMContentLoaded", async function () {
    if(role !== "Student"){
        setUpChats();
    }
    if(currentChatId === null){
        const button = document.getElementById('chat-message-submit');
        button.disabled = true;
        button.style.backgroundColor = "#ccc";
        const button_file = document.getElementById('chat-file-upload');
        button_file.disabled = true;
        button_file.style.backgroundColor = "#ccc";
        if(role !== "Student") {
            const button_viewed = document.getElementById('chat-message-view');
            button_viewed.disabled = true;
            button_viewed.style.backgroundColor = "#ccc";
        }
    }
    else{
        const button = document.getElementById('chat-message-submit');
        button.disabled = false;
        button.style.backgroundColor = "#007bff";
        const button_file = document.getElementById('chat-file-upload');
        button_file.disabled = false;
        button_file.style.backgroundColor = "#007bff";
        if(role !== "Student") {
            const button_viewed = document.getElementById('chat-message-view');
            button_viewed.disabled = false;
            button_viewed.style.backgroundColor = "#139313";
        }
    }
});

onSnapshot(q, (querySnapshot) => {
    const messages = [];
    querySnapshot.forEach((doc) => {
        messages.push(doc.data());
    });
    // Обновление интерфейса только если это текущий чат
    if (currentChatId === querySnapshot.query._query.path.segments[1]) {
        updateChatUI(messages);
    }});

// Modify onSnapshot for chats to update the chat list without changing the selected chat
onSnapshot(q2, (chatsRef) => {
    if (role !== "Student") {
        const chats = [];
        chatsRef.forEach((doc) => {
            chats.push(doc.data());
        });
        const list = document.querySelector('.chat-list');
        list.innerHTML = '';
        chats.forEach((chat) => {
            const messageElement = document.createElement('li');

            if (chat.chat_id === currentChatId) {
                messageElement.classList.add('selected');
            }

            messageElement.setAttribute('onclick', "selectChat('" + chat.chat_id + "')")
            messageElement.textContent = chat.chatName;

            list.appendChild(messageElement);
        });
    }});


let unsubscribeChatMessages = null;  // Global variable to store the unsubscribe function for chat messages


document.addEventListener('click', function(event) {
    // Check if the clicked element matches the selector '.li-select'
    if (event.target && event.target.classList.contains('li-select')) {
        selectChat(event.target.id);
    }
});
async function selectChat(task) {
    if (role === "Student") {
        currentChatId = `${userId}_task${task}_${tour}_tour_${year}`;
    } else {
        currentChatId = task;
    }
    // Unsubscribe from any previous chat's message updates
    if (unsubscribeChatMessages) {
        unsubscribeChatMessages();
    }

    // Проверяем, существует ли чат в Firestore
    const chatRef = doc(db, "chats", currentChatId);
    const chatDoc = await getDoc(chatRef);
    if (!chatDoc.exists()) {
        await setDoc(chatRef, {
            task_name: task,
            chat_id: currentChatId,
            userId: userId,
            chatName: username + " " + user_class + " клас " + tasks[user_class][task],
            class: user_class,
            activity: serverTimestamp(),
            chat_state: "sent",
            tour: tour,
            year: year,
            chat_started: false
        });
    }
    if (role !== "Student") {
        // Обновляем поле viewed, если чат открыт админом
        const chatState = chatDoc.data().chat_state;

        // Update to "viewed" only if the current state is "sent"
        if (role !== "Student" && chatState === "sent") {
            await updateDoc(chatRef, {
                chat_state: "viewed"
            });
            updateChatBorderColor('viewed'); // Update the border color for "viewed"
        }
    }

    const button = document.getElementById('chat-message-submit');
    button.disabled = false;
    button.style.backgroundColor = "#007bff";

    const button_file = document.getElementById('chat-file-upload');
    button_file.disabled = false;
    button_file.style.backgroundColor = "#007bff";

    if(role !== "Student") {
        const button_viewed = document.getElementById('chat-message-view');
        button_viewed.disabled = false;
        button_viewed.style.backgroundColor = "#139313";
        const button_viewed_icon = document.querySelector('#chat-message-view i');
        button_viewed_icon.classList.add('fa-solid');
        if(chatDoc.data().chat_state === "answered") {
            button_viewed_icon.classList.remove('fa-remove');
            button_viewed_icon.classList.add('fa-check');
        }
        else{
            button_viewed_icon.classList.add('fa-remove');
            button_viewed_icon.classList.remove('fa-check');
        }

    }

    // Загружаем сообщения для выбранного чата
    const chatMessagesRef = collection(db, "messages");
    const q = query(chatMessagesRef, where("chat_id", "==", currentChatId), orderBy("timestamp"));

    // Set up a new onSnapshot listener and store the unsubscribe function
    unsubscribeChatMessages = onSnapshot(q, async (querySnapshot) => {
        if (querySnapshot.empty) {
            updateChatUI([]);
            return;
        }

        const messages = [];
        querySnapshot.forEach((doc) => {
            messages.push(doc.data());
        });
        // Обновляем интерфейс только если это текущий чат
        if (currentChatId === messages[0].chat_id) {
            updateChatUI(messages);

            const chatRef = doc(db, "chats", currentChatId);
            const chatDoc = await getDoc(chatRef);
            const chatState = chatDoc.data().chat_state;
            // Check if the last message was sent by a student
            const lastMessage = messages[messages.length - 1];

            if ((role !== "Student") && (lastMessage.sender_id !== userId) && (chatState === "sent")) {
                // If the role is Admin and the new message is from a student, mark the chat as viewed
                await updateDoc(chatRef, {
                    chat_state: "viewed"
                });
                const button_viewed_icon = document.querySelector('#chat-message-view i');
                button_viewed_icon.classList.add('fa-remove');
                button_viewed_icon.classList.remove('fa-check');
            }
        }
    });

    // Обновляем интерфейс для выбора чата
    document.querySelectorAll('.chat-list li').forEach(item => {
        item.classList.remove('selected');
    });
    if(role === "Student") {
        document.querySelectorAll(`.li-select`)[parseInt(task) - 1].classList.add('selected');
    }
    else {
        document.getElementById(task).classList.add('selected');
    }
}
async function change_status() {
    const chatRef = doc(db, "chats", currentChatId); // Получаем ссылку на документ чата
    await updateDoc(chatRef, {
        chat_state: "answered" // Если сообщение отправляет студент, флаг viewed становится false
    });
    updateChatBorderColor('answered');
}
async function sendMessage(senderId, senderName, messageText) {
    const chatRef = doc(db, "chats", currentChatId); // Получаем ссылку на документ чата
    const chatDoc = await getDoc(chatRef);
    if (role === "Student") {
        await updateDoc(chatRef, {
            activity: serverTimestamp(),
            chat_state: "sent" // Если сообщение отправляет студент, флаг viewed становится false
        });
        if(chatDoc.data().chat_started === false){
            await updateDoc(chatRef, {
                chat_started: true,
            });
        }
    } else {
        await updateDoc(chatRef, {
            activity: serverTimestamp(),
            chat_state: "answered" // Если сообщение отправляет админ, статус чата меняется на "answered"
        });
    }

    await addDoc(collection(db, "messages"), {
        chat_id: currentChatId,
        sender_id: senderId,
        sender_name: senderName,
        user_role: role,
        message_text: messageText,
        timestamp: serverTimestamp()
    });

    // Update the chat's last activity timestamp
    await updateDoc(chatRef, {
        activity: serverTimestamp()
    });}

function updateChatUI(messages) {
    const chatLog = document.querySelector('#chat-log');

    // Clear the chat log
    chatLog.innerHTML = '';

    // Add each message to the chat log
    messages.forEach((message) => {

        if(message.message_text.trim() === ""){
            return;
        }

        const messageElement = document.createElement('div');
        const messageElementHigh = document.createElement('div');
        messageElementHigh.classList.add('message-high');
        const messageElementHighName = document.createElement('div');
        messageElementHighName.classList.add('message-name');

        const messageElementHighTime = document.createElement('div');
        messageElementHighTime.classList.add('timestamp');
        const messageElementText = document.createElement('div');



        if (message.user_role === "Student") {
            // The message is from the student (the current user)
            messageElement.classList.add('message-student');
        } else {
            // The message is from an admin
            messageElement.classList.add('message-admin');
        }

        if (message.type === "file") {
            // If the message is a file, display it as a downloadable link
            messageElement.innerHTML = `
                <div class="file-message">
                    <span>${message.sender_name} завантажив файл: </span>
                    <a href="${message.file_url}" download="${message.message_text}" target="_blank">
                        ${message.message_text}
                    </a>
                </div>
            `;
        } else {
            // Otherwise, it's a text message
            messageElementText.textContent = message.message_text;

            messageElementHighTime.textContent = formatTimestamp(message.timestamp.seconds, message.timestamp.nanoseconds);
            messageElementHighName.textContent = message.sender_name;
        }
        messageElement.appendChild(messageElementHigh);
        messageElement.appendChild(messageElementText);
        messageElementHigh.appendChild(messageElementHighName);
        messageElementHigh.appendChild(messageElementHighTime);
        chatLog.appendChild(messageElement);
    });

    // Scroll to the bottom of the chat log
    chatLog.scrollTop = chatLog.scrollHeight;}

async function setUpChats() {
    if (role !== "Student") {
        const chatsRef = collection(db, "chats");
        const queryChats = query(chatsRef, orderBy("activity", "desc"));

        onSnapshot(queryChats, (chatsSnapshot) => {
            const list = document.querySelector('.chat-list');
            list.innerHTML = '';  // Clear existing chat list

            chatsSnapshot.forEach((doc) => {
                const chat = doc.data();
                if(Number(chat.tour) !== tour){
                    return;
                }
                if(chat.year !== year){
                    return;
                }
                if(chat.chat_started === false){
                    return;
                }
                const chatElement = document.createElement('li');
                chatElement.classList.add('li-select');
                chatElement.setAttribute('id', chat.chat_id);
                chatElement.textContent = chat.chatName;

                // Apply the correct border color based on the chat state
                switch (chat.chat_state) {
                    case 'sent':
                        chatElement.classList.add('chat-sent');
                        break;
                    case 'viewed':
                        chatElement.classList.add('chat-viewed');
                        break;
                    case 'answered':
                        chatElement.classList.add('chat-answered');
                        break;
                }

                if (chat.chat_id === currentChatId) {
                    chatElement.classList.add('selected');
                }

                list.appendChild(chatElement);
            });
        });
    }}

function updateChatBorderColor(state) {
    const selectedItem = document.querySelector(`.chat-list .selected`);
    if (selectedItem) {
        selectedItem.classList.remove('chat-sent', 'chat-viewed', 'chat-answered');
        switch (state) {
            case 'sent':
                selectedItem.classList.add('chat-sent');
                break;
            case 'viewed':
                selectedItem.classList.add('chat-viewed');
                break;
            case 'answered':
                selectedItem.classList.add('chat-answered');
                break;
        }
    }
    const button_viewed_icon = document.querySelector('#chat-message-view i');
    if(state === 'answered') {
        button_viewed_icon.classList.remove('fa-remove');
        button_viewed_icon.classList.add('fa-check');
    }
    else{
        button_viewed_icon.classList.add('fa-remove');
        button_viewed_icon.classList.remove('fa-check');
    }
}

document.querySelector('#chat-message-submit').onclick = function(e) {
    if(currentChatId !== null){
        const messageInputDom = document.querySelector('#chat-message-input');
        const message = messageInputDom.value;
        sendMessage(userId, username, message);
        messageInputDom.value = '';
    }
    else{
        console.log("Виберіть чат");
    }};

document.querySelector('#chat-message-view').onclick = function(e) {
    if(currentChatId !== null){
        const view_button_icon = document.querySelector('#chat-message-view i');
        view_button_icon.classList.add('fa-solid','fa-check');
        view_button_icon.classList.remove('fa-remove');

        change_status();
    }
    else{
        console.log("Виберіть чат");
    }};

document.getElementById('chat-file-upload').onclick = function() {
    // Trigger the file input when the button is clicked
    document.getElementById('chat-file-input').click();};

document.getElementById('chat-file-input').onchange = async function(e) {
    if(currentChatId !== null){
        const file = e.target.files[0]; // Get the selected file
        if (file) {
            // Upload the file to Firebase Storage
            const fileRef = storageRef(storage, `chat_files/${currentChatId}/${file.name}`);
            await uploadBytes(fileRef, file);

            // Get the file's download URL
            const downloadURL = await getDownloadURL(fileRef);

            // Send a message with the file link
            await sendFileMessage(userId, username, file.name, downloadURL);

            // Reset the file input
            document.getElementById('chat-file-input').value = '';
        }
    }
    else{
        console.log("Виберіть чат");
    }};

async function sendFileMessage(senderId, senderName, fileName, fileURL) {


    const chatRef = doc(db, "chats", currentChatId); // Get reference to the chat
    const chatDoc = await getDoc(chatRef);
    if (role === "Student") {
        await updateDoc(chatRef, {
            activity: serverTimestamp(),
            chat_state: "sent" // Если сообщение отправляет студент, флаг viewed становится false
        });
        if(chatDoc.data().chat_started === false){
            await updateDoc(chatRef, {
                chat_started: true,
            });
        }
    } else {
        await updateDoc(chatRef, {
            activity: serverTimestamp(),
            chat_state: "answered" // Если сообщение отправляет админ, статус чата меняется на "answered"
        });
    }
    const messageData = {
        chat_id: currentChatId,
        sender_id: senderId,
        sender_name: senderName,
        message_text: fileName,
        file_url: fileURL, // Store the file URL
        type: "file",      // Indicate this message is a file
        user_role: role,
        timestamp: serverTimestamp()
    };

    // Add the file message to Firestore
    await addDoc(collection(db, "messages"), messageData);

    // Update the chat's last activity timestamp
    await updateDoc(chatRef, {
        activity: serverTimestamp()
    });}
function formatTimestamp(seconds, nanoseconds) {
    const timestampInMillis = (seconds * 1000) + (nanoseconds / 1000000);
    const date = new Date(timestampInMillis);
    const hours = String(date.getHours()).padStart(2, '0'); // Форматируем дату в нужный формат: HH:mm:ss dd:MM:YY
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const secondsStr = String(date.getSeconds()).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0'); // месяцы начинаются с 0
    const year = String(date.getFullYear()); // последние две цифры года

    return `${hours}:${minutes}:${secondsStr} ${day}.${month}.${year}`;
}
window.selectChat = selectChat;
