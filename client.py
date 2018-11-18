'''
    Filename: client.py
    Description:
        Client that allows you to request server names from client.
'''

import datetime
import pickle
import sys
import time
from socket import *

# Network constants pointing to the server
HOST, PORT = '127.0.0.1', 25000

# ------------------------ / Logging


def timestamp():
    return str(datetime.datetime.utcnow())


# Client log file.
log_file = open("client.log", "a")


def log(log_message, keep_silent=False):
    '''
        Writes log message to file
        Prints log message to output if keep_silent is false
    '''
    if not keep_silent:
        print(log_message)
    log_file.write(timestamp() + " : " + log_message + "\n")


def terminate(log_message):
    " Logs message to output then termiantes connection"
    log("Terminating: " + log_message)
    sys.exit(0)


# ------------------------ / Client
OPERATION_FAILURE = 'Operation-Failed'  # Opaque value to indiciate failure


def safe_execute(failure, operation, return_arity=1):
    '''
        Tries to return result generated by operation
        Executes failure if operation failes
        Makes getting result from tries alot easier.
    '''
    try:
        return operation()
    except Exception as e:
        failure(e)
        return (OPERATION_FAILURE,)*return_arity


def get_user_input():
    '''
        Prompts the user for an input
        If input is empty, reprompts user
    '''
    artist_name = input('Enter artist to lookup >').strip()
    while not artist_name:
        print("That input is empty! Please enter the name again")
        artist_name = input('Enter artist to lookup >').strip()
    return artist_name


def send_close_request(socket):
    "Waits for user input to close the connection"
    input("Press `Enter` to close connection.")
    socket.send("quit".encode())


# Socket Opening
with socket(AF_INET, SOCK_STREAM) as s:

    # Try and make connection
    safe_execute(
        failure=lambda e: terminate(
            "Fail to establish a connection to server. {}".format(str(e))),
        operation=lambda: s.connect((HOST, PORT)))
    log("Established connection")

    # Prompt for input
    artist_input = safe_execute(
        failure=lambda e: terminate("User terminaed via Cntl-C"),
        operation=get_user_input)

    # Send input to server
    safe_execute(
        failure=lambda e: terminate("Server refused query. {}".format(str(e))),
        operation=lambda: s.send(artist_input.encode()))
    log("Sent request `{0}` to server".format(artist_input), keep_silent=True)

    time_now = time.time()

    # Get response, assume artist has no more than 4 songs.
    response = safe_execute(
        failure=lambda e: terminate(
            "Failed to receive a response. {}".format(str(e))),
        operation=lambda: s.recv(4096))

    duration = time.time()-time_now  # how long it took to get response.
    log("Took {0} seconds to get a respnose".format(
        duration), keep_silent=True)
    log("Length is {0} bytes".format(len(response)), keep_silent=True)

    # Deserialise response from the server.
    songs = safe_execute(
        failure=lambda e: terminate(
            "Server response was malformed. {}".format(str(e))),
        operation=lambda: pickle.loads(response))

    if not songs:
        log("Arist `{0}` does have any songs".format(artist_input))
    else:
        log("Songs corresponding to arist:")
        log(str(songs), keep_silent=True)
        for song in songs:
            print("\t-", song)

    # Attempt to close the connection
    safe_execute(
        failure=lambda e: terminate(
            "Server refused close-connection request. {}".format(str(e))),
        operation=lambda: send_close_request(s))
    log("Close request was successful.", keep_silent=True)
