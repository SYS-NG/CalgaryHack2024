import os
import json
import math
import openai
from flask import Blueprint, request, jsonify
from flask_cors import CORS

# Flask Blueprint
reportGenerator = Blueprint('reportGenerator', __name__)
CORS(reportGenerator)

openai.api_key = os.environ.get('OPENAI_API_KEY')
client = openai.OpenAI()

class Report:
    def __init__(self, metrics):

        # Sample Metrics
        # metrics = {
        #     "blinks_per_minute": blinks_per_minute,
        #     "gaze_fractions": gaze_fractions,
        #     "prominent_gaze": prominent_gaze,
        #     "expression_fractions": expression_fractions,
        #     "prominent_expression": prominent_expression,
        # }

        self.score   = 0
        self.metrics = metrics
        self.result  = {}
        self.scores  = {
            # Attentiveness
            "Attentiveness_Score": 0,
            "Attentiveness_feedback": "",
            "Attentiveness_Stars": 0,
            "Attentiveness_Ideal_Score": 100,
            # Confidence
            "Confidence_Score": 0,
            "Confidence_feedback": "",
            "Confidence_Stars": 0,
            "Confidence_Ideal_Score": 100,
            # Empathy
            "Empathy_Score": 0,
            "Empathy_feedback": "",
            "Empathy_Stars": 0,
            "Empathy_Ideal_Score": 100,
            # Socialability
            "Socialability_Score": 0,
            "Socialability_feedback": "",
            "Socialability_Stars": 0,
            "Socialability_Ideal_Score": 100,
            # Expressiveness
            "Expressiveness_Score": 0,
            "Expressiveness_feedback": "",
            "Expressiveness_Stars": 0,
            "Expressiveness_Ideal_Score": 100,
        }
        self.scoreFuncs = [
            self.scoreConfidence,
            self.scoreAttentiveness,
            self.scoreEmpathy,
            self.scoreSocialability,
            self.scoreExpressiveness 
        ]

        self.gptPrompt = """
            You are a helpful feedback generator.
            You are helping a user generate feedback based on some metrics on their interaction.
            Feedback could be in these areas: Confidence, Attentiveness, Empathy, Socialability, Expressiveness.
            The metrics are based on the user's blinks per minute, gaze fractions, prominent gaze, expression fractions, and prominent expression.
            Attentiveness is based on how long user's gaze is centered.
            Confidence is based on the user's blink rate and gaze fractions. Blinking too much or too little can affect confidence. Looking around too much also indicates low confidence.
            Empathy is based on the user's expression fractions. Positive expressions like happiness, surprise, and sadness are considered connecting expressions, while negative expressions like anger, disgust, and fear are considered disconnecting expressions.
            Socialability is based on the user's gaze fractions and expression fractions. A high center gaze and positive expressions indicate high socialability.
            Expressiveness is based on the user's expression fractions. A high fraction of neutral expressions indicates low expressiveness.
             
            Feedback should be contructive and helpful. Especially if their scores are not ideal. Also take into account the provided metrics.
            Do NOT contradict in the feedbacks. Keep consistent critisim and praise.
            Scores that are close to the ideal score should be praised. Scores that are far from the ideal score should be critisized.
            A difference of 5 or less from the ideal score should be praised with 5 stars, with some feedback if possible.
            A difference of 5-20 should be praised with 4 stars, with some constructive feedback.
            A difference of 20-40 should be praised with 3 stars, with fair critism and encourage.
            A difference of 40-60 should be evaluated with 2 stars, please provide advice on how to improve.
            A difference of 60-80 should be critisized with 1 star, please provide in advice on how to improve.
            A difference of 80 or more should be critisized with 0 stars, much needed advice.
             
            Generate each feedback as a json object with the following keys: Confidence_feedback, Attentiveness_feedback, Empathy_feedback, Socialability_feedback, Expressiveness_feedback.
        """

        self.ideal_scores = {
            "Confidence_Score": 100,
            "Attentiveness_Score": 100,
            "Empathy_Score": 100,
            "Socialability_Score": 100,
            "Expressiveness_Score": 100 
        }

    def scoreConfidence(self):

        #================================================================================================
        blinks_per_minute = self.metrics["blinks_per_minute"]

        # Score the blink rate
        # 0 - 10: low blink rate
        # 11 - 20: Normal blink rate
        # 21 - 30: High blink rate
        # 31+: Very high blink rate
        # The score is gaussian distributed around the ideal blink rate of 15-20 blinks per minute

        # Define the ideal blink rate and the standard deviation
        ideal_blink_rate = 17.5  # Midpoint of 15-20
        std_dev = 8  # This can be adjusted depending on how quickly you want the score to decrease

        # Calculate the score using the Gaussian function
        blink_score = math.exp(-0.5 * ((blinks_per_minute- ideal_blink_rate) / std_dev) ** 2)

        #================================================================================================
        gaze_fractions   = self.metrics["gaze_fractions"]
        center_gaze      = gaze_fractions["C"]

        if center_gaze > 0.55:
            gaze_score = 1
        else:
            # Quadratic decrease for x <= 10
            # Adjust the coefficients as needed
            gaze_score -(center_gaze - 0.55) ** 2 + 1
        
        #================================================================================================
        # Confidence score is the weighted average of the blink score and the gaze score
        score = int((blink_score * 0.3 + gaze_score * 0.7) * 100)

        # Store the score in the scores dictionary
        self.scores["Confidence_Score"] = score

    def scoreAttentiveness(self):
        #================================================================================================
        # Based on gaze fractions
        gaze_fractions   = self.metrics["gaze_fractions"]
        center_gaze      = gaze_fractions["C"]

        # Define the ideal center gaze and the standard deviation
        ideal_center_gaze = 0.7
        std_dev = 8

        # Calculate the score using the Gaussian function
        blink_score = math.exp(-0.5 * ((center_gaze - ideal_center_gaze) / std_dev) ** 2)

        #================================================================================================
        # Attentiveness score is blink score
        score = int(blink_score * 100)

        # Store the score in the scores dictionary
        self.scores["Attentiveness_Score"] = score
    
    def scoreEmpathy(self):
        #================================================================================================
        expression_fractions = self.metrics["expression_fractions"]
        connecting_expression = expression_fractions["happy"] + expression_fractions["surprise"] + expression_fractions["sad"]
        disconnecting_expression = expression_fractions["angry"] + expression_fractions["disgust"] + expression_fractions["fear"]
        neutral_expression  = expression_fractions["neutral"]

        ratio = (connecting_expression + neutral_expression) / disconnecting_expression

        # Define the point of sharp drop and the steepness of the drop
        drop_point = 0.8
        steepness = 7  # Increase this for a sharper drop

        # Calculate the score using the logistic function
        expression_score = 1 / (1 + math.exp(-steepness * (ratio - drop_point)))

        #================================================================================================
        # blinking too little lowers the empathy score
        blinks_per_minute = self.metrics["blinks_per_minute"]
        if blinks_per_minute > 10:
            blink_score = 1
        else:
            # Exponential decrease for x <= 10
            # Adjust the base as needed
            blink_score = 0.5 ** (10 - blinks_per_minute) 

        #================================================================================================
        # Empathy score is blink score and expression score
        score = int((blink_score * 0.3 + expression_score * 0.7) * 100)

        # Store the score in the scores dictionary
        self.scores["Empathy_Score"] = score
    
    def scoreSocialability(self):
        #================================================================================================
        # Based on gaze fractions
        gaze_fractions   = self.metrics["gaze_fractions"]
        center_gaze      = gaze_fractions["C"]

        # Define the ideal center gaze and the standard deviation
        ideal_center_gaze = 0.7
        std_dev = 8

        # Calculate the score using the Gaussian function
        blink_score = math.exp(-0.5 * ((center_gaze - ideal_center_gaze) / std_dev) ** 2)

        #================================================================================================
        # Expression fractions
        expression_fractions = self.metrics["expression_fractions"]

        # Define weights for different emotions
        weights = {
            'happy': 1.5,
            'neutral': 1.0,
            'surprise': 1.2,
        }

        # Calculate weighted sum of positive emotions
        positive_score = sum(expression_fractions[emotion] * weights.get(emotion, 1.0) for emotion in weights.keys())

        # Calculate sociability score
        expression_score = positive_score / sum(weights.values())

        #================================================================================================
        # Socialability score is blink score and expression score
        score = int((blink_score * 0.2 + expression_score * 0.8) * 100)

        # Store the score in the scores dictionary
        self.scores["Socialability_Score"] = score
    
    def scoreExpressiveness(self):
        #================================================================================================
        expression_fractions = self.metrics["expression_fractions"]
        neutral_expression  = expression_fractions["neutral"]
        all_other_expression = 1 - neutral_expression

        ratio = all_other_expression/ neutral_expression

        expression_score = 1 / (1 + math.exp(-ratio))

        #================================================================================================
        # Expressiveness score is expression score
        score = 50 + int(expression_score * 50)

        # Store the score in the scores dictionary
        self.scores["Expressiveness_Score"] = score
    
    def analyzeGaze(self) -> dict:

        results = {}

        gaze_fractions   = self.metrics["gaze_fractions"]
        prominent_gaze   = self.metrics["prominent_gaze"]

        results["gaze_fractions"] = gaze_fractions

    def getScores(self):
        for func in self.scoreFuncs:
            func()
    
    def starBasedOnDifference(self, difference):
        difference = abs(difference)
        if difference < 5:
            return 5
        elif difference < 20:
            return 4
        elif difference < 40:
            return 3
        elif difference < 60:
            return 2
        elif difference < 80:
            return 1
        else:
            return 0
        
    def generate(self):
        # Get the scores
        confidence_score = self.scores["Confidence_Score"]
        attentiveness_score = self.scores["Attentiveness_Score"]
        empathy_score = self.scores["Empathy_Score"]
        socialability_score = self.scores["Socialability_Score"]
        expressiveness_score = self.scores["Expressiveness_Score"]

        # Get Score differences from ideal scores
        confidence_diff = self.ideal_scores["Confidence_Score"] - confidence_score
        attentiveness_diff = self.ideal_scores["Attentiveness_Score"] - attentiveness_score
        empathy_diff = self.ideal_scores["Empathy_Score"] - empathy_score
        socialability_diff = self.ideal_scores["Socialability_Score"] - socialability_score
        expressiveness_diff = self.ideal_scores["Expressiveness_Score"] - expressiveness_score

        # Give stars based on the differences
        self.scores["Confidence_Stars"] = self.starBasedOnDifference(confidence_diff)
        self.scores["Attentiveness_Stars"] = self.starBasedOnDifference(attentiveness_diff)
        self.scores["Empathy_Stars"] = self.starBasedOnDifference(empathy_diff)
        self.scores["Socialability_Stars"] = self.starBasedOnDifference(socialability_diff)
        self.scores["Expressiveness_Stars"] = self.starBasedOnDifference(expressiveness_diff)

        # Store the ideal scores
        self.scores["Confidence_Ideal_Score"] = self.ideal_scores["Confidence_Score"]
        self.scores["Attentiveness_Ideal_Score"] = self.ideal_scores["Attentiveness_Score"]
        self.scores["Empathy_Ideal_Score"] = self.ideal_scores["Empathy_Score"]
        self.scores["Socialability_Ideal_Score"] = self.ideal_scores["Socialability_Score"]
        self.scores["Expressiveness_Ideal_Score"] = self.ideal_scores["Expressiveness_Score"]

        # Prompt GPT-3 to generate feedback based on the interaction
        input_text = f"""
            Please generate some feedback based on these interaction metrics.
            Confidence Score = {confidence_score}, Ideal Confidence Score = {self.ideal_scores["Confidence_Score"]},
            Attentiveness Score = {attentiveness_score}, Ideal Attentiveness Score = {self.ideal_scores["Attentiveness_Score"]},
            Empathy Score = {empathy_score}, Ideal Empathy Score = {self.ideal_scores["Empathy_Score"]},
            Socialability Score = {socialability_score}, Ideal Socialability Score = {self.ideal_scores["Socialability_Score"]},
            Expressiveness Score = {expressiveness_score}, Ideal Expressiveness Score = {self.ideal_scores["Expressiveness_Score"]}.

            blink_rate = {self.metrics["blinks_per_minute"]}, ideal_blink_rate = 15-20,
            gaze_fractions = {self.metrics["gaze_fractions"]}, ideal_center_gaze = 0.7,
            expression_fractions = {self.metrics["expression_fractions"]},
            their most prominent expression = {self.metrics["prominent_expression"]}.

            Note the difference between the scores and the ideal scores. Use the difference to generate feedback.
            Score of 100 does NOT mean better. If it is fair from ideal score, it still needs critisism.

            Do not reveal any numbers to the user. Just use the metrics to generate feedback.
        """

        response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          response_format={ "type": "json_object" },
          messages=[
            {"role": "system", "content": self.gptPrompt},
            {"role": "user", "content": input_text}, 
          ]
        )

        confidence_backup_feedback = "Your confidence looks good." if confidence_score > 80 else "You could work on your presenting your confidence."
        attentiveness_backup_feedback = "You are very attentive." if attentiveness_score > 80 else "You could work on being more attentive."
        empathy_backup_feedback = "You are very empathetic." if empathy_score > 80 else "You could work on being more empathetic."
        socialability_backup_feedback = "You are very sociable." if socialability_score > 80 else "You could work on being more sociable."
        expressiveness_backup_feedback = "You are very expressive." if expressiveness_score > 80 else "You could work on being more expressive."

        # Extract the feedback from the response, where response is a json string
        # First turn the string into a dictionary
        response_dict = json.loads(response.choices[0].message.content)
        # Then extract the feedback from the dictionary
        self.scores["Confidence_feedback"] = response_dict.get("Confidence_feedback", confidence_backup_feedback)
        self.scores["Attentiveness_feedback"] = response_dict.get("Attentiveness_feedback", attentiveness_backup_feedback)
        self.scores["Empathy_feedback"] = response_dict.get("Empathy_feedback", empathy_backup_feedback)
        self.scores["Socialability_feedback"] = response_dict.get("Socialability_feedback", socialability_backup_feedback)
        self.scores["Expressiveness_feedback"] = response_dict.get("Expressiveness_feedback", expressiveness_backup_feedback)

