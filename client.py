''' 
    Differnet Errors I've encounted:
        Enter artist to lookup> foobar
            Traceback (most recent call last):
            File "client.py", line 14, in <module>
                songs = pickle.loads(s.recv(4096))
            ConnectionAbortedError: [WinError 10053] An established connection was aborted by the software in your host machine
'''

from socket import *
import pickle, datetime, time, sys

HOST, PORT = '127.0.0.1', 25000

# ------------------------ / Logging
def timestamp():
    return str(datetime.datetime.utcnow())

log_file = open("client.log", "a")
def log(log_message):
    log_file.write(timestamp() + " : " + log_message + "\n") 
    
def terminate(log_message):
    log("Terminating... Reason: " + log_message)
    sys.exit(0)
# ------------------------ / Client 
OPERATION_FAILURE = 'Operation-Failed' # Opaque value to indiciate failure
def safe_execute(failure, operation, return_arity=1):
    try:
        return operation()
    except Exception:
        failure()
        return (OPERATION_FAILURE,)*return_arity 

def send_close_request(socket):
    input("Press `Enter` to close connection.")
    socket.send("quit".encode())

with socket(AF_INET, SOCK_STREAM) as s:
    safe_execute(
        failure=lambda: terminate("Fail to establish a connection to server"),
        operation= lambda: s.connect((HOST, PORT))
    )
    log("Established connection")

    print("Prompting for response")
    artist_input = input('Enter artist to lookup >')

    safe_execute(
        failure=lambda: terminate("Server refused query, connection closed?"),
        operation=lambda: s.send(artist_input.encode()))
    log("Sent request `{0}` to server".format(artist_input))
    
    # Assumption for return size: Song Title < 1kb, Max number of songs stored per artist = 4 => 4096 bytes.
    time_now = time.time()
    response = safe_execute(
        failure=lambda: terminate("Failed to receive a response."),
        operation= lambda: s.recv(4096))

    duration = time.time()-time_now

    log("Took {0} seconds to get a respnose".format(duration))
    log("Length is {0} bytes".format(len(response)))
    songs = safe_execute(
        failure=lambda: terminate("Server response was malformed"),
        operation = lambda: pickle.loads(response))

    if not songs:
        print("Arist `{0}` does have any songs".format(artist_input))
    else:
        for song in songs:
            print("FOUND SONG:", song)
    
    safe_execute(
        failure=lambda: terminate("Server refused close-connection request, has it already been closed?"),
        operation= lambda: send_close_request(s)
    )
    log("Sent Close Request")