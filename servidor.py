import socket

class Servidor:
    def __init__(self, host="0.0.0.0", porta=5000):
        self.host = host
        self.porta = porta
        self.clientes = {}  # Dicionário para armazenar dados dos clientes

    def iniciar(self):
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.bind((self.host, self.porta))
        servidor_socket.listen(5)
        print(f"Servidor rodando em {self.host}:{self.porta}")

        while True:
            cliente_socket, endereco = servidor_socket.accept()
            print(f"Nova conexão de {endereco}")
            dados = cliente_socket.recv(1024).decode()
            if dados:
                self.processar_dados(endereco, dados)
            cliente_socket.close()

    def processar_dados(self, endereco, dados):
        print(f"Dados recebidos de {endereco}: {dados}")
        self.clientes[endereco] = dados  # Armazena os dados no dicionário

servidor = Servidor()
servidor.iniciar()