class InterviewReport(Report):
    def __init__(self, metrics):
        super().__init__(metrics)
        self.ideal_scores = {
            "Confidence_Score": 90,
            "Attentiveness_Score": 100,
            "Empathy_Score": 100,
            "Socialability_Score": 100,
            "Expressiveness_Score": 50
        }

        self.gptPrompt += """
            Note that this is an interview scenario. Here are the reasoning behind the ideal scores:
            Confidence: The ideal confidence score is 90. This is because the interviewee should be confident, but not overly so. Overconfidence can be off-putting.
            Attentiveness: The ideal attentiveness score is 100. The interviewee should be fully attentive during the interview.
            Empathy: The ideal empathy score is 100. The interviewee should be empathetic and understanding.
            Socialability: The ideal socialability score is 100. The interviewee should be sociable and engaging.
            Expressiveness: The ideal expressiveness score is 50. The interviewee should be expressive, but not overly so. Overexpressiveness can be off-putting.
        """

class EvaluationReport(Report):
    def __init__(self, metrics):
        super().__init__(metrics)
        self.ideal_scores = {
            "Confidence_Score": 100,
            "Attentiveness_Score": 100,
            "Empathy_Score": 100,
            "Socialability_Score": 100,
            "Expressiveness_Score": 100 
        }

        self.gptPrompt += """
            Note that this is initial evaluation for our social cue learning platform. The scores to gauge a general interaction.
        """

