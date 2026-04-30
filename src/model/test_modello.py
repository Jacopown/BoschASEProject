"""
Evaluate the trained model on the test set: per-class accuracy
(MAE) for steering and speed across DRITTO / SINISTRA / DESTRA / STOP.

Usage (from project root):
    python -m src.model.test_modello
"""
import os
import sys

import cv2
import numpy as np
import pandas as pd
import tensorflow as tf


MODEL_PATH = "models/modello_bosch.h5"
TEST_DIR = "src/data/dataset_testing"
LABELS_CSV = os.path.join(TEST_DIR, "labels.csv")


def prepare_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    img = cv2.resize(img, (128, 128))
    img = img.astype(np.float32) / 255.0
    return np.expand_dims(img, axis=(0, -1))


def main():
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: model not found: {MODEL_PATH}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(LABELS_CSV):
        print(f"ERROR: labels.csv not found: {LABELS_CSV}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading model {MODEL_PATH}...")
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)

    # The model has two output heads; figure out which is steer vs speed
    # by checking output names. Falls back to assuming order [steer, speed].
    out_names = [o.name.lower() for o in model.outputs]
    steer_idx = next((i for i, n in enumerate(out_names) if "steer" in n), 0)
    speed_idx = 1 - steer_idx

    print(f"Loading labels {LABELS_CSV}...")
    labels = pd.read_csv(LABELS_CSV)
    print(f"  {len(labels)} samples\n")

    # Run predictions and collect errors
    rows = []
    for _, row in labels.iterrows():
        img = prepare_image(os.path.join(TEST_DIR, row["file_name"]))
        if img is None:
            continue
        pred = model.predict(img, verbose=0)
        pred_steer = float(pred[steer_idx][0][0])
        pred_speed = float(pred[speed_idx][0][0])
        rows.append({
            "type_label": row["type_label"],
            "steer_abs_err": abs(pred_steer - float(row["steering_target"])),
            "speed_abs_err": abs(pred_speed - float(row["speed_target"])),
        })

    df = pd.DataFrame(rows)

    # Per-class accuracy (MAE) for both heads
    print("=" * 50)
    print(f"{'CLASS':<10} | {'STEER MAE':>10} | {'SPEED MAE':>10}")
    print("-" * 50)
    for cls in ["DRITTO", "SINISTRA", "DESTRA", "STOP"]:
        g = df[df["type_label"] == cls]
        if g.empty:
            continue
        print(f"{cls:<10} | {g['steer_abs_err'].mean():>10.4f} | "
              f"{g['speed_abs_err'].mean():>10.4f}")
    print("-" * 50)
    print(f"{'OVERALL':<10} | {df['steer_abs_err'].mean():>10.4f} | "
          f"{df['speed_abs_err'].mean():>10.4f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
