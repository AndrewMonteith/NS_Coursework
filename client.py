from socket import *
import pickle

HOST, PORT = '127.0.0.1', 25000

with socket(AF_INET, SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    input = input('Enter artist to lookup> ')

    s.send(input.encode()) # Could be connection reset error here

    # Assumption for return size: Song Title < 1kb, Max number of songs stored per artist = 4 => 4096 bytes.
    songs = pickle.loads(s.recv(4096))

    if not songs:
        print("Arist `%s` does have any songs" % input)
    else:
        for song in songs:
            print("FOUND SONG:", song)

    s.close()