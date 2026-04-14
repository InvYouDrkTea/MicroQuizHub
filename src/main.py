from flask import Flask, request, abort, render_template, send_file, jsonify
from jinja2 import TemplateNotFound
import os
import time
from . import resource

os.makedirs("attachment/", exist_ok=True)
os.makedirs("group/", exist_ok=True)
os.makedirs("paper/", exist_ok=True)
os.makedirs("quiz/", exist_ok=True)

res = resource.Resource()

def verify_token(quiz_id, token):
    quiz_info = res.get_quiz(quiz_id)
    if quiz_info is None:
        return False
    group_id = quiz_info[1].get("group")
    
    if group_id is None:
        return True
    group = res.get_group(group_id)
    if group is None:
        return False
    return token in group.get("token", [])

def check_submission(quiz_id, token):
    quiz_info = res.get_quiz(quiz_id)
    if quiz_info is None:
        return 1, "Quiz not found"
    quiz_config = quiz_info[1]
    group_id = quiz_config.get("group")

    if group_id is None:
        token = ""
    else:
        if not verify_token(quiz_id, token):
            return 1, "Token invalid"

    deadline = quiz_config.get("deadline")
    if deadline is not None:
        try:
            deadline_sec = int(deadline)
            if deadline_sec > 0 and time.time() > deadline_sec:
                return 3, "Quiz closed"
        except (ValueError, TypeError):
            pass

    answer_data = res.get_answer(quiz_id)
    allow_resubmit = quiz_config.get("allow_resubmit", False)

    if group_id is None:
        return 0, "OK"

    if answer_data is None:
        return 0, "OK"

    answer_list = answer_data.get("answer", [])
    for entry in answer_list:
        if entry.get("token") == token:
            if not allow_resubmit:
                return 2, "Submitted, resubmission not allowed"
            else:
                break
    return 0, "OK"

def return_json(code, message):
    return {"code": code, "message": message}

app = Flask(__name__, template_folder="page/")

@app.route("/page/<path:filename>")
def page(filename):
    try:
        return render_template(filename)
    except TemplateNotFound:
        return abort(404, "Page not found")

@app.route("/asset/<path:filename>")
def asset(filename):
    try:
        return send_file(os.path.join("asset/", filename))
    except FileNotFoundError:
        return abort(404, "Asset not found")

@app.route("/quiz/<quiz_id>")
def quiz(quiz_id):
    quiz_data = res.get_quiz(quiz_id)
    if quiz_data is None:
        return abort(404, "Quiz not found")
    return jsonify(quiz_data[1])

@app.route("/verify", methods=["POST"])
def verify():
    request_json = request.get_json()
    try:
        quiz_id = request_json["quiz"]
        token = request_json["token"]
    except (KeyError, TypeError):
        return abort(400, "Missing required keys: quiz and token or values are invalid")

    code, message = check_submission(quiz_id, token)
    return jsonify(return_json(code, message))

@app.route("/paper/<paper_id>")
def paper(paper_id):
    paper_data = res.get_paper(paper_id)
    if paper_data is None:
        return abort(404, "Paper not found")
    return jsonify(paper_data)

@app.route("/submit", methods=["POST"])
def submit():
    request_json = request.get_json()

    try:
        quiz_id = request_json["quiz"]
        token = request_json["token"]
        user_answers = request_json["answer"]
    except (KeyError, TypeError):
        return abort(400, "Missing required keys: quiz, token, answer or values are invalid")

    quiz_info = res.get_quiz(quiz_id)
    if quiz_info is None:
        return abort(404, "Quiz not found")

    quiz_config = quiz_info[1]
    group_id = quiz_config.get("group")

    effective_token = token
    if group_id is None:
        effective_token = ""

    code, message = check_submission(quiz_id, effective_token)
    if code != 0:
        return jsonify(return_json(code, message))

    answer_data = res.get_answer(quiz_id)
    if answer_data is None:
        answer_data = {"id": quiz_id, "answer": []}

    if group_id is None:
        answer_data["answer"].append({"token": effective_token, "answer": user_answers})
    else:
        existing_idx = None
        for idx, entry in enumerate(answer_data["answer"]):
            if entry.get("token") == effective_token:
                existing_idx = idx
                break
        new_entry = {"token": effective_token, "answer": user_answers}
        if existing_idx is not None:
            answer_data["answer"][existing_idx] = new_entry
        else:
            answer_data["answer"].append(new_entry)

    if res.save_answer(quiz_id, answer_data):
        return jsonify(return_json(0, "Submitted successfully"))
    else:
        return abort(500, "Failed to save answer")

@app.route("/result/<quiz_id>", methods=["GET"])
def get_result(quiz_id):
    quiz_info = res.get_quiz(quiz_id)
    if quiz_info is None or quiz_info[1] is None:
        return abort(404, "Quiz not found")
    quiz_config = quiz_info[1]
    group_id = quiz_config.get("group")

    if group_id is None:
        return abort(400, "Result not available for this quiz")

    token = request.args.get("token")
    if not token:
        return abort(400, "Missing token parameter")
    if not verify_token(quiz_id, token):
        return abort(400, "Token invalid")

    result = res.get_result(quiz_id)
    if result is None:
        return abort(404, "Result not found")
    for i in result["result"]:
        if i["token"] == token:
            return jsonify(i)
    return abort(404, "Result not found")

@app.route("/attachment/<path:filename>")
def attachment(filename):
    try:
        return send_file(os.path.join(os.getcwd(), "attachment/", filename))
    except FileNotFoundError:
        return abort(404, "Attachment not found")