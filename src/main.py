import sounddevice as sd
import numpy as np
import wave
import keyboard
import speech_recognition as sr
import datetime

# Paramètres d'enregistrement
RATE = 44100  # Taux d'échantillonnage
CHANNELS = 1  # Mono
PHRASE_TO_DETECT = "ok  tartine"


def start_recording():
    """Enregistre l'audio et arette avec Espace."""
    print("Enregistrement en cours... Appuyez sur 'Espace' pour arrêter.")

    # Generate a unique filename based on the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_FILE = f"enregistrement_{timestamp}.wav"

    audio_frames = []

    # Fonction de callback pour capturer les frames audio
    def callback(indata, frames, time, status):
        audio_frames.append(indata.copy())

    # Démarrer l'enregistrement avec un InputStream
    with sd.InputStream(samplerate=RATE, channels=CHANNELS, callback=callback, dtype='int16'):
        # Attendre que l'utilisateur appuie sur 'Espace' pour arrêter l'enregistrement
        keyboard.wait('space')
        print("Enregistrement terminé.")

    # Convertir les frames en un tableau numpy
    audio_data = np.concatenate(audio_frames, axis=0)

    # Sauvegarder dans un fichier WAV
    try:
        with wave.open(OUTPUT_FILE, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # Taille d'échantillon (16 bits -> 2 bytes)
            wf.setframerate(RATE)
            wf.writeframes(audio_data.tobytes())
        print(f"Enregistrement sauvegardé dans {OUTPUT_FILE}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement dans le fichier : {e}")

    # Lecture de l'enregistrement
    print("Nous allons maintenant écouter votre enregistrement")
    sd.play(audio_data, RATE)
    sd.wait()  # Attendre que la lecture soit terminée
    print("Fin de la lecture")


def listen_for_phrase():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print(f"En attente de la phrase '{PHRASE_TO_DETECT}' pour démarrer l'enregistrement...")

    while True:
        with mic as source:
            # Ajuster le bruit ambiant et écouter
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            # Reconnaître la phrase
            text = recognizer.recognize_google(audio, language="fr-FR")
            print(f"Phrase entendue : {text}")

            # Vérifier si la phrase détectée correspond à celle que nous attendons
            if PHRASE_TO_DETECT.lower() in text.lower():
                print("Phrase de déclenchement détectée !")
                start_recording()
                break  # Arrêter après l'enregistrement

        except sr.UnknownValueError:
            print("Aucune phrase reconnue, réessayez...")
        except sr.RequestError:
            print("Erreur avec le service de reconnaissance vocale.")


# Démarrer l'écoute de la phrase
listen_for_phrase()
