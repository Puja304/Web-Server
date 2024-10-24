from socket import *
import os
from datetime import *
import threading

# will be used for syntax check for 400 bad request
methods_valid = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'CONNECT', 'TRACE']
methods_supported = ['GET']

cache = {}  #a dictionary that will cache responses. 

# serverPort = 8080
# serverSocket = socket(AF_INET, SOCK_STREAM)
# serverSocket.bind(('',serverPort))
# serverSocket.listen(5)


# checks for method validity and syntax validity
def is_valid_syntax(head):
    if(len(head.split()) != 3):
        return False
    method, path, vers = head.split()
    inMethods = method in methods_valid
    if (inMethods and path and vers.startswith('HTTP/')):
        return True
    else:
        return False            

#checks for method compatibality. must have passed is_valid_syntax before reaching here
def is_supported(head):
    method = head.split()[0]
    print(f'Method: {method}')
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
    
#creates a basic response for status codes that we generate
def create_response(code, file_or_error):
    return (f'HTTP/1.1 {code}\r\n'
                    'Content-Type: text/html\r\n'
                    f'{file_or_error}'
                    '\r\n\r\n'
                    ) 


# def ask_origin_server_or_cache(method, path, headers): 
#     # first check if we have url as a key in our cache
#     if path in cache:
#         print("Cache Hit")
#         return cache[path]

#     print("Cache Miss")
#     host_line = [line for line in headers.split('\n') if line.startswith("Host:")]
#     if not host_line:
#         return "HTTP/1.1 400 Bad Request\r\n\r\n"  # Host header is required for HTTP/1.1
#     hostname  =host_line[0].split()[1]  # Extract hostname from 'Host: ' line
#     originSocket = socket(AF_INET, SOCK_STREAM)

#     #hostname = path.split('/')[2]
#     port = 80
#     if(path):
#         originSocket.connect(hostname, port)
#         print(hostname)
#         originSocket.send(f"{method} {path} HTTP/1.1\r\rHost: {hostname}\r\n\r\n".encode())

#         response = b""
#         while True: 
#             part = originSocket.recv(1024)
#             if not part:
#                 break
#             response += part

#         originSocket.close()
#         cache[path] = response.decode()
#         return response.decode()
#     # if yes, return the value associated with it
#     # if not, ask contact origin server
#     # if their reposne is successfull (200 Ok),add it to cache
#     # return the response (whatever it was)
#     return response

