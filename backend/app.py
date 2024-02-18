from reportGenerator.reportGenerator import reportGenerator
from videoProcessing.videoProcessor import videoProcessor
import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(reportGenerator, url_prefix='/reportGenerator')
app.register_blueprint(videoProcessor, url_prefix='/videoProcessor')


@app.route('/videoParser', methods=['POST'])
def video_parser():
    home = os.path.expanduser('~')
    downloads_path = os.path.join(home, 'Downloads')
    webm_file_path = downloads_path + "/" + "recorded-video.webm"

    if not webm_file_path or not os.path.exists(webm_file_path):
        return jsonify({"error": "Invalid or missing file path"}), 400

    # Set the paths for output files
    output_mp4_path = './result.mp4'
    output_wav_path = './result.wav'
    
    try:
        # Convert webm to mp4
        subprocess.run(['ffmpeg', '-y','-i', webm_file_path, '-c:v', 'copy', '-c:a', 'aac', output_mp4_path], check=True)
        
        # Extract audio to wav
        subprocess.run(['ffmpeg', '-y', '-i', webm_file_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', output_wav_path], check=True)
        return jsonify({"message": "Conversion successful"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "A processing error occurred"}), 500


if __name__ == '__main__':
    app.run(debug=True)