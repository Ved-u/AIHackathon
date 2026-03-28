const net = require("net");
const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

app.post("/query", (req, res) => {
  const client = new net.Socket();
  let data = "";
  let responded = false;

  const safeSend = (fn) => {
    if (!responded) {
      responded = true;
      fn();
    }
  };

  client.connect(50001, "127.0.0.1", () => {
    client.write(JSON.stringify({ message: req.body.query }));
  });

  client.on("data", chunk => {
    data += chunk.toString();
    client.end();   // 🔥 critical
  });

  client.on("end", () => {
    safeSend(() => {
      try {
        const parsed = JSON.parse(data);
        res.json(parsed);
      } catch {
        res.status(500).send("Invalid JSON from Python");
      }
    });
  });

  client.on("error", err => {
    safeSend(() => res.status(500).send(err.message));
  });

  client.setTimeout(100000);
  client.on("timeout", () => {
    client.destroy();
    safeSend(() => res.status(504).send("Python timeout"));
  });
});

app.listen(8000, () => console.log("Server running on 8000"));