# Cosine Power Distribution

This interactive demo visualizes the normalized cosine-power hemisphere distribution with `theta` limited to `[0, pi/2]`:

```text
p(theta, phi) = ((s + 1) / (2*pi)) * cos(theta)^s, 0 <= theta <= pi/2
```

The distribution is rotationally symmetric around the surface normal, so `phi` changes direction around the lobe while `theta` controls the falloff away from the normal across the upper hemisphere only. Larger `s` values make the lobe narrower and raise the peak value at `theta = 0`.

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

The lobe is drawn as a radial surface over the upper hemisphere. Color and radius both encode relative density, with the peak at the normal direction. The panel also reports:

- `peak p(0, phi) = (s + 1) / (2*pi)`
- the half-maximum angle where `cos(theta)^s = 0.5`
- the normalization reminder that the integral over the hemisphere is `1`
