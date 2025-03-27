import socket
import threading
import time
import datetime
import ntplib

# Configuração do servidor
HOST = '0.0.0.0'  # Bind para todos os endereços IP
PORT = 8000

# Lista de servidores NTP do pool
NTP_SERVERS = [
    'pool.ntp.org',
    '0.pool.ntp.org',
    '1.pool.ntp.org',
    '2.pool.ntp.org'
]

# Variáveis globais
ntp_time_offset = 0  # Diferença entre o tempo do sistema e o tempo NTP
last_ntp_sync = 0    # Último momento de sincronização com NTP

def sync_with_ntp():
    """Sincroniza o tempo do servidor com o NTP Pool"""
    global ntp_time_offset, last_ntp_sync
    
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] Iniciando sincronização com servidores NTP...")
    
    client = ntplib.NTPClient()
    
    # Tenta conectar a diferentes servidores NTP em caso de falha
    for server in NTP_SERVERS:
        try:
            response = client.request(server, timeout=5)
            
            # Calcula o offset entre o tempo local e o tempo NTP
            ntp_time_offset = response.offset
            last_ntp_sync = time.time()
            
            ntp_time = datetime.datetime.fromtimestamp(time.time() + ntp_time_offset)
            local_time = datetime.datetime.fromtimestamp(time.time())
            
            print(f"✓ Sincronizado com NTP {server}")
            print(f"  - Offset: {ntp_time_offset:.6f}s")
            print(f"  - Hora local:   {local_time.strftime('%H:%M:%S.%f')[:-3]}")
            print(f"  - Hora NTP:     {ntp_time.strftime('%H:%M:%S.%f')[:-3]}")
            
            return True
        except Exception as e:
            print(f"✗ Falha ao sincronizar com {server}: {e}")
    
    print("✗ Não foi possível sincronizar com nenhum servidor NTP")
    return False

def get_current_time():
    """Retorna o tempo atual corrigido pelo offset do NTP"""
    return time.time() + ntp_time_offset

def ntp_sync_thread():
    """Thread para sincronizar periodicamente com servidores NTP"""
    global last_ntp_sync
    
    # Sincronização inicial
    sync_with_ntp()
    
    while True:
        # Verifica se é hora de sincronizar novamente (a cada 1 minuto)
        current_time = time.time()
        time_since_last_sync = current_time - last_ntp_sync
        
        if time_since_last_sync >= 60:  # 60 segundos = 1 minuto
            sync_with_ntp()
        else:
            # Exibir informação de status a cada 15 segundos
            if time_since_last_sync % 15 < 1:  # Aproximadamente a cada 15 segundos
                time_until_next_sync = 60 - time_since_last_sync
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Próxima sincronização NTP em {time_until_next_sync:.0f}s")
        
        # Aguarda um pouco antes de verificar novamente
        time.sleep(1)

def handle_client(client_socket, client_address):
    """Processa as solicitações de um cliente"""
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] Conexão estabelecida com {client_address}")
    
    try:
        while True:
            # Recebe a solicitação do cliente
            data = client_socket.recv(1024)
            if not data:
                break
                
            # O cliente envia um timestamp quando a mensagem foi enviada
            request_time = float(data.decode())
            
            # Envia o tempo atual do servidor (corrigido pelo NTP)
            current_time = get_current_time()
            response = f"{request_time}:{current_time}"
            client_socket.send(response.encode())
            
            # Exibe informações para depuração
            now = datetime.datetime.now().strftime('%H:%M:%S')
            sent_time = datetime.datetime.fromtimestamp(current_time).strftime('%H:%M:%S.%f')[:-3]
            print(f"[{now}] Solicitação de tempo de {client_address}")
            print(f"  - Tempo enviado: {sent_time}")
            
    except Exception as e:
        print(f"✗ Erro na comunicação com {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Conexão com {client_address} encerrada")

def start_server():
    """Inicia o servidor de tempo"""
    print("\n" + "="*60)
    print(f"SERVIDOR DE TEMPO - ALGORITMO DE CRISTIAN")
    print("="*60)
    
    # Inicia o thread de sincronização NTP
    ntp_thread = threading.Thread(target=ntp_sync_thread)
    ntp_thread.daemon = True
    ntp_thread.start()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] Servidor de tempo iniciado em {HOST}:{PORT}")
    print("Sincronizando com servidores NTP...")
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()