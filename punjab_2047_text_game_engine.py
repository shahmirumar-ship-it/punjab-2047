<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Punjab 2047 - HOI4 Grand Strategy Engine</title>
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <style>
    body { font-family: sans-serif; padding: 20px; background: #0b1220; color: white; }
    button { margin: 5px; padding: 10px; cursor: pointer; }
    .box { margin-top: 10px; padding: 10px; border: 1px solid #334155; border-radius: 8px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .tile { padding: 10px; border: 1px solid #334155; border-radius: 8px; text-align: center; }
  </style>
</head>
<body>
<div id="root"></div>

<script type="text/babel">
// ===================== CORE WORLD =====================
const initialWorld = {
  year: 2047,
  month: 1,
  turn: 1,
  log: "",

  global_tension: 60,
  world_war: false,

  player: {
    legitimacy: 55,
    military: 40,
    economy: 40,
    stability: 45,
    intel: 30,
    diplomacy: 35,
    manpower: 120,
    political_power: 50
  },

  // ================= FACTIONS =================
  factions: {
    Pakistanis: { power: 40, manpower: 80, aggression: 50, ideology: "nationalist" },
    Rajis: { power: 35, manpower: 70, aggression: 60, ideology: "radical" },
    Punjabis: { power: 45, manpower: 90, aggression: 40, ideology: "regionalist" },
    Gujjarsitanis: { power: 30, manpower: 60, aggression: 55, ideology: "tribal" }
  },

  // ================= MAP =================
  map: {
    Lahore: "neutral",
    Multan: "neutral",
    Islamabad: "Pakistanis",
    Faisalabad: "Punjabis",
    Gujrat: "Gujjarsitanis",
    Rawalpindi: "Rajis"
  },

  divisions: {
    player: 3,
    Pakistanis: 2,
    Rajis: 2,
    Punjabis: 2,
    Gujjarsitanis: 2
  },

  // ================= INDUSTRY =================
  factories: 3,
  fuel: 50,

  // ================= TECHNOLOGY =================
  tech: {
    infantry: 1,
    economy: 1,
    intelligence: 1
  },

  // ================= FOCUS TREE =================
  focus: "none",
  focuses_completed: []
};

// ===================== UTIL =====================
function clamp(v) {
  v = Number(v);
  return Math.max(0, Math.min(100, v));
}

function rand(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ===================== COMBAT SYSTEM =====================
function resolveBattle(attacker, defender, tech) {
  const atk = attacker.power * rand(5, 12) * tech.infantry;
  const def = defender.power * rand(5, 12);

  if (atk > def * 1.2) return "attacker";
  if (def > atk * 1.2) return "defender";
  return "stalemate";
}

// ===================== AI =====================
function aiTick(w) {
  Object.keys(w.factions).forEach(f => {
    w.factions[f].power = clamp(w.factions[f].power + rand(-2, 3));

    if (Math.random() > 0.7) {
      const tiles = Object.keys(w.map);
      const t = tiles[Math.floor(Math.random() * tiles.length)];
      w.map[t] = f;
      w.log = `${f} expanded into ${t}`;
    }
  });

  return w;
}

// ===================== FOCUS TREE =====================
function applyFocus(w, focus) {
  if (w.focuses_completed.includes(focus)) return w;

  w.focus = focus;

  switch(focus) {
    case "military_industrial":
      w.player.military += 10;
      w.factories += 1;
      break;
    case "economic_boom":
      w.player.economy += 10;
      w.fuel += 20;
      break;
    case "internal_stability":
      w.player.stability += 15;
      break;
    case "spy_network":
      w.player.intel += 15;
      break;
    case "diplomatic_push":
      w.player.diplomacy += 15;
      break;
  }

  w.focuses_completed.push(focus);
  return w;
}

// ===================== GAME ENGINE =====================
function App() {
  const [world, setWorld] = React.useState(initialWorld);
  const [gameOver, setGameOver] = React.useState("");

  function recruit() {
    const w = { ...world };
    w.player.manpower -= 10;
    w.divisions.player += 1;
    w.log = "Division recruited";
    setWorld(w);
  }

  function attack(tile) {
    const w = { ...world };
    const owner = w.map[tile];
    if (owner === "player") return;

    const attacker = { power: w.divisions.player };
    const defender = { power: w.divisions[owner] || 1 };

    const result = resolveBattle(attacker, defender, w.tech);

    if (result === "attacker") {
      w.map[tile] = "player";
      w.divisions.player += 1;
      w.log = `Captured ${tile}`;
    } else if (result === "defender") {
      w.divisions.player -= 1;
      w.log = `Lost at ${tile}`;
    } else {
      w.log = `Stalemate at ${tile}`;
    }

    setWorld(w);
  }

  function endTurn(w) {
    w.turn++;
    w.month++;
    if (w.month > 12) { w.month = 1; w.year++; }

    w.global_tension += rand(-2, 4);
    w.player.stability = clamp(w.player.stability + rand(-2, 2));
    w.player.economy = clamp(w.player.economy + rand(-2, 2));

    return w;
  }

  function step(action) {
    let w = { ...world };

    if (action === 1) w.player.military += 5;
    if (action === 2) w.player.economy += 5;
    if (action === 3) w.player.stability += 5;
    if (action === 4) w.player.intel += 5;
    if (action === 5) w.player.diplomacy += 5;

    w = aiTick(w);
    w = endTurn(w);

    setWorld({ ...w });

    const allControlled = Object.values(w.map).every(v => v === "player");
    if (w.player.stability <= 0 || w.player.military <= 0 || allControlled) {
      setGameOver("💀 Game Over / World Conquered");
    }
  }

  const p = world.player;

  return (
    <div>
      <h1>🌍 Punjab 2047 - HOI4 GRAND STRATEGY</h1>

      <div className="box">
        <h2>Nation Overview</h2>
        <p>Legitimacy: {p.legitimacy}</p>
        <p>Military: {p.military}</p>
        <p>Economy: {p.economy}</p>
        <p>Stability: {p.stability}</p>
        <p>Intel: {p.intel}</p>
        <p>Diplomacy: {p.diplomacy}</p>
      </div>

      <div className="box">
        <h2>Production</h2>
        <button onClick={recruit}>Recruit Division</button>
        <p>Divisions: {world.divisions.player}</p>
        <p>Factories: {world.factories}</p>
      </div>

      <div className="box">
        <h2>Focus Tree</h2>
        <button onClick={() => setWorld(applyFocus({ ...world }, "military_industrial"))}>Military Industry</button>
        <button onClick={() => setWorld(applyFocus({ ...world }, "economic_boom"))}>Economic Boom</button>
        <button onClick={() => setWorld(applyFocus({ ...world }, "internal_stability"))}>Stability</button>
        <button onClick={() => setWorld(applyFocus({ ...world }, "spy_network"))}>Spy Network</button>
        <button onClick={() => setWorld(applyFocus({ ...world }, "diplomatic_push"))}>Diplomacy</button>
      </div>

      <div className="box">
        <h2>War Map</h2>
        <div className="grid">
          {Object.entries(world.map).map(([k,v]) => (
            <div key={k} className="tile">
              <b>{k}</b>
              <p>{v}</p>
              <button onClick={() => attack(k)}>Attack</button>
            </div>
          ))}
        </div>
      </div>

      <div className="box">
        <h2>Battle Log</h2>
        <p>{world.log}</p>
      </div>

      <h2 style={{color:"red"}}>{gameOver}</h2>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);

</script>
</body>
</html>
