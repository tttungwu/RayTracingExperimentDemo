from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


WIDTH = 512
HEIGHT = 512
FOV_Y_DEG = np.float32(60.0)
CAMERA_ORIGIN = np.array([0.0, 5.0, 0.0], dtype=np.float32)
LOOK_AT = np.array([0.0, 0.0, -20.0], dtype=np.float32)
UP = np.array([0.0, 1.0, 0.0], dtype=np.float32)
SPHERE_RADIUS = np.float32(10000000.0)
SPHERE_CENTER = np.array([0.0, -SPHERE_RADIUS, 0.0], dtype=np.float32)
EPSILON = np.float32(1e-4)
OUTPUT_DIR = Path(__file__).resolve().parent


def normalize(v: np.ndarray) -> np.ndarray:
    v = v.astype(np.float32)
    n = np.linalg.norm(v, axis=-1, keepdims=True).astype(np.float32)
    n = np.where(n > np.float32(0.0), n, np.float32(1.0)).astype(np.float32)
    return (v / n).astype(np.float32)


def generate_camera_rays():
    aspect = np.float32(WIDTH / HEIGHT)
    tan_half_fov = np.tan(np.deg2rad(FOV_Y_DEG * np.float32(0.5))).astype(np.float32)
    forward = normalize((LOOK_AT - CAMERA_ORIGIN)[None, None, :])[0, 0]
    right = normalize(np.cross(forward, UP)[None, None, :])[0, 0]
    true_up = normalize(np.cross(right, forward)[None, None, :])[0, 0]

    xs = np.linspace(-1.0, 1.0, WIDTH, dtype=np.float32)
    ys = np.linspace(1.0, -1.0, HEIGHT, dtype=np.float32)
    px, py = np.meshgrid(xs, ys)

    dirs = (
        forward[None, None, :]
        + (px * tan_half_fov * aspect)[..., None] * right[None, None, :]
        + (py * tan_half_fov)[..., None] * true_up[None, None, :]
    ).astype(np.float32)
    return normalize(dirs)


