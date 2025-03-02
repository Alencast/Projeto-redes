import socket
import json
import psutil
from cryptography.fernet import Fernet

class Cliente:
    def __init__(self, servidor_ip="127.0.0.1", servidor_porta=5000, chave="CHAVE_DO_SERVIDOR_AQUI"):
        self.servidor_ip = servidor_ip
        self.servidor_porta = servidor_porta
        self.cifra = Fernet(chave)  # Não precisa de .encode()

    def coletar_dados(self):
        dados = {
            "cpus": psutil.cpu_count(),
            "ram_livre": psutil.virtual_memory().available // (1024 * 1024),
            "disco_livre": psutil.disk_usage('/').free // (1024 * 1024 * 1024),
            "temperatura": self.obter_temperatura()
        }
        return dados

    def obter_temperatura(self):
        try:
            temps = psutil.sensors_temperatures()
            if "coretemp" in temps:
                return temps["coretemp"][0].current
            return -1  # se não tiver sensor
        except:
            return -1

    def enviar_dados(self):
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((self.servidor_ip, self.servidor_porta))

        dados = self.coletar_dados()
        dados_cifrados = self.cifra.encrypt(json.dumps(dados).encode())
        cliente_socket.send(dados_cifrados)

        resposta_cifrada = cliente_socket.recv(1024)
        resposta = json.loads(self.cifra.decrypt(resposta_cifrada).decode())

        # Imprimir os dados completos
        print(f"📊 Quantidade de Processadores: {dados['cpus']}")
        print(f"📊 Memória RAM Livre: {dados['ram_livre']} MB")
        print(f"📊 Espaço em Disco Livre: {dados['disco_livre']} GB")
        if dados['temperatura'] != -1:
            print(f"📊 Temperatura do Processador: {dados['temperatura']}°C")
        else:
            print(f"📊 Temperatura do Processador: Indisponível")
        
        # Imprimir a média simples
        print(f"📊 Média simples dos dados: {resposta['media']:.2f}")

        cliente_socket.close()

if __name__ == "__main__":
    chave_servidor = 'L1rgGDcr7TGULGI3__aowDBWkb9dT2tZgNUtLez400M=='  # Substitua pela chave dada no servidor
    cliente = Cliente(chave=chave_servidor)
    cliente.enviar_dados()
