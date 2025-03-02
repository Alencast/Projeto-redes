import socket
import json
import time
import psutil
from cryptography.fernet import Fernet
from zeroconf import Zeroconf, ServiceBrowser, ServiceStateChange

class Cliente:
    def __init__(self, chave="CHAVE_DO_SERVIDOR_AQUI"):
        self.chave = Fernet(chave)
        self.servidor_ip = None
        self.servidor_porta = None
        self.zeroconf = Zeroconf()

    def localizar_servidor(self):
        """Procura pelo servidor usando mDNS"""
        def on_service_state_change(zeroconf, service_type, name, state_change):
            if state_change == ServiceStateChange.Added:
                info = zeroconf.get_service_info(service_type, name)
                if info:
                    self.servidor_ip = socket.inet_ntoa(info.addresses[0])
                    self.servidor_porta = info.port
                    print(f"🌐 Servidor encontrado em {self.servidor_ip}:{self.servidor_porta}")

        # Criar um navegador de serviços
        browser = ServiceBrowser(self.zeroconf, "_computador._tcp.local.", handlers=[on_service_state_change])

        print("🔍 Buscando servidor na rede...")
        time.sleep(5)  # Aguarda 5 segundos para que o serviço seja encontrado

        if not self.servidor_ip:
            print("❌ Nenhum servidor encontrado. Verifique se o servidor está rodando.")

    def coletar_dados(self):
        """Coleta os dados da máquina usando psutil"""
        dados = {
            "cpus": psutil.cpu_count(),
            "ram_livre": psutil.virtual_memory().available // (1024 * 1024),
            "disco_livre": psutil.disk_usage('/').free // (1024 * 1024 * 1024),
            "temperatura": self.obter_temperatura()
        }
        return dados

    def obter_temperatura(self):
        """Obtém a temperatura do processador, se for possível"""
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return temps['coretemp'][0].current
            return -1  # Retorna -1 se não houver temperatura disponível
        except Exception as e:
            print(f"❌ Erro ao obter temperatura: {e}")
            return -1

    def enviar_dados(self):
        if not self.servidor_ip or not self.servidor_porta:
            print("❌ Não foi possível localizar o servidor.")
            return

        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((self.servidor_ip, self.servidor_porta))

        dados = self.coletar_dados()
        dados_cifrados = self.chave.encrypt(json.dumps(dados).encode())
        cliente_socket.send(dados_cifrados)

        resposta_cifrada = cliente_socket.recv(1024)
        resposta = json.loads(self.chave.decrypt(resposta_cifrada).decode())

        print(f"📊 Quantidade de Processadores: {dados['cpus']}")
        print(f"📊 Memória RAM Livre: {dados['ram_livre']} MB")
        print(f"📊 Espaço em Disco Livre: {dados['disco_livre']} GB")

        if dados['temperatura'] != -1:
            print(f"📊 Temperatura do Processador: {dados['temperatura']}°C")
        else:
            print("📊 Temperatura do Processador: Indisponível")

        print(f"📊 Média simples dos dados: {resposta['media']:.2f}")

        cliente_socket.close()

if __name__ == "__main__":
    chave_servidor = 'k_ZsmWIeCqisoxttehu9rSnjVAGm2aUEVTNjsnB3KkE='  # Insira a chave correta aqui
    cliente = Cliente(chave=chave_servidor)
    cliente.localizar_servidor()
    cliente.enviar_dados()
