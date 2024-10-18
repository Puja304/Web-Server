from socket import *

methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'CONNECT', 'TRACE']

serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

print('The server is ready to receive')

def is_valid_syntax(request):
    head = request.split('\n')[0]
    method, path, vers = head.split("")
    inMethods = method in methods
    if (method == methods[inMethods]) and path and vers:
        return True
    else:
        return False 


def handle_request(request):
    #head = request.split('\n')[0]
    #print(f"Head: {head}")
    return 'some response'

while True:
    connectionSocket,addr = serverSocket.accept()
    request = connectionSocket.recv(1024).decode()

    response = handle_request(request)

    connectionSocket.send(response.encode())

    connectionSocket.close()