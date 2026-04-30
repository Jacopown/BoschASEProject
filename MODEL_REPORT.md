# Model Report

## What the model does

Given a 128×128 image, the model predicts
two numbers:

- **Steering** — a value in `[-1, 1]`. Negative = turn left, positive = turn
  right, near zero = go straight.
- **Speed** — a value in `[0.0, 1.0]`. Higher = faster.


## Training data

20k synthetic images generated with `dataset_generator.py`, balanced
across 4 classes:

| Class      | Line angle    | Meaning           |
|------------|---------------|-------------------|
| DRITTO     | -5° to +5°    | go straight       |
| SINISTRA   | -55° to -6°   | turn left         |
| DESTRA     | +6° to +55°   | turn right        |
| STOP       | -95° to -85°  | horizontal → stop |

The expected steering is computed from the line angle, the expected speed
from the line thickness (thicker line → faster).

## How it was trained

A small convolutional neural network (CNN) with two output heads, trained
for 20 epochs on the 20k images using mean squared error as the loss
function. The trained model is saved as `models/modello_bosch.h5` and
converted to TensorFlow Lite (`models/modello_bosch.tflite`) for
deployment on the car. Full details are in `train_model.py`.

## Evaluation on the test set

The model is evaluated on a separate **test set** of 1000 images
(`src/data/dataset_testing/`, 250 per class) generated with **different
background colors** than the training set, so the model cannot rely on
memorized colors.

The metric used is **Mean Absolute Error (MAE)**: the average distance
between predicted and true value. Lower is better.


### Results

| Class    | Steering MAE | Speed MAE |
|----------|-------------:|----------:|
| DRITTO   |       0.0069 |    0.0378 |
| SINISTRA |       0.0112 |    0.0408 |
| DESTRA   |       0.0171 |    0.0382 |
| STOP     |       0.0056 |    0.0350 |
| **Overall** |   **0.0102** | **0.0379** |

### Reading the numbers

- **Steering** — overall MAE ≈ 1% of the full range. The model is very
  precise on this head, with all four classes well below 0.02.
- **Speed** — overall MAE ≈ 4% of the full range. Solid, but uniformly
  worse than steering. This is consistent across all four classes, so
  it is a property of the speed head itself rather than a class-specific
  problem (predicting line thickness is harder than predicting line
  angle from a low-resolution grayscale image).

Overall, the steering head is the strong one; the speed head is
acceptable but expected to degrade faster under input noise.
