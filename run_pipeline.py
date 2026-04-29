"""
This is the pipeline that has to be run on the Pi and the Idea is to define a "clean" path and to see how the model behaves in that situation.
After this peocede with making the images "dirty" and checking again the effect of that "dirt" on the model interpretations.
"""
import os
import time
import csv
import argparse
import numpy as np
import cv2
import tensorflow as tf

from src.utils.serial_controller import SerialController
from src.utils.images_generator import generate_image, generate_colors,add_noise,add_black_stripe

#I define my path for testing 
# Format: (label, angle_deg, thickness, duration_sec)
EASY_PATH = [
    ("DRITTO_1",          0,   10,   4),
    ("DESTRA_slight",    20,   10,   4),
    ("DRITTO_2",          0,   10,   5),
    ("SINISTRA_slight", -20,   10,   4),
    ("DRITTO_3",          0,   10,   5),
    ("DESTRA_sharp",     45,   10,   3),
    ("SINISTRA_sharp",  -45,   10,   3),
    ("STOP",            -90,   10,   4),
]

def compute_expected(angle_deg, thickness):
    """Replicate the mapping from dataset_generator.py"""
    speed_target = float(np.interp(thickness, [2, 14], [0.1, 1.0]))
    if abs(angle_deg) > 55:
        steering_target = 0.0  # STOP
    else:
        steering_target = float(np.interp(angle_deg, [-55, 55], [-1.0, 1.0]))
    return steering_target, speed_target

