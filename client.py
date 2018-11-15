from socket import *
import pickle
import datetime
import time
import sys

HOST, PORT = '127.0.0.1', 25000

# ------------------------ / Logging


def timestamp():
    return str(datetime.datetime.utcnow())


log_file = open("client.log", "a")


def log(log_message, keep_silent=False):
    if not keep_silent:
        print(log_message)
    log_file.write(timestamp() + " : " + log_message + "\n")


def terminate(log_message):
    log("Terminating: " + log_message)
    sys.exit(0)


# ------------------------ / Client
OPERATION_FAILURE = 'Operation-Failed'  # Opaque value to indiciate failure


def safe_execute(failure, operation, return_arity=1):
    try:
        return operation()
    except Exception as e:
        failure(e)
        return (OPERATION_FAILURE,)*return_arity


def get_user_input():
    artist_name = input('Enter artist to lookup >').strip()
    while not artist_name:
        print("That input is empty! Please enter the name again")
        artist_name = input('Enter artist to lookup >').strip()
    return artist_name


def send_close_request(socket):
    input("Press `Enter` to close connection.")
    socket.send("quit".encode())


with socket(AF_INET, SOCK_STREAM) as s:
    safe_execute(
        failure=lambda e: terminate(
            "Fail to establish a connection to server. {}".format(str(e))),
        operation=lambda: s.connect((HOST, PORT)))
    log("Established connection")

    artist_input = safe_execute(
        failure=lambda e: terminate("User terminaed via Cntl-C"),
        operation=get_user_input)

    safe_execute(
        failure=lambda e: terminate("Server refused query. {}".format(str(e))),
        operation=lambda: s.send(artist_input.encode()))
    log("Sent request `{0}` to server".format(artist_input), keep_silent=True)

    # Assumption for return size: Song Title < 1kb, Max number of songs stored per artist = 4 => 4096 bytes.
    time_now = time.time()
    response = safe_execute(
        failure=lambda e: terminate(
            "Failed to receive a response. {}".format(str(e))),
        operation=lambda: s.recv(4096))

    duration = time.time()-time_now

    log("Took {0} seconds to get a respnose".format(
        duration), keep_silent=True)
    print("Response:", response)
    log("Length is {0} bytes".format(len(response)), keep_silent=True)
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

    safe_execute(
        failure=lambda e: terminate(
            "Server refused close-connection request. {}".format(str(e))),
        operation=lambda: send_close_request(s)
    )
    log("Sent Close Request", keep_silent=True)
