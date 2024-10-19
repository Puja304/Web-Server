from socket import *

methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'CONNECT', 'TRACE']
methods_supported = ['GET', 'POST']

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


def is_valid_syntax(request):
    return True

def is_supported(head):
    return True

def has_valid_path(head):
    return True

def has_if_not_mod(request):
    return True

def notModded(request):
    return True

def handle_request(request):
    head = request.split('\n')[0]

    if (is_valid_syntax(head)):
        print('valid syntax')
        if(is_supported(head)):
            print('is supprted')
            if(has_valid_path(head)):
                print('Valid part')
                if(has_if_not_mod(request)):
                    print("run function to see if it has been modified")
                    print('If not modified: return relevant repsponse for  304 Not Modified')
                else:
                    print('return relevant repsponse for 200 OK')
            else:
                print("return relevant repsponse for 404 Not Found")

        else:
            print('return relevant repsponse for 501 Not Implemented')
        
    else:
        return 'return relevant repsponse for 400 Bad Error'

while True:
    connectionSocket,addr = serverSocket.accept()
    request = connectionSocket.recv(1024).decode()

    response = handle_request(request)

    connectionSocket.send(response.encode())

    connectionSocket.close()