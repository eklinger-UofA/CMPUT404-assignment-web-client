#!/usr/bin/env python
# coding: utf-8

# Copyright 2014 Eric Klinger
#
# class HTTPClient.
# Serve as a semi-HTTP 1.1 client. Send http requests and parse the
# responses from a http server
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sys
import socket
import re
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        try:
            return int(url.split(':')[2].split('/')[0])
        except:
            return 80

    def connect(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host,port))
        return s

    def get_code(self, data):
        lines = data.splitlines()
        response_header = lines[0]
        tokens = response_header.split(" ")
        return int(tokens[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        lines = data.splitlines()
        body_index = lines.index('')+1
        body_lines = lines[body_index:]

        body = ""
        for line in body_lines:
            body += line
            body += '\r\n'

        return body

    def get_host(self, url, port):
        host_name = url.split('/')[2].split(':%s' % port)[0]
        return host_name

    def get_path(self, url, host, port):
        if port != 80:
            host = host + ":" + str(port)
        path = url.split(host)[-1]
        if not path:
            path = '/'
        return path

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        port = self.get_host_port(url)
        host = self.get_host(url, port)
        s = self.connect(host, port)
        get_path = self.get_path(url, host, port)

        request = ""
        request += "GET %s HTTP/1.1\r\n" % get_path
        request += "Host: %s\r\n" % host
        request += "Accept: */*\r\n\r\n"
        s.send(request)

        data = self.recvall(s).strip()
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        port = self.get_host_port(url)
        host = self.get_host(url, port)
        s = self.connect(host, port)
        get_path = self.get_path(url, host, port)

        body = ""
        if args:
            body = urllib.urlencode(args)

        request = ""
        request += "POST %s HTTP/1.1\r\n" % get_path
        request += "Host: %s\r\n" % host
        request += "Accept: */*\r\n"
        request += "Content-Length: %d\r\n" % len(body)
        request += "Content-Type: application/x-www-form-urlencoded\r\n\r\n"
        if body:
            request += body
            request += "\r\n"
        s.send(request)

        data = self.recvall(s).strip()
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )
