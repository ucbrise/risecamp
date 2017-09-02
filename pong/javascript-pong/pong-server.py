from __future__ import print_function, absolute_import
from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import mimetypes
mimetypes.init()
import os
import requests
from datetime import datetime
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%y-%m-%d:%H:%M:%S',
    level=logging.INFO)

logger = logging.getLogger(__name__)



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
        logger.info("local path {}".format(local_path))
        if not in_static_dir(local_path):
            self.send_error(403, "Forbidden")
        elif not os.path.exists(local_path) or not os.path.isfile(local_path):
            self.send_error(404, "Not Found")
        else:
            with open(local_path, "rb") as f:
                self.send_response(200)
                mtype, encoding = mimetypes.guess_type(local_path)
                self.send_header('Content-Type', mtype)
                self.end_headers()
                self.wfile.write(f.read())
                return

    def do_POST(self):
        clipper_url = "http://localhost:1337/pong/predict"
        content_length = int(self.headers['Content-Length'])
        req_json = self.rfile.read(content_length)
        headers = {'Content-Type': 'application/json'}
        start = datetime.now()
        clipper_response = requests.post(clipper_url, headers=headers, data=req_json)
        end = datetime.now()
        latency = (end - start).total_seconds() * 1000.0
        logger.info("Clipper responded with '{txt}' in {time} ms".format(
            txt=clipper_response.text, time=latency))
        self.send_response(clipper_response.status_code)
        # Forward headers
        for k, v in clipper_response.headers:
            logger.info("Adding response header [{k}, {v}]".format(k=k, v=v))
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(clipper_response.text)


class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass


def run(port=3000):
    server_addr = ('', port)
    logger.info("Starting Pong Server on {}".format(server_addr))
    server = ThreadingServer(server_addr, PongServer)
    server.serve_forever()

if __name__ == '__main__':
    run()
