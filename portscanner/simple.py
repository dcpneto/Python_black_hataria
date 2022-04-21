import socket
from colorama import init, Fore

init()
GREEN = Fore.GREEN
RESET = Fore.RESET
GRAY = Fore.LIGHTBLACK_EX

def is_port_open(host, port):
    """
    determina qual `host` tem quais `port` aberta
    """
    # cria um novo socket
    s = socket.socket()
    try:
        # testa conexao usando a porta
        s.connect((host, port))
        # menor timeout = menos precisao
        s.settimeout(0.2)
    except:
        # nao conectou, porta fechada
        return False
    else:
        # conectou, porta aberta
        return True

# obtem o host do usuario
host = input("Enter the host:")
# passa pelas portas de 1 ate 1024
for port in range(1, 1025):
    if is_port_open(host, port):
        print(f"{GREEN}[+] {host}:{port} aberta     {RESET}")
    else:
        print(f"{GRAY}[!] {host}:{port} fechada    {RESET}", end="\r")
