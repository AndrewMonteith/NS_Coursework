from socket import *
import datetime

HOST, PORT = '127.0.0.1', 25000

def timestamp():
    return str(datetime.datetime.utcnow())

log_file = open("server.log", "a")
def server_log(log_message):
    log_file.write(timestamp() + " : " + log_message)

def accept_artist_name(clientSock, addr):
    # Accepting 1024 bytes means at most we can handle a song artist whos name can
    # be up to 1024 letters. I feel this is a same assumption.
    raw_got = clientSock.recv(1024)
    print(raw_got)
    artist_name = raw_got.decode()
    server_log("Connection from `%s` requesting artist `%s`" % (str(addr), artist_name))
    return artist_name

def listen_on_socket(serverSock):
    serverSock.listen(1) 
    serverSock.settimeout(None) 

    while True:
        clientSock, addr = serverSock.accept()
        server_log("Received connection from %s." % (str(addr)))

        artist_name = accept_artist_name(clientSock, addr)

        print("Received artist name:", artist_name)

def launch_server():
    with socket(AF_INET, SOCK_STREAM) as serverSock:
        # try to bind to port, listening for OSError if port already in use.
        try:
            serverSock.bind((HOST, PORT))
        except OSError:
            server_log("Failed to bind to host %s on port %d" % (HOST, PORT))
            return
        except e:
            server_log("Failed to open server for reason `%s`" % (str(e)))
            return

        listen_on_socket(serverSock)
    
server_log('Attempting launch server on %s:%d' % (HOST, PORT))
launch_server()    
