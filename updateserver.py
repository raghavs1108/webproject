import sqlite3
from gevent import monkey; monkey.patch_all()
from gevent import sleep
import time
import bottle
import sys
from bottle import get, post, request, response
from bottle import GeventServer, run
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors

@get('/')
@enable_cors
def receiveupdate():
	prev = -1;
	# broadcast the data in the group chat to all the users...
	response.content_type  = 'text/event-stream'
	response.cache_control = 'no-cache'
	# Set client-side auto-reconnect timeout, ms.
	while True:
		f = open("datafile.txt")
		lines = f.readlines()
		cur = int(lines[-1].split(":")[0])
		yield 'retry: 100\n'
		if cur != prev:
			prev = cur
			data = lines[-1].split(":")
			yield 'data: '+ data[1]+";"+data[2]+"\n\n"
		f.close()


if __name__ == '__main__':
	run(host="127.0.0.1", port=8081, server=GeventServer)