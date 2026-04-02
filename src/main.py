from flask import Flask, request, abort, render_template, send_file, jsonify
from jinja2 import TemplateNotFound
import os
from . import resource

os.makedirs("attachment/", exist_ok=True)
os.makedirs("group/", exist_ok=True)
os.makedirs("paper/", exist_ok=True)
os.makedirs("quiz/", exist_ok=True)

res = resource.Resource()

def verify_token(quiz_id, token_value):
    quiz = res.get_quiz(quiz_id)[1]
    group = res.get_group(quiz["group"])
    if token_value in group["token"]:
        return True
    return False

def return_json(code, message):
    return_json = {"code": code, "message": message}
    return return_json

app = Flask(__name__, template_folder="page/")

@app.route("/page/<path:filename>")
def page(filename):
    try:
        return render_template(filename)
    except TemplateNotFound:
        return abort(404, "Page not found")

@app.route("/quiz/<quiz_id>")
def quiz(quiz_id):
    quiz = res.get_quiz(quiz_id)
    if quiz == None:
        return abort(404, "Quiz not found")
    return jsonify(quiz[1])

@app.route("/token", methods=["POST"])
def token():
    request_json = request.get_json()
    try:
        if verify_token(request_json["quiz"], request_json["token"]):
            return jsonify(return_json(0, "Token valid"))
        return jsonify(return_json(1, "Token invalid"))
    except (KeyError, TypeError):
        return jsonify(return_json(2, "Data unexpected"))

@app.route("/paper/<paper_id>")
def paper(paper_id):
    paper = res.get_paper(paper_id)
    if paper == None:
            return abort(404, "Paper not found")
    return jsonify(paper)

@app.route("/submit", methods=["POST"])
def submit(): # To be modified
    request_json = request.get_json()
    try:
        request_json["answer"]
    except KeyError:
        return abort(400, "Missing required key: answer")
    try:
        if verify_token(request_json["quiz"], request_json["token"]):
            pass
        else:
            return abort(400, "Token invalid")
    except (KeyError, TypeError):
        return abort(400, "Missing required keys: survey and ticket or values are invalid")
    answer = res.get_answer(request_json["survey"])
    if answer == None:
        answer = []
    for i in range(len(answer)):
        if answer[i]["ticket"] == request_json["ticket"]:
            answer[i]["answer"] = request_json["answer"]
            if res.save_answer(request_json["survey"], answer):
                return "succeed"
            return abort(500, "Failed to save answer")
    answer.append({"ticket":request_json["ticket"], "answer":request_json["answer"]})
    if res.save_answer(request_json["survey"], answer):
        return "succeed"
    return abort(500, "Failed to save answer")

@app.route("/attachment/<path:filename>")
def attachment(filename):
    try:
        return send_file(os.path.join(os.getcwd(), "attachment/", filename))
    except FileNotFoundError:
        return abort(404, "Attachment not found")
