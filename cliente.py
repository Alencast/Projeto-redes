import socket
import psutil

class Cliente:
    def __init__(self, servidor_ip, servidor_porta=5000):
        self.servidor_ip = servidor_ip
        self.servidor_porta = servidor_porta

    def coletar_dados(self):
        dados = {
            "cpus": psutil.cpu_count(),
            "ram_livre": psutil.virtual_memory().available // (1024 * 1024)  #  tá em MB
        }
        return str(dados)

    def enviar_dados(self):
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((self.servidor_ip, self.servidor_porta))
        dados = self.coletar_dados()
        cliente_socket.send(dados.encode())
        cliente_socket.close()

cliente = Cliente("127.0.0.1")  # Se for rodar localmente ->  127.0.0.1
cliente.enviar_dados()
