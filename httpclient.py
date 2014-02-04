#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        """ Get the host port from the URL.

        URL should be in this form:
        print("http://%s:%d/dsadsadsadsa\n" % (BASEHOST,BASEPORT) )

        """
        try:
            return int(url.split(':')[2].split('/')[0])
        except:
            return 80

    def connect(self, host, port):
        """
        HOST = ''   # Symbolic name meaning the local host
        PORT = 24069    # Arbitrary non-privileged port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        """
        # use sockets!
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

    def get_get_path(self, url, host, port):
        if port != 80:
            host = host + ":" + str(port)
        print "splitting url on this host: %s" % host
        path = url.split(host)[-1]
        print "Got this path from the url: %s" % path
        if not path:
            path = '/'
        return path

    # read everything from the socket
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
        """
        GET / HTTP/1.1\r\n
        User-Agent: curl/7.29.0\r\n
        Host: slashdot.org\r\n
        Accept: */*\r\n
        \r\n
        """
        port = self.get_host_port(url)
        print port
        host = self.get_host(url, port)
        #s = self.connect('localhost', port)
        s = self.connect(host, port)
        addrInfo = socket.getaddrinfo(host, port)

        print "trying to GET from this url: %s" % url
        #get_path = url.split(':%s' % port)[-1]
        get_path = self.get_get_path(url, host, port)

        request = ""
        request += "GET %s HTTP/1.1\r\n" % get_path
        #request += "User-Agent: curl/7.29.0\r\n"
        #request += "User-Agent: curl/7.21.4 (universal-apple-darwin11.0) libcurl/7.2 1.4 OpenSSL/0.9.8y zlib/1.2.5\r\n"
        request += "Host: %s\r\n" % host
        request += "Accept: */*\r\n\r\n"
        print "sending this request:\n %s" % request
        s.send(request)
        data = self.recvall(s).strip()
        #print "Return start ***********************"
        #lines = return_value.splitlines()
        #print "lines: %s" % lines
        #print return_value
        #print "Return end *************************"
        #response_header = lines[0]
        #print "header: %s" % response_header
        #tokens = response_header.split(" ")
        #print "tokens: %s" % tokens

        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        port = self.get_host_port(url)
        print port
        host = self.get_host(url, port)
        socket = self.connect('localhost', port)

        print "trying to POST from this url: %s" % url
        #get_path = url.split(':%s' % port)[-1]
        get_path = self.get_get_path(url, host, port)

        """
        body = ""
        print "args.keys: %s" % args.keys()
        print "args.values: %s" % args.values()
        for key in args.keys():
            value = "%s" % args[key][0]
            print "Key: %s and value: %s" % (key, value)
            body += "%s=%s&" % (key, args[key])
        body = body.rstrip('&')
        """
        body = ""
        if args:
            body = urllib.urlencode(args)

        request = ""
        request += "POST %s HTTP/1.1\r\n" % get_path
        #request += "User-Agent: curl/7.29.0\r\n"
        request += "Host: %s\r\n" % host
        request += "Accept: */*\r\n"
        #request += "Content-Length: %d\r\n" % sys.getsizeof(body)
        request += "Content-Length: %d\r\n" % len(body)
        request += "Content-Type: application/x-www-form-urlencoded\r\n\r\n"
        if body:
            request += body
            request += "\r\n"

        print "sending this request: %s" % request
        socket.send(request)
        data = self.recvall(socket).strip()

        print "data from the socket: %s" % data

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
