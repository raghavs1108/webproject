import sqlite3
from gevent import monkey; monkey.patch_all()
from gevent import sleep
from gevent import Greenlet
from gevent.coros import BoundedSemaphore
import time
import bottle
import sys
from bottle import get, post, request, response
from bottle import GeventServer, run
from gevent.pool import Group
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

sse_test_page = """
<!DOCTYPE html>
<html>
	<head>
		<meta charset="UTF-8" />
		<script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/1.8.3/jquery.min.js "></script>
		<script>
			$(document).ready(function() {
				var es = new EventSource("stream");
				es.onmessage = function (e) {
					$("#log").html($("#log").html()
						+ "<p>Event: " + e.event + ", data: " + e.data + "</p>");
				};
			})
		</script>
	</head>
	<body>
		<div id="log" style="font-family: courier; font-size: 0.75em;"></div>
	</body>
</html>
"""
con = None
try:
    con = sqlite3.connect('chatty.db')
    cur = con.cursor()
except Exception as e:
	print "Exception occured "+e.args[0]
except Error as e:
	print "error occured "+ e.args[0] 

query = "CREATE TABLE IF NOT EXISTS user (username PRIMARY KEY NOT NULL, password NOT NULL); "
cur.execute(query)
query = "SELECT * FROM user;"
cur.execute(query)
print cur.fetchall()


@get('/')
@enable_cors
def index():
	return sse_test_page

@get('/checkuser/:username')
@enable_cors
def checkuser(username):
	# connect to mysql server, check if the user exists, and if so, return his password. Otherwise, return the string "error: not registered"
	query = "SELECT * FROM user WHERE username=?"
	cur.execute(query, (username,))
	res = cur.fetchall()
	print username
	print res
	if len(res) > 0:
		print res
		return res[0][0]+";"+res[0][1]
	else :
		return "unregistered"

@get('/registeruser/:username/:password')
@enable_cors
def registeruser(username, password):
	# connect to mysql server, check if the user exists, and if so, return his password. Otherwise, return the string "error: not registered"
	query = "SELECT * FROM user WHERE username=?"
	cur.execute(query, (username,))
	res = cur.fetchall()
	if len(res) > 0:
		print res
		return "already registered"
	else :
		query = "INSERT INTO user VALUES(?, ?)"
		cur.execute(query, (username,password))
		return "registered"


fileModified = False
@get('/updateserver/:username/:data')
@enable_cors
def updateserver(username, data):
	global fileModified
	# perform file or database update
	f = open("datafile.txt", mode="rw+")
	lines = f.readlines()
	index = 0
	if len(lines) > 0:
		# already created.
		lastLine = lines[-1]
		index = int(lastLine.split(":")[0])
		index = index+1
		f.write(str(index)+":"+username+":"+data+"\n")
	else:
		f.write(str(0)+":"+username+":"+data+"\n")
	f.close()
	return str(index)+":"+username+":"+data+"\n"
	fileModified = True 

sem = BoundedSemaphore()

class Chatlet(Greenlet):

    def __init__(self, message, n):
        Greenlet.__init__(self)
        self.message = message
        self.n = n
        print 'Hello World'

    def _run(self):
        print(self.n)
        print 'Hello World'
        prev = -1; 
        while True:
            print self.n
            sleep(2)
            sem.acquire()
            f = open("datafile.txt")
            lines = f.readlines()
            f.close()
            print 'Im in', self.n
            sem.release()
            cur = int(lines[-1].split(":")[0])
            print cur
            if cur != prev:
                prev = cur 
                data = lines[-1].split(":")
                #print 'data:'
                yield 'data: '+ data[1]+";"+data[2]+"\n\n"
            '''
            yield 'retry: 100\n'
            if cur != prev:
                prev = cur 
                data = lines[-1].split(":")
                yield 'data: '+ data[1]+";"+data[2]+"\n\n"
            '''
        '''
        
        prev = -1; 
        # broadcast the data in the group chat to all the users...
        # Set client-side auto-reconnect timeout, ms.
        while True:
            print(self.n)
            f = open("datafile.txt")
            lines = f.readlines()
            cur = int(lines[-1].split(":")[0])
            yield 'retry: 100\n'
            if cur != prev:
                prev = cur 
                data = lines[-1].split(":")
                yield 'data: '+ data[1]+";"+data[2]+"\n\n"
            f.close()
        '''

N = 1
@get('/requestupdate')
def request_update():
    global N
    thread = Chatlet.spawn('Hello', N)
    N += 1


if __name__ == '__main__':
	run(host="127.0.0.1", port=8080, server=GeventServer)
