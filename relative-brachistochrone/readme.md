# Relativity Trajectory Simulator

Use this code as described in my [blog post](https://curtislowder.com/blog/2025-06-29-Simulating-Relativity/). Output will be saved to `./output/{name}/*`

## Examples

```bash
python3 main.py -d 10ly -m maneuvers/simple.csv --graph
```

```bash
python3 main.py --demo avatar_isv --animate
```

## Help

```
Run relativistic spaceship simulations.

options:
  -h, --help            show this help message and exit
  --maneuver-file MANEUVER_FILE, --file MANEUVER_FILE, -m MANEUVER_FILE
                        Path to CSV maneuver file with (accel_g, duration_s) rows.
  --demo {alpha_centauri_brachistochrone,alpha_centauri_coasting,burst_and_coast,slow_burn,avatar_isv}
                        Run a built-in maneuver demo (e.g., slow_burn, burst_and_coast).
  -n NAME, --name NAME  Name of maneuver (default: test)
  -d TARGET_DISTANCE, --target-distance TARGET_DISTANCE
                        Target distance with unit (e.g.: 3.0 au, default without unit meters, default: 4.37 light years).
  -s STEP, --step STEP  Step size in seconds of proper time (default: 60).
  --ship-model SHIP_MODEL
                        Ship model to use for animation (default: base)
  --use-sail            Use sail in animation (default: false)
  --hide-status         Print status at end of simulation.
  --verbose, -v         Print status at end of simulation.
  --graph, -g           Generate graphs into output path. Saved to file in ./output/{{name}}
  --log, -l             Log raw data to csvfile Saved to file ./output/data.csv
  --animate, -a         Generate animations Saved to file ./output/{name}.mp4
```