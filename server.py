from multiprocessing import Process, Queue, Value
from wsgiref.simple_server import make_server
import readline
import json

import falcon

import control 


class StatusResource:
    def __init__(self, completion):
        self.completion = completion

    def on_get(self, req, resp):
        resp.body = json.dumps({
            'status': 'ready' if completion.value < 0 else 'busy',
            'completion': completion.value,
        })

class CommandResource:
    def __init__(self, q):
        self.q = q

    def on_post(self, req, resp):
        data = req.stream.read(req.content_length or 0)
        self.q.put(json.loads(data))

 
q = Queue()
completion = Value('f', -1)

printer = Process(target=control.run_printer, args=(q, completion))
printer.start()

app = falcon.API()
app.add_route('/api/status', StatusResource(completion))
app.add_route('/api/command', CommandResource(q))


if __name__ == '__main__':
    with make_server('127.0.0.1', 8000, app) as httpd:
        httpd.serve_forever()


"""
For reference, command line version of machine server:
    cmd = input('drawbot> ')
    while cmd != 'STOP':
        q.put([cmd])    
        cmd = input('drawbot> ')
    q.put('STOP')

    printer.join()
"""
