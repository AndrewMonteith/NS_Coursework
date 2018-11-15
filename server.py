'''
    Filename: server.py
    Author: Andrew Monteith
    Description:
        Simple server that responds to queries from a given client, where
        the query is simply a song writer and the response is all
        songs that the server knows the author has written.
'''

from socket import *
import sys
import datetime
import os.path
import re
import time
import pickle

HOST, PORT = '127.0.0.1', 25000

# ----------- / Logging


def timestamp():
    return str(datetime.datetime.utcnow())


log_file = open("server.log", "a")


def log(log_message):
    log_file.write(timestamp() + " : " + log_message + "\n")


def terminate(log_message):
    log("Terminating... Reason: " + log_message)
    sys.exit(0)

# ----------- / Song Reading


def song_entries(text_lines):
    starts_with_ranking, ends_in_year = re.compile(
        r"^\d{1,3}\s?-"), re.compile(r"\d{4}$")
    line_buffer = ''
    for line in map(str.strip, text_lines):
        if starts_with_ranking.search(line):
            line_buffer += line
        elif line_buffer:
            line_buffer += ('   ' + line)

        if line_buffer and ends_in_year.search(line):
            yield line_buffer
            line_buffer = ''


def load_songs(text_lines):
    Songs = {}

    def add_song(artist, title):
        if artist not in Songs:
            Songs[artist] = []
        Songs[artist].append(title)

    extract_data_re = re.compile(
        r"\d{1,3}\s?-\s?((?:\S|\S )+)(?:\s{2}\s*|-)((?:\S|\S )+)\s{2}\s*\d{4}")
    for line in song_entries(text_lines):
        match = extract_data_re.match(line)
        if match:
            (song_name, song_artist) = extract_data_re.match(line).groups()
            add_song(song_artist, song_name)

    return Songs


def load_songs_from_file(song_file_name):
    if not os.path.isfile(song_file_name):
        terminate("Failed to find the file " + song_file_name)

    with open(song_file_name, "r") as f:
        return load_songs(f.readlines())


Songs = load_songs_from_file("100worst.txt")

# ------------- / Socket Programming
OPERATION_FAILURE = 'Operation-Failed'  # Opaque value to indiciate failure


def safe_execute(failure, operation, return_arity=1):
    try:
        return operation()
    except Exception:
        failure()
        return (OPERATION_FAILURE,)*return_arity


def accept_artist_name(clientSock, addr):
    # Accepting 1024 bytes means at most we can handle a song artist whos name can
    # be up to 1024 letters. I feel this is a same assumption.
    return clientSock.recv(1024).decode()


def wait_for_close_request(clientSock):
    clientSock.recv(1024)
    clientSock.close()


def listen_on_socket(serverSock):
    serverSock.listen(1)
    serverSock.settimeout(None)

    log("Server Started")

    while True:
        clientSock, addr = safe_execute(
            failure=lambda: log(
                "Failed to receive a connection from the client"),
            operation=lambda: serverSock.accept(),
            return_arity=2)

        if clientSock == OPERATION_FAILURE:
            return
        log("Received a connection from {0}".format(addr))

        time_connected = time.time()

        def report_connection_terminated(reason):
            def _report():
                connection_length = time.time()-time_connected
                log("Connection terminated. Duration {0}. Reason {1}".format(
                    connection_length, reason))
            return _report

        artist_name = str(safe_execute(
            failure=report_connection_terminated(
                "Failed to receive an artist from the client"),
            operation=lambda: accept_artist_name(clientSock, addr)))

        if artist_name == OPERATION_FAILURE:
            return

        log("Recevied a query request with artist {0}".format(artist_name))

        songs = Songs.get(artist_name, [])
        if not songs:
            log("Client requested artist `{0}` that does not exist in our records".format(
                artist_name))

        op_success = safe_execute(
            failure=report_connection_terminated(
                "Connection was closed by client before response was sent"),
            operation=lambda: clientSock.send(pickle.dumps(songs)))

        if op_success == OPERATION_FAILURE:
            return
        log("Sent response with {0} songs in.".format(len(songs)))

        op_success = safe_execute(
            failure=report_connection_terminated(
                "Client never sent close request"),
            operation=lambda: wait_for_close_request(clientSock))
        if op_success == OPERATION_FAILURE:
            return
        log("Connection successfully closed.")


def launch_server():
    with socket(AF_INET, SOCK_STREAM) as serverSock:
        # try to bind to port, listening for OSError if port already in use.
        try:
            serverSock.bind((HOST, PORT))
        except OSError:
            log("Failed to bind to host %s on port %d" % (HOST, PORT))
            return
        except Exception as e:
            log("Failed to open server for reason `%s`" % (str(e)))
            return

        listen_on_socket(serverSock)
    log_file.close()


log('Attempting launch server on %s:%d' % (HOST, PORT))
launch_server()
