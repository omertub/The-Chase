# almog shoob
# omer tubul


import socket


def start(my_socket):
    #  run 1 round of the game
    while True:  # until msg=='done'
        msg = my_socket.recv(1024).decode()  # get msg
        if msg == 'done':  # check if game is over
            return
        print(msg)  # print msg
        if 'choose' in msg.lower():  # let client answer if needed
            msg = get_input(['1', '2', '3', '4', 'help'])  # get input from client
            my_socket.send(msg.encode())  # send answer to server


def get_input(valid_inputs_list):
    # get list of valid user inputs
    # return valid input from the user
    options = '/'.join(valid_inputs_list)  # to print later
    while True:  # until user input is valid
        msg = input()  # get input
        if msg.lower() in valid_inputs_list:  # check validity
            return msg  # if valid, return
        print('Not valid entry, please enter: ' + options)  # if not valid, ask again


def main():
    # open socket in my device. AF_INET=get IPv4 address, SOCK_STREAM=protocol TCP
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print('Hi! Do you want to play? (yes/no): ')  # ask before making contact with the server
    answer = get_input(['yes', 'no'])
    if answer.lower() == 'no':
        print('Bye!')
        return
    if answer.lower() == 'yes':
        my_socket.connect((HOST, PORT))  # connect with the server
        msg = my_socket.recv(1024).decode()  # msg if access approved or not
        print(msg + '\n')
        if msg == "OK let's play":  # approved
            start(my_socket)  # start game
            print('\n')
        else:  # denied, game manager is full
            return

    # after 1 game, stay connected while the client wants to keep playing
    while True:  # until answer=='no'
        print('Do you want to play again? (yes/no): ')  # ask
        answer = get_input(['yes', 'no'])
        my_socket.send(answer.lower().encode())  # send the server my answer
        if answer.lower() == 'no':  # exit
            print('Bye!')
            my_socket.close()
            return
        if answer.lower() == 'yes':  # start another round
            start(my_socket)
            print('\n')


# general code start here
HOST = '127.0.0.1'  # The server's IP address
PORT = 65432  # The port used by the server

if __name__ == "__main__":
    main()
