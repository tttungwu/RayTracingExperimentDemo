# Discriminant Precision Loss

This experiment demonstrates precision loss in the ray-sphere intersection discriminant when using `float32`.

It compares two formulations for an orthographic camera looking at a unit sphere placed at increasing distances:

- `original`: computes the quadratic discriminant as `delta = b*b - 4*a*c`
- `stable`: computes the equivalent geometric term as `delta = r*r - l*l`

At long distances, `b*b` and `4*a*c` become large and nearly equal. Their subtraction loses low-order bits in `float32`, which can make the discriminant inaccurate enough to miss hits or damage the sphere silhouette and shading.

The stable version keeps the important subtraction near the scale of the sphere radius, so it remains visually stable farther from the camera.

## Run

From the repository root:

```powershell
python experiments/discriminant_precision_loss/discriminant_precision_loss_demo.py
```

Or from this directory:

```powershell
python discriminant_precision_loss_demo.py
```

## Outputs

The script writes one side-by-side comparison image for each distance into this directory:

- `dist_100_comparison.png`
- `dist_2000_comparison.png`
- `dist_4100_comparison.png`

Each image places the `original` result on the left and the `stable` result on the right. The script also attempts to remove stale single-output images matching `dist_*_original.png` and `dist_*_stable.png` from this experiment directory.

It also prints debug values for the center pixel, including `b*b`, `4*a*c`, the computed discriminant, and hit counts.
