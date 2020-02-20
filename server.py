from multiprocessing import Process, Queue, Value
import argparse
import readline

import falcon

import control 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Drawbot control server.')
    parser.add_argument('method', nargs='?', default='http',
        choices=['http', 'cli'],
        help='Determines the method used for input'
        )
    args = parser.parse_args()

    q = Queue()
    completion = Value('f', -1)

    printer = Process(target=control.run_printer, args=(q, completion))
    printer.start()

    if args.method == 'cli':
        cmd = input('drawbot> ')
        while cmd != 'STOP':
            q.put([cmd])    
            cmd = input('drawbot> ')
        q.put('STOP')

    printer.join()

