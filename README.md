# Algoritmo de Cristian para Sincronização de Relógios Físicos

Este projeto implementa o algoritmo de Cristian para sincronização de relógios em uma rede distribuída com múltiplos dispositivos usando Docker para garantir que cada dispositivo tenha seu próprio IP.

## Requisitos

- Docker
- Docker Compose

## Estrutura do Projeto

- `time_server.py`: Servidor de tempo sincronizado com NTP Pool
- `time_client.py`: Cliente que sincroniza seu relógio com o servidor usando o algoritmo de Cristian
- `Dockerfile.server`: Configuração do container para o servidor
- `Dockerfile.client`: Configuração do container para os clientes
- `docker-compose.yml`: Orquestração da rede de dispositivos
- `requirements.txt`: Dependências Python

## Funcionamento

- O servidor sincroniza seu relógio com o NTP Pool a cada 1 minuto
- Cada cliente sincroniza seu relógio com o servidor a cada 1 minuto
- Os clientes aplicam o algoritmo de Cristian para compensar o atraso de rede
- Os ajustes nos relógios são feitos gradualmente para evitar saltos bruscos
- Cada dispositivo é executado em um container Docker com um IP distinto

## Como Executar com Docker

Para iniciar toda a rede distribuída:

```
docker-compose up --build
```

Isto iniciará:

- 1 servidor de tempo sincronizado com NTP (IP: 192.168.10.6)
- 4 clientes com relógios inicialmente deslocados (IPs: 192.168.10.7 até 192.168.10.10)

Para executar em segundo plano:

```
docker-compose up -d --build
```

Para visualizar os logs em tempo real (recomendado):

```
# Ver todos os logs juntos
docker-compose logs -f

# Ver apenas logs do servidor
docker-compose logs -f time-server

# Ver apenas logs de um cliente específico
docker-compose logs -f client1
```

Para interromper todos os containers:

```
docker-compose down
```

## Visualização e Monitoramento

Para melhorar a experiência de visualização, o sistema foi configurado para:

1. **Exibir logs em tempo real**: O buffering do Python foi desativado para que as saídas apareçam imediatamente
2. **Atualização frequente**: Os clientes mostram atualizações a cada 5 segundos
3. **Formatação clara**: Os logs incluem timestamps e informações detalhadas para facilitar o entendimento
4. **Contagem regressiva**: Os clientes mostram o tempo restante até a próxima sincronização

Comandos úteis para monitoramento:

```
# Ver todos os containers em execução
docker ps

# Ver logs de um container específico
docker logs -f time-server
docker logs -f client1

# Ver estatísticas de uso de recursos
docker stats
```

## Algoritmo de Cristian

O algoritmo de Cristian implementado funciona da seguinte forma:

1. O cliente registra o tempo local antes de enviar a solicitação (t0)
2. O cliente envia a solicitação para o servidor
3. O servidor responde com seu tempo atual (t1)
4. O cliente registra o tempo local quando recebe a resposta (t3)
5. O cliente calcula o RTT (Round Trip Time): RTT = t3 - t0
6. O cliente estima o atraso da rede como RTT/2
7. O cliente calcula o tempo correto: tempo_correto = t1 + (RTT/2)
8. O cliente ajusta gradualmente seu relógio com base na diferença calculada

## Problemas de Sincronização

Se houver problemas com a sincronização:

1. Verifique se a rede Docker está configurada corretamente
2. Reinicie os containers com `docker-compose restart`
3. Verifique se o servidor está conseguindo se conectar aos servidores NTP
4. Aumente o limite de tempo de timeout para conexões NTP se necessário
