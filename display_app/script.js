let socket;
let test_text = null;
let play;
let fizzle;
let murmur;
let started = false;
let playIndex = 1;

const TIME_FACTOR = 100;

function preload() {
  fizzle = loadSound("assets/fizzle.mp3");
  murmur = loadSound("assets/murmur.mp3");
}

function keyPressed() {
  if (started) return;
  fullscreen(true);
  userStartAudio();
  started = true;
  const msg = String(playIndex).padStart(4, "0");
  sendOsc("/repeat", msg);
}

function setup() {
  createCanvas(windowWidth, windowHeight);
  play = new Play();
  setupOsc(6000, 5000);
  fill(0);
  noStroke();
  textAlign(CENTER);
  rectMode(CENTER);
  ellipseMode(CENTER);
  textFont("fira-code, monospace");
  frameRate(24);
  murmur.loop();
  murmur.setVolume(0.6);
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

function draw() {
  play.draw();
}

function receiveOsc(address, value) {
  console.log("received OSC: " + address + ", " + value);
  const path = `json/${value}.json`;
  play.loadPlay(path);
}

function sendOsc(address, value) {
  console.log("Sending OSC Message");
  socket.emit("message", [address].concat(value));
}

function setupOsc(oscPortIn, oscPortOut) {
  socket = io.connect("http://127.0.0.1:8081", {
    port: 8081,
    rememberTransport: false,
  });
  socket.on("connect", function () {
    socket.emit("config", {
      server: { port: oscPortIn, host: "127.0.0.1" },
      client: { port: oscPortOut, host: "127.0.0.1" },
    });
  });
  socket.on("message", function (msg) {
    if (msg[0] == "#bundle") {
      for (var i = 2; i < msg.length; i++) {
        receiveOsc(msg[i][0], msg[i].splice(1));
      }
    } else {
      receiveOsc(msg[0], msg.splice(1));
    }
  });
}

class Play {
  constructor() {
    this.running = false;
    this.play = null;
    this.idx = 0;
    this.length = 0;
    this.w1 = null;
    this.w2 = null;
    this.m = null;
  }
  loadPlay(path) {
    loadJSON(path, (response) => {
      murmur.setVolume(0);
      fizzle.play();
      console.log(response);
      this.play = response;
      this.length = this.play.cues.length;
      this.idx = -1;
      this.running = true;
      this.advance();
    });
  }
  draw() {
    if (!this.running) {
      background(0);
      fill(200, 80);
      textSize(width / 20);
      text("[REPEAT PLAY]", width / 2, height / 2);
      return;
    }
    background(0);
    fill(200, 80);
    textSize(width / 40);
    text(this.play.title, width / 2, (width / 40) * 2);
    const verticalCenter = height / 2;
    const horizontalIncrement = width / 4;
    if (this.w1) {
      push();
      translate(horizontalIncrement, verticalCenter);
      this.w1.draw(horizontalIncrement, horizontalIncrement);
      const w1Alpha = this.w1.active ? 80 : 40;
      fill(200, w1Alpha);
      textSize(width / 60);
      text("[Woman 1]", 0, height / 3);
      pop();
    }
    if (this.m) {
      push();
      translate(horizontalIncrement * 2, verticalCenter);
      this.m.draw(horizontalIncrement, horizontalIncrement);
      const mAlpha = this.m.active ? 80 : 40;
      fill(200, mAlpha);
      textSize(width / 60);
      text("[Man]", 0, height / 3);
      pop();
    }
    if (this.w2) {
      push();
      translate(horizontalIncrement * 3, verticalCenter);
      this.w2.draw(horizontalIncrement, horizontalIncrement);
      const w2Alpha = this.w2.active ? 80 : 40;
      fill(200, w2Alpha);
      textSize(width / 60);
      text("[Woman 2]", 0, height / 3);
      pop();
    }
  }
  advance() {
    if (this.idx == this.length) {
      this.running = false;
      fizzle.play();
      murmur.setVolume(0.8, 6);
      console.log("finished play");
      playIndex++;
      const msg = String(playIndex).padStart(4, "0");
      sendOsc("/repeat", msg);
      return;
    }
    if (this.idx == -1) {
      setTimeout(() => {
        this.idx++;
        murmur.setVolume(0.075, 1);
        this.advance();
      }, TIME_FACTOR * 40);
      return;
    }
    const nextLine = this.play.cues[this.idx];
    switch (nextLine.speaker) {
      case "W1":
        delete this.w1;
        this.w1 = new Line(nextLine.line);
        break;
      case "W2":
        delete this.w2;
        this.w2 = new Line(nextLine.line);
        break;
      case "M":
        delete this.m;
        this.m = new Line(nextLine.line);
        break;
      default:
        console.error(`Error reading line at idx ${this.idx} - ${nextLine}`);
    }
    const waitTime = nextLine.line.length * TIME_FACTOR;
    this.idx++;
    setTimeout(() => {
      if (this.m) {
        this.m.deactivate();
      }
      if (this.w1) {
        this.w1.deactivate();
      }
      if (this.w2) {
        this.w2.deactivate();
      }
      setTimeout(() => {
        this.advance();
      }, TIME_FACTOR * 5);
    }, waitTime);
  }
}

class Line {
  constructor(line) {
    this.line = line;
    this.age = 50;
    this.active = true;
  }
  draw(w = 200, h = 200) {
    push();
    textSize(width / 100);
    if (this.active) {
      const fillWobble = random(-5, 5);
      fill(180 + fillWobble);
      const xWobble = random(-0.5, 0.5);
      const yWobble = random(-0.5, 0.5);
      const strokeWobble = random(0, 3);
      strokeWeight(strokeWobble);
      stroke(180 + fillWobble, 40);
      ellipse(0 + xWobble, 0 + yWobble, w, h);
      fill(20);
    } else {
      fill(int(this.age));
      if (this.age > 0) {
        this.age -= 0.25;
      } else {
        this.age = 0;
      }
    }
    text(this.line, 0, h / 4, w * 0.8, h);
    pop();
  }
  deactivate() {
    this.active = false;
  }
}
