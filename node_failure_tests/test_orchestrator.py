# node_failure_tests/test_orchestrator.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import numpy as np
import time
import tensorflow as tf
from common.model import create_simple_model
from failure_simulator import NodeFailureSimulator, FailureScenario
from metrics_collector import MetricsCollector
import threading
from typing import List, Dict, Tuple

class TestOrchestrator:
    """Orquestrador modificado para incluir testes de falha de nós"""
    
    def __init__(self, client_endpoints: List[str], num_rounds: int = 10):
        self.client_endpoints = client_endpoints
        self.num_rounds = num_rounds
        
        # Inicializa componentes de teste
        self.failure_simulator = NodeFailureSimulator(client_endpoints)
        self.metrics_collector = MetricsCollector()
        
        # Carrega dados de teste
        print("Carregando dados de teste do MNIST...")
        _, (self.x_test, self.y_test) = tf.keras.datasets.mnist.load_data()
        self.x_test = self.x_test / 255.0
        print("Dados de teste carregados.")
        
        # Inicializa parâmetros de timeout adaptativo
        self.client_timing_stats = {
            endpoint: {"avg_rtt": 30.0, "dev_rtt": 5.0} 
            for endpoint in client_endpoints
        }
        self.MIN_TIMEOUT = 10
        self.MAX_TIMEOUT = 180
        self.ALPHA = 0.125
        self.BETA = 0.25
    
    def run_baseline_training(self, experiment_name: str = "baseline_no_failures"):
        """Executa treinamento sem falhas simuladas (baseline)"""
        print("🏁 Iniciando experimento baseline (sem falhas)")
        self.metrics_collector = MetricsCollector(experiment_name)
        self._run_federated_training(None)
        
    def run_scenario_test(self, scenario: FailureScenario, experiment_name: str = None):
        """Executa um teste com um cenário específico de falha ou baseline"""
        if scenario is None:
            # Executa baseline sem falhas
            if experiment_name is None:
                experiment_name = "baseline_no_failures"
            print("🏁 Iniciando experimento baseline (sem falhas)")
            self.metrics_collector = MetricsCollector(experiment_name)
            self._run_federated_training(None)
        else:
            # Executa cenário com falhas
            if experiment_name is None:
                experiment_name = f"test_{scenario.name}"
                
            print(f"🧪 Iniciando teste de cenário: {scenario.name}")
            self.metrics_collector = MetricsCollector(experiment_name)
            self.failure_simulator.start_scenario(scenario)
            self._run_federated_training(scenario)
    
    def run_all_scenarios(self):
        """Executa todos os cenários de teste predefinidos"""
        scenarios = self.failure_simulator.get_predefined_scenarios()
        
        print(f"🎯 Executando {len(scenarios)} cenários de teste...")
        
        # Primeiro executa baseline
        self.run_baseline_training()
        baseline_results = self.metrics_collector.export_to_excel()
        
        # Depois executa cada cenário
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{'='*60}")
            print(f"Executando cenário {i}/{len(scenarios)}: {scenario.name}")
            print(f"{'='*60}")
            
            self.run_scenario_test(scenario)
            results_path = self.metrics_collector.export_to_excel()
            
            # Pausa entre cenários para limpeza
            print("⏳ Aguardando 30 segundos antes do próximo cenário...")
            time.sleep(30)
        
        print("\n✅ Todos os cenários de teste foram executados!")
        return baseline_results
    
    def _run_federated_training(self, scenario: FailureScenario = None):
        """Executa o ciclo de treinamento federado com monitoramento de falhas"""
        print("--- Iniciando Treinamento Federado com Monitoramento ---")
        
        # Inicializa o modelo global
        global_model = create_simple_model()
        global_model.compile(loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        
        # Loop principal de treinamento
        for round_num in range(self.num_rounds):
            print(f"\n--- RODADA {round_num + 1}/{self.num_rounds} ---")
            
            round_start_time = time.time()
            
            # Atualiza o simulador de falhas
            self.failure_simulator.update_round()
            
            # Pega os pesos do modelo global
            global_weights = global_model.get_weights()
            global_weights_serializable = [w.tolist() for w in global_weights]
            
            # Coleta métricas da rodada
            client_updates = []
            total_samples = 0
            response_times = []
            timeout_count = 0
            failed_clients_this_round = []
            slow_clients_this_round = []
            client_contributions = {}
            
            # Envia o modelo para cada cliente
            for i, endpoint in enumerate(self.client_endpoints):
                client_start_time = time.time()
                
                # Verifica se o cliente deve falhar
                should_fail, failure_reason = self.failure_simulator.should_client_fail(i, round_num)
                
                if should_fail:
                    print(f"💥 Cliente {i+1} simulando falha: {failure_reason}")
                    failed_clients_this_round.append(i)
                    
                    # Simula diferentes tipos de falha
                    if "timeout" in failure_reason.lower():
                        timeout_count += 1
                        response_times.append(self.MAX_TIMEOUT)
                    elif "slow" in failure_reason.lower():
                        slow_clients_this_round.append(i)
                        delay = self.failure_simulator.get_failure_delay(i)
                        time.sleep(delay)  # Simula resposta lenta
                        response_times.append(delay + 5.0)  # Tempo base + delay
                    else:
                        response_times.append(0.0)  # Falha imediata
                    
                    continue
                
                # Cliente normal - tenta comunicação
                try:
                    # Adiciona delay se o cliente está marcado como lento
                    extra_delay = self.failure_simulator.get_failure_delay(i)
                    if extra_delay > 0:
                        print(f"🐌 Cliente {i+1} com resposta lenta (+{extra_delay:.1f}s)")
                        time.sleep(extra_delay)
                        slow_clients_this_round.append(i)
                    
                    # Calcula timeout adaptativo
                    stats = self.client_timing_stats[endpoint]
                    current_timeout = stats["avg_rtt"] + 4 * stats["dev_rtt"]
                    current_timeout = max(self.MIN_TIMEOUT, min(current_timeout, self.MAX_TIMEOUT))
                    
                    print(f"📤 Enviando modelo para cliente {i+1} ({endpoint})...")
                    
                    response = requests.post(
                        endpoint,
                        json={'weights': global_weights_serializable},
                        timeout=current_timeout
                    )
                    
                    client_end_time = time.time()
                    response_time = client_end_time - client_start_time
                    response_times.append(response_time)
                    
                    response.raise_for_status()
                    
                    # Atualiza estatísticas de timing
                    delta = abs(response_time - stats["avg_rtt"])
                    stats["dev_rtt"] = (1 - self.BETA) * stats["dev_rtt"] + self.BETA * delta
                    stats["avg_rtt"] = (1 - self.ALPHA) * stats["avg_rtt"] + self.ALPHA * response_time
                    
                    result = response.json()
                    client_weights = [np.array(w, dtype=np.float32) for w in result['weights']]
                    sample_count = result['sample_count']
                    
                    client_updates.append((client_weights, sample_count))
                    total_samples += sample_count
                    client_contributions[i] = sample_count
                    
                    print(f"✅ Cliente {i+1} respondeu com sucesso ({response_time:.2f}s)")
                    
                except requests.exceptions.Timeout:
                    print(f"⏰ TIMEOUT: Cliente {i+1} não respondeu no tempo limite")
                    timeout_count += 1
                    failed_clients_this_round.append(i)
                    response_times.append(current_timeout)
                    
                except requests.exceptions.RequestException as e:
                    print(f"❌ ERRO: Não foi possível contatar cliente {i+1}. {e}")
                    failed_clients_this_round.append(i)
                    response_times.append(0.0)
            
            # Tempo de agregação
            aggregation_start_time = time.time()
            
            # Verifica se algum cliente respondeu
            if not client_updates:
                print("⚠️  Nenhum cliente respondeu. Pulando agregação.")
                loss, accuracy = global_model.evaluate(self.x_test, self.y_test, verbose=0)
                aggregation_time = time.time() - aggregation_start_time
            else:
                # Agrega as atualizações
                print(f"🔄 Agregando pesos de {len(client_updates)} clientes...")
                new_weights = [np.zeros_like(w) for w in global_weights]
                
                for client_weights, sample_count in client_updates:
                    weight_contribution = sample_count / total_samples
                    for j in range(len(new_weights)):
                        new_weights[j] += client_weights[j] * weight_contribution
                
                global_model.set_weights(new_weights)
                loss, accuracy = global_model.evaluate(self.x_test, self.y_test, verbose=0)
                aggregation_time = time.time() - aggregation_start_time
                
                print("✅ Modelo global atualizado")
            
            # Registra métricas da rodada
            self.metrics_collector.record_round(
                round_number=round_num + 1,
                scenario_name=scenario.name if scenario else None,
                total_clients=len(self.client_endpoints),
                responding_clients=len(client_updates),
                failed_clients=failed_clients_this_round,
                slow_clients=slow_clients_this_round,
                response_times=response_times,
                timeout_count=timeout_count,
                global_loss=float(loss),
                global_accuracy=float(accuracy),
                aggregation_time=aggregation_time,
                total_samples=total_samples,
                client_contributions=client_contributions
            )
            
            # Status da rodada
            status = self.failure_simulator.get_status_summary()
            print(f"📊 RESULTADOS DA RODADA {round_num + 1}:")
            print(f"   • Acurácia: {accuracy:.4f} | Perda: {loss:.4f}")
            print(f"   • Clientes responderam: {len(client_updates)}/{len(self.client_endpoints)}")
            print(f"   • Falhas: {len(failed_clients_this_round)} | Timeouts: {timeout_count}")
            print(f"   • Tempo médio resposta: {np.mean(response_times):.2f}s")
            if status['active_scenario']:
                print(f"   • Cenário ativo: {status['active_scenario']} ({status['remaining_rounds']} rodadas restantes)")
            
            time.sleep(2)  # Pausa entre rodadas
        
        print("\n--- Treinamento Federado Concluído ---")
        
        # Exporta métricas
        excel_path = self.metrics_collector.export_to_excel()
        json_path = self.metrics_collector.export_to_json()
        
        return excel_path, json_path

def main():
    """Função principal para executar os testes"""
    
    # Configuração dos endpoints dos clientes
    CLIENT_ENDPOINTS = [
        "http://client-1:5000/fit",
        "http://client-2:5000/fit", 
        "http://client-3:5000/fit",
    ]
    
    # Cria o orquestrador de testes
    test_orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=10)
    
    print("🚀 Iniciando suite de testes de falha de nós")
    print("=" * 60)
    
    # Executa todos os cenários
    test_orchestrator.run_all_scenarios()
    
    print("\n🎉 Todos os testes foram concluídos!")
    print("📁 Verifique os resultados na pasta 'node_failure_tests/results'")

if __name__ == '__main__':
    # Espera os clientes iniciarem
    print("⏳ Aguardando 15 segundos para os clientes iniciarem...")
    time.sleep(15)
    main()
