import os
import time
import tensorflow as tf
import random

from src.utils.serial_controller import SerialController
from src.utils.images_generator import generate_image, generate_colors

def main():
    # Setup Modello
    model_path = os.path.join(os.path.abspath("./models/"), "modello_bosch.h5")
    print(f"Caricamento modello da {model_path}...")
    try:
        model = tf.keras.models.load_model(model_path, compile=False)
        print("Modello caricato con successo.")
    except Exception as e:
        print(f"Errore nel caricamento del modello: {e}")
        return

    # Setup Seriale
    # NOTA: Cambiare "/dev/ttyACM0" con la porta seriale corretta per il proprio sistema
    PORTA_SERIALE = "/dev/ttyACM0"
    print(f"Inizializzazione connessione seriale su {PORTA_SERIALE}...")
    controller = SerialController(port=PORTA_SERIALE)
    
    try:
        controller.connect()
        controller.set_power_state_on()
        time.sleep(1)

        for iterazione in range(5): # Eseguiamo la pipeline 5 volte come esempio
            print(f"\n--- Iterazione {iterazione + 1} ---")

            # Generazione immagine
            angle_deg = random.uniform(-55, 55) # Esempio: angolo casuale tra -45 e 45 gradi
            thickness = random.randint(2, 14) # Esempio: spessore casuale            
            
            # Genera un colore di sfondo
            # Nota: generate_colors ritorna una lista, prendiamo il primo elemento
            bg_color = generate_colors(1)[0] 
            
            print(f"Generazione immagine con Angolo: {angle_deg:.2f}, Spessore: {thickness}, Colore: {bg_color}")
            image = generate_image(angle_deg, thickness, bg_color)
            
            # Pre-elaborazione immagine per il modello
            # Assicurati che l'immagine sia nel formato atteso dal modello (es. float32, normalizzata, batch_size)
            image_processed = tf.cast(image, tf.float32) / 255.0
            image_processed = tf.expand_dims(image_processed, axis=0) # Aggiunge dimensione batch

            # Predizione del modello
            predictions = model.predict(image_processed)
            speed, steer = predictions[0] # Assumendo che il modello restituisca speed e steer

            print(f"Predizione Modello: Velocità = {speed:.2f}, Sterzo = {steer:.2f}")

            # Invio comandi al controller seriale
            # Conversione dei valori predetti in un range appropriato per il controller
            controller_speed = int(speed * 500) 
            controller_steer = int(steer * 55) 

            controller.set_speed(controller_speed)
            controller.set_steer(controller_steer)
            
            time.sleep(2) # Pausa tra un'iterazione e l'altra

    except KeyboardInterrupt:
        print("\nInterrotto dall'utente.")
    except Exception as e:
        print(f"\nErrore durante l'esecuzione: {e}")
    finally:
        print("\nChiusura connessione e spegnimento motori...")
        if controller.is_connected():
            controller.set_speed(0)
            controller.set_steer(0)
            controller.disconnect()


if __name__ == "__main__":
    main()
