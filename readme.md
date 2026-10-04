# Pulse Garden

Pulse Garden is an original rhythm game made with **Python and Pygame**.

Move around the arena and reach the glowing target before each beat. Your distance from the target when the beat occurs determines your judgement.

The level has a fixed number of targets and ends with a results screen instead of looping forever.

## Features

-  Beat-based rhythm gameplay
-  Procedurally generated level
-  Distance-based timing judgements
-  Perfect / Good / Bad / Miss system
-  Combo tracking
-  Score and rank system
-  Accuracy calculation
-  Proper level completion screen
-  Restart completed levels with `R`
-  16:9 game aspect ratio
-  2× SSAA for smoother rendering
-  Resizable window
-  Fullscreen support
-  Designed for high-refresh-rate displays
-  Particle effects and animated targets
-  Direction indicator showing the next target

## Requirements

- Python 3.10+
- Pygame

Install Pygame with:

```bash
pip install pygame
```

## Running

Run the game with:

```bash
python main.py
```

Or, if you use Python 3 explicitly:

```bash
python3 main.py
```

## Controls

| Key | Action |
|---|---|
| `W` / `↑` | Move up |
| `A` / `←` | Move left |
| `S` / `↓` | Move down |
| `D` / `→` | Move right |
| `F11` | Toggle fullscreen |
| `R` | Restart after completing the level |
| `Esc` | Exit fullscreen / quit |

There is intentionally **no dash mechanic**.

## Gameplay

A route of targets is generated when the level starts.

The blue player must move toward the currently highlighted target.

When the next beat occurs, the game checks the player's distance from the target.

### Judgements

| Distance | Judgement | Score |
|---:|---|---:|
| ≤ 25 px | PERFECT | +1000 |
| ≤ 50 px | GOOD | +600 |
| ≤ 80 px | BAD | +250 |
| > 80 px | MISS | +0 |

Perfect, Good, and Bad hits increase the combo.

A Miss resets the combo.

The target always advances after every beat, including after a Miss.

## Level Structure

Each level contains **120 generated nodes**.

The first node is the starting position. The remaining nodes form the playable rhythm route.

After the final target is judged, the game enters the results screen.

The level does **not** regenerate or continue indefinitely.

The results screen shows:

- Final score
- Accuracy
- Maximum combo
- Perfect count
- Good count
- Bad count
- Miss count
- Final rank

Press `R` to generate and play a new level.

## Ranking

The final rank is based on accuracy:

| Accuracy | Rank |
|---:|:---:|
| 100% | SS |
| 95%+ | S |
| 85%+ | A |
| 70%+ | B |
| 50%+ | C |
| Below 50% | D |

Accuracy uses weighted judgements:

- Perfect = 100%
- Good = 60%
- Bad = 25%
- Miss = 0%

## Rendering

The game uses a **2× Super-Sample Anti-Aliasing (SSAA)** pipeline.

The logical game resolution is:

```text
1280 × 720
```

With 2× SSAA, the internal render resolution is:

```text
2560 × 1440
```

The result is downscaled to the actual window resolution using Pygame's smooth scaling.

The game uses a **16:9 aspect ratio**, allowing it to fill a 2560×1440 display in fullscreen without stretching or letterboxing.

## Level Generation

Targets are procedurally generated while keeping each new target within a reachable distance of the previous one.

The generator also keeps a minimum distance between recent targets to prevent the route from becoming overly tangled.

This means the player can follow the route using normal movement without relying on a dash mechanic.

## Project Structure

A minimal project can look like this:

```text
pulse-garden/
├── main.py
└── README.md
```

## Technology

Pulse Garden is built using:

- **Python**
- **Pygame**
- Standard Python modules such as `math` and `random`

No external game engine is required.

## License

This project is provided as an original personal project. You are free to modify it for your own use.
