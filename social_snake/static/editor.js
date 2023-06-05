const BLOCK_SIZE = 40;
const GRID_WEIGHT = 2.5;

let spawn_point = null;
let blocks = {};
let save_btn;
let save_alert;

function setup() {
    let cnv = createCanvas(1280, 720);
    cnv.removeAttribute("style");
    document
        .querySelector("canvas")
        .addEventListener("contextmenu", (event) => event.preventDefault());

    save_btn = select("#save-btn");
    save_btn.mouseClicked(save_maze);

    save_alert = select("#save-alert");
    save_alert.style("display", "none");

    cursor(CROSS);
    noLoop();

    fetch("/api/mazedata/" + maze_id.toString())
        .then((res) => res.json())
        .then((data) => {
            spawn_point = data.spawn_point;
            blocks = data.blocks;
            loop();
        });
}

function save_maze() {
    save_btn.addClass("btn-disabled");

    let new_data = new URLSearchParams();
    new_data.append(
        "maze_data",
        JSON.stringify({
            spawn_point: spawn_point,
            blocks: blocks,
        })
    );
    new_data.append("csrf_token", csrf_token);
    new_data.append("submit", "Save");

    fetch("/editor/" + maze_id, {
        method: "POST",
        body: new_data,
    })
        .then((res) => res.json())
        .then((res) => {
            save_btn.removeClass("btn-disabled");

            if (res) {
                save_alert.style("display", "block");
            }
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

            if (
                spawn_point != null &&
                spawn_point[0] == grid_x &&
                spawn_point[1] == grid_y
            ) {
                spawn_point = null;
            }
        } else if (mouseButton === RIGHT) {
            delete blocks[coord_str];
        } else if (mouseButton === CENTER) {
            spawn_point = [grid_x, grid_y];
            delete blocks[coord_str];
        }
    }

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

    if (spawn_point != null) {
        fill(0, 255, 0);
        rect(
            spawn_point[0] * BLOCK_SIZE + GRID_WEIGHT / 2,
            spawn_point[1] * BLOCK_SIZE + GRID_WEIGHT / 2,
            BLOCK_SIZE - GRID_WEIGHT,
            BLOCK_SIZE - GRID_WEIGHT
        );
    }
}
