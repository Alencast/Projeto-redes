import socket
import json
import threading
import base64
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.fernet import Fernet
from zeroconf import Zeroconf, ServiceInfo

class Servidor:
    def __init__(self, host='0.0.0.0', porta=5000):
        self.host = host
        self.porta = porta
        self.clientes = {}  # Armazena os PCs conectados
        self.lock = threading.Lock()
        # Gera parâmetros Diffie-Hellman e a chave do servidor
        parameters = dh.generate_parameters(generator=2, key_size=2048)
        self.server_private_key = parameters.generate_private_key()
        self.server_public_key = self.server_private_key.public_key()

    def iniciar(self):
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.bind((self.host, self.porta))
        servidor_socket.listen(5)
        print(f"🔵 Servidor rodando em {self.host}:{self.porta}")

        # Anuncia o serviço via mDNS
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

    def diffie_hellman_handshake(self, sock):
        # Envia a chave pública do servidor para o cliente
        server_public_bytes = self.server_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        sock.sendall(server_public_bytes)
        # Recebe a chave pública do cliente
        client_public_bytes = sock.recv(1024)
        client_public_key = serialization.load_pem_public_key(client_public_bytes)
        # Calcula a chave compartilhada
        shared_key = self.server_private_key.exchange(client_public_key)
        # Deriva uma chave simétrica a partir da chave compartilhada
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"handshake data"
        ).derive(shared_key)
        # Fernet requer uma chave codificada em base64
        fernet_key = base64.urlsafe_b64encode(derived_key)
        return Fernet(fernet_key)

    def tratar_cliente(self, cliente_socket, endereco):
        try:
            # Realiza o handshake e obtém o objeto Fernet configurado
            cifra = self.diffie_hellman_handshake(cliente_socket)
            
            dados_cifrados = cliente_socket.recv(1024)
            dados_json = cifra.decrypt(dados_cifrados).decode()
            dados = json.loads(dados_json)
            with self.lock:
                self.clientes[endereco] = dados
            print(f"📥 Dados recebidos de {endereco}: {dados}")

            media = sum(dados.values()) / len(dados)
            resposta = {"media": media}
            cliente_socket.send(cifra.encrypt(json.dumps(resposta).encode()))
        except Exception as e:
            print(f"❌ Erro com {endereco}: {e}")
        finally:
            cliente_socket.close()

    def listar_computadores(self):
        with self.lock:
            if not self.clientes:
                print("ℹ️ Nenhum PC conectado.")
                return []
            lista = list(self.clientes.items())
        print("PCs conectados:")
        for idx, (endereco, dados) in enumerate(lista):
            print(f"[{idx}] IP: {endereco[0]}, Porta: {endereco[1]}")
        return lista

    def detalhar_computador(self, indice):
        lista = self.listar_computadores()
        if indice < 0 or indice >= len(lista):
            print("❌ Índice inválido.")
            return
        endereco, dados = lista[indice]
        print(f"Detalhes do PC {indice}:")
        print(f"Endereço: {endereco}")
        for chave, valor in dados.items():
            print(f"{chave}: {valor}")

    def comando_interativo(self):
        while True:
            print("\nDigite 'listar' para ver os PCs conectados,")
            print("ou 'detalhar <número>' para ver os detalhes de um PC,")
            print("ou 'sair' para encerrar o comando interativo.")
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
                print("Encerrando comando interativo.")
                break
            else:
                print("❌ Comando não reconhecido.")

if __name__ == "__main__":
    servidor = Servidor()
    servidor_thread = threading.Thread(target=servidor.iniciar, daemon=True)
    servidor_thread.start()
    servidor.comando_interativo()
