import logging

def only_when_not_empty(func):
    def new(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return
    return new

def set_logger_format():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt = '%m/%d/%Y %H:%M:%S', level=logging.INFO)

def turn_off_default_loggers():
    werkzeug = logging.getLogger('werkzeug')
    engineio = logging.getLogger('engineio.server')
    socketio = logging.getLogger('socketio.server')
    werkzeug.setLevel(logging.ERROR)
    engineio.setLevel(logging.ERROR)
    socketio.setLevel(logging.ERROR)
