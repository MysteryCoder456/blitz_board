const playerList = document.querySelector("#player-list"):
const ws = new WebSocket("/game/ws");

let receivedPlayers = false;

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

        // TODO: add player avatars from received player list

        receivedPlayers = true;
    }
}
