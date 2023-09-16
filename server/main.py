# import main Flask class and request object
from flask import Flask, request, jsonify
import json
from ner import parse_task, add_info

# create the Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "Home Page"

@app.route("/parse", methods=["POST"])
def parse():
    print("parse")
    print(request.data)
    data = json.loads(request.data.decode("utf-8"))
    if data["status"] == "init":
        task, missing_info = parse_task(data["text"])
    elif data["status"] == "add":
        task, missing_info = add_info(data["task"], data["info"])
        # task: previously returned task
        # info: {keywords: phrase}
    else:
        return {"msg": "Unrecognized status."}
    ret_msg = {
        "task": task.__dict__,
        "missing": missing_info
    }
    print(ret_msg)
    return ret_msg

@app.route("/schedule", methods=["GET"])
def schedule():
    print("schedule")
    print(request.data)
    data = json.loads(request.data.decode("utf-8"))
    

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)