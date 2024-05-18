from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2  # For video frame processing
import tensorflow as tf  # For loading the trained model
import numpy as np  # For array manipulation
import os
import numpy as np
from typing import List
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv3D, LSTM, Dense, Dropout, Bidirectional, MaxPool3D, Activation, Reshape, SpatialDropout3D, BatchNormalization, TimeDistributed, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler


app = Flask(__name__)
print('cors')
CORS(app,resources={r"/process_video": {"origins": "http://localhost:3000"}})
print('completed')
vocab = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789 "]
char_to_num = tf.keras.layers.StringLookup(vocabulary=vocab, oov_token="")
num_to_char = tf.keras.layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), oov_token="", invert=True
)

def load_model():
    model = Sequential()
    model.add(Conv3D(128, 3, input_shape=(75,46,140,1), padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPool3D((1,2,2)))

    model.add(Conv3D(256, 3, padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPool3D((1,2,2)))

    model.add(Conv3D(75, 3, padding='same'))
    model.add(Activation('relu'))
    model.add(MaxPool3D((1,2,2)))

    model.add(TimeDistributed(Flatten()))

    model.add(Bidirectional(LSTM(128, kernel_initializer='Orthogonal', return_sequences=True)))
    model.add(Dropout(.5))

    model.add(Bidirectional(LSTM(128, kernel_initializer='Orthogonal', return_sequences=True)))
    model.add(Dropout(.5))

    model.add(Dense(char_to_num.vocabulary_size()+1, kernel_initializer='he_normal', activation='softmax'))
    return model

def load_weights(model):
    weights_path = os.path.join('/Users/srinivasreddyaedula/Downloads/models - checkpoint 96', 'checkpoint')  # Path to the saved weights file
    model.load_weights(weights_path)
    return model
try:
    model = load_model()
    model = load_weights(model)

# Model loaded successfully
    print("Model loaded successfully.")

except OSError as e:
    # Handle the case where the file cannot be opened or is not a valid model file
    print("Error loading model file:", e)

except Exception as e:
    # Handle any other exceptions that might occur during model loading
    print("An error occurred during model loading:", e)

@app.route('/process_video', methods=['POST'])
def process_video():
    # Get video data from the request
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video file uploaded'})
    
    video_data = request.files['video']
    print('video received')
    # Process video frames
    video_path = '/Users/srinivasreddyaedula/Backend' + video_data.filename
    video_data.save(video_path)
    frames = load_video((video_path))
    ground_truth=load_ground_truth_labels('/Users/srinivasreddyaedula/Downloads/data 3')
    # Make predictions using the model
    predictions = model.predict(tf.expand_dims(frames, axis=0))
    # print(ground_truth)
    # Convert predictions into sentences
    sentences = generate_sentences(predictions)
    accuracy = calculate_accuracy(ground_truth,sentences)
    print(accuracy)
    # Return sentences and accuracy
    return jsonify({'sentences': sentences, 'accuracy': accuracy})

    

# def process_video_frames(path):
#     # Process video frames here using OpenCV or any other library
#     # Convert frames into a format suitable for input to the model
#     path = bytes.decode(path.numpy())
#     file_name = path.split('/')[-1].split('.')[0]
#     # File name splitting for windows
#     #file_name = path.split('\\')[-1].split('.')[0]
#     video_path = os.path.join('/content/drive/MyDrive/data 3','s1',f'{file_name}.mpg')
#     alignment_path = os.path.join('/content/drive/MyDrive/data 3','alignments','s1',f'{file_name}.align')
#     frames = load_video(video_path)
#     alignments = load_alignments(alignment_path)


#     return frames, alignments
# def load_alignments(path:str) -> List[str]:
#     with open(path, 'r') as f:
#         lines = f.readlines()
#     tokens = []
#     for line in lines:
#         line = line.split()
#         if line[2] != 'sil':
#             tokens = [*tokens,' ',line[2]]
#     return char_to_num(tf.reshape(tf.strings.unicode_split(tokens, input_encoding='UTF-8'), (-1)))[1:]
def load_video(path:str) -> List[float]:

    cap = cv2.VideoCapture(path)
    frames = []
    for _ in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
        ret, frame = cap.read()
        frame = tf.image.rgb_to_grayscale(frame)
        frames.append(frame[190:236,80:220,:])
    cap.release()

    mean = tf.math.reduce_mean(frames)
    std = tf.math.reduce_std(tf.cast(frames, tf.float32))
    return tf.cast((frames - mean), tf.float32) / std

def generate_sentences(predictions):
    # Convert model predictions into sentences
    decoded = tf.keras.backend.ctc_decode(predictions, input_length=[75], greedy=True)[0][0].numpy()
    
    vocab = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789"]
    char_to_num = tf.keras.layers.StringLookup(vocabulary=vocab, oov_token="")
    num_to_char = tf.keras.layers.StringLookup(vocabulary=char_to_num.get_vocabulary(), oov_token="", invert=True)
    print(num_to_char(tf.constant([ 2])).numpy())
    sentences = []
    sentence_str=""
    for sentence in decoded:
        # print(sentence)
        for word in sentence:
            
            if 0 <= word < len(vocab) :
                # print(word)
    
                character_numpy=num_to_char(tf.constant(word)).numpy()
                for char in character_numpy:
                    # print(char)
                    sentence_str += chr(char)
            else:
                sentence_str +=' '
            # print(sentence_str)
        sentences.append(sentence_str)
        # print(sentences)
    return sentences
def load_ground_truth_labels(dataset_path):
    # print(dataset_path)
    ground_truth = {}
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith('.align'):
                video_id = file.split('.')[0]
                align_path = os.path.join(root, file)
                with open(align_path, 'r') as align_file:
                    align_data = align_file.read().strip().split('\n')
                    transcript = ' '.join(line.split()[-1] for line in align_data)
                    ground_truth[video_id] = transcript
    return ground_truth
def calculate_accuracy(ground_truth, prediction):
    print(prediction)
    max_letters=0
    total_letters = 0
    print(ground_truth)
    for video_id, truth in ground_truth.items():
        # Remove certain tokens from ground truth (e.g., 'sil')
        print('for')
        accurate_letters = 0
        total_letters=0
        truth_tokens = truth.split()
        truth_tokens = [token for token in truth_tokens if token != 'sil']
        truth_modified = ' '.join(truth_tokens)
        pred = prediction[0] 
       
        pred_stripped = pred.strip() 
        print('efg')
        for truth_char, pred_char in zip(truth_modified, pred_stripped):
            print('abc')
            if truth_char == pred_char:
                accurate_letters += 1
            total_letters += 1
        max_letters=max(max_letters,accurate_letters)
        print(total_letters)
    if(total_letters==0):
        return 0
    accuracy = max_letters / total_letters
    
    return accuracy*100

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)