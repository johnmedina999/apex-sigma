import logging
import zmq


class DataSender():

    context = zmq.Context()

    def __init__(self, port):
        self.logger = logging.getLogger(__class__.__name__)
        self.socket = DataSender.context.socket(zmq.PUSH)
        self.socket.connect('tcp://127.0.0.1:%s' % port)


    def __del__(self):
        self.socket.close()


    def send_data(self, data):
        try: self.socket.send_json(data, zmq.NOBLOCK)
        except zmq.error.Again: pass
