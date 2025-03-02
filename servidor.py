import socket
import json
import threading
from cryptography.fernet import Fernet
from zeroconf import Zeroconf, ServiceInfo

class Servidor:
    def __init__(self, host='0.0.0.0', porta=5000):
        self.host = host
        self.porta = porta
        self.clientes = {}  # Armazena os PCs conectados: chave = endereço e valor = dados
        self.chave = Fernet.generate_key()
        self.cifra = Fernet(self.chave)
        self.lock = threading.Lock()  

    def iniciar(self):
        #  servidor de rede
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.bind((self.host, self.porta))
        servidor_socket.listen(5)

        print(f"🔵 Servidor rodando em {self.host}:{self.porta}")
        print(f"🔑 Chave de criptografia: {self.chave.decode()} (Copie para o cliente)")

        # Multicast DNS
        zeroconf = Zeroconf()
        info = ServiceInfo(
            "_computador._tcp.local.",
            "Servidor de Computador._computador._tcp.local.",
            addresses=[socket.inet_aton(self.host)],
            port=self.porta,
            properties={},
            server="com.example.server.local."
        )
        zeroconf.register_service(info)
        print(f"🔍 Servidor anunciado como: {info.name}")

        while True:
            try:
                cliente_socket, endereco = servidor_socket.accept()
                print(f"✅ Nova conexão de {endereco}")
                thread = threading.Thread(target=self.tratar_cliente, args=(cliente_socket, endereco))
                thread.start()
            except Exception as e:
                print(f"❌ Erro ao aceitar conexão: {e}")

    def tratar_cliente(self, cliente_socket, endereco):
        try:
            dados_cifrados = cliente_socket.recv(1024)
            dados_json = self.cifra.decrypt(dados_cifrados).decode()
            dados = json.loads(dados_json)
            with self.lock:
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
        with self.lock:
            if not self.clientes:
                print("ℹ️ Nenhum pc conectado.")
                return []
            lista = list(self.clientes.items())
        print("Pcs conectados:")
        for idx, (endereco, dados) in enumerate(lista):
            print(f"[{idx}] IP: {endereco[0]}, Porta: {endereco[1]}")
        return lista

    def detalhar_computador(self, indice):
        lista = self.listar_computadores()
        if indice < 0 or indice >= len(lista):
            print("❌ inválido.")
            return
        endereco, dados = lista[indice]
        print(f"Detalhes do pcc {indice}:")
        print(f"Endereço: {endereco}")
        for chave, valor in dados.items():
            print(f"{chave}: {valor}")

    def comando_interativo(self):
        while True:
            print("\nDigite 'listar' para ver os pcs conectados,")
            print("ou 'detalhar <número>' para ver os detalhes de um pc,")
            print("ou 'sair' pra encerrar o programa.")
            comando = input("Comando: ").strip().lower()
            if comando == "listar":
                self.listar_computadores()
            elif comando.startswith("detalhar"):
                partes = comando.split()
                if len(partes) == 2 and partes[1].isdigit():
                    indice = int(partes[1])
                    self.detalhar_computador(indice)
                else:
                    print("❌ Uso correto: detalhar <número>")
            elif comando == "sair":
                print("Encerrando.")
                break
            else:
                print("❌ Comando não existe.")

if __name__ == "__main__":
    servidor = Servidor()
    servidor_thread = threading.Thread(target=servidor.iniciar, daemon=True)
    servidor_thread.start()
    servidor.comando_interativo()
