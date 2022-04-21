import argparse
import socket
from colorama import init, Fore

from threading import Thread, Lock
from queue import Queue


init()
GREEN = Fore.GREEN
RESET = Fore.RESET
GRAY = Fore.LIGHTBLACK_EX

# numero de threads desejadas
N_THREADS = 200
# fila das threads
q = Queue()
print_lock = Lock()

def port_scan(port):
    """
    Scaneia as portas na variavel global `host`
    """
    try:
        s = socket.socket()
        s.connect((host, port))
    except:
        with print_lock:
            print(f"{GRAY}{host:15}:{port:5} fechada  {RESET}", end='\r')
    else:
        with print_lock:
            print(f"{GREEN}{host:15}:{port:5} aberta    {RESET}")
    finally:
        s.close()


def scan_thread():
    global q
    while True:
        # obtem o numero da porta na fila
        worker = q.get()
        # scaneia a porta
        port_scan(worker)
        # avisa quando terminar o scan
        q.task_done()


def main(host, ports):
    global q
    for t in range(N_THREADS):
        # inicia as threads
        t = Thread(target=scan_thread)
        # determina com o daemon quando sera encerrado
        t.daemon = True
        # inicia o daemon
        t.start()

    for worker in ports:
        # insere cada porta em uma thread para ir escaneando
        q.put(worker)
    
    # aguarda as threads terminarem para encerrar
    q.join()


if __name__ == "__main__":
    # passa os argumentos
    parser = argparse.ArgumentParser(description="Port Scanner")
    parser.add_argument("host", help="Host para escanear")
    parser.add_argument("--ports", "-p", dest="port_range", default="1-65535", help="range do scan, padrao > 1-65535 (todas as portas)")
    args = parser.parse_args()
    host, port_range = args.host, args.port_range

    start_port, end_port = port_range.split("-")
    start_port, end_port = int(start_port), int(end_port)

    ports = [ p for p in range(start_port, end_port)]

    main(host, ports)
