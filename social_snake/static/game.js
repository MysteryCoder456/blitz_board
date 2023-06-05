const BLOCK_SIZE = 40;
const GRID_WEIGHT = 2.5;

let blocks = {};

let head = [-1, -1];
let tail = [];
let dir = [1, 0];

function setup() {
    let cnv = createCanvas(1280, 720);
    cnv.removeAttribute("style");
    document
        .querySelector("canvas")
        .addEventListener("contextmenu", (event) => event.preventDefault());

    cursor(CROSS);
    noLoop();

    fetch("/api/mazedata/" + maze_id.toString())
        .then((res) => res.json())
        .then((data) => {
            head = data.spawn_point;
            blocks = data.blocks;
            loop();
        });
}

function keyPressed() {
    if (keyCode == 87 && dir[1] != 1) {
        dir = [0, -1];
    } else if (keyCode == 83 && dir[1] != -1) {
        dir = [0, 1];
    } else if (keyCode == 68 && dir[0] != -1) {
        dir = [1, 0];
    } else if (keyCode == 65 && dir[0] != 1) {
        dir = [-1, 0];
    }
}

function draw() {
    if (frameCount % (getTargetFrameRate() * 0.25) == 0) {
        head[0] += dir[0];
        head[1] += dir[1];
    }

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

    // Draw Walls
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

    // Draw Player
    fill(46, 101, 210);
    rect(
        head[0] * BLOCK_SIZE + GRID_WEIGHT / 2,
        head[1] * BLOCK_SIZE + GRID_WEIGHT / 2,
        BLOCK_SIZE - GRID_WEIGHT,
        BLOCK_SIZE - GRID_WEIGHT
    );
}
