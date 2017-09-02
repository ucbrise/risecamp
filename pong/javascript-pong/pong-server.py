from __future__ import print_function, absolute_import
# import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import mimetypes
mimetypes.init()
import os


PORT = 3000

# NOTE: This is definitely not secure
def in_static_dir(file):
    directory = os.path.abspath("static/")
    #make both absolute
    directory = os.path.join(os.path.realpath(directory), '')
    file = os.path.realpath(file)

    #return true, if the common prefix of both is equal to directory
    #e.g. /a/b/c/d.rst and directory is /a/b, the common prefix is /a/b
    return os.path.commonprefix([file, directory]) == directory

class PongServer(BaseHTTPRequestHandler):

    def _respond_not_found(self):
        pass

    # GET requests serve the corresponding file from the "static/" subdirectory
    def do_GET(self):

        local_path = os.path.abspath(os.path.join("static", self.path.lstrip("/")))
        print("local path {}".format(local_path))
        if not in_static_dir(local_path):
            self.send_error(403, "Forbidden")
        elif not os.path.exists(local_path) or not os.path.isfile(local_path):
            self.send_error(404, "Not Found")
        else:
            with open(local_path, "rb") as f:
                self.send_response(200)
                mtype, encoding = mimetypes.guess_type(local_path)
                self.send_header('Content-type', mtype)
                self.end_headers()
                self.wfile.write(f.read())
                return






        # self.send_response(200)
        # self.send_header('Content-type', 'text/html')
        # self.end_headers()
        # self.wfile.write("<html><body><h1>hello world</h1></body></html>")




def run(server_class=HTTPServer, handler_class=PongServer, port=3000):
        server_addr = ('', port)
        server = server_class(server_addr, handler_class)
        server.serve_forever()

if __name__ == '__main__':
    run()
