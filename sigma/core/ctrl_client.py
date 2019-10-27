
import time
import zmq


class CtrlClient():

    context = zmq.Context()

    def __init__(self, logger, port, handler):
        self.logger  = logger
        self.handler = handler
        self.socket  = None
        self.port    = port
        
        self.__register()


    async def request(self, data, args):
        try: self.socket.send_json(data, zmq.NOBLOCK)
        except zmq.error.Again:
            self.logger.error('Request failed to send')
            return False

        if self.poller.poll(0.1*1000): 
            await self.handler(self.socket.recv_json(), *args)
            return True
        else:
            self.logger.error('Timed out')
            self.__register()
            return False
            

    def __register(self):
        if self.socket != None: self.socket.close()
        self.socket = CtrlClient.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.connect("tcp://127.0.0.1:%s" % self.port)

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
