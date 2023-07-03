const playerCardTemplate = document.querySelector("#player-card-template");
const statusHeader = document.querySelector("#status-header");
const playerList = document.querySelector("#player-list");
const typingArea = document.querySelector("#typing-area");
const startBtn = document.querySelector("#start-btn");

const socket = io("/game", {
    auth: {
        player_id: myID,
        game_id: gameID,
    },
});

let gameStarted = false;
let testSentenceLength = 0;

let currentCharIndex = 0;
let typedSentence = "";
let finishHasRun = false;

if (myID === hostID) {
    startBtn.onclick = () => socket.emit("test start");
}

function createPlayerCard(playerData) {
    const newCard = playerCardTemplate.content.cloneNode(true);

    const div = newCard.querySelector("div");
    div.id = `player-card-${playerData.player_id}`;

    const username = div.querySelector(".player-name");
    username.innerText = playerData.username;

    // TODO: Set profile picture too

    return newCard;
}

function isIllegalKeyEvent(ev) {
    return (
        ev.metaKey ||
        ev.altKey ||
        ev.ctrlKey ||
        ev.shiftKey ||
        ev.repeat ||
        ev.key.startsWith("Arrow") ||
        ev.key.startsWith("Page")
    );
}

socket.on("player list", (players) => {
    // Creating player cards for each player
    players.forEach((playerData) => {
        const card = createPlayerCard(playerData);
        playerList.appendChild(card);
    });
});

socket.on("player join", (player) => {
    // Create player card for new player
    const card = createPlayerCard(player);
    playerList.appendChild(card);
});

socket.on("player leave", (playerId) => {
    // Remove corresponding player card
    const card = playerList.querySelector(`#player-card-${playerId}`);
    card.remove();
});

socket.on("test start", (testSentence) => {
    statusHeader.innerText = "Game Started!";

    if (myID === hostID) {
        startBtn.remove();
    }

    // Create the typing area elements
    for (let i = 0; i < testSentence.length; i++) {
        const newSpan = document.createElement("span");
        newSpan.id = `char-${i}`;
        newSpan.innerText = testSentence[i];
        typingArea.appendChild(newSpan);
    }

    gameStarted = true;
    testSentenceLength = testSentence.length;
});

socket.on("test progress", ({ player_id, progress }) => {
    const cardProgress = playerList.querySelector(
        `#player-card-${player_id} progress`,
    );
    cardProgress.value = progress;
});

document.onkeydown = (ev) => {
    if (!gameStarted) {
        return;
    }

    // Check if test is complete
    if (currentCharIndex >= testSentenceLength) {
        if (!finishHasRun) {
            socket.emit("test complete", typedSentence);
        }

        finishHasRun = true;
        return;
    }

    // Check only alphanumeric keys
    if (isIllegalKeyEvent(ev)) {
        return;
    }

    // FIXME: highlight error if user makes a mistake at space character

    if (ev.code === "Backspace") {
        currentCharIndex--;
        typedSentence = typedSentence.slice(0, currentCharIndex);

        const charElem = typingArea.querySelector(`#char-${currentCharIndex}`);
        charElem.className = "";
    } else {
        const charElem = typingArea.querySelector(`#char-${currentCharIndex}`);

        if (charElem.innerText === ev.key) {
            charElem.className = "text-white";
        } else {
            charElem.className = "text-red-500";
        }

        currentCharIndex++;
        typedSentence += ev.key;
    }

    // Send current progress to server
    const progress = currentCharIndex / testSentenceLength;
    socket.emit("test progress", progress);
};
