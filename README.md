# Ray-Sphere Intersection Precision Demos

This repository contains two small CPU ray tracing demos written with `numpy + Pillow`, both using `float32` on purpose to expose numerical precision issues in ray-sphere intersection.

Dependencies for both demos:

```powershell
pip install numpy pillow
```

## Demo 1: Discriminant Precision Loss

Script:

- [raytrace_demo.py](c:\Develop\Project\Temp\RaySphereIntersection\raytrace_demo.py)

This demo uses an orthographic camera and compares two `float32` intersection formulations:

- `original`: `delta = b*b - 4*a*c`
- `stable`: `delta = r*r - l*l`

Generated images:

- `dist_100_original.png`
- `dist_100_stable.png`
- `dist_2000_original.png`
- `dist_2000_stable.png`
- `dist_4100_original.png`
- `dist_4100_stable.png`

Run:

```powershell
python raytrace_demo.py
```

Why `distance = 4100` breaks in `float32`:

```text
delta = b*b - 4*a*c
```

For the center ray at `z = 4100`:

- `b` is about `-8200`
- `b*b` is about `67,240,000`
- `4ac` is also about `67,240,000`

The true discriminant is tiny compared with those two large terms. In `float32`, both large values are rounded before subtraction, so their low-order bits are lost. That catastrophic cancellation can make `delta` inaccurate, which leads to missed hits, broken silhouettes, and incorrect diffuse shading.

The stable form:

```text
delta = r*r - l*l
```

keeps the important subtraction near unit scale, so it avoids large-number cancellation and remains visually stable at long distances.

## Demo 2: Catastrophic Cancellation in Quadratic Root Solving

Script:

- [huge_sphere_demo.py](c:\Develop\Project\Temp\RaySphereIntersection\huge_sphere_demo.py)

This demo uses a perspective camera looking downward at a huge sphere that behaves like a ground plane near `y = 0`. It compares:

- `original`: direct quadratic roots with `(-b ± sqrt(delta)) / (2a)`
- `stable`: PBRT / Press-style stable root computation using `q`

Generated images:

- `huge_sphere_original.png`
- `huge_sphere_stable.png`

Run:

```powershell
python huge_sphere_demo.py
```

Why catastrophic cancellation happens here:

For rays that hit the huge sphere very close to the camera, `-b` and `sqrt(delta)` become nearly equal in magnitude. In the original formula, one root is computed from subtracting those two large, similar numbers. In `float32`, that subtraction destroys many significant digits, so the near intersection `t` becomes inaccurate.

That inaccurate `t` shifts the hit point enough to produce checkerboard wobble, banding, or discontinuities.

Why the stable method works:

Instead of directly evaluating both `-b ± sqrt(delta)` terms, it first computes:

```text
q = -0.5 * (b + sign(b) * sqrt(delta))
```

and then recovers the roots as:

```text
t0 = q / a
t1 = c / q
```

This avoids the dangerous subtraction for the sensitive root, so the near hit distance stays much more accurate.
