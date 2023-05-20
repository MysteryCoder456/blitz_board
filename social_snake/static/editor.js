const BLOCK_SIZE = 40;

function setup() {
    createCanvas(1280, 720);
    select("canvas").removeAttribute("style");
    cursor(CROSS);
}

function draw() {
    background(0);
    strokeWeight(2.5);

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
}
