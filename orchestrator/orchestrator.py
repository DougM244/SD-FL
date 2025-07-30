# orchestrator/orchestrator.py

# 1. Imports
import requests
import numpy as np
import time
import tensorflow as tf
from common.model import create_simple_model

# 2. Constantes e Configurações
CLIENT_ENDPOINTS = [
    "http://client-1:5000/fit",
    "http://client-2:5000/fit",
    "http://client-3:5000/fit",
]
NUM_ROUNDS = 10

# 3. Carregamento dos Dados de Teste (que só o orquestrador conhece)
print("Carregando dados de teste do MNIST...")
_, (x_test, y_test) = tf.keras.datasets.mnist.load_data()
# Normaliza os pixels para o intervalo [0, 1]
x_test = x_test / 255.0
print("Dados de teste carregados.")


def run_federated_training():
    """
    Executa o ciclo completo de treinamento federado.
    """
    print("--- Iniciando Treinamento Federado ---")
    
    # Inicializa o modelo global
    global_model = create_simple_model()
    
    # O modelo precisa ser compilado uma vez para poder ser usado na avaliação
    global_model.compile(loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Inicializar os parâmetros do timeout adaptativo para cada cliente
    client_timing_stats = {endpoint: {"avg_rtt": 30.0, "dev_rtt": 5.0} for endpoint in CLIENT_ENDPOINTS}
    MIN_TIMEOUT = 10
    MAX_TIMEOUT = 180
    ALPHA = 0.125 # Fator de ponderação para a média
    BETA = 0.25 # Fator de ponderação para o desvio padrão

    # Loop principal de treinamento
    for round_num in range(NUM_ROUNDS):
        print(f"\n--- RODADA {round_num + 1}/{NUM_ROUNDS} ---")
        
        # --- PARTE QUE ESTAVA FALTANDO ---
        # Pega os pesos do modelo global atual para enviar aos clientes
        global_weights = global_model.get_weights()
        global_weights_serializable = [w.tolist() for w in global_weights]

        # Inicializa listas para guardar as atualizações recebidas dos clientes
        client_updates = []
        total_samples = 0

        # Envia o modelo para cada cliente e coleta as atualizações
        for i, endpoint in enumerate(CLIENT_ENDPOINTS):
            try:
                # Calcular o timeout para esta chamada específica
                stats = client_timing_stats[endpoint]
                current_timeout = stats["avg_rtt"] + 4 * stats["dev_rtt"]
                # Garantir que o timeout está dentro de limites razoáveis
                current_timeout = max(MIN_TIMEOUT, min(current_timeout, MAX_TIMEOUT))

                print(f"Enviando modelo para o cliente {i+1} ({endpoint})...")

                start_time = time.time()
                response = requests.post(
                    endpoint, 
                    json={'weights': global_weights_serializable}, 
                    timeout= current_timeout  # Usando o timeout adaptativo
                )
                end_time = time.time()

                # Lança um erro se a resposta for 4xx ou 5xx
                response.raise_for_status() 

                # Medir o tempo e atualizar as estatísticas se for bem-sucedido
                sample_rtt = end_time - start_time

                # Atualiza o desvio padrão (referente ao time)
                delta = abs(sample_rtt - stats["avg_rtt"])
                stats["dev_rtt"] = (1 - BETA) * stats["dev_rtt"] + BETA * delta

                # Atualiza a média (referente ao time)
                stats["avg_rtt"] = (1 - ALPHA) * stats["avg_rtt"] + ALPHA * sample_rtt
                
                result = response.json()
                client_weights = [np.array(w, dtype=np.float32) for w in result['weights']]
                sample_count = result['sample_count']

                client_updates.append((client_weights, sample_count))
                total_samples += sample_count
                print(f"Cliente {i+1} respondeu com sucesso.")

            except requests.exceptions.RequestException as e:
                print(f"ERRO: Não foi possível contatar o cliente {i+1}. {e}")
        # --- FIM DA PARTE QUE ESTAVA FALTANDO ---
        
        # Agora esta verificação funciona, pois 'client_updates' existe
        if not client_updates:
            print("Nenhum cliente respondeu. Pulando a rodada.")
            # Avalia o modelo mesmo assim para não pular um ponto no gráfico
            loss, accuracy = global_model.evaluate(x_test, y_test, verbose=0)
            print(f"⚠️  AVALIAÇÃO GLOBAL (sem atualização) - Rodada {round_num + 1}: Perda = {loss:.4f}, Acurácia = {accuracy:.4f}")
            continue

        # Agrega as atualizações usando o algoritmo Federated Averaging
        print("Agregando os pesos dos clientes...")
        new_weights = [np.zeros_like(w) for w in global_weights]

        for client_weights, sample_count in client_updates:
            # Pondera a contribuição de cada cliente pelo número de amostras
            weight_contribution = sample_count / total_samples
            for i in range(len(new_weights)):
                new_weights[i] += client_weights[i] * weight_contribution
        
        # Atualiza o modelo global com os novos pesos agregados
        global_model.set_weights(new_weights)
        print("Modelo global atualizado.")

        # Avalia a performance do novo modelo global com os dados de teste
        loss, accuracy = global_model.evaluate(x_test, y_test, verbose=0)
        print(f"✅ AVALIAÇÃO GLOBAL - Rodada {round_num + 1}: Perda = {loss:.4f}, Acurácia = {accuracy:.4f}")
        
        time.sleep(2)

    print("\n--- Treinamento Federado Concluído ---")


if __name__ == '__main__':
    # Pequena espera para garantir que os servidores Flask dos clientes estejam no ar
    print("Orquestrador esperando 10 segundos para os clientes iniciarem...")
    time.sleep(10)
    run_federated_training()