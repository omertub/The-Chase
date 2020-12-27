# almog shoob
# omer tubul

import socket
import threading
import random
import time


class Board:
    # this class manage the board in part 2 of the game

    def __init__(self, prize_option):
        # set initial position for player & chaser
        self.chaser_i = 0
        self.player_i = 1 + prize_option  # prize_option=1/2/3

    def __str__(self):
        # return string of the board for printing
        b = ''
        for i in range(7):  # 7 steps in the board
            if i == self.chaser_i:  # chaser position
                b += '|' + str(i) + '|  chaser  |\n'
            elif i == self.player_i:  # player position
                b += '|' + str(i) + '|  player  |\n'
            else:
                b += '|' + str(i) + '|          |\n'
        b += '|7|   bank   |\n'  # bank position
        return b

    def player_step(self):  # player one step ahead
        self.player_i += 1

    def chaser_step(self):  # chaser one step ahead
        self.chaser_i += 1

    def get_chaser_i(self):  # get chaser stage
        return self.chaser_i

    def get_player_i(self):  # get player stage
        return self.player_i


class Question:
    # this class manage a question with 4 option and 1 answer

    def __init__(self, ques, op1, op2, op3, op4, answer):
        self.ques = ques  # question text
        self.options = [op1, op2, op3, op4]  # answers text (strings list)
        self.answer = answer  # the right answer (int)

    def __str__(self):
        # return a string of question with 4 option
        st1 = self.ques + '\n'
        for i in range(4):
            st1 = st1 + str(i+1) + '. ' + self.options[i] + '\n'
        return st1

    def get_answer(self):  # get right answer number (int)
        return self.answer

    def get_option(self, i):  # get specific option text
        return self.options[i]


