const msgTemplate = document.querySelector("#msg-template");
const msgBox = document.querySelector("#msg-box");
const sendInput = document.querySelector("#send-input");
const sendBtn = document.querySelector("#send-btn");
const alertAudio = document.querySelector("#alert-sfx");

const socket = io("/chat", {
    auth: {
        channel_id: channelId,
    },
});

function sendMessage() {
    const msgContent = sendInput.value.trim();

    if (msgContent.length === 0) {
        return;
    }

    socket.emit("send message", msgContent);
    sendInput.value = "";
}

msgBox.scrollTop = msgBox.scrollHeight + 50;
sendBtn.onclick = () => sendMessage();

document.onkeydown = (ev) => {
    if (ev.key === "Enter") {
        sendMessage();
    }
}

socket.on("new message", (msg) => {
    // Create new message element
    const msgEl = msgTemplate.content.cloneNode(true);

    const div = msgEl.querySelector(".message");
    div.id = `msg-${msg.id}`;

    if (msg.author_id === myId) {
        div.dir = "rtl"
    }

    // Update element contents
    msgEl.querySelector(".msg-author").innerText = msg.author;
    msgEl.querySelector(".msg-timestamp").innerText = msg.timestamp;
    msgEl.querySelector(".msg-content").innerText = msg.content;

    if (msg.author_avatar) {
        msgEl.querySelector("img").src = msg.author_avatar;
    }

    // Add element to DOM
    msgBox.appendChild(msgEl);
    msgBox.scrollTop = msgBox.scrollHeight + 50;

    // Play SFX
    if (msg.author_id !== myId) {
        alertAudio.play();
    }
});
