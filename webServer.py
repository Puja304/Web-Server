from socket import *
import os

methods_valid = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'CONNECT', 'TRACE']
methods_supported = ['GET', 'POST']

serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

print('The server is ready to receive')

def is_valid_syntax(head):
    method, path, vers = head.split(" ")
    inMethods = method in methods_valid
    if (inMethods and path and vers.startswith('HTTP/')):
        return True
    else:
        return False            

def is_supported(head):
    method = head.split()[0]
    if method in methods_supported:
        return True
    else:
        return False

def has_valid_path(head):
    path = head.split()[1]
    if os.path.isfile(path.strip('/')):
        return True
    else:
        return False

def has_if_mod_since(request):
    if 'If-Modified-Since' in request:
        return True
    else:
        return False

def handle_request(request):
    head = request.split('\n')[0]

    if (is_valid_syntax(head)):
        # print('valid syntax')
        if(is_supported(head)):
            # print('is supported')
            if(has_valid_path(head)):
                # print('Valid part')
                if(has_if_mod_since(request)):
                    print("run function to see if it has been modified")
                    print('If not modified: return relevant response for  304 Not Modified')
                else:
                    response="200 OK"
                    return
                    #print('return relevant repsponse for 200 OK')
            else:
                response="404 Not Found"
                return
                #print("return relevant repsponse for 404 Not Found")

        else:
            response="501 Not Implemented"
            return
            #print('return relevant repsponse for 501 Not Implemented')
        
    else:
        reponse="400 Bad Error"
        return
        #return 'return relevant repsponse for 400 Bad Error'

while True:
    connectionSocket, addr = serverSocket.accept()
    request = connectionSocket.recv(1024).decode()

    response = handle_request(request)

    connectionSocket.send(response.encode())

    connectionSocket.close()

    