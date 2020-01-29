import pickle
import socket


if __name__ == "__main__":
    # Get the hostname and IP address of this machine and display it.
    host_name = socket.gethostname()

    try:
        host_ip = socket.gethostbyname(socket.gethostname())
        # On many linux systems, this always gives 127.0.0.1. Hence...
    except:
        host_ip = ''

    if not host_ip or host_ip.startswith('127.'):
        # Now we get the address the hard way.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('4.2.2.1', 0))
        host_ip = s.getsockname()[0]

    print("Server Hostname:: ", host_name)
    print("Server IP:: ", host_ip)

    destconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destconn.bind((host_ip, 1200))
    destconn.listen(5)

    serverconn, _ = destconn.accept()

    while True:
        msg = input("Next address: ")
        serverconn.send(pickle.dumps(int(msg)))
        next_address = pickle.loads(serverconn.recv(16))
        print("Arrived at %d" % next_address)
