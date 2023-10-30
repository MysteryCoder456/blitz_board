const msgBox = document.querySelector("#msg-box");
const sendInput = document.querySelector("#send-input");
const sendBtn = document.querySelector("#send-btn");

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
