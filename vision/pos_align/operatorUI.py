import pickle
import socket
import threading


def address():
    while True:
        robot_info = pickle.loads(conn2.recv(4096))
        # print("Address: %d, Status: %s" % (robot_info['addr'], robot_info['status']))


def destination():
    while True:
        msg = input("Next message: ")
        conn3.send(pickle.dumps(msg))


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

    addrconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addrconn.bind((host_ip, 60002))
    addrconn.listen(5)

    destconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destconn.bind((host_ip, 60003))
    destconn.listen(5)

    conn2, _ = addrconn.accept()
    conn3, _ = destconn.accept()

    t2 = threading.Thread(target=address)
    t3 = threading.Thread(target=destination)

    t2.start()
    t3.start()

    t2.join()
    t3.join()
