import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler

class HttpHandler(SimpleHTTPRequestHandler):
    pass

def serve(site):
    server_address = ('', int(site.cli_options.port) or 0)
    httpd = HTTPServer(server_address, HttpHandler)
    os.chdir(site.output_path)
    print("Listening on {}:{} from {}".format(httpd.server_name, httpd.server_port, os.getcwd()))
    httpd.serve_forever()

def serve_standalone(site):
    """ start and serve in a new thread """
    thread = threading.Thread(target=serve, args=([site]), name="sitekicker-server")
    return thread