class Game:
    # This class manage the whole game and do the communication with the client

    def __init__(self, ques, client_socket):
        self.client = client_socket
        self.b = None  # will update after part 1
        self.questions = ques  # 'Question' list
        self.ques_left = list(range(15))  # what questions left
        self.ques_left_amount = 15  # how much questions left
        self.there_is_help = True  # help flag, only 1 use

    def get_question(self):
        # pop and return random question from the list
        ques_num = random.randint(0, self.ques_left_amount - 1)
        self.ques_left_amount -= 1
        return self.questions.pop(ques_num)

    def get_chaser_answer(self, q):
        # give the right answer in 75%
        rand_num = random.randint(1, 4)
        if rand_num <= 3:  # 75%
            return q.get_answer()  # give right answer
        else:  # 15% - give wrong answer
            options = [1, 2, 3, 4]  # all option
            options.pop(q.get_answer()-1)  # pop right option
            return options[random.randint(0, 2)]  # return random wrong option

    def update_board(self, player_answer, chaser_answer, answer):
        # check who rights and move him 1 step ahead (+send msg)
        if player_answer == answer:
            self.b.player_step()
            line = 'You are RIGHT!'
        else:
            line = 'You are WRONG!'
        self.client.send(line.encode())
        if chaser_answer == answer:
            self.b.chaser_step()
            line = 'The Chaser is RIGHT!\n'
        else:
            line = 'The Chaser is WRONG!\n'
        self.client.send(line.encode())

    def check_win_lose(self):
        # return 1 if player win, 2 if player lose, 0 else
        if self.b.get_player_i() == 7:  # player got to the bank
            return 1  # win
        if self.b.get_chaser_i() == self.b.get_player_i():  # chaser catch the player
            return 2  # lose
        return 0  # nothing

    def get_help(self, q):
        # send to the client 2 answers out of 4
        real_answer = q.get_answer()  # first option is the right one
        options = [1, 2, 3, 4]  # second option is random out of 4
        options.pop(real_answer-1)  # pop right option
        second_option = options[random.randint(0, 2)]  # get random wrong option
        for i in range(4):  # send the 2 options to the client
            if (i+1) in (real_answer, second_option):
                line = str(i+1) + '. ' + q.get_option(i)
                self.client.send(line.encode())

    def play(self):
        # this is the main part of the code, this function run the game and most of the communication

        prize = 0
        # part 1: 3 questions of 5000 NIS each
        line = 'Welcome to the first part!\n' + '3 questions of 5000 NIS start NOW\n'
        self.client.send(line.encode())
        for i in range(3):  # 3 questions
            q = self.get_question()  # get random question from stock
            line = str(q) + '\nChoose your answer (1-4): '
            self.client.send(line.encode())
            answer = int(self.client.recv(80).decode())  # get client answer
            # check answer and update prize
            if answer == q.get_answer():
                line = 'Well Done! you are right!\n'
                self.client.send(line.encode())
                prize += 5000
            else:
                line = 'You are wrong! Maybe next time!\n'
                self.client.send(line.encode())

        # part 2: choose where to start
        line = ('Welcome to the second part!\n' + 'You have ' + str(prize) + ' NIS for now\n' +
                'You can stay with it but you also can...\n' +
                '1. step back: compete for ' + str(prize * 2) + ' NIS and start 2 steps from the chaser\n' +
                '2. stay: compete for ' + str(prize) + ' NIS and start 3 steps from the chaser\n' +
                '3. step ahead: compete for ' + str(prize // 2) + ' NIS and start 4 steps from the chaser\n' +
                'Choose an option (1-3): \n')
        self.client.send(line.encode())
        answer = int(self.client.recv(80).decode())
        prize *= 2 if answer == 1 else 1/2 if answer == 3 else 1  # update prize (*1 or *1/2 or *2)
        prize = int(prize)  # and not float
        self.b = Board(answer)  # initialize board
        line = '--One time you can type \'help\' and get 2 wrong answers disabled--\n'
        self.client.send(line.encode())

        # part 2: let the chaser chase!
        for i in range(12):  # 12 questions left
            self.client.send(str(self.b).encode())  # send board
            q = self.get_question()  # get random question from stock
            chaser_answer = self.get_chaser_answer(q)  # get chaser answer (75% right)
            line = str(q) + '\nChoose your answer (1-4): '
            self.client.send(line.encode())

            # get client answer: int (1/2/3/4) -or- 'help'
            while True:  # until client choose answer (1/2/3/4)
                player_answer = self.client.recv(80).decode()  # get answer
                if player_answer.lower() == 'help':
                    if self.there_is_help:
                        self.get_help(q)  # send 2 option instead of 4
                        self.there_is_help = False  # update flag
                        line = '\nChoose your answer (1-4): '  # ask for new answer
                        self.client.send(line.encode())
                        continue
                    else:  # client already used his help, ask for an answer
                        line = 'You already used it!\n' + 'Choose your answer (1-4): '
                        self.client.send(line.encode())
                        continue
                # else: answer is 1/2/3/4
                break

            # update board, check if the game end (win/lose)
            self.update_board(int(player_answer), chaser_answer, q.get_answer())
            win_lose = self.check_win_lose()
            if win_lose == 1:  # win
                line = 'Well Done! You Win ' + str(prize) + ' NIS!'
                self.client.send(line.encode())
                return
            elif win_lose == 2:  # lose
                line = 'Oh No! You Lose! Maybe Next Time...'
                self.client.send(line.encode())
                return


class GamesManager:
    # this class manage threads of different players

    def __init__(self):
        print("[INITIALIZING GAME MANAGER]")

    def new_client(self, cl_socket, addr):
        # This is the THREAD function
        # this function run game after game...
        while True:  # until again=='no'
            g = Game(questions.copy(), cl_socket)  # create new game
            g.play()  # start paly
            time.sleep(1)  # wait after game is done, to prevent issues of sending multiple msgs
            cl_socket.send('done'.encode())  # tell client game is over
            again = cl_socket.recv(80).decode()  # get client answer for another game
            if again.lower() == 'no':  # if no - thread is finish
                break

        # close socket, print info
        cl_socket.close()
        print(f"[DISCONNECTION] {addr} disconnected")
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")


    def start(self):
        # this function open new thread for each client, up to 3
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # open socket, AF_INET=get IPv4 address, SOCK_STREAM=protocol TCP
        s.bind((HOST, PORT))  # bind socket to the address (ip,port)
        print("[STARTING] server is starting...")
        s.listen()  # start listen to clients
        print(f"[LISTENING] Server is listening on {HOST, PORT}")
        while True:  # for ever, the mainly work is this code
            cl_socket, addr = s.accept()  # accept client
            # if there are no more than 3 players already- accept, else- continue (wait for next request)
            if threading.activeCount() == MAX_GAMES_LIVE + 1:  # this thread + max amount of games
                # already 3 players, request denied
                cl_socket.send('Game manager is full, please try again later'.encode())
                cl_socket.close()
                print(f"[CONNECTION DENIED] {addr}")
                continue
            # else: make new thread and start the game
            cl_socket.send("OK let's play".encode())  # verification msg for client
            print(f"[NEW CONNECTION] {addr} connected.")
            thread = threading.Thread(target=self.new_client, args=(cl_socket, addr))  # open thread via 'new_client' function
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


# main code
def main():
    gm = GamesManager()  # create game manager
    gm.start()  # start accepting clients


# global variables
MAX_GAMES_LIVE = 3  # max number of player on the server
HOST = '127.0.0.1'  # host IP
# HOST = socket.gethostbyname(socket.gethostname())  # 172.20.144.1
PORT = 65432  # host port
# questions stock
q1 = Question('Who is the oldest?', 'Ninet Tayeb', 'Bar Refaeli', 'Esti Ginzburg', 'Shiri Mimon', 4)
q2 = Question('What is the name of the Simpson family dog?', 'Santa\'s Little Helper', 'Buck', 'Brian', 'Seven', 1)
q3 = Question('Which word is not associated with the \'friends\' series?', 'gleba', 'Gimbalia', 'Unagi', 'Phalange', 2)
q4 = Question('What is G. Yafit first name?', 'Geula', 'Galit', 'Yafit', 'Gila', 3)
q5 = Question('Who was the fourth chief of staff of the IDF?', 'Mordechai Maklef', 'Moshe Dayan', 'Yigal Yadin', 'Yaakov Dori', 2)
q6 = Question('How many times in his life has Benjamin Netanyahu married?', 'two', 'four', 'three', 'one', 3)
q7 = Question('What pill do you have to take to get into the Matrix?', 'red', 'green', 'blue', 'yellow', 1)
q8 = Question('In which country IKEA company was established?', 'Israel', 'Germany', 'Netherlands', 'Sweden', 4)
q9 = Question('Which nut has more calories?', 'Peanut', 'Pecan', 'Cashew', 'Walnut', 2)
q10 = Question('What color is the second \'g\' in the Google logo?', 'Yellow', 'Red', 'Green', 'Blue', 4)
q11 = Question('Where is the tallest building in the world?', 'Vancouver', 'Paris', 'Dubai', 'New York', 3)
q12 = Question('What year did World War II end?', '1945', '1943', '1950', '1941', 1)
q13 = Question('Which browser was developed by Apple?', 'Chrome', 'Mozilla', 'Firefox', 'Safari', 4)
q14 = Question('Which flag does not consist of 3 colors?', 'Ireland', 'Austria', 'Bulgaria', 'Germany', 2)
q15 = Question('What is the fourth planet at a distance from the sun?', 'Earth', 'Jupiter', 'Mars', 'Saturn', 3)
questions = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15]

if __name__ == '__main__':
    main()
