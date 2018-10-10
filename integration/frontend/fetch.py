#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import _mysql
import json

class PongResultsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        c = _mysql.connect(host='risecamp-integration.ce3rlnajlapb.us-east-1.rds.amazonaws.com', user='risecamp', passwd='risecamp', db='risecamp')
        c.query('select ai_type, sum(ai_score), sum(human_score) from results group by ai_type;')
        r = c.use_result()

        x = r.fetch_row()
        result = {}
        while x != ():
            result[str(x[0][0], 'utf-8')] = int(x[0][1]) - int(x[0][2])
            x = r.fetch_row()

        c.close()

        self.send_response(200, 'ok')

        self.send_header('content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")

        self.end_headers()
        self.wfile.write(bytes(json.dumps(result), 'utf-8'))

if __name__ == '__main__':
    httpd = HTTPServer(('localhost', 2000), PongResultsHandler)
    httpd.serve_forever()

