const BLOCK_SIZE = 40;
const GRID_WEIGHT = 2.5;

let blocks = {};

function setup() {
    let cnv = createCanvas(1280, 720);
    cnv.removeAttribute("style");
    document
        .querySelector("canvas")
        .addEventListener("contextmenu", (event) => event.preventDefault());

    select("#save-btn").mouseClicked(save_maze);

    cursor(CROSS);
    noLoop();

    fetch("/api/mazedata/" + maze_id.toString())
        .then((res) => res.json())
        .then((data) => {
            blocks = data.blocks;
            loop();
        });
}

function save_maze() {
    // TODO: Send post request to server with new blocks data
    let new_data = new URLSearchParams();
    new_data.append(
        "maze_data",
        JSON.stringify({
            blocks: blocks,
        })
    );
    new_data.append("csrf_token", csrf_token);
    new_data.append("submit", "Save");

    fetch("/editor/" + maze_id, {
        method: "POST",
        body: new_data,
    });
}

function draw() {
    background(0);
    strokeWeight(GRID_WEIGHT);

    // Horizontal Gridlines
    for (let y = 1; y < height / BLOCK_SIZE; y++) {
        if (y % 2 == 0) {
            stroke(200);
        } else {
            stroke(100);
        }

        line(0, y * BLOCK_SIZE, width, y * BLOCK_SIZE);
    }

    // Vertical Gridlines
    for (let x = 1; x < width / BLOCK_SIZE; x++) {
        if (x % 2 == 0) {
            stroke(200);
        } else {
            stroke(100);
        }

        line(x * BLOCK_SIZE, 0, x * BLOCK_SIZE, height);
    }

    noStroke();

    if (mouseIsPressed) {
        let grid_x = Math.floor(mouseX / BLOCK_SIZE);
        let grid_y = Math.floor(mouseY / BLOCK_SIZE);
        let coord_str = grid_x.toString() + "," + grid_y.toString();

        if (mouseButton === LEFT) {
            blocks[coord_str] = "wall";
        } else if (mouseButton === RIGHT) {
            delete blocks[coord_str];
        }
    }

    for (let b in blocks) {
        let [grid_x, grid_y] = b.split(",").map((a) => int(a));
        let type = blocks[b];

        if (type == "wall") {
            fill(255);
        } else if (type == "point") {
            fill(0, 255, 0);
        }

        rect(
            grid_x * BLOCK_SIZE + GRID_WEIGHT / 2,
            grid_y * BLOCK_SIZE + GRID_WEIGHT / 2,
            BLOCK_SIZE - GRID_WEIGHT,
            BLOCK_SIZE - GRID_WEIGHT
        );
    }
}
