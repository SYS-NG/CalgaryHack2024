import os
import cv2
import dlib
import time
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from deepface import DeepFace 
from scipy.signal import find_peaks
from collections import Counter
from flask import Blueprint, request, jsonify
from flask_cors import CORS

VERBOSE = False

CENTER = "C"
LEFT   = "L"
RIGHT  = "R"

# Create a blueprint for the videoProcessor
videoProcessor = Blueprint('VideoProcessor', __name__)
CORS(videoProcessor)

class VideoProcessor():
    def __init__(self, video_path):

        if os.path.exists(video_path):
            pass
        else:
            print(f"Error: Video file '{video_path}' not found.")

        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.face_detector      = dlib.get_frontal_face_detector()
        self.landmark_predictor = dlib.shape_predictor("./videoProcessing/shape_predictor_68_face_landmarks.dat")

        self.fps = 0
        self.total_frames = 0
        self.timeframe = 0

        # Emotion Model
        # Load the pre-trained emotion detection model
        self.model = DeepFace.build_model("Emotion")

        # Define emotion labels
        self.emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

        # Set mode based on the video source
        if isinstance(self.video_path, int):
            self.mode = "camera"
        else:
            self.mode = "file"
        
        # Extract info from video
        if self.mode == "file":
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.timeframe = self.total_frames / self.fps

            print(f"Video FPS: {self.fps}, Total frames: {self.total_frames}, Timeframe: {self.timeframe} seconds.")

        if self.mode == "camera":
            # Setup showing the video size
            cv2.namedWindow("Eye", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Binary_Threshold", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
        
        # Create storage of metrics
        self.gaze_directions         = []
        self.eye_width_height_ratios = []
        self.expressions             = []
    
    def get_metrics(self):
        return {
            "gaze_directions": self.gaze_directions,
            "eye_width_height_ratios": self.eye_width_height_ratios,
            "expressions": self.expressions,
            "timeframe": self.timeframe,
            "fps": self.fps,
            "total_frames": self.total_frames,
        }
    
    def blink_detection(self, landmarks):

        # get the pixels corresponding to the top and bottom of the eye
        eye_top = landmarks.part(38).y
        eye_bot = landmarks.part(40).y

        # get the pixels corresponding to the left and right of the eye
        eye_left  = landmarks.part(36).x
        eye_right = landmarks.part(39).x

        # Calculate the width and height of the eye
        eye_width  = eye_right - eye_left
        eye_height = eye_bot - eye_top

        # Calculate the eye width to height ratio
        eye_width_height_ratio = eye_width / eye_height

        return eye_width_height_ratio

    def gaze_detection(self, eye_roi):

        gaze_direction = CENTER # Default gaze direction

        rows, cols, _ = eye_roi.shape
        gray_roi = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY)

        # Thresholding the eye region for pupil detection
        threshold = 47
        _,  binary_roi = cv2.threshold(gray_roi, threshold, 255, cv2.THRESH_BINARY_INV)

        # Based on the thresholded image, find the contours to define the pupil
        contours, _ = cv2.findContours(binary_roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Sort the contours based on the area, and get the largest contour
        # This reduces the impact of noise in the image
        contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)

        if len(contours) > 0:
            cnt = contours[0]

            # Calculate the centroid of the contour
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.circle(eye_roi, (cX, cY), 2, (0, 0, 255), -1)

                # define left and right boundaries of the eye region
                left_bound  = cols*3//7
                right_bound = cols*5//7

                # Draw verticle lines at 3/5 and 4/5 of the eye region
                cv2.line(eye_roi, (left_bound, 0), (left_bound, rows), (0, 255, 0), 1)
                cv2.line(eye_roi, (right_bound, 0), (right_bound, rows), (0, 255, 0), 1)

                # Split the region of interest into 3 parts
                # Based on the centroid of the contour
                # detect the eye movement: left, right, or center
                if cX < left_bound:
                    gaze_direction = LEFT
                elif cX > right_bound:
                    gaze_direction = RIGHT
                else:
                    gaze_direction = CENTER
        
        return gaze_direction, binary_roi
    
    def get_eye_roi(self, landmarks, frame):
        # Calculate pixels corresponding to left and right eye 
        # from the facial landmarks
        # Left eye
        LE_top   = landmarks.part(37).y
        LE_bot   = landmarks.part(41).y
        LE_left  = landmarks.part(36).x
        LE_right = landmarks.part(39).x

        # Right eye
        RE_top   = landmarks.part(43).y
        RE_bot   = landmarks.part(47).y
        RE_left  = landmarks.part(42).x
        RE_right = landmarks.part(45).x

        # Region of interest for left and right eye
        left_eye_roi  = frame[LE_top:LE_bot, LE_left:LE_right]
        right_eye_roi = frame[RE_top:RE_bot, RE_left:RE_right]

        return left_eye_roi, right_eye_roi

    def preprocess_face_roi_for_emotion_detection(self, face_roi):
        # Resize the face ROI to match the input shape of the model
        resized_face = cv2.resize(face_roi, (48, 48), interpolation=cv2.INTER_AREA)
        print(resized_face.shape)
        # Normalize the resized face ROI
        normalized_face = resized_face / 255.0
        print(normalized_face.shape)
        # Reshape the image to match the input shape of the model
        preprocessed_face = normalized_face.reshape(1, 48, 48, 3)

        return preprocessed_face 

    def detect_emotion(self, preprocessed_face):
        # Get the emotion prediction
        emotion_prediction = self.model.predict(preprocessed_face)
        # Get the emotion label
        emotion_label = self.emotion_labels[np.argmax(emotion_prediction)]

        return emotion_label


    def process(self):
        
        frame = None

        # Declare variables for storing the gaze direction and eye width to height ratio
        gaze_direction         = CENTER
        eye_width_height_ratio = 0
        emotion_label          = self.emotion_labels[-1]

        # Declare variables for storing the left and right eye region and threshold
        eye_roi  = None
        binary_roi    = None

        start_time = time.time()
        skip_n_frames  = 2
        skipped_frames = 0
        num_frames     = 0

        while True:
            ret, frame = self.cap.read()
            if skipped_frames < skip_n_frames:
                skipped_frames += 1
                continue

            print(num_frames)
            num_frames += 1
            skipped_frames = 0

            if ret is False:
                break
            
            if self.mode == "camera":
                self.total_frames += 1
            
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector(gray_frame)

            for face in faces:
                landmarks  = self.landmark_predictor(gray_frame, face)

                # Get the region of interest for the face and the eyes
                # Include a margin around the face
                face_top    = face.top() - 50
                face_bottom = face.bottom() + 50
                face_left   = face.left() - 50
                face_right  = face.right() + 50
                face_roi    = gray_frame[face_top:face_bottom, face_left:face_right]

                # face_roi   = gray_frame[face.top():face.bottom(), face.left():face.right()]
                eye_roi, _ = self.get_eye_roi(landmarks, frame) 

                #=========================
                # Blink detection
                #=========================
                eye_width_height_ratio = self.blink_detection(landmarks)

                #=========================
                # Pupil detection
                #========================= 
                gaze_direction, binary_roi = self.gaze_detection(eye_roi)

                #=========================
                # Emotion detection
                #=========================
                analyzed_face = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)
                emotion_label = analyzed_face[0]["dominant_emotion"]

                # Add box and label to the frame
                cv2.rectangle(frame, (face_left, face_top), (face_right, face_bottom), (0, 255, 0), 2)
                cv2.putText(frame, emotion_label, (face.left(), face.top()), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                break


            # Show the video feed if the mode is camera
            if self.mode == "camera":
                if frame is not None:
                    cv2.imshow("Frame", frame)
                if binary_roi is not None:
                    cv2.imshow("Binary_Threshold", binary_roi)
                if eye_roi is not None:
                    cv2.imshow("Eye", eye_roi)

                # Print the gaze direction
                if VERBOSE:
                    if gaze_direction == LEFT:
                        print("Looking left")
                    elif gaze_direction == RIGHT:
                        print("Looking right")
                    else:
                        print("Looking center") 
            
            # Add metrics extracted from frame into storage
            self.gaze_directions.append(gaze_direction)
            self.eye_width_height_ratios.append(eye_width_height_ratio)
            self.expressions.append(emotion_label)

            key = cv2.waitKey(30)
            if key == 27:
                break
        
        if self.mode == "camera":
            self.timeframe = time.time() - start_time
            self.fps = self.total_frames // self.timeframe
            cv2.destroyAllWindows()
        
        # Return the extracted metrics, as a dictionary of lists of metrics

        return self.get_metrics()

def process_gaze_directions(gaze_directions):
    # get fraction spent looking in each direction
    gaze_directions_count = Counter(gaze_directions)    

    # Store fraction in dictionary
    gaze_fractions = {gaze_direction: count / len(gaze_directions) for gaze_direction, count in gaze_directions_count.items()}

    # Calculate individual fractions
    # total_gaze  = len(gaze_directions)
    # left_gaze   = gaze_directions_count["L"]
    # right_gaze  = gaze_directions_count["R"]
    # center_gaze = gaze_directions_count["C"]

    # # calculate the fraction of time spent looking in each direction
    # left_gaze_fraction   = left_gaze / total_gaze
    # right_gaze_fraction  = right_gaze / total_gaze
    # center_gaze_fraction = center_gaze / total_gaze

    # return left_gaze_fraction, right_gaze_fraction, center_gaze_fraction

    return gaze_fractions


def process_eye_width_height_ratios(eye_width_height_ratios, timeframe):
    # Extracts the peaks from the eye_width_height_ratios
    peaks, _ = find_peaks(eye_width_height_ratios, height=5)
    # Get number of peaks which indicates the number of blinks
    num_blinks = len(peaks)

    # Only show plot if specified
    if VERBOSE:
        # plot the extracted metrics eye_width_height_ratios
        plt.plot(eye_width_height_ratios)
        # plot the peaks overlaid on the eye_width_height_ratios
        plt.plot(peaks, [eye_width_height_ratios[i] for i in peaks], "x")
        # Title
        plt.title("Eye Width to Height Ratios, blinks: " + str(num_blinks))
        plt.show()

    blinks_per_minute = num_blinks / timeframe * 60

    return blinks_per_minute

def process_expressions(expressions):
    # Get the fraction of time spent on each expression
    expression_fractions = {
        "angry": 0,
        "disgust": 0,
        "fear": 0,
        "happy": 0,
        "sad": 0,
        "surprise": 0,
        "neutral": 0
    }
    expression_count = Counter(expressions)
    total_expressions = len(expressions)
    for expression, count in expression_count.items():
        expression_fractions[expression] = count / total_expressions
    return expression_fractions

def localProcessVideo(video_path):
    vid_processor     = VideoProcessor(video_path)
    extracted_metrics = vid_processor.process()

    # Process the extracted metrics: eye_width_height_ratios
    blinks_per_minute =  process_eye_width_height_ratios(extracted_metrics["eye_width_height_ratios"], extracted_metrics["timeframe"])

    # Process the extracted metrics: gaze_directions
    gaze_fractions = process_gaze_directions(extracted_metrics["gaze_directions"])
    prominent_gaze = max(gaze_fractions, key=gaze_fractions.get)

    # Process the extracted metrics: expressions
    expression_fractions = process_expressions(extracted_metrics["expressions"])
    prominent_expression = max(expression_fractions, key=expression_fractions.get)

    # return dictionary of processed metrics
    results = {
        "blinks_per_minute": blinks_per_minute,
        "gaze_fractions": gaze_fractions,
        "prominent_gaze": prominent_gaze,
        "expression_fractions": expression_fractions,
        "prominent_expression": prominent_expression,
    }

    return results

@videoProcessor.route('/processVideo', methods=['POST'])
def processVideo():
    video_path = request.json['video_path']
    vid_processor     = VideoProcessor(video_path)
    extracted_metrics = vid_processor.process()

    # Process the extracted metrics: eye_width_height_ratios
    blinks_per_minute =  process_eye_width_height_ratios(extracted_metrics["eye_width_height_ratios"], extracted_metrics["timeframe"])

    # Process the extracted metrics: gaze_directions
    gaze_fractions = process_gaze_directions(extracted_metrics["gaze_directions"])
    prominent_gaze = max(gaze_fractions, key=gaze_fractions.get)

    # Process the extracted metrics: expressions
    expression_fractions = process_expressions(extracted_metrics["expressions"])
    prominent_expression = max(expression_fractions, key=expression_fractions.get)

    # return dictionary of processed metrics
    results = {
        "blinks_per_minute": blinks_per_minute,
        "gaze_fractions": gaze_fractions,
        "prominent_gaze": prominent_gaze,
        "expression_fractions": expression_fractions,
        "prominent_expression": prominent_expression,
    }

    return results
if __name__ == "__main__":
    print("Processing video")
    # localProcessVideo('C:\\Users\\szeyu\\Documents\\GitHub\\CalgaryHack2024\\data\\test.mp4')
    _ = localProcessVideo(1)
    print("Video processed")
