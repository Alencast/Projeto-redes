import socket
import json
import time
import psutil
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange

class Cliente:
    def __init__(self):
        self.servidor_ip = None
        self.servidor_porta = None
        self.zeroconf = Zeroconf()
        self.client_private_key = None  # Será gerada durante o handshake

    def localizar_servidor(self):
        """Procura pelo servidor usando mDNS."""
        def on_service_state_change(zeroconf, service_type, name, state_change):
            if state_change == ServiceStateChange.Added:
                info = zeroconf.get_service_info(service_type, name)
                if info:
                    self.servidor_ip = socket.inet_ntoa(info.addresses[0])
                    self.servidor_porta = info.port
                    print(f"🌐 Servidor encontrado em {self.servidor_ip}:{self.servidor_porta}")

        ServiceBrowser(self.zeroconf, "_computador._tcp.local.", handlers=[on_service_state_change])
        print("🔍 Buscando servidor na rede...")
        time.sleep(5)
        if not self.servidor_ip:
            print("❌ Nenhum servidor encontrado. Verifique se o servidor está rodando.")

    def diffie_hellman_handshake(self, sock):
        # Recebe a chave pública do servidor
        server_public_bytes = sock.recv(1024)
        server_public_key = serialization.load_pem_public_key(server_public_bytes)
        # Utiliza os parâmetros do servidor para gerar a chave do cliente
        parameters = server_public_key.parameters()
        self.client_private_key = parameters.generate_private_key()
        client_public_bytes = self.client_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        sock.sendall(client_public_bytes)
        # Calcula a chave compartilhada
        shared_key = self.client_private_key.exchange(server_public_key)
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"handshake data"
        ).derive(shared_key)
        fernet_key = base64.urlsafe_b64encode(derived_key)
        return Fernet(fernet_key)

    def coletar_dados(self):
        """Coleta os dados da máquina usando psutil."""
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
            if 'coretemp' in temps:
                return temps['coretemp'][0].current
            return -1
        except Exception as e:
            print(f"❌ Erro ao obter temperatura: {e}")
            return -1

    def enviar_dados(self):
        if not self.servidor_ip or not self.servidor_porta:
            print("❌ Não foi possível localizar o servidor.")
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.servidor_ip, self.servidor_porta))

        # handshake
        cifra = self.diffie_hellman_handshake(sock)

        dados = self.coletar_dados()
        dados_cifrados = cifra.encrypt(json.dumps(dados).encode())
        sock.send(dados_cifrados)

        resposta_cifrada = sock.recv(1024)
        resposta = json.loads(cifra.decrypt(resposta_cifrada).decode())

        print(f"📊 Quantidade de Processadores: {dados['cpus']}")
        print(f"📊 Memória RAM Livre: {dados['ram_livre']} MB")
        print(f"📊 Espaço em Disco Livre: {dados['disco_livre']} GB")
        if dados['temperatura'] != -1:
            print(f"📊 Temperatura do Processador: {dados['temperatura']}°C")
        else:
            print("📊 Temperatura do Processador: Indisponível")
        print(f"📊 Média simples dos dados: {resposta['media']:.2f}")

        sock.close()

if __name__ == "__main__":
    cliente = Cliente()
    cliente.localizar_servidor()
    cliente.enviar_dados()
