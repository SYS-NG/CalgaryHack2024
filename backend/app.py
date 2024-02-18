from flask import Flask, request, jsonify
from flask_cors import CORS
from reportGenerator.reportGenerator import reportGenerator
from videoProcessing.videoProcessor import videoProcessor

app = Flask(__name__)
CORS(app)

app.register_blueprint(reportGenerator, url_prefix='/reportGenerator')
app.register_blueprint(videoProcessor, url_prefix='/videoProcessor')

if __name__ == '__main__':
    app.run(debug=True)