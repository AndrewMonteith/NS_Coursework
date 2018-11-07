from socket import *
import sys, datetime, os.path, re

HOST, PORT = '127.0.0.1', 25000

#------------------------------------ / Logging

def timestamp():
    return str(datetime.datetime.utcnow())

log_file = open("server.log", "a")
def server_log(log_message):
    log_file.write(timestamp() + " : " + log_message)

def terminate(log_message):
    server_log("Terminating... Reason: " + log_message)
    sys.exit(0)

#-------------------------------------- / Song Reading
def remove_character(str, letter):
    return re.sub(letter, '', str)

def song_entries(text_lines):
    starts_with_ranking, ends_in_year = re.compile("^\d{1,3}\s?-"), re.compile("\d{4}$")
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

    extract_data_re = re.compile(r"\d{1,3}\s?-\s?((?:\S|\S )+)(?:\s{2}\s*|-)((?:\S|\S )+)\s{2}\s*\d{4}")
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

print(Songs)

raise Exception("foobar")

#-------------------------------------- / Socket Programming

def accept_artist_name(clientSock, addr):
    # Accepting 1024 bytes means at most we can handle a song artist whos name can
    # be up to 1024 letters. I feel this is a same assumption.
    raw_got = clientSock.recv(1024)
    
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
