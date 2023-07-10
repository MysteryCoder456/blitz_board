const playerCardTemplate = document.querySelector("#player-card-template");
const statusHeader = document.querySelector("#status-header");
const playerList = document.querySelector("#player-list");
const startBtn = document.querySelector("#start-btn");
const typingArea = document.querySelector("#typing-area");
const cursor = document.querySelector("#cursor");

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

    if (playerData.player_id === myID) {
        const youSpan = document.createElement("SPAN");
        youSpan.innerText = " (You)";
        youSpan.className = "text-slate-500";
        username.appendChild(youSpan);
    }

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
        ev.key.startsWith("Page") ||
        ev.key === "Escape"
    );
}

function updateCursorPosition() {
    const charElem = typingArea.querySelector(`#char-${currentCharIndex}`);
    const charBB = charElem.getBoundingClientRect();

    cursor.style.left = `${charElem.offsetLeft}px`;
    cursor.style.top = `${charElem.offsetTop}px`;
    cursor.style.width = `${charBB.width}px`;
    cursor.style.height = `${charBB.height}px`;
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

    // Display cursor
    cursor.style.display = "block";
    updateCursorPosition();

    // Set color of first character under cursor
    const charElem = typingArea.querySelector(`#char-${currentCharIndex}`);
    charElem.style.color = "rgb(var(--selective-yellow))";
});

socket.on("test progress", ({ player_id, progress }) => {
    const cardProgress = playerList.querySelector(
        `#player-card-${player_id} progress`,
    );
    cardProgress.value = progress;
});

socket.on("test complete", ({ player_id, speed, accuracy }) => {
    const finishedSpan = document.createElement("SPAN");
    finishedSpan.innerHTML = "<b>FINISHED!</b>";
    finishedSpan.style.color = "rgb(var(--spring-green))";

    const infoSpan = document.createElement("SPAN");
    infoSpan.innerText = ` (${speed} WPM, ${accuracy}% Accuracy)`;
    infoSpan.className = "text-slate-500";

    const cardProgress = playerList.querySelector(
        `#player-card-${player_id} progress`,
    );
    cardProgress.parentNode.appendChild(finishedSpan);
    cardProgress.parentNode.appendChild(infoSpan);
    cardProgress.remove(cardProgress);
});

window.onresize = updateCursorPosition;

document.onkeydown = (ev) => {
    if (!gameStarted) {
        return;
    }

    // Check if test is complete
    if (currentCharIndex >= testSentenceLength - 1) {
        if (!finishHasRun) {
            cursor.style.display = "none";
            statusHeader.innerText = "Game Finished!";
            socket.emit("test complete", typedSentence);
        }

        finishHasRun = true;
    }

    // Check only alphanumeric keys
    if (isIllegalKeyEvent(ev)) {
        return;
    }

    // FIXME: highlight error if user makes a mistake at space character

    if (ev.code === "Backspace") {
        const charElem = typingArea.querySelector(`#char-${currentCharIndex}`);
        charElem.style.color = "#64748B";

        currentCharIndex--;
        typedSentence = typedSentence.slice(0, currentCharIndex);

        const newCharElem = typingArea.querySelector(
            `#char-${currentCharIndex}`,
        );
        newCharElem.style.color = "rgb(var(--selective-yellow))";
    } else {
        const charElem = typingArea.querySelector(`#char-${currentCharIndex}`);

        if (charElem.innerText === ev.key) {
            charElem.style.color = "var(--ghost-white)";
        } else {
            charElem.style.color = "rgb(var(--red-munsell))";
        }

        currentCharIndex++;
        typedSentence += ev.key;

        const newCharElem = typingArea.querySelector(
            `#char-${currentCharIndex}`,
        );
        newCharElem.style.color = "rgb(var(--selective-yellow))";
    }

    updateCursorPosition();

    // Send current progress to server
    const progress = currentCharIndex / testSentenceLength;
    socket.emit("test progress", progress);
};
