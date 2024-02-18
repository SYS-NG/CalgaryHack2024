import tensorflow as tf
import librosa
import numpy as np
from pydub import AudioSegment, effects
import noisereduce as nr
import matplotlib.pyplot as plt
import soundfile as sf
import os

def get_model():
    # Load first model
    saved_model_path = './ser/ser_model.json'
    saved_weights_path = './ser/ser_model_weights.h5'

    with open(saved_model_path , 'r') as json_file:
        json_savedModel = json_file.read()

    model = tf.keras.models.model_from_json(json_savedModel)  # Assuming json_savedModel is defined
    model.load_weights(saved_weights_path)
    model.compile(loss='categorical_crossentropy', 
                    optimizer='RMSProp', 
                    metrics=['categorical_accuracy'])
    
    return model
    

def preprocess(file_path):
    total_length = 173056
    frame_length = 2048
    hop_length = 512

    _, sr = librosa.load(path = file_path, sr = None)
    rawsound = AudioSegment.from_file(file_path, duration = None) 
    normalizedsound = effects.normalize(rawsound, headroom = 5.0) 
    normal_x = np.array(normalizedsound.get_array_of_samples(), dtype = 'float32')
    xt, index = librosa.effects.trim(normal_x, top_db=30)

    try:
        padded_x = np.pad(xt, (0, total_length-len(xt)), 'constant')
    except:
        print("error")
        print("file:", file)
        return None
    # normal_x = np.array(normalizedsound.get_array_of_samples(), dtype = 'float32') 
    # Noise reduction                  
    final_x = nr.reduce_noise(padded_x, sr=sr)
    final_x = np.nan_to_num(final_x)
    final_x = np.where(np.isfinite(final_x), final_x, 0)
        
    f1 = librosa.feature.rms(y=final_x, frame_length=frame_length, hop_length=hop_length, center=True, pad_mode='reflect').T # Energy - Root Mean Square
    f2 = librosa.feature.zero_crossing_rate(y=final_x, frame_length=frame_length, hop_length=hop_length,center=True).T # ZCR
    f3 = librosa.feature.mfcc(y=final_x, sr=sr, S=None, n_mfcc=13, hop_length = hop_length).T # MFCC   
    X = np.concatenate((f2, f1, f3), axis = 1)
    
    X_3D = np.expand_dims(X, axis=0)
    
    return X_3D

def main_method():
    FILE_PATH = './result.wav'
    SAMPLE_RATE = 24414  # Same as RATE in the original script
    CHUNK_DURATION = 1  # Duration of chunks to analyze (in seconds)
    emo_list = ["neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"]
    model = get_model()

    # Function to split audio file into 1-second chunks and process each chunk
    def process_audio_file(file_path):
        total_predictions = []  # List to store predictions for each chunk
        
        # Load audio file
        audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)
        
        # Calculate the number of chunks
        num_chunks = int(np.floor(len(audio) / sr / CHUNK_DURATION))
        
        for i in range(num_chunks):
            # Extract the chunk
            start_sample = i * sr * CHUNK_DURATION
            end_sample = start_sample + sr * CHUNK_DURATION
            chunk = audio[start_sample:end_sample]
            
            # Save chunk to temporary WAV file
            chunk_file_path = 'temp_chunk.wav'
            sf.write(chunk_file_path, chunk, sr)
            
            # Preprocess the chunk
            x = preprocess(chunk_file_path)  # Ensure your preprocess function is adapted for handling the chunk
            
            # Model's prediction => an 8 emotion probabilities array
            predictions = model.predict(x, use_multiprocessing=True)
            pred_list = list(predictions)
            pred_np = np.squeeze(np.array(pred_list).tolist(), axis=0)  # Simplify the predictions list
            total_predictions.append(pred_np)
            
            # Optionally, visualize the prediction for each chunk
            # fig = plt.figure(figsize=(10, 2))
            # plt.bar(emo_list, pred_np, color='darkturquoise')
            # plt.ylabel("Probability (%)")
            # plt.show()
            
            # Print the predominant emotion for the chunk
            max_emo = np.argmax(predictions)
            print('max emotion for chunk:', emo_list[max_emo])
            print(100 * '-')
        
        # After processing all chunks, calculate and visualize the mean prediction
        mean_predictions = np.mean(np.array(total_predictions), axis=0)
        return mean_predictions
        fig = plt.figure(figsize=(10, 5))
        plt.bar(emo_list, mean_predictions, color='indigo')
        plt.ylabel("Mean probability (%)")
        plt.title("Overall Emotion Distribution")
        plt.show()

    # Call the function to process the audio file
    weights = process_audio_file(FILE_PATH)

    return weights