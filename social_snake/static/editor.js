const BLOCK_SIZE = 15;

function setup() {
    createCanvas(1920, 1080);
    select("canvas").removeAttribute("style");
}

function draw() {
    background(0);

    textSize(52);
    fill(255);
    text("Hello world", 960, 540);
}
