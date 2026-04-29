# Robotic Vehicle Lane Follower

This project implements a deep learning pipeline to control a robotic vehicle, enabling it to follow lanes based on visual input. The system uses a convolutional neural network (CNN) trained to predict steering angle and speed from synthetic camera images.

## Features

- **Synthetic Dataset Generation**: Dynamically creates a labeled dataset of images with varied line orientations, thicknesses, and background colors.
- **Fault Injection**: Simulates real-world sensor issues by adding salt-and-pepper noise or black stripe occlusions to generated images.
- **Manual Driving**: Provides a keyboard-controlled interface to drive the vehicle manually for testing and calibration.
- **Model Training**: Includes a multi-head CNN (predicting both steering and speed) trained using TensorFlow/Keras.
- **TFLite Integration**: Supports conversion and execution of the model in TensorFlow Lite format for optimized performance on embedded hardware like Raspberry Pi.
- **Advanced Testing Pipeline**: An automated pipeline that can run in "clean" or "dirty" (fault-injected) modes, logging performance data and images to CSV for analysis.
- **Hardware Abstraction**: A serial controller interface manages communication with the vehicle's low-level systems (speed, steering, braking, and power). Commands follow the protocol described in the [BFMC Debugging Documentation](https://bosch-future-mobility-challenge-documentation.readthedocs-hosted.com/data/embeddedplatform/debugging.html).
- **Pre-trained Model**: The repository is shipped with a pre-trained model (`models/modello_bosch.h5` and `.tflite`) ready for immediate testing and deployment.

## Project Structure

```
/
├── environment.yml         # Conda environment with all dependencies
├── run_pipeline.py         # Main script to run the inference pipeline (supports clean/dirty modes)
├── firmware/               # Low-level control firmware for Nucleo board
│   ├── environment.yml     # Firmware development environment
│   └── Embedded_Platform/  # Mbed-os project source and build files
├── models/
│   ├── modello_bosch.h5    # Trained TensorFlow/Keras model
│   └── modello_bosch.tflite # Converted TensorFlow Lite model
├── results/                # Output directory for pipeline results (logs and images)
└── src/
    ├── data/
    │   └── dataset_generator.py # Script to generate training/testing datasets
    ├── model/
    │   ├── converti_in_tflite.py # Converts .h5 model to .tflite
    │   ├── test_modello.py       # Evaluates the model on a test set
    │   └── train_model.py        # Trains the multi-head neural network
    └── utils/
        ├── images_generator.py   # Utilities for image creation and fault injection (noise, stripes)
        ├── manual_driving.py     # Keyboard-based manual control script
        └── serial_controller.py  # Serial communication interface for the vehicle
```

## Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Jacopown/BoschASEProject.git
    cd BoschASEProject
    ```

2.  **Create Conda Environment**
    ```bash
    conda env create -f environment.yml
    conda activate bosch-ase-env
    ```

## Firmware Setup and Build

### Prerequisites
Before building the firmware, ensure you have the following installed on your system:
- **CMake**: Required for the build system.
- **GNU Arm Embedded Toolchain**: A cross-compiler to build the project for the Nucleo-F401RE. You can download it from [Arm Developer](https://developer.arm.com/downloads/-/gnu-rm).

### Environment Creation
To create the necessary development environment for the firmware, use the `environment.yml` file located in the `firmware/` directory:
```bash
conda env create -f firmware/environment.yml
conda activate embedded-platform
```

### Pre-compiled Binary
The project ships with a pre-compiled binary file ready to be flashed to the Nucleo board:
`firmware/Embedded_Platform/cmake_build/NUCLEO_F401RE/develop/GCC_ARM/robot_car.bin`

### Rebuilding from Source
In case of changes to the firmware source code, you can clean and rebuild the binary using `mbed-tools` from the `firmware/Embedded_Platform/` directory:

1. **Deploy libraries**:
   ```bash
   mbed-tools deploy
   ```
2. **Configure the project**:
   ```bash
   mbed-tools configure -m NUCLEO_F401RE -t GCC_ARM
   ```
3. **Compile the binary**:
   ```bash
   mbed-tools compile -m NUCLEO_F401RE -t GCC_ARM
   ```

## Usage Guide

### 1. Generate the Dataset
Generate images for training or testing. The script uses different color distributions for test sets to ensure robustness.
- **Training set:** `python src/data/dataset_generator.py -s 10000 -o src/data/dataset_training/`
- **Test set:** `python src/data/dataset_generator.py -s 2000 -o src/data/dataset_testing/ --is_test`

### 2. Train and Convert the Model
- **Train:** `python src/model/train_model.py` (Saves to `models/modello_bosch.h5`)
- **Convert:** `python src/model/converti_in_tflite.py` (Saves to `models/modello_bosch.tflite`)

### 3. Manual Driving
Use the keyboard to control the vehicle. This is useful for checking the serial connection and motor calibration.
```bash
python src/utils/manual_driving.py
```
**Controls:**
- `W` / `S`: Increase / Decrease speed
- `A` / `D`: Steer Left / Right
- `Q`: Brake
- `SPACE`: Reset speed and steering to zero
- `CTRL+C`: Stop and disconnect

### 4. Run the Automated Pipeline
The `run_pipeline.py` script executes a predefined path and records how the model interprets each step. It can inject faults to test model resilience.

- **Clean Mode:**
  ```bash
  python run_pipeline.py --mode clean --fps 15
  ```
- **Dirty Mode (Fault Injection):**
  ```bash
  python run_pipeline.py --mode dirty --fault both --noise-pct 15 --stripe-width 8 --fps 10
  ```
- **Testing without Hardware:**
  Add the `--no-serial` flag to run the pipeline simulation without a physical vehicle connection.

Results (CSV logs and processed images) are saved in the `results/` directory.

## Serial Communication
The `SerialController` expects the vehicle to be connected via a serial port (default: `/dev/ttyACM0`). Commands are sent in a custom string format:
- Speed: `#speed:VALUE;;`
- Steer: `#steer:VALUE;;`
- Brake: `#brake:STEER;;`
- Power: `#kl:30;;` (ON) / `#kl:0;;` (OFF)
