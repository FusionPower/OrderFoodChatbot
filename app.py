from flask import Flask, request, render_template
from flask_cors import CORS
import json
from QSR_GPT_API import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html') 

@app.route('/', methods=['POST'])
def get_chatbot_response():
    user_input = request.json['text']  
    # add prompt stopper to signal completion should happen
    user_input += " ->"
    botResponse = getBotResponse(user_input, actionHistory, orderHistory)
    return json.dumps({'chatbot_response': botResponse})


if __name__ == '__main__':
    # The bot can have many actions like greet, add items to order, update order etc.
    actionHistory = []
    # the order can change every step of the way, it might be useful to keep a history
    orderHistory = []
    app.run(debug=True)
