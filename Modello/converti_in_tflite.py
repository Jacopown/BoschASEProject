import tensorflow as tf

# caricamento del mio file .h5
model = tf.keras.models.load_model('modello_bosch.h5', compile=False)

# converto il tutto in formato h5
converter = tf.lite.TFLiteConverter.from_keras_model(model)
# Ottimizzazione
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

#salva il mio nuovo file 
with open('modello_bosch.tflite', 'wb') as f:
    f.write(tflite_model)

print("Conversione completata! Ora hai il file 'modello_bosch.tflite'")]
