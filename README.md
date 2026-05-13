# Ray Tracing Experiment Demo

This repository collects small CPU ray tracing experiments that are useful for studying rendering algorithms, numerical precision, and implementation tradeoffs.

The current experiments are intentionally compact and written with `numpy + Pillow`. They use `float32` in places where precision issues are easier to observe.

## Setup

Install the shared dependencies:

```powershell
pip install numpy pillow
```

## Experiments

| Experiment | Directory | Focus |
| --- | --- | --- |
| Discriminant Precision Loss | [experiments/discriminant_precision_loss](experiments/discriminant_precision_loss) | Ray-sphere intersection misses and shading artifacts caused by evaluating `b*b - 4*a*c` at long distances in `float32`. |
| Quadratic Root Cancellation | [experiments/quadratic_root_cancellation](experiments/quadratic_root_cancellation) | Near-hit instability caused by catastrophic cancellation in the direct quadratic root formula. |

Each experiment directory contains its own README, runnable script, and generated images after execution.

## Run Everything

From the repository root:

```powershell
python experiments/discriminant_precision_loss/discriminant_precision_loss_demo.py
python experiments/quadratic_root_cancellation/quadratic_root_cancellation_demo.py
```

Generated images are written next to the script for each experiment.