def preprocess_for_model(img):
    """Convert to grayscale, resize to 128x128, normalize, add batch+channel dims."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (128, 128))
    gray = gray.astype(np.float32) / 255.0
    return np.expand_dims(gray, axis=(0, -1))  # (1, 128, 128, 1)

def apply_faults(img, fault, noise_pct, stripe_width, stripe_angle):
    """Apply the requested fault(s) to the image."""
    out = img.copy()
    h, w, _ = out.shape
    center = (w // 2, h // 2)

    if fault in ("noise", "both"):
        out = add_noise(out, noise_pct)
    if fault in ("stripe", "both"):
        out = add_black_stripe(out, stripe_width, stripe_angle, center)
    return out

def predict_tflite(interpreter, input_details, output_details, img_input):
    """Run inference with TFLite interpreter. Returns (steer, speed)."""
    interpreter.set_tensor(input_details[0]['index'], img_input)
    interpreter.invoke()

# There are two outputs: steering and speed. Output order can vary, so match by name.
    out0 = interpreter.get_tensor(output_details[0]['index'])
    out1 = interpreter.get_tensor(output_details[1]['index'])

    name0 = output_details[0]['name'].lower()
    if 'steer' in name0:
        steer = float(out0[0][0])
        speed = float(out1[0][0])
    else:
        speed = float(out0[0][0])
        steer = float(out1[0][0])
    return steer, speed

def main():
    parser = argparse.ArgumentParser(description="Run easy path on the Bosch car.")
    parser.add_argument("--mode", choices=["clean", "dirty"], required=True,
                        help="Run with clean images or with fault-injected images.")
    parser.add_argument("--fault", choices=["noise", "stripe", "both"], default="noise",
                        help="Fault type (only used in dirty mode).")
    parser.add_argument("--noise-pct", type=float, default=10.0,
                        help="Percentage of pixels to corrupt (0-100).")
    parser.add_argument("--stripe-width", type=int, default=5,
                        help="Width in pixels of the occlusion stripe.")
    parser.add_argument("--stripe-angle", type=float, default=45.0,
                        help="Angle in degrees of the occlusion stripe.")
    parser.add_argument("--output-dir", type=str, default="results",
                        help="Directory where CSV and images will be saved.")
    parser.add_argument("--port", type=str, default="/dev/ttyACM0",
                        help="Serial port of the car.")
    parser.add_argument("--fps", type=int, default=10,
                        help="Frames per second to simulate.")
    parser.add_argument("--model-path", type=str, default="models/modello_bosch.tflite",
                        help="Path to the TFLite model.")
    parser.add_argument("--no-serial", action="store_true",
                        help="Skip serial communication (for testing on a machine without the car).")
    args = parser.parse_args()

    # Prepare output directories
    run_dir = os.path.join(args.output_dir, args.mode)
    img_dir = os.path.join(run_dir, "images")
    os.makedirs(img_dir, exist_ok=True)
    csv_path = os.path.join(run_dir, f"{args.mode}_run.csv")

    # Load TFLite model
    print(f"Caricamento modello TFLite da {args.model_path}...")
    interpreter = tf.lite.Interpreter(model_path=args.model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("Modello caricato con successo.")

    # Setup serial (only if not disabled)
    controller = None
    if not args.no_serial:
        print(f"Inizializzazione connessione seriale su {args.port}...")
        controller = SerialController(port=args.port)
    else:
        print("Modalità --no-serial attiva: nessun comando verrà inviato al veicolo.")

    # CSV setup
    csv_file = open(csv_path, "w", newline="")
    writer = csv.writer(csv_file)
    writer.writerow([
        "step", "frame", "label", "mode", "angle_deg", "thickness",
        "expected_steer", "expected_speed",
        "predicted_steer", "predicted_speed",
        "steer_error", "speed_error",
        "controller_speed", "controller_steer",
        "fault_type", "fault_params", "image_filename",
    ])

    try:
        if controller is not None:
            controller.connect()
            controller.set_power_state_on()
            time.sleep(1)

        for step_idx, (label, angle_deg, thickness, duration) in enumerate(EASY_PATH, start=1):
            print(f"\n--- Step {step_idx}/{len(EASY_PATH)}: {label} "
                  f"(angle={angle_deg}, thickness={thickness}, duration={duration}s) ---")

            num_frames = int(duration * args.fps)
            for frame_idx in range(1, num_frames + 1):
                start_time = time.time()
                
                # Generate clean image with random bg color to ensure variety
                bg_color = generate_colors(1)[0]
                clean_img = generate_image(angle_deg, thickness, bg_color)

                # Apply faults if needed
                if args.mode == "dirty":
                    used_img = apply_faults(
                        clean_img, args.fault,
                        args.noise_pct, args.stripe_width, args.stripe_angle
                    )
                    fault_type = args.fault
                    fault_params = (
                        f"noise_pct={args.noise_pct};"
                        f"stripe_w={args.stripe_width};"
                        f"stripe_a={args.stripe_angle}"
                    )
                else:
                    used_img = clean_img
                    fault_type = "none"
                    fault_params = ""

                # Save images to disk
                clean_name = f"step{step_idx:02d}_f{frame_idx:03d}_{label}_clean.png"
                cv2.imwrite(os.path.join(img_dir, clean_name), clean_img)
                if args.mode == "dirty":
                    dirty_name = f"step{step_idx:02d}_f{frame_idx:03d}_{label}_dirty.png"
                    cv2.imwrite(os.path.join(img_dir, dirty_name), used_img)
                    image_filename = dirty_name
                else:
                    image_filename = clean_name

                # Preprocess and predict
                img_input = preprocess_for_model(used_img)
                steer, speed = predict_tflite(
                    interpreter, input_details, output_details, img_input
                )

                # Expected values (ground truth from path params)
                exp_steer, exp_speed = compute_expected(angle_deg, thickness)
                steer_err = steer - exp_steer
                speed_err = speed - exp_speed

                print(f"Step {step_idx} Frame {frame_idx}/{num_frames} | "
                      f"Predicted: steer={steer:+.4f}, speed={speed:+.4f} | "
                      f"Expected: steer={exp_steer:+.4f}, speed={exp_speed:+.4f}")

                # Send commands to the car (if serial enabled)
                controller_steer = int(steer * 55)
                if label.startswith("STOP"):
                    controller_speed = 0
                    if controller is not None:
                        controller.set_brake(0)
                    else:
                        pass
                else:
                    controller_speed = int(speed * 500)
                    if controller is not None:
                        controller.set_speed(controller_speed)
                        controller.set_steer(controller_steer)

                # Write CSV row
                writer.writerow([
                    step_idx, frame_idx, label, args.mode, angle_deg, thickness,
                    f"{exp_steer:.4f}", f"{exp_speed:.4f}",
                    f"{steer:.4f}", f"{speed:.4f}",
                    f"{steer_err:.4f}", f"{speed_err:.4f}",
                    controller_speed, controller_steer,
                    fault_type, fault_params, image_filename,
                ])
                csv_file.flush()

                # Control FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, (1.0 / args.fps) - elapsed)
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\nInterrotto dall'utente.")
    except Exception as e:
        print(f"\nErrore durante l'esecuzione: {e}")
    finally:
        print("\nChiusura connessione e spegnimento motori...")
        try:
            if controller is not None and controller.is_connected():
                controller.set_speed(0)
                controller.set_steer(0)
                controller.disconnect()
        except Exception:
            pass
        csv_file.close()
        print(f"Risultati salvati in: {csv_path}")
        print(f"Immagini salvate in:  {img_dir}")

if __name__ == "__main__":
    main()
