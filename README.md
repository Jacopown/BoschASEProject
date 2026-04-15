# Robotic Vehicle Lane Follower

This project implements a deep learning pipeline to control a robotic vehicle, enabling it to follow lanes based on visual input. The system uses a convolutional neural network (CNN) trained to predict steering angle and speed from camera images.

## Features

- **Synthetic Dataset Generation**: Dynamically creates a labeled dataset of images with varied line orientations, thicknesses, and background colors.
- **Model Training**: Includes scripts to train a TensorFlow/Keras model for lane-following.
- **Model Conversion**: Supports conversion of the trained model to TensorFlow Lite for efficient deployment on embedded systems.
- **Hardware Integration**: Communicates with vehicle hardware via serial port to control motors for steering and speed.
- **End-to-End Pipeline**: A top-level script runs the full inference loop: generating a test image, getting a model prediction, and sending commands to the hardware.

## Project Structure

```
/
├── .gitignore
├── environment.yml         # Conda environment with all dependencies
├── LICENSE
├── README.md
├── run_pipeline.py         # Main script to run the live inference pipeline with hardware
├── models/
│   ├── modello_bosch.h5    # Trained TensorFlow/Keras model
│   └── modello_bosch.tflite    # Converted TensorFlow Lite model
└── src/
    ├── data/
    │   ├── __init__.py
    │   └── dataset_generator.py # Script to generate the training and testing datasets
    ├── model/
    │   ├── converti_in_tflite.py # Converts the .h5 model to .tflite
    │   ├── test_modello.py       # Script to evaluate the model's performance on a test set
    │   └── train_model.py        # Script for training the neural network
    └── utils/
        ├── __init__.py
        ├── images_generator.py   # Utility functions for creating line images
        └── serial_controller.py  # Class for managing serial communication with the vehicle
```

## Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd BoschASEProject
    ```

2.  **Create Conda Environment**
    All project dependencies are listed in the `environment.yml` file. Use Conda to create the environment and install them.
    ```bash
    conda env create -f environment.yml
    conda activate bosch-ase-env
    ```
    *(Note: You may need to rename the environment in `environment.yml` or the `conda activate` command if you change it.)*

## Usage Guide

### 1. Generate the Dataset

The `dataset_generator.py` script creates the images and a `labels.csv` file needed for training and testing.

-   **To create a training set:**
    ```bash
    python src/data/dataset_generator.py --dataset_size 10000 --output_dir dataset_training/
    ```
-   **To create a separate test set** (with different background colors):
    ```bash
    python src/data/dataset_generator.py --dataset_size 2000 --output_dir dataset_testing/ --is_test
    ```

### 2. Train the Model

The `train_model.py` script trains the network using the generated dataset. You will need to configure the script to point to your training data directory.

```bash
python src/model/train_model.py
```
After training, the script will save the model as `modello_bosch.h5` in the `models/` directory.

### 3. Test the Model

The `test_modello.py` script evaluates the trained model against a test dataset. The script expects the test images to be in a `dataset_testing/` folder in the root directory.

```bash
python src/model/test_modello.py
```
This will print a table of predicted steer and speed values for each image in the test set.

### 4. Convert the Model to TFLite

For deployment on less powerful hardware, convert the Keras model to TensorFlow Lite using `converti_in_tflite.py`.

```bash
python src/model/converti_in_tflite.py
```
This will create `modello_bosch.tflite` in the `models/` directory.

### 5. Run the Live Pipeline

The `run_pipeline.py` script provides an end-to-end demonstration. It loads the model, generates a sample image, predicts the vehicle's speed and steering, and sends the corresponding commands over the serial port.

**Before running, you must update the `PORTA_SERIALE` variable in the script to match your device's serial port.**

```bash
python run_pipeline.py
```
The vehicle should start moving based on the model's predictions. The script will run for a few iterations and then safely disconnect.
