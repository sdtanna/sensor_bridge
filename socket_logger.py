import logging
class socket_logger(logging.StreamHandler):
    def __init__(self,socket_handler):
        super().__init__()
        self.sh = socket_handler
    def emit(self, record):
        msg = self.format(record)
        if self.sh.connected:
            self.sh.send_data_to_websocket("log", msg)