class DateReport(Report):
    def __init__(self, metrics):
        super().__init__(metrics)
        self.ideal_scores = {
            "Confidence_Score": 70,
            "Attentiveness_Score": 100,
            "Empathy_Score": 100,
            "Socialability_Score": 100,
            "Expressiveness_Score": 85 
        }

        self.gptPrompt += """
            Note that this a first date scenario for potential romantic partner. Here are the reasoning behind the ideal scores for a first date:
            Confidence: The ideal confidence score is 70. This is because while on a first date, the person should be confident, but not overly so. Overconfidence can be off-putting and comes off as arrogant.
            Attentiveness: The ideal attentiveness score is 100. The person should be fully attentive during the date.
            Empathy: The ideal empathy score is 100. The person should be empathetic and understanding.
            Socialability: The ideal socialability score is 100. The person should be sociable and engaging.
            Expressiveness: The ideal expressiveness score is 85. The person should be expressive, and be themselves! But some restraint is shows that they mature and in control of their emotions.
        """

# Map to store the report type and the corresponding class
reportTypeMap = {
    "interview": InterviewReport,
    "evaluation": EvaluationReport,
    "date": DateReport,
}

def generateJsonReport(metrics: dict, reportType: str):

    report = reportTypeMap[reportType](metrics)
    report.getScores()
    report.generate()

    return json.dumps(report.scores, indent=4, sort_keys=True)

@reportGenerator.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Report Generator is working!'})

@reportGenerator.route('/generateReport', methods=['POST'])
def generateReport():

    metrics    = request.json['metrics']
    reportType = request.json['reportType']

    report = reportTypeMap[reportType](metrics)
    report.getScores()
    report.generate()

    return jsonify(report.scores)

if __name__ == "__main__":
    metrics = {
        "blinks_per_minute": 12,
        "gaze_fractions": {
            "L": 0.5,
            "R": 0.10,
            "C": 0.85,
        },
        "prominent_gaze": "C",
        "expression_fractions": {
            "neutral": 0.2,
            "happy": 0.5,
            "sad": 0.1,
            "angry": 0.1,
            "surprise": 0.1,
            "fear": 0.0,
            "disgust": 0.0
        },
        "prominent_expression": "happy",
    }

    resStr = generateJsonReport(metrics, "interview")
    print(resStr)