def ask_origin_server_or_cache(request): 
    # first check if we have url as a key in our cache
    # if yes, return the value associated with it
    # if not, ask contact origin server
    # if their reposne is successfull (200 Ok),add it to cache
    # return the response (whatever it was)
    head = request.split('\n')[0]

    # find components of request
    method, path, vers = head.split()   # separate sections for further checks
    print(path)
    # determine name of host to connect with
    host = request.split('\n')[1]
    host = host.split(':')[1]
    # Check if the response is in the cache
    if path in cache:
        print("Cache hit!")
        # if they have if-modified-since, we compare it to our cached response to see if we should send that one or get a new one
        if 'If-Modified-Since' in request:
            lines = request.split('\n')
            requested_date = ''
            for line in lines:
                if line.startswith('If-Modified-Since'):
                    print(f'The Line is:  {line}')
                    requested_date = line.split(':', 1)[1].strip()
                    print(f'requested_date = {requested_date}')
            previous = cache[path].split('\n')
            last_modified = ''

            print(f'Cached response: {cache[path]}')
            for line in previous:
                if line.startswith('Last-Modified') or line.startswith('Date'):
                    print(f'The Line is:  {line}')
                    last_modified = line.split(':', 1)[1].strip()

            if requested_date and last_modified:  # Ensure both dates are not empty
                # Convert the date strings to datetime objects
                requested_datetime = datetime.strptime(requested_date, '%a, %d %b %Y %H:%M:%S GMT')
                last_modified_datetime = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S GMT')

                # Compare the dates
                if requested_datetime < last_modified_datetime:
                    # Requested date is older than the last modified date
                    code="304 Not Modified"
                    return create_response(code, '')
                else:
                    print("Must request origin")
                    # Requested date is newer or the same, so we continue on to the normal step of requesting from original server
            
        else:
            return cache[path].encode()  # Return cached response

    print("Cache miss, querying origin server...")

    if not path:
        # default path when not mentioned
        path = '/'
    # Parse the host and path from the URL

    # Create a socket to connect to the origin server
    with socket(AF_INET, SOCK_STREAM) as proxy_socket:
        # print(f"Connecting to host: {host.strip()}")
        try:
            print('Checkpoint 0')
            # print(f'Method: {method}\n Path = {path}\n Headers = {headers}')
            proxy_socket.connect((host.strip(), 80))  # Connect to the host on port 80
            # request_line = (f'{method} {path} HTTP/1.1\r\n'
            #                 f'Host: {host}\r\n'
            #                 f'{headers}'
            #                 'Connection: close\r\n\r\n')
            print('Checkpoint 1')
            # print(request_line)
            # proxy_socket.sendall(request_line.encode())
            print(request)
            #making sure we remove the connection header from our proxy request
            if('Connection' in request):
                lines = request.splitlines()
                # Create a new list without the 'Connection' header
                filtered_lines = [line for line in lines if not (line.startswith("Connection:") or line.startswith('Proxy-Connection'))]
                # Join the filtered lines back into a single string
                modified_request = "\r\n".join(filtered_lines)
                modified_request = modified_request + '\r\n'
                print(f'Modified Request: {modified_request}')

            # send the rest of the request as is
            proxy_socket.sendall(modified_request.encode())
            print('Checkpoint 2')
            response = b""
            print('Checkpoint 3')
            while True:
                print('Checkpoint 4')
                # receive the response
                part = proxy_socket.recv(4096)
                print('Checkpoint 5')
                if not part:
                    break
                response += part
                # only cache it if it's 200 OK
                if '200 OK' in response.decode():
                    cache[path] = response.decode()
                
                #return the response
                return response
            # if there is an error connecting (invalid host name, etc) then we give a 404 Not Found error
        except Exception as e:
            print(e)
            return create_response('404 Not Found', '\r\n<html><body><h1>404 Not Found</h1><p>We cannot find it</p></body></html>')

    # Store the response in the cache
    print('Checkpoint 5')
    # printing for debugging purposes
    print(f'Response: {response}')
    # return response

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

            # method, path, vers = head.split()   # separate sections for further checks
            # path = path.split('/')[2]
            # host = request.split('\n')[1]
            # host = host.split(':')[1]
            # # print(f'host = {host}')
            # # print(f'path = {path}')
            # headers = request.split('\n')[1] # extracting the rest of the header (not request line)
            # print(f'Header: {headers}')
            try:
#method,path, vers + headers, host
                response = ask_origin_server_or_cache(request)
                #print(response)
                response = response.decode()
                # print("Checkpoint 6")
                # responseHead = response.split(b'\r\n\r\n', 1)[0] #get the header in bytes, split at double \r\n\r\n
                # #print(responseHead) 
                # print("Checkpoint 7")
                # status = responseHead.split(b'\r\n')[0].decode()  # split the header to get the first value i.e. the status code 
                # #print(status)
                # print("Checkpoint 8")
                # responseBody = response.split(b'\r\n\r\n', 1)[1]  # get the part after the first set of two \r\n\r\n = body
                # #print(responseBody)
                print("Checkpoint 6")
                # if ("200 OK" in response) or ('404 Not Found' in response) or ('304 Not Modified' in response):
                #         print(f'Type: {type(response)}')
                return response
            
            except Exception as dne:
                print(dne)
                # if there is an error, return it. error only occurs when it sends our own 404 or 304 response, in which case we handle it in handle_client
                return response

        else:
            code="501 Not Implemented"
            file_or_error = f'\r\n<html><body><h1>{code}</h1><p>The server does not support the functionality required to fulfill the request.</p></body></html>'
            return create_response(code, file_or_error)
            
        
    else:
        code="400 Bad Request"
        file_or_error = f'\r\n<html><body><h1>{code}</h1><p>The request could not be understood by the server due to malformed syntax.</p></body></html>'
        return create_response(code, file_or_error)


def handle_client(client_socket):
    # keeps us connected for for multiple requests
    while True:
        try:
            request = client_socket.recv(1024).decode()
            if not request:  # If the client has disconnected
                print("Client disconnected.")
                break
            
            response = handle_request(request)
            client_socket.send(response.encode())
        except Exception as e:
            print(f"Error handling request: {e}")
            break
    
    client_socket.close()

serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5)  # Maximum 5 connections

print('The server is ready to receive')

while True:
    connectionSocket, addr = serverSocket.accept()
    #request = connectionSocket.recv(1024).decode()

    connection_handler = threading.Thread(target=handle_client, args=(connectionSocket,))
    connection_handler.start()
    #response = handle_request(request)

    #connectionSocket.send(response.encode())

    #connectionSocket.close()
