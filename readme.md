# Pulse Garden

Pulse Garden is an original rhythm game made with **Python and Pygame**.

Move through a procedurally generated route and hit each target on the beat. Your distance from the target in Movement Mode, or your mouse position and timing in Click Mode, determines your judgement.

The game contains a fixed 120-target level and ends with a results screen instead of looping forever.

## Features

- 🎵 Beat-based rhythm gameplay
- 🌌 Procedurally generated levels
- 🎮 Two different game modes
- 🕹️ Movement Mode at **256 BPM**
- 🖱️ Click Mode at **128 BPM**
- 🎯 Distance-based judgements
- ⏱️ Click timing judgements
- ✨ Perfect / Good / Bad / Miss system
- 🔥 Combo tracking
- 🏆 Score system
- 📊 Accuracy calculation
- 🏅 SS / S / A / B / C / D ranks
- 🏁 Proper level completion screen
- 🔄 Restart completed levels with `R`
- 🖥️ 16:9 game aspect ratio
- 📐 2× rendering pipeline
- 🪟 Resizable window
- 🖥️ Fullscreen support
- ⚡ Designed for high-refresh-rate displays
- ✨ Particle effects
- 🧭 Direction indicator in Movement Mode
- 🔄 Targets automatically advance after every beat, including misses

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

Or:

```bash
python3 main.py
```

## Game Modes

### Movement Mode

Movement Mode uses **256 BPM**.

Control the blue player with the keyboard and move toward the glowing target.

The game checks your distance from the target whenever the beat occurs.

Controls:

| Key | Action |
| --- | --- |
| `W` / `↑` | Move up |
| `A` / `←` | Move left |
| `S` / `↓` | Move down |
| `D` / `→` | Move right |

### Click Mode

Click Mode uses **128 BPM**.

The mouse cursor is used instead of keyboard movement. Click near the glowing target around the beat.

Click Mode uses larger targets to make them easier to see and click.

| Input | Action |
| --- | --- |
| Left Mouse Button | Click the current target |

The click is judged using both:

- Distance from the target
- Timing relative to the beat

If you don't click, the target automatically becomes a **MISS** when the beat occurs.

## Judgements

### Movement Mode

| Distance | Judgement | Score |
| -------: | --------- | ----: |
| ≤ 25 px | PERFECT | +1000 |
| ≤ 50 px | GOOD | +600 |
| ≤ 80 px | BAD | +250 |
| > 80 px | MISS | +0 |

### Click Mode

Click timing determines the judgement:

| Timing Error | Judgement | Score |
| ------------: | --------- | ----: |
| ≤ 0.045 s | PERFECT | +1000 |
| ≤ 0.090 s | GOOD | +600 |
| ≤ 0.140 s | BAD | +250 |
| > 0.140 s | MISS | +0 |

The click must also be within **80 pixels** of the target.

## Automatic Target Progression

Every target is judged exactly once per beat.

The target advances regardless of the result:

```text
PERFECT → next target
GOOD    → next target
BAD     → next target
MISS    → next target
```

This means the level never gets stuck waiting for the player to hit a target.

In Click Mode, doing nothing on a beat automatically produces a MISS.

## Combo

Perfect, Good, and Bad judgements increase the combo.

A Miss resets the combo to zero.

The game records your maximum combo for the results screen.

## Level Structure

Each level contains **120 nodes**.

The first node is the player's starting position, leaving **119 targets to judge**.

The level ends after the final target is judged.

There is no infinite regeneration or endless gameplay loop.

After completing the level, the results screen displays:

- Final score
- Accuracy
- Maximum combo
- Perfect count
- Good count
- Bad count
- Miss count
- Final rank
- BPM

Press `R` to generate and play a new level.

## Ranking

The final rank is based on accuracy.

| Accuracy | Rank |
| --------: | :---: |
| 100.00% | SS |
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

A true **SS** requires 100% accuracy.

## Rendering

Pulse Garden uses a **2× rendering pipeline**.

The logical game resolution is:

```text
1280 × 720
```

The internal render resolution is:

```text
2560 × 1440
```

The rendered image is then smoothly scaled to the current window size.

The game uses a **16:9 aspect ratio**, making it suitable for 2560×1440 displays and fullscreen gameplay.

## Level Generation

Targets are procedurally generated when a level begins.

Each target is generated within a reachable distance of the previous target.

The generator also maintains a minimum distance between recent targets to prevent the route from becoming too tangled.

Movement Mode is specifically designed around the **256 BPM** timing interval, keeping target distances short enough to be reachable without a dash.

## Controls

| Key / Input | Action |
| --- | --- |
| `1` | Select Movement Mode |
| `2` | Select Click Mode |
| `W` / `↑` | Move up |
| `A` / `←` | Move left |
| `S` / `↓` | Move down |
| `D` / `→` | Move right |
| Left Mouse Button | Click target |
| `F11` | Toggle fullscreen |
| `R` | Restart after completing a level |
| `Esc` | Exit fullscreen / quit |



## Project Structure

```text
pulse-garden/
├── main.py
└── README.md
```

## Technology

Pulse Garden is built with:

- **Python**
- **Pygame**
- Python's standard `math` and `random` modules

No external game engine is required.

## License

This project is provided as an original personal project. You are free to modify it for your own use.