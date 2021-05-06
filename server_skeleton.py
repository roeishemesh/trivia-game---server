import socket
import chatlib
import select
import random
import outside_data
import json

questions = outside_data.load_question()
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later

SERVER_PORT = 5678
SERVER_IP = "0.0.0.0"
MAX_MSG_LENGTH = 1024

messages_to_send = []


# HELPER SOCKET METHODS

def build_and_send_message(conn, cmd, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    global messages_to_send
    protocol_msg = chatlib.build_message(cmd, data)
    # conn.send(protocol_msg.encode())
    messages_to_send.append((conn, protocol_msg))

    print("[SERVER] ", protocol_msg)  # Debug print


def recv_message_and_parse(connect):
    """
        Recieves a new message from given socket,
        then parses the message using chatlib.
        Paramaters: conn (socket object)
        Returns: cmd (str) and data (str) of the received message.
        If error occured, will return None, None
        """
    data = connect.recv(1024).decode()
    paras_data = chatlib.parse_message(data)
    # print(data)
    print("[CLIENT] ", paras_data)  # Debug print
    return paras_data


# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """
    print("setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("listing for client...")
    return server_socket


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, "ERROR", error_msg)


def create_random_question(conn):
    global questions
    global logged_users
    questions_list = [i for i in questions.keys()]
    asked_question = logged_users.get(conn.getpeername()).get("asked_question")
    questions_bank = list(set(questions_list) - set(asked_question))
    if len(questions_bank) == 0:
        build_and_send_message(conn, "END_QUESTION", "")
    else:
        selected_question = random.choice(questions_bank)
        asked_question.append(selected_question)
        build_and_send_message(conn, "YOUR_QUESTION",
                               f"{str(selected_question)}#{questions.get(selected_question).get('question')}#"
                               f"{'#'.join(questions.get(selected_question).get('answers'))}")


def send_users(conn):
    users_dict = outside_data.open_users_dict()
    build_and_send_message(conn, "USERS_LIST", "#".join(list(users_dict.keys())))


def append_new_user(data):
    user_and_password = data.split("#")
    with open(r"C:\Users\Roei\OneDrive\שולחן העבודה\studies\python\net.py\running_task\users.json", "r") as json_file:
        json_data = json.load(json_file)
        users_dict = json_data["users"]
        users_dict[user_and_password[0]] = {'password': user_and_password[1], 'best_score': 0}
    with open(r"C:\Users\Roei\OneDrive\שולחן העבודה\studies\python\net.py\running_task\users.json", "w") as json_file:
        json.dump({"users": users_dict}, json_file, indent=4)


# MESSAGE HANDLING


def handle_answer_message(conn, data):
    global questions
    global logged_users
    question_num = data.split("#")[0]
    client_answer = data.split("#")[1]
    currect_answer = questions.get(int(question_num)).get("correct")
    if int(client_answer) == currect_answer:
        logged_users[conn.getpeername()]["score"] += 5
        build_and_send_message(conn, "CORRECT_ANSWER", "")
    else:
        build_and_send_message(conn, "WRONG_ANSWER", str(currect_answer))


def change_score(conn):
    playing_user = logged_users.get(conn.getpeername()).get("user_name")
    player_score = logged_users.get(conn.getpeername()).get("score")
    best_score = outside_data.open_users_dict()[playing_user]["best_score"]
    print("the player score is:", player_score)
    if player_score > best_score:
        outside_data.change_score(playing_user, player_score)


def handle_getscore_message(conn):
    build_and_send_message(conn, "MY_SCORE", str(logged_users.get(conn.getpeername()).get("score")))


def my_best_score(conn, user_name):
    build_and_send_message(conn, "YOUR_BEST_SCORE",
                           str(outside_data.open_users_dict().get(user_name).get("best_score")))


def handle_highscore_message(conn):
    highscore_list = []
    highscore_msg = ""
    for user in list(outside_data.open_users_dict().keys()):
        highscore_list.append([user, outside_data.open_users_dict().get(user).get("best_score")])
    sorted_highscore_list = sorted(highscore_list, key=lambda a: a[1], reverse=True)
    for i in sorted_highscore_list:
        highscore_msg = highscore_msg + f"{i[0]}:{str(i[1])}\n"
    build_and_send_message(conn, "ALL_SCORE", highscore_msg)


def handle_logged_message(conn):
    global logged_users
    logged_users_list = []
    for user in logged_users.values():
        logged_users_list.append(user["user_name"])
    logged_users_str = ",".join(logged_users_list)
    build_and_send_message(conn, "LOGGED", logged_users_str)


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users
    del logged_users[conn.getpeername()]
    conn.close()


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global logged_users  # To be used later
    with open(r"C:\Users\Roei\OneDrive\שולחן העבודה\studies\python\net.py\running_task\users_test", "r") as json_file:
        json_data = json.load(json_file)
        users_dict = json_data["users"]
    msg = data.split("#")
    if msg[0] in users_dict:
        if msg[1] == str(users_dict.get(msg[0]).get("password")):
            build_and_send_message(conn, "LOGIN_OK", "")
            logged_users[conn.getpeername()] = {"user_name": msg[0], "asked_question": [], "score": 0}
        else:
            error_msg = "your password is wrong"
            send_error(conn, error_msg)
    else:
        error_msg = "this user is not exist"
        send_error(conn, error_msg)


# Implement code ...


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users  # To be used later
    server_cmd = ["LOGIN", "MY_SCORE", "HIGHSCORE", "LOGGED", "USERS_LIST", "NEW_USER", "GET_QUESTION", "SEND_ANSWER",
                  "END_GAME", "BEST_SCORE"]
    if cmd in server_cmd:
        if cmd == "LOGIN":
            handle_login_message(conn, data)
        if cmd == "MY_SCORE":
            handle_getscore_message(conn)
            print(logged_users.get(conn.getpeername()))
        if cmd == "HIGHSCORE":
            handle_highscore_message(conn)
        if cmd == "LOGGED":
            handle_logged_message(conn)
        if cmd == "USERS_LIST":
            send_users(conn)
        if cmd == "NEW_USER":
            append_new_user(data)
        if cmd == "GET_QUESTION":
            create_random_question(conn)
        if cmd == "SEND_ANSWER":
            handle_answer_message(conn, data)
        if cmd == "END_GAME":
            change_score(conn)
        if cmd == "BEST_SCORE":
            my_best_score(conn, logged_users.get(conn.getpeername()).get("user_name"))
    else:
        error_msg = "I don't know this command"
        send_error(conn, error_msg)


# Implement code ...


# def main(): good one
#     global questions
#     print("Welcome to Trivia Server!")
#     server_socket = setup_socket()
#     client_sockets = []
#     while True:
#         ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, [], [])
#         for current_socket in ready_to_read:
#             if current_socket is server_socket:
#                 (client_socket, client_address) = current_socket.accept()
#                 print("new client joined!", client_address)
#                 client_sockets.append(client_socket)
#             else:
#                 print("new data from client")
#                 try:
#                     data = recv_message_and_parse(current_socket)
#                     if data[0] == "LOGOUT":
#                         print(
#                             f"the Client \'{logged_users.get(current_socket.getpeername()).get('user_name')}\'"
#                             f" is closing the connection"
#                             f"\nConnection closed")
#                         client_sockets.remove(current_socket)
#                         handle_logout_message(current_socket)
#                     else:
#                         handle_client_message(current_socket, data[0], data[1])
#
#                 except ConnectionResetError:
#                     print(f"we have problam with the client: {logged_users.get(current_socket.getpeername()).get('user_name')}"
#                           f"\nClosing the connection with him")
#                     client_sockets.remove(current_socket)
#                     handle_logout_message(current_socket)


def main():
    global questions
    global messages_to_send
    print("Welcome to Trivia Server!")
    server_socket = setup_socket()
    client_sockets = []
    while True:
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                (client_socket, client_address) = current_socket.accept()
                print("new client joined!", client_address)
                client_sockets.append(client_socket)
            else:
                print("new data from client")
                try:
                    data = recv_message_and_parse(current_socket)
                    if data[0] == "LOGOUT":
                        print(
                            f"the Client \'{logged_users.get(current_socket.getpeername()).get('user_name')}\'"
                            f" is closing the connection"
                            f"\nConnection closed")
                        client_sockets.remove(current_socket)
                        handle_logout_message(current_socket)
                    else:
                        handle_client_message(current_socket, data[0], data[1])
                        for message in messages_to_send:
                            current_socket, data = message
                            if current_socket in ready_to_write:
                                current_socket.send(data.encode())
                                messages_to_send.remove(message)

                except ConnectionResetError:
                    print(f"we have problam with the client: {logged_users.get(current_socket.getpeername()).get('user_name')}"
                          f"\nClosing the connection with him")
                    client_sockets.remove(current_socket)
                    handle_logout_message(current_socket)


if __name__ == '__main__':
    main()
