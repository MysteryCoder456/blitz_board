const BLOCK_SIZE = 40;
const GRID_WEIGHT = 2.5;

let blocks = {};

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
            blocks = data.blocks;
            loop();
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
