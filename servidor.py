import socket
import json
import threading
from cryptography.fernet import Fernet

class Servidor:
    def __init__(self, host='0.0.0.0', porta=5000):
        self.host = host
        self.porta = porta
        self.clientes = {}  # Armazenar os pcs encontrados
        self.chave = Fernet.generate_key()
        self.cifra = Fernet(self.chave)

    def iniciar(self):
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.bind((self.host, self.porta))
        servidor_socket.listen(5)

        print(f"🔵 Servidor rodando em {self.host}:{self.porta}")
        print(f"🔑 Chave de criptografia: {self.chave.decode()} (Copie para o cliente)")

        while True:
            cliente_socket, endereco = servidor_socket.accept()
            print(f"✅ Nova conexão de {endereco}")
            thread = threading.Thread(target=self.tratar_cliente, args=(cliente_socket, endereco))
            thread.start()

    def tratar_cliente(self, cliente_socket, endereco):
        try:
            dados_cifrados = cliente_socket.recv(1024)
            dados_json = self.cifra.decrypt(dados_cifrados).decode()
            dados = json.loads(dados_json)

            self.clientes[endereco] = dados
            print(f"📥 Dados recebidos de {endereco}: {dados}")

            media = sum(dados.values()) / len(dados)
            resposta = {"media": media}
            cliente_socket.send(self.cifra.encrypt(json.dumps(resposta).encode()))
        except Exception as e:
            print(f"❌ Erro com {endereco}: {e}")
        finally:
            cliente_socket.close()

    def listar_computadores(self):
        for ip, dados in self.clientes.items():
            print(f"💻 {ip}: {dados}")

if __name__ == "__main__":
    servidor = Servidor()
    servidor.iniciar()
