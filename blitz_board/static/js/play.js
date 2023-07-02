const playerCardTemplate = document.querySelector("#player-card-template");
const playerList = document.querySelector("#player-list");
const typingArea = document.querySelector("#typing-area");

const socket = io("/game", {
    auth: {
        player_id: myID,
        game_id: gameID,
    },
});

let currentCharIndex = 0;
let typedSentence = "";
let finishHasRun = false;

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

document.onkeydown = (ev) => {
    // Check if test is complete
    if (currentCharIndex >= testSentence.length) {
        if (!finishHasRun) {
            emit("test complete", typedSentence);
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
};
