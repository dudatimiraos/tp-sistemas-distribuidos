import socket
import threading
import time
import datetime
import random
import sys

# Configuração do cliente
SERVER_HOST = 'time-server'  # Nome do serviço no Docker Compose
SERVER_PORT = 8000

class ClockClient:
    def __init__(self, client_id, initial_offset=0):
        """
        Inicializa um cliente de relógio
        
        Args:
            client_id: identificador único do cliente
            initial_offset: diferença inicial entre o relógio local e o real (em segundos)
        """
        self.client_id = client_id
        self.offset = initial_offset  # Diferença entre relógio local e tempo real
        self.adjustment_rate = 0.1    # Taxa de ajuste gradual (10% da diferença)
        self.stop_flag = False
        self.last_sync_time = 0       # Última vez que sincronizou com o servidor
        
    def local_time(self):
        """Retorna o tempo local do cliente (possivelmente incorreto)"""
        return time.time() + self.offset
        
    def display_time(self):
        """Exibe o tempo local do cliente"""
        while not self.stop_flag:
            local = self.local_time()
            real = time.time()
            
            local_dt = datetime.datetime.fromtimestamp(local)
            real_dt = datetime.datetime.fromtimestamp(real)
            
            # Calcular o tempo até a próxima sincronização
            time_since_last_sync = time.time() - self.last_sync_time
            time_until_next_sync = max(0, 60 - time_since_last_sync)
            
            print(f"Cliente {self.client_id} | "
                  f"Tempo local: {local_dt.strftime('%H:%M:%S.%f')[:-3]} | "
                  f"Tempo real: {real_dt.strftime('%H:%M:%S.%f')[:-3]} | "
                  f"Diferença: {self.offset:.6f}s | "
                  f"Próxima sincronização em {time_until_next_sync:.0f}s")
            
            # Atualizar a exibição a cada 60 segundos
            time.sleep(60)
    
    def sync_time(self):
        """Sincroniza o tempo com o servidor usando o algoritmo de Cristian"""
        while not self.stop_flag:
            try:
                # Atualizar o timestamp da última sincronização
                self.last_sync_time = time.time()
                
                # Mostrar informações de conexão
                print(f"Cliente {self.client_id} | Sincronizando agora com {SERVER_HOST}:{SERVER_PORT}")
                
                # Conectar ao servidor
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((SERVER_HOST, SERVER_PORT))
                
                # Registrar o tempo de envio
                t0 = time.time()
                
                # Enviar solicitação de tempo
                client_socket.send(str(t0).encode())
                
                # Receber resposta
                response = client_socket.recv(1024).decode()
                
                # Registrar o tempo de recepção
                t3 = time.time()
                
                # Analisar a resposta
                t0_echo, t1 = map(float, response.split(':'))
                
                # Calcular RTT (Round Trip Time) e o offset do relógio
                rtt = t3 - t0
                
                # Estimar o atraso da rede (metade do RTT)
                network_delay = rtt / 2
                
                # Estimar o tempo correto (algoritmo de Cristian)
                correct_time = t1 + network_delay
                
                # Calcular a diferença entre o tempo local e o tempo correto
                current_local_time = self.local_time()
                time_difference = correct_time - current_local_time
                
                # Ajustar o relógio gradualmente
                adjustment = time_difference * self.adjustment_rate
                self.offset += adjustment
                
                # Exibir informação detalhada
                local_dt = datetime.datetime.fromtimestamp(current_local_time)
                correct_dt = datetime.datetime.fromtimestamp(correct_time)
                
                print(f"Cliente {self.client_id} | Sincronização completa:")
                print(f"  - RTT: {rtt:.6f}s")
                print(f"  - Tempo local antes: {local_dt.strftime('%H:%M:%S.%f')[:-3]}")
                print(f"  - Tempo correto: {correct_dt.strftime('%H:%M:%S.%f')[:-3]}")
                print(f"  - Diferença: {time_difference:.6f}s")
                print(f"  - Ajuste aplicado: {adjustment:.6f}s")
                
            except Exception as e:
                print(f"Cliente {self.client_id} | Erro na sincronização: {e}")
            finally:
                if 'client_socket' in locals():
                    client_socket.close()
                
            # Aguardar até a próxima sincronização (exatamente 1 minuto = 60 segundos)
            time.sleep(60)
    
    def start(self):
        """Inicia os threads de exibição e sincronização"""
        print(f"Cliente {self.client_id} | Iniciando threads de exibição e sincronização")
        
        display_thread = threading.Thread(target=self.display_time)
        display_thread.daemon = True
        display_thread.start()
        
        sync_thread = threading.Thread(target=self.sync_time)
        sync_thread.daemon = True
        sync_thread.start()
        
        return display_thread, sync_thread
    
    def stop(self):
        """Para todos os threads do cliente"""
        self.stop_flag = True

def main():
    try:
        # Verificar se foi fornecido um ID de cliente
        if len(sys.argv) > 1:
            client_id = int(sys.argv[1])
        else:
            client_id = random.randint(1, 100)
        
        # Criar um offset inicial aleatório (entre -10 e 10 segundos)
        initial_offset = random.uniform(-10, 10)
        
        # Inicializar o cliente
        client = ClockClient(client_id, initial_offset)
        
        print(f"Cliente {client_id} iniciado com offset inicial de {initial_offset:.6f}s")
        
        # Iniciar os threads do cliente
        threads = client.start()
        
        # Aguardar interrupção por teclado
        for thread in threads:
            thread.join()
            
    except KeyboardInterrupt:
        print("Cliente encerrado pelo usuário")
        if 'client' in locals():
            client.stop()

if __name__ == "__main__":
    main()