from socket import *
import os
from datetime import *

methods_valid = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'CONNECT', 'TRACE']
methods_supported = ['GET', 'POST']



serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

print('The server is ready to receive')

def is_valid_syntax(head):
    method, path, vers = head.split()
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
    
def create_response(code, file_or_error):
    return (f'HTTP/1.1 {code}\r\n'
                    'Content-Type: text/html\r\n'
                    f'{file_or_error}'
                    ) 

def handle_request(request):

    head = request.split('\n')[0]

    if (is_valid_syntax(head)):
        # print('valid syntax')
        if(is_supported(head)):
            # print('is supported')
            if(has_valid_path(head)):
                # print('Valid part')
                #accessing file:
                file_path = './test.html'
                file_last_modified = os.stat(file_path).st_mtime
                if(has_if_mod_since(request)):
                    if_modified_since = head.split()[3].split(':')[1]
                    client_time = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT').timestamp()
                    if client_time < file_last_modified:
                        return ('HTTP/1.1 304 Not Modified\r\n\r\n')
                else:
                    code="200 OK"
                    with open(file_path, 'r') as file:
                        file_content = file.read()
                    file_or_error = (f'Last Modified: {datetime.fromtimestamp(file_last_modified, tz=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")}\r\n'
                                     '\r\n'
                                     f'{file_content}')
                    return create_response(code, file_or_error)
                    #print('return relevant repsponse for 200 OK')
            else:
                code="404 Not Found"
                file_or_error = f'\r\n<html><body><h1>{code}</h1><p>The request could not be understood by the server due to malformed syntax.</p></body></html>'
                return create_response(code, file_or_error)

        else:
            code="501 Not Implemented"
            file_or_error = f'\r\n<html><body><h1>{code}</h1><p>The server does not support the functionality required to fulfill the request.</p></body></html>'
            return create_response(code, file_or_error)
            
        
    else:
        code="400 Bad Error"
        file_or_error = f'\r\n<html><body><h1>{code}</h1><p>The request could not be understood by the server due to malformed syntax.</p></body></html>'
        return create_response(code, file_or_error)

while True:
    connectionSocket, addr = serverSocket.accept()
    request = connectionSocket.recv(1024).decode()

    response = handle_request(request)

    connectionSocket.send(response.encode())

    connectionSocket.close()

    