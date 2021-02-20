# Almog Shoob
# Omer Tubul

import socket


def start(my_socket):
    """ run 1 round of the game """
    while True:  # until msg[1]== '2'
        msg = my_socket.recv(1024).decode()  # get msg
        if msg[1] == '2':  # check if game is over
            return
        print(msg[3:])  # print msg
        if msg[1] == '0':  # let client answer if needed
            msg = get_input(['1', '2', '3', '4', 'help'])  # get input from client
            my_socket.send(msg.encode())  # send answer to server


def get_input(valid_inputs_list):
    """ @params: 
        valid_inputs_list - list of valid inputs
    @ret val: 
        valid input from the user in lower case
    """
    options = '/'.join(valid_inputs_list)  # to print later
    while True:  # until user input is valid
        msg = input()  # get input
        if msg.lower() in valid_inputs_list:  # check validity
            return msg.lower()  # if valid, return
        print(msg + ' is not a valid entry, please enter: ' + options)  # if not valid, ask again


def main():
    # open socket in my device. AF_INET=get IPv4 address, SOCK_STREAM=protocol TCP
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print('Hi! Do you want to play? (yes/no): ')  # ask before making contact with the server
    answer = get_input(['yes', 'no'])
    if answer == 'no':
        print('Bye!')
        return
    if answer == 'yes':
        my_socket.connect((HOST, PORT))  # connect with server
        msg = my_socket.recv(1024).decode()  # server's response
        print(msg[3:] + '\n')
        if msg[1] == '0':  # approved
            start(my_socket)  # start game
            print('\n')
        else:  # denied, game manager is full
            return

    # when game finishs, do not disconnect if client wish to keep playing
    while True:  # until answer=='no'
        print('Do you want to play again? (yes/no): ')
        answer = get_input(['yes', 'no'])
        my_socket.send(answer.encode())  # send answer to server
        if answer == 'no':  # exit
            print('Bye!')
            return
        if answer == 'yes':  # start another round
            start(my_socket)
            print('\n')


# general code start here
HOST = '127.0.0.1'  # The server's IP address
PORT = 65430  # The port used by the server

if __name__ == "__main__":
    main()
