from socket import *

HOST, PORT = '127.0.0.1', 25000

with socket(AF_INET, SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    input = input('Enter artist to lookup> ')

    s.send(input.encode())

    s.close()