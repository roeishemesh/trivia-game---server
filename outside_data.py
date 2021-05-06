import requests
import json
import random
import html

json_file_url = r"C:\Users\Roei\OneDrive\שולחן העבודה\studies\python\net.py\running_task\users.json"

def load_question():
    try:
        url = r"https://opentdb.com/api.php?amount=50&difficulty=easy&type=multiple"
        response = requests.get(url)
        response_dict = json.loads(response.text)
        question_list = response_dict["results"]
        question_num = 1
        question_dict = {}
        for i in question_list:
            question = html.unescape(html.unescape(i['question']))
            answers = [html.unescape(x) for x in i["incorrect_answers"] + [i['correct_answer']]]
            random.shuffle(answers)
            correct = answers.index(html.unescape(i['correct_answer'])) + 1
            question_dict[question_num] = {"question": question, "answers": answers,
                                           "correct": correct}

            question_num += 1
        return question_dict
    except FileNotFoundError:
        print("Sorry load question problem\nplease call to the server development")


def open_users_dict():
    global json_file_url
    with open(json_file_url, "r") as json_file:
        json_data = json.load(json_file)
        users_dict = json_data["users"]
        return users_dict


def change_score(user_name,new_score):
    global json_file_url
    with open(json_file_url, "r") as json_file:
        json_data = json.load(json_file)
        users = json_data["users"]
        users[user_name]["best_score"] = new_score
    with open(json_file_url, "w") as json_file:
        json.dump({"users": users}, json_file, indent=4)

def append_new_user(data):
    user_and_password = data.split("#")
    with open(json_file_url, "r") as json_file:
        json_data = json.load(json_file)
        users = json_data["users"]
        users[user_and_password[0]] = {'password': user_and_password[1], 'best_score': 0}
    with open(json_file_url, "w") as json_file:
        json.dump({"users": users}, json_file, indent=4)

