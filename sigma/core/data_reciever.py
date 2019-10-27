import time
import zmq


class DataReciever():

    context = zmq.Context()

    def __init__(self, port, handler):
        self.handler = handler

        self.socket = DataReciever.context.socket(zmq.PULL)
        self.socket.connect('tcp://127.0.0.1:%s' % port)

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)


    async def read_data(self, args):
        if self.poller.poll(0.1*1000): 
            await self.handler(self.socket.recv_json(), *args)