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
#cpu_temp = temps['coretemp'][0].current if 'coretemp' in temps else None
    def obter_temperatura(self):
     try:
        temps = psutil.sensors_temperatures()
        # Tenta acessar a temperatura da CPU, usando o 'coretemp' se disponível
        cpu_temp = temps['coretemp'][0].current if 'coretemp' in temps else None
        return cpu_temp if cpu_temp is not None else -1  # Retorna -1 se a temperatura não estiver disponível
     except Exception as e:
        print(f"❌ Erro ao obter temperatura: {e}")
        return -1

    def enviar_dados(self):
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((self.servidor_ip, self.servidor_porta))

        dados = self.coletar_dados()
        dados_cifrados = self.cifra.encrypt(json.dumps(dados).encode())
        cliente_socket.send(dados_cifrados)

        resposta_cifrada = cliente_socket.recv(1024)
        resposta = json.loads(self.cifra.decrypt(resposta_cifrada).decode())

        # Imprimir os paranaues
        print(f"📊 Quantidade de Processadores: {dados['cpus']}")
        print(f"📊 Memória RAM Livre: {dados['ram_livre']} MB")
        print(f"📊 Espaço em Disco Livre: {dados['disco_livre']} GB")

        if dados['temperatura'] != -1: #-1 deu erro
            print(f"📊 Temperatura do Processador: {dados['temperatura']}°C")
        else:
            print(f"📊 Temperatura do Processador: Indisponível")
        
        # Imprimir a média simples
        print(f"📊 Média simples dos dados: {resposta['media']:.2f}")

        cliente_socket.close()

if __name__ == "__main__":
    chave_servidor = 'UnsGhXg2x7I79TlV4260oumqwjVqwMEkcA-fqo_tGoM='  # lembrar de substituir pela chave dada no servidor
    cliente = Cliente(chave=chave_servidor)
    cliente.enviar_dados()
