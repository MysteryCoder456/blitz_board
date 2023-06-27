const playerCardTemplate = document.querySelector("#player-card-template");
const playerList = document.querySelector("#player-list");

let proto = "wss:";

if (document.location.protocol === "http:") {
    proto = "ws:";
}

const ws = new WebSocket(`${proto}//${document.location.host}/game/ws`);

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
    const parsedMsg = JSON.parse(ev.data);

    switch (parsedMsg.msg_type) {
        case "player_list": {
            // Creating player cards for each player
            parsedMsg.data.forEach((playerData) => {
                const card = createPlayerCard(playerData);
                playerList.appendChild(card);
            });
            break;
        }

        case "new_player": {
            const card = createPlayerCard(parsedMsg.data);
            playerList.appendChild(card);
            break;
        }

        case "player_left": {
            const card = playerList.querySelector(
                `#player-card-${parsedMsg.data}`,
            );
            card.remove();
            break;
        }

        default:
            break;
    }
};
