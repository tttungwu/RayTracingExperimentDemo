# Quadratic Root Cancellation

This experiment demonstrates catastrophic cancellation while solving quadratic roots for ray-sphere intersections in `float32`.

It uses a perspective camera looking down at a huge sphere whose surface behaves like a ground plane near `y = 0`. The rendered checker pattern makes small hit-point errors easy to see.

The experiment compares:

- `original`: direct roots with `(-b +/- sqrt(delta)) / (2*a)`
- `stable`: PBRT / Press-style root solving through an intermediate `q`

For near intersections, `-b` and `sqrt(delta)` can be almost equal in magnitude. The direct formula subtracts those similar values for one root, destroying significant digits and shifting the hit point.

The stable method computes:

```text
q = -0.5 * (b + sign(b) * sqrt(delta))
t0 = q / a
t1 = c / q
```

This avoids the dangerous subtraction for the sensitive root and keeps the near hit distance much more accurate.

## Run

From the repository root:

```powershell
python experiments/quadratic_root_cancellation/quadratic_root_cancellation_demo.py
```

Or from this directory:

```powershell
python quadratic_root_cancellation_demo.py
```

## Outputs

The script writes one side-by-side comparison image into this directory:

- `huge_sphere_comparison.png`

The image places the `original` result on the left and the `stable` result on the right. The script also attempts to remove stale single-output images named `huge_sphere_original.png` and `huge_sphere_stable.png`.

It also prints debug values for a few sample pixels, including `b`, `sqrt(delta)`, both direct root numerators, and the selected hit distance.
