# Ray-Sphere Intersection Precision Demo

This demo renders a single sphere with an orthographic camera and compares two `float32` ray-sphere intersection methods:

- `original`: `delta = b*b - 4*a*c`
- `stable`: `delta = r*r - l*l`

It generates six images in the current directory:

- `dist_100_original.png`
- `dist_100_stable.png`
- `dist_2000_original.png`
- `dist_2000_stable.png`
- `dist_4100_original.png`
- `dist_4100_stable.png`

## Run

```powershell
python raytrace_demo.py
```

Dependencies:

```powershell
pip install numpy pillow
```

## Why distance 4100 breaks in float32

With the original quadratic discriminant:

```text
delta = b*b - 4*a*c
```

for the center ray at distance `z = 4100`:

- `b` is about `-8200`
- `b*b` is about `67,240,000`
- `4ac` is also about `67,240,000`

The true discriminant near the sphere surface is very small compared with those large terms. In `float32`, both large values are rounded before subtraction, so most significant digits cancel out. This catastrophic cancellation can make `delta` flip sign or jump in value, causing:

- missed hits
- broken silhouettes
- incorrect normals and diffuse shading

The stable form computes the perpendicular distance from the ray to the sphere center first:

```text
delta = r*r - l*l
```

Here `l*l` stays near `0..1` for relevant rays, so the subtraction happens between similarly scaled numbers. That avoids the large-number cancellation and keeps the sphere visible and smoothly shaded even at distance `4100`.

## Huge Sphere Demo

There is also a second demo for catastrophic cancellation in quadratic root solving with a perspective camera and a huge nearby sphere:

- [huge_sphere_demo.py](c:\Develop\Project\Temp\RaySphereIntersection\huge_sphere_demo.py)

Run it with:

```powershell
python huge_sphere_demo.py
```

It generates:

- `huge_sphere_original.png`
- `huge_sphere_stable.png`
