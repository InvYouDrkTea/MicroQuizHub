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
    group = res.get_group(quiz_info[1]["group"])
    if token in group["token"]:
        return True
    return False

def check_submission(quiz_id, token):
    quiz_config = res.get_quiz(quiz_id)[1]
    if not verify_token(quiz_id, token):
        return 1, "Token invalid"
    # 3. 检查截止时间（秒级时间戳）
    deadline = quiz_config.get("deadline")
    if deadline is not None:
        try:
            deadline_sec = int(deadline)
            if deadline_sec > 0 and time.time() > deadline_sec:
                return 3, "Quiz has expired"
        except (ValueError, TypeError):
            pass  # 无效 deadline 忽略

    # 4. 读取现有答案，检查重复提交
    answer_data = res.get_answer(quiz_id)
    allow_resubmit = quiz_config.get("allow_resubmit", False)

    # 兼容 answer_data 可能为 None 或列表的情况（但按需求不向下兼容，这里仍做安全处理）
    if answer_data is None:
        # 无任何提交记录，肯定可提交
        return 0, "OK"
    
    answer_list = answer_data.get("answer", [])
    for entry in answer_list:
        if entry.get("token") == token:
            if not allow_resubmit:
                return 2, "Already submitted, resubmission not allowed"
            else:
                break  # 允许重提交，跳出循环返回可提交
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
    # 1. 参数校验
    try:
        quiz_id = request_json["quiz"]
        token = request_json["token"]
        user_answers = request_json["answer"]
    except (KeyError, TypeError):
        return abort(400, "Missing required keys: quiz, token, answer or values are invalid")
    if res.get_quiz(quiz_id) is None:
        return abort(404, "Quiz not found")
    # 2. 调用统一检查函数
    code, message = check_submission(quiz_id, token)
    if code != 0:
        return jsonify(return_json(code, message))

    # 3. 获取测验配置（再次获取，用于保存时可能需要的其他信息，但无需重复检查）
    quiz_info = res.get_quiz(quiz_id)
    if quiz_info is None:
        abort(404, "Quiz not found")
    quiz_config = quiz_info[1]
    allow_resubmit = quiz_config.get("allow_resubmit", False)

    # 4. 读取现有答案文件 answer.json
    answer_data = res.get_answer(quiz_id)
    if answer_data is None:
        answer_data = {"id": quiz_id, "answer": []}
    
    # 5. 查找该 token 是否已有提交记录
    existing_idx = None
    for idx, entry in enumerate(answer_data["answer"]):
        if entry.get("token") == token:
            existing_idx = idx
            break

    # 6. 处理重复提交（再次确认，因为 check_submission 已做，但可能 allow_resubmit 为 True 时 existing_idx 存在仍可覆盖）
    if existing_idx is not None and not allow_resubmit:
        # 理论上不会进入这里，因为 check_submission 已经拦截，但防御
        return jsonify(return_json(2, "Already submitted, resubmission not allowed"))

    # 7. 更新或添加答案
    new_entry = {"token": token, "answer": user_answers}
    if existing_idx is not None:
        answer_data["answer"][existing_idx] = new_entry
    else:
        answer_data["answer"].append(new_entry)

    # 8. 保存到 answer.json
    if res.save_answer(quiz_id, answer_data):
        return jsonify(return_json(0, "Submitted successfully"))
    else:
        return abort(500, "Failed to save answer")

@app.route("/result/<quiz_id>", methods=["GET"])
def get_result(quiz_id):
    if res.get_quiz(quiz_id)[1] is None:
        return abort(404, "Quiz not found")
    token = request.args.get("token")
    if not token:
        return abort(400, "Missing token parameter")
    if not verify_token(quiz_id, token):
        return jsonify(return_json(1, "Token invalid"))
    result_data = res.get_result(quiz_id)
    if result_data is None:
        return abort(404, "Result not found")
    return jsonify({"code": 0, "message": "Success", "result": result_data["result"]})

@app.route("/attachment/<path:filename>")
def attachment(filename):
    try:
        return send_file(os.path.join(os.getcwd(), "attachment/", filename))
    except FileNotFoundError:
        return abort(404, "Attachment not found")