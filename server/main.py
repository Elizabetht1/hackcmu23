# import main Flask class and request object
from flask import Flask, request, jsonify
import json
from ner import parse_task, add_info, Task
import sys
import dateparser
sys.path.insert(0, "sched")
import scheduler

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
    if "task" not in data:
        task, missing_info = parse_task(data["text"])
    elif data["task"]["status"] == "incomplete":
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

@app.route("/propose", methods=["POST"])
def propose():
    print("propose")
    print(request.data)
    data = json.loads(request.data.decode("utf-8"))
    task = Task(**data["task"])
    duration = dateparser.parse(task.duration)
    duration = (3600 * duration.hour + 60 * duration.minute + duration.second) // 3600
    schedule = scheduler.propose([task.start_time, task.location, duration, task.deadline, task.task_str, task.text])
    return {"msg": "success", "schedule": schedule}

@app.route("/schedule", methods=["POST"])
def schedule():
    print("schedule")
    print(request.data)
    data = json.loads(request.data.decode("utf-8"))
    schedule = data["schedule"]
    scheduler.schedule([schedule["start_time"], schedule["end_time"], schedule["task"], schedule["location"], schedule["description"]])
    return {"msg": "success"}

if __name__ == '__main__':
    app.run(debug=True, port=5005)