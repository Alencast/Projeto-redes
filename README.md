<div align="center">
  <h1>Monitoramento Remoto de Computadores 🌐💻</h1> 
  <p>Um sistema de monitoramento remoto utilizando Python, criptografia Diffie-Hellman e multicastDNS.</p>
</div>

<div style = "display:flex"> 
    <p>Integrantes: </p>
    <ul>
      <li>Robson Alves de Alencastro</li>
      <li>Lucas de Moraes dos Santos</li>
    </ul>
  </div>

---

## 🚀 Etapa 1 - Conexão e Descoberta de Rede  
O primeiro passo do projeto envolve a descoberta automática de servidores e a comunicação segura entre cliente e servidor.

### 📌 Coisas a fazer:
✅ Implementar o servidor  
✅ Implementar o cliente  
✅ Utilizar mDNS pra descoberta automática  
✅ Criar a comunicação via sockets  
✅ Implementar handshake Diffie-Hellman  
✅ Implementar criptografia Fernet para os dados  

---

## 📊 Etapa 2 - Coleta de Dados do Sistema  
Nessa etapa, o cliente coleta dados da máquina e  envia ao servidor.

### 📌 Coisas a fazer:
✅ Coletar número de CPUs  
✅ Coletar memória RAM disponível  
✅ Coletar espaço livre em disco  
✅ Coletar temperatura da CPU  
✅ Enviar os dados para o servidor  

---

## 🔍 Etapa 3 - Processamento e Resposta  
O servidor recebe os dados dos clientes e responde.

### 📌 Coisas a fazer:
✅ Armazenar dados dos clientes conectados  
✅ Calcular a média dos valores recebidos  
✅ Retornar resposta criptografada ao cliente  
✅ Implementar tratamento de erros(caso não seja possível retornar algum dos dados do pc, por exemplo)  

---

## 🎛️ Etapa 4 - Interface de Administração  
O servidor precisa exibir informações dos clientes conectados e permitir consultas.

### 📌 Coisas a fazer:
✅ Criar comando para listar clientes conectados  
✅ Criar comando para detalhar um cliente específico  
✅ Melhorar a exibição dos dados coletados  

---

💻 **Trabalho da matéria de Redes de computadores do curso de TADS no IFRN Cnat, utilizando os conceitos aprendidos em sala.**
