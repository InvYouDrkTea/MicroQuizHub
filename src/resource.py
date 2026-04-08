import json
import os
from cachetools import cached, TTLCache

quiz_cache = TTLCache(maxsize=8, ttl=30)
paper_cache = TTLCache(maxsize=8, ttl=30)
group_cache = TTLCache(maxsize=8, ttl=30)

class Resource:
    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @cached(quiz_cache)
    def get_quiz(self, quiz_id):
        quiz_dir = []
        for i in os.scandir("quiz"):
            if i.is_dir():
                quiz_dir.append(i.path)
        for i in quiz_dir:
            try:
                quiz = self.load_json(os.path.join(i, "quiz.json"))
                if quiz["id"] == quiz_id:
                    return (i, quiz)
            except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
                continue
        return None

    @cached(group_cache)
    def get_group(self, group_id):
        group_dir = os.scandir("group")
        for i in group_dir:
            try:
                group = self.load_json(i.path)
                if group["id"] == group_id:
                    return group
            except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
                continue
        return None

    @cached(paper_cache)
    def get_paper(self, paper_id):
        paper_dir = os.scandir("paper")
        for i in paper_dir:
            try:
                paper = self.load_json(i.path)
                if paper["id"] == paper_id:
                    return paper
            except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
                continue
        return None
    
    def get_result(self, quiz_id):
        quiz_path = self.get_quiz(quiz_id)
        if quiz_path is None:
            return None
        path = quiz_path[0]
        try:
            data = self.load_json(os.path.join(path, "result.json"))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            data = None
        return data
    
    def get_answer(self, quiz_id):
        quiz_path = self.get_quiz(quiz_id)
        if quiz_path is None:
            return None
        path = quiz_path[0]
        try:
            data = self.load_json(os.path.join(path, "answer.json"))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            data = None
        return data
    
    def save_answer(self, quiz_id, data):
        quiz_path = self.get_quiz(quiz_id)
        if quiz_path is None:
            return False
        path = quiz_path[0]
        self.save_json(os.path.join(path, "answer.json"), data)
        return True