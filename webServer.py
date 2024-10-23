from socket import *
import os
from datetime import *
import threading

methods_valid = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'CONNECT', 'TRACE']
methods_supported = ['GET', 'POST']

cache = {}  #a dictionary that will cache responses. 

# serverPort = 8080
# serverSocket = socket(AF_INET, SOCK_STREAM)
# serverSocket.bind(('',serverPort))
# serverSocket.listen(5)

print('The server is ready to receive')

def is_valid_syntax(head):
    if(len(head.split()) != 3):
        return False
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


# these functions are now obsolete for part 3: 

# def has_valid_path(head):   
#     path = head.split()[1]
#     if os.path.isfile(path.strip('/')):
#         return True
#     else:
#         return False

# def has_if_mod_since(request):
#     if 'If-Modified-Since' in request:
#         return True
#     else:
#         return False
    
def create_response(code, file_or_error):
    return (f'HTTP/1.1 {code}\r\n'
                    'Content-Type: text/html\r\n'
                    f'{file_or_error}'
                    ) 


def ask_origin_server_or_cache(method, path, headers): 
    # first check if we have url as a key in our cache
    if path in cache:
        print("Cache Hit")
        return cache[path]

    print("Cache Miss")
    host_line = [line for line in headers.split('\n') if line.startswith("Host:")]
    if not host_line:
        return "HTTP/1.1 400 Bad Request\r\n\r\n"  # Host header is required for HTTP/1.1
    hostname  =host_line[0].split()[1]  # Extract hostname from 'Host: ' line
    originSocket = socket(AF_INET, SOCK_STREAM)

    #hostname = path.split('/')[2]
    port = 80
    if(path):
        originSocket.connect(hostname, port)
        originSocket.send(f"{method} {path} HTTP/1.1\r\rHost: {hostname}\r\n\r\n".encode())

        response = b""
        while True: 
            part = originSocket.recv(1024)
            if not part:
                break
            response += part

        originSocket.close()
        cache[path] = response.decode()
        return response.decode()
    # if yes, return the value associated with it
    # if not, ask contact origin server
    # if their reposne is successfull (200 Ok),add it to cache
    # return the response (whatever it was)
    return response



def handle_request(request):
    head = request.split('\n')[0]

    if (is_valid_syntax(head)):
        #print('valid syntax')
        if(is_supported(head)):
            # Obsolete for part 3: 
            #print('is supported')
            #print('Valid part')
            #accessing file:


            # file_path = './test.html'
            # file_last_modified = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
            # if(has_if_mod_since(request)):
            #     #print("has request")
            #     if_modified_since = request.split('\n')[4]
            #     if_modified_since = if_modified_since.replace('If-Modified-Since: ', '').strip()
            #     client_time = datetime.strptime(if_modified_since, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=timezone.utc)
            #     if client_time.timestamp() >= file_last_modified.timestamp():
            #         response = ('HTTP/1.1 304 Not Modified\r\n\r\n')
            #         return response
            # code="200 OK"
            # file_last_modified_str = file_last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
            # with open(file_path, 'r') as file:
            #     file_content = file.read()
            # file_or_error = (f'Last Modified: {file_last_modified_str}\r\n'
            #                 '\r\n'
            #                 f'{file_content}')
            # return create_response(code, file_or_error)
            # #print('return relevant repsponse for 200 OK')

            print(request)
            method, path, vers = head.split()   # separate sections for further checks
            headers = request.split('\n', 1)[1] # extracting the rest of the header (not request line)

            try:

                response = ask_origin_server_or_cache(method,path, vers + headers)
                print(repr(response))
                #print(response)
                responseHead = response.split(b'\r\n\r\n', 1)[0] #get the header in bytes, split at double \r\n\r\n
                #print(responseHead) 
                status = responseHead.split(b'\r\n')[0].decode()  # split the header to get the first value i.e. the status code 
                #print(status)
                responseBody = response.split(b'\r\n\r\n', 1)[1]  # get the part after the first set of two \r\n\r\n = body
                #print(responseBody)

                if ("200 OK" in status) or ('404 Not Found' in status) or ('304 Not Modified' in status) :
                    return response.decode()

            except Exception as dne:
                code="400 Bad Request"
                file_or_error = f'\r\n<html><body><h1>{code}</h1><p>400 Bad Request (Syntax Error)</p></body></html>'
                return create_response(code, file_or_error)

        else:
            code="501 Not Implemented"
            file_or_error = f'\r\n<html><body><h1>{code}</h1><p>The server does not support the functionality required to fulfill the request.</p></body></html>'
            return create_response(code, file_or_error)
            
        
    else:
        code="400 Bad Request"
        file_or_error = f'\r\n<html><body><h1>{code}</h1><p>The request could not be understood by the server due to malformed syntax.</p></body></html>'
        return create_response(code, file_or_error)\


def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    response = handle_request(request)
    client_socket.send(response.encode()) 
    client_socket.close()

def start_server():
    serverPort = 8081
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen(5)  #maximum 5 connections at a time

    while True:
        connectionSocket, addr = serverSocket.accept()
        #request = connectionSocket.recv(1024).decode()

        connection_handler = threading.Thread(target=handle_client, args=(connectionSocket,))
        connection_handler.start()
        #response = handle_request(request)

        #connectionSocket.send(response.encode())

        #connectionSocket.close()

if __name__ == "__main__":
    start_server()