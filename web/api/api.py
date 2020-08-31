from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
import cgi
import json
import sys
import subprocess
from domain_list import result_list


class RestHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>Request Received!</h1></body></html>")
        return

    def do_POST(self):
        self._set_headers()
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']})
        self.send_response(200)
        self.end_headers()
        keys_list = form.keys()
        for k in keys_list:
            if k == "domain_list":
                type_acc = form.getvalue("domain_list")
                self.wfile.write(json.dumps({'data': result_list(type_acc)}))
            if k == "check":
                output = subprocess.Popen("echo $PATH", shell=True, stdout=subprocess.PIPE)
                ips = output.communicate()[0].rstrip()
                self.wfile.write(json.dumps({'data': ips}))
        return


listen_ip = sys.argv[1]
listen_port = int(sys.argv[2])

httpd = HTTPServer((listen_ip, listen_port), RestHTTPRequestHandler)
while True:
    httpd.handle_request()
