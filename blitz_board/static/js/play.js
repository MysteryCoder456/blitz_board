const playerCardTemplate = document.querySelector("#player-card-template");
const playerList = document.querySelector("#player-list");

let proto = "wss:";

if (document.location.protocol === "http:") {
    proto = "ws:";
}

const ws = new WebSocket(`${proto}//${document.location.host}/game/ws`);

let receivedPlayers = false;

function createPlayerCard(playerData) {
    const newCard = playerCardTemplate.content.cloneNode(true);

    const div = newCard.querySelector("div");
    div.id = `player-card-${playerData.player_id}`;

    const username = div.querySelector(".player-name");
    username.innerText = playerData.username;

    // TODO: Set profile picture too

    return newCard;
}

ws.onopen = (_ev) => {
    const initial_data = {
        player_id: myID,
        game_id: gameID,
    };
    ws.send(JSON.stringify(initial_data));
};

ws.onmessage = (ev) => {
    if (!receivedPlayers) {
        const parsedMsg = JSON.parse(ev.data);
        console.log(parsedMsg);

        // Creating player cards for each player
        parsedMsg.forEach((playerData) => {
            const card = createPlayerCard(playerData);
            playerList.appendChild(card);
        });

        receivedPlayers = true;
    }
};