def to_image(rgb: np.ndarray) -> Image.Image:
    img = np.clip(rgb * np.float32(255.0), 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(img, mode="RGB")


def save_comparison_image(original_rgb: np.ndarray, stable_rgb: np.ndarray, path: Path) -> None:
    label_height = 40
    gap = 8
    original_img = to_image(original_rgb)
    stable_img = to_image(stable_rgb)

    canvas = Image.new(
        "RGB",
        (WIDTH * 2 + gap, HEIGHT + label_height),
        color=(18, 18, 18),
    )
    draw = ImageDraw.Draw(canvas)

    original_x = 0
    stable_x = WIDTH + gap
    canvas.paste(original_img, (original_x, label_height))
    canvas.paste(stable_img, (stable_x, label_height))

    draw.text((12, 12), "original", fill=(235, 235, 235))
    draw.text((stable_x + 12, 12), "stable", fill=(235, 235, 235))
    canvas.save(path)


def remove_stale_single_outputs() -> None:
    for name in ("huge_sphere_original.png", "huge_sphere_stable.png"):
        path = OUTPUT_DIR / name
        if path.exists():
            try:
                path.unlink()
            except PermissionError:
                print(f"warning: could not remove stale single-output image: {path}")


def checker_color(points: np.ndarray, hit_mask: np.ndarray) -> np.ndarray:
    tile_size = np.float32(0.5)
    inv_tile = np.float32(1.0) / tile_size
    local_x = points[..., 0]
    local_z = points[..., 2]
    u = np.floor(local_x * inv_tile).astype(np.int32)
    v = np.floor(local_z * inv_tile).astype(np.int32)
    pattern = ((u + v) & 1) == 0

    red = np.array([0.92, 0.16, 0.18], dtype=np.float32)
    blue = np.array([0.12, 0.26, 0.88], dtype=np.float32)
    color = np.where(pattern[..., None], red, blue).astype(np.float32)

    sky = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    return np.where(hit_mask[..., None], color, sky).astype(np.float32)


def intersect_original(ray_dirs: np.ndarray):
    f = (CAMERA_ORIGIN - SPHERE_CENTER).astype(np.float32)
    a = np.sum(ray_dirs * ray_dirs, axis=-1, dtype=np.float32).astype(np.float32)
    b = (np.float32(2.0) * np.sum(f * ray_dirs, axis=-1, dtype=np.float32)).astype(np.float32)
    c = np.float32(np.dot(f, f) - SPHERE_RADIUS * SPHERE_RADIUS)

    delta = (b * b - np.float32(4.0) * a * c).astype(np.float32)
    valid = delta >= np.float32(0.0)
    sqrt_delta = np.sqrt(np.maximum(delta, np.float32(0.0))).astype(np.float32)

    t0 = ((-b - sqrt_delta) / (np.float32(2.0) * a)).astype(np.float32)
    t1 = ((-b + sqrt_delta) / (np.float32(2.0) * a)).astype(np.float32)
    t = np.minimum(t0, t1).astype(np.float32)
    t = np.where(t < np.float32(0.0), np.maximum(t0, t1), t).astype(np.float32)

    return {
        "a": a,
        "b": b,
        "c": c,
        "delta": delta,
        "sqrt_delta": sqrt_delta,
        "t0": t0,
        "t1": t1,
        "t": t,
        "valid": valid,
        "minus_b_plus_sqrt": (-b + sqrt_delta).astype(np.float32),
        "minus_b_minus_sqrt": (-b - sqrt_delta).astype(np.float32),
    }


def intersect_stable(ray_dirs: np.ndarray):
    f = (CAMERA_ORIGIN - SPHERE_CENTER).astype(np.float32)
    a = np.sum(ray_dirs * ray_dirs, axis=-1, dtype=np.float32).astype(np.float32)
    b = (np.float32(2.0) * np.sum(f * ray_dirs, axis=-1, dtype=np.float32)).astype(np.float32)
    c = np.float32(np.dot(f, f) - SPHERE_RADIUS * SPHERE_RADIUS)

    delta = (b * b - np.float32(4.0) * a * c).astype(np.float32)
    valid = delta >= np.float32(0.0)
    sqrt_delta = np.sqrt(np.maximum(delta, np.float32(0.0))).astype(np.float32)

    sign_b = np.where(b > np.float32(0.0), np.float32(1.0), np.float32(-1.0)).astype(np.float32)
    q = (-np.float32(0.5) * (b + sign_b * sqrt_delta)).astype(np.float32)

    safe_q = np.where(np.abs(q) > EPSILON, q, np.float32(np.nan)).astype(np.float32)
    t0 = (q / a).astype(np.float32)
    t1 = (c / safe_q).astype(np.float32)
    t = np.minimum(t0, t1).astype(np.float32)
    t = np.where(t < np.float32(0.0), np.maximum(t0, t1), t).astype(np.float32)

    return {
        "a": a,
        "b": b,
        "c": c,
        "delta": delta,
        "sqrt_delta": sqrt_delta,
        "q": q,
        "t0": t0,
        "t1": t1,
        "t": t,
        "valid": valid,
        "minus_b_plus_sqrt": (-b + sqrt_delta).astype(np.float32),
        "minus_b_minus_sqrt": (-b - sqrt_delta).astype(np.float32),
    }


def render(method: str, ray_dirs: np.ndarray):
    if method == "original":
        result = intersect_original(ray_dirs)
    elif method == "stable":
        result = intersect_stable(ray_dirs)
    else:
        raise ValueError(f"Unknown method: {method}")

    hit_mask = np.logical_and(result["valid"], result["t"] > np.float32(0.0))
    points = (CAMERA_ORIGIN + result["t"][..., None] * ray_dirs).astype(np.float32)
    rgb = checker_color(points, hit_mask)
    return rgb, result


def print_debug(label: str, result: dict) -> None:
    sample_pixels = [
        ("center", HEIGHT // 2, WIDTH // 2),
        ("low_center", int(HEIGHT * 0.82), WIDTH // 2),
        ("bottom_right", int(HEIGHT * 0.90), int(WIDTH * 0.78)),
    ]
    print(f"[{label}]")
    for name, y, x in sample_pixels:
        b = float(result["b"][y, x])
        sqrt_delta = float(result["sqrt_delta"][y, x])
        plus = float(result["minus_b_plus_sqrt"][y, x])
        minus = float(result["minus_b_minus_sqrt"][y, x])
        t0 = float(result["t0"][y, x])
        t1 = float(result["t1"][y, x])
        t = float(result["t"][y, x])
        print(
            f"  {name}: "
            f"b={b:.9g}, sqrt(delta)={sqrt_delta:.9g}, "
            f"-b+sqrt={plus:.9g}, -b-sqrt={minus:.9g}, "
            f"t0={t0:.9g}, t1={t1:.9g}, t={t:.9g}"
        )
    print(f"  hit_pixels={int(np.count_nonzero(np.logical_and(result['valid'], result['t'] > 0.0)))}")


def main():
    ray_dirs = generate_camera_rays()
    remove_stale_single_outputs()

    original_rgb, original_result = render("original", ray_dirs)
    stable_rgb, stable_result = render("stable", ray_dirs)

    save_comparison_image(original_rgb, stable_rgb, OUTPUT_DIR / "huge_sphere_comparison.png")

    print_debug("original", original_result)
    print_debug("stable", stable_result)


if __name__ == "__main__":
    main()
