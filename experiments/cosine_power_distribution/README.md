# Cosine Power Distribution

This interactive demo visualizes the normalized cosine-power hemisphere distribution with `theta` limited to `[0, pi/2]`:

```text
p(theta, phi) = ((s + 1) / (2*pi)) * cos(theta)^s, 0 <= theta <= pi/2
```

The distribution is rotationally symmetric around the surface normal, so `phi` changes direction around the lobe while `theta` controls the falloff away from the normal across the upper hemisphere only. Larger `s` values make the lobe narrower and raise the peak value at `theta = 0`.

When `s = 0`, the formula is the uniform hemisphere density `1 / (2*pi)`, so the radial plot is a small hemisphere with nonzero radius at `theta = pi/2`. For any `s > 0`, the value approaches `0` at `theta = pi/2`.

## Run

Open the HTML file directly in a browser:

```powershell
start experiments/cosine_power_distribution/cosine_power_distribution_demo.html
```

Or double-click `cosine_power_distribution_demo.html` from this directory.

## Controls

- Click the viewport to capture the mouse.
- Move with `W`, `A`, `S`, `D`.
- Move up with `Space`; move down with `Ctrl`.
- Look around with the mouse.
- Press `Esc` to release the mouse.
- Adjust `s` with the slider or number input.

## Visualization

The lobe is drawn as a radial surface over the upper hemisphere with radius equal to the actual formula value `p(theta, phi)`. The mesh uses denser theta sampling near `theta = 0`, where large `s` values change most rapidly. Color uses the same density value on a fixed scale from `0` to the maximum supported peak at `s = 128`. The panel also reports:

- `peak p(0, phi) = (s + 1) / (2*pi)`
- the half-maximum angle where `cos(theta)^s = 0.5`
- the normalization reminder that the integral over the hemisphere is `1`
