import math
from pathlib import Path

import numpy as np
from PIL import Image


WIDTH = 512
HEIGHT = 512
VIEW_HALF_SIZE = np.float32(1.25)
SPHERE_RADIUS = np.float32(1.0)
DISTANCES = (100.0, 2000.0, 4100.0)
OUTPUT_DIR = Path(".")


def normalize(v: np.ndarray) -> np.ndarray:
    v = v.astype(np.float32)
    n = np.linalg.norm(v).astype(np.float32)
    return (v / n).astype(np.float32)


def make_ortho_rays():
    xs = np.linspace(-VIEW_HALF_SIZE, VIEW_HALF_SIZE, WIDTH, dtype=np.float32)
    ys = np.linspace(VIEW_HALF_SIZE, -VIEW_HALF_SIZE, HEIGHT, dtype=np.float32)
    px, py = np.meshgrid(xs, ys)

    origins = np.stack(
        [px, py, np.zeros((HEIGHT, WIDTH), dtype=np.float32)],
        axis=-1,
    ).astype(np.float32)
    directions = np.zeros_like(origins, dtype=np.float32)
    directions[..., 2] = np.float32(1.0)
    return origins, directions


def save_image(rgb: np.ndarray, path: Path) -> None:
    img = np.clip(rgb * np.float32(255.0), 0.0, 255.0).astype(np.uint8)
    Image.fromarray(img, mode="RGB").save(path)


def render_sphere(distance: float, method: str, origins: np.ndarray, directions: np.ndarray):
    distance32 = np.float32(distance)
    center = np.array([0.0, 0.0, distance32], dtype=np.float32)
    f = (origins - center).astype(np.float32)

    light_dir = normalize(np.array([1.0, 1.0, -1.0], dtype=np.float32))
    l_to_light = (-light_dir).astype(np.float32)

    if method == "original":
        a = np.sum(directions * directions, axis=-1, dtype=np.float32).astype(np.float32)
        b = (
            np.float32(2.0)
            * np.sum(f * directions, axis=-1, dtype=np.float32)
        ).astype(np.float32)
        c = (
            np.sum(f * f, axis=-1, dtype=np.float32)
            - np.float32(SPHERE_RADIUS * SPHERE_RADIUS)
        ).astype(np.float32)

        bb = (b * b).astype(np.float32)
        four_ac = (np.float32(4.0) * a * c).astype(np.float32)
        delta = (bb - four_ac).astype(np.float32)

        hit = delta >= np.float32(0.0)
        sqrt_delta = np.sqrt(np.maximum(delta, np.float32(0.0), dtype=np.float32)).astype(np.float32)
        t = ((-b - sqrt_delta) / (np.float32(2.0) * a)).astype(np.float32)
    elif method == "stable":
        d_hat = directions / np.linalg.norm(directions, axis=-1, keepdims=True).astype(np.float32)
        proj_len = np.sum(f * d_hat, axis=-1, dtype=np.float32).astype(np.float32)
        proj = (proj_len[..., None] * d_hat).astype(np.float32)
        perp = (f - proj).astype(np.float32)
        l2 = np.sum(perp * perp, axis=-1, dtype=np.float32).astype(np.float32)
        delta = (np.float32(SPHERE_RADIUS * SPHERE_RADIUS) - l2).astype(np.float32)

        hit = delta >= np.float32(0.0)
        t_proj = (-proj_len).astype(np.float32)
        t_offset = np.sqrt(np.maximum(delta, np.float32(0.0), dtype=np.float32)).astype(np.float32)
        t = (t_proj - t_offset).astype(np.float32)

        a = np.sum(directions * directions, axis=-1, dtype=np.float32).astype(np.float32)
        b = (
            np.float32(2.0)
            * np.sum(f * directions, axis=-1, dtype=np.float32)
        ).astype(np.float32)
        c = (
            np.sum(f * f, axis=-1, dtype=np.float32)
            - np.float32(SPHERE_RADIUS * SPHERE_RADIUS)
        ).astype(np.float32)
        bb = (b * b).astype(np.float32)
        four_ac = (np.float32(4.0) * a * c).astype(np.float32)
    else:
        raise ValueError(f"Unknown method: {method}")

    valid_hit = np.logical_and(hit, t >= np.float32(0.0))
    points = (origins + t[..., None] * directions).astype(np.float32)
    normals = (points - center).astype(np.float32)
    normal_len = np.linalg.norm(normals, axis=-1, keepdims=True).astype(np.float32)
    safe_normal_len = np.where(normal_len > np.float32(0.0), normal_len, np.float32(1.0)).astype(np.float32)
    normals = (normals / safe_normal_len).astype(np.float32)

    diffuse = np.sum(normals * l_to_light, axis=-1, dtype=np.float32).astype(np.float32)
    diffuse = np.maximum(diffuse, np.float32(0.0), dtype=np.float32)
    diffuse = np.where(valid_hit, diffuse, np.float32(0.0)).astype(np.float32)

    rgb = np.repeat(diffuse[..., None], 3, axis=-1).astype(np.float32)

    center_px = (HEIGHT // 2, WIDTH // 2)
    cy, cx = center_px
    debug = {
        "distance": distance,
        "method": method,
        "center_bb": float(bb[cy, cx]),
        "center_4ac": float(four_ac[cy, cx]),
        "center_delta": float(delta[cy, cx]),
        "delta_min": float(delta.min()),
        "delta_max": float(delta.max()),
        "hit_pixels": int(np.count_nonzero(valid_hit)),
    }
    return rgb, debug


def main():
    origins, directions = make_ortho_rays()

    for distance in DISTANCES:
        for method in ("original", "stable"):
            rgb, debug = render_sphere(distance, method, origins, directions)
            out_name = f"dist_{int(distance)}_{method}.png"
            save_image(rgb, OUTPUT_DIR / out_name)
            print(
                f"[{method}] dist={int(distance)} "
                f"hit_pixels={debug['hit_pixels']} "
                f"center(bb={debug['center_bb']:.7g}, 4ac={debug['center_4ac']:.7g}, delta={debug['center_delta']:.7g}) "
                f"delta_range=[{debug['delta_min']:.7g}, {debug['delta_max']:.7g}]"
            )


if __name__ == "__main__":
    main()
