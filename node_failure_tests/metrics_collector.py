# node_failure_tests/metrics_collector.py

import time
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import os

@dataclass
class RoundMetrics:
    """Métricas coletadas em cada rodada do treinamento"""
    round_number: int
    timestamp: str
    scenario_name: Optional[str]
    total_clients: int
    responding_clients: int
    failed_clients: List[int]
    slow_clients: List[int]
    response_times: List[float]
    avg_response_time: float
    max_response_time: float
    min_response_time: float
    timeout_count: int
    global_loss: float
    global_accuracy: float
    convergence_rate: float
    aggregation_time: float
    total_samples: int
    client_contributions: Dict[int, int]  # client_id -> sample_count
    
@dataclass
class ExperimentMetrics:
    """Métricas completas de um experimento"""
    experiment_id: str
    start_time: str
    end_time: str
    total_rounds: int
    scenarios_tested: List[str]
    average_accuracy: float
    final_accuracy: float
    convergence_round: Optional[int]
    total_failures: int
    resilience_score: float
    rounds: List[RoundMetrics]

class MetricsCollector:
    """Coleta e exporta métricas do treinamento federado com falhas de nós"""
    
    def __init__(self, experiment_name: str = None):
        self.experiment_name = experiment_name or f"fl_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.experiment_id = f"{self.experiment_name}_{int(time.time())}"
        self.start_time = datetime.now().isoformat()
        self.rounds_data: List[RoundMetrics] = []
        self.scenarios_tested: List[str] = []
        
    def record_round(self, 
                    round_number: int,
                    scenario_name: Optional[str],
                    total_clients: int,
                    responding_clients: int,
                    failed_clients: List[int],
                    slow_clients: List[int],
                    response_times: List[float],
                    timeout_count: int,
                    global_loss: float,
                    global_accuracy: float,
                    aggregation_time: float,
                    total_samples: int,
                    client_contributions: Dict[int, int]):
        """Registra as métricas de uma rodada"""
        
        # Calcula métricas derivadas
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        max_response_time = max(response_times) if response_times else 0.0
        min_response_time = min(response_times) if response_times else 0.0
        
        # Taxa de convergência (melhoria da acurácia em relação à rodada anterior)
        convergence_rate = 0.0
        if len(self.rounds_data) > 0:
            prev_accuracy = self.rounds_data[-1].global_accuracy
            convergence_rate = global_accuracy - prev_accuracy
        
        round_metrics = RoundMetrics(
            round_number=round_number,
            timestamp=datetime.now().isoformat(),
            scenario_name=scenario_name,
            total_clients=total_clients,
            responding_clients=responding_clients,
            failed_clients=failed_clients.copy(),
            slow_clients=slow_clients.copy(),
            response_times=response_times.copy(),
            avg_response_time=avg_response_time,
            max_response_time=max_response_time,
            min_response_time=min_response_time,
            timeout_count=timeout_count,
            global_loss=global_loss,
            global_accuracy=global_accuracy,
            convergence_rate=convergence_rate,
            aggregation_time=aggregation_time,
            total_samples=total_samples,
            client_contributions=client_contributions.copy()
        )
        
        self.rounds_data.append(round_metrics)
        
        if scenario_name and scenario_name not in self.scenarios_tested:
            self.scenarios_tested.append(scenario_name)
        
        print(f"📊 Métricas registradas para rodada {round_number}")
    
    def calculate_resilience_score(self) -> float:
        """
        Calcula um score de resiliência baseado no desempenho durante falhas
        Score entre 0.0 (baixa resiliência) e 1.0 (alta resiliência)
        """
        if not self.rounds_data:
            return 0.0
        
        total_score = 0.0
        failure_rounds = 0
        
        for round_data in self.rounds_data:
            if round_data.failed_clients or round_data.slow_clients:
                failure_rounds += 1
                # Pontuação baseada na proporção de clientes respondendo
                client_availability = round_data.responding_clients / round_data.total_clients
                # Pontuação baseada na manutenção da acurácia
                accuracy_factor = round_data.global_accuracy
                # Pontuação baseada no tempo de resposta
                response_factor = max(0, 1.0 - (round_data.avg_response_time / 60.0))  # Normaliza para 60s
                
                round_score = (client_availability * 0.4 + accuracy_factor * 0.4 + response_factor * 0.2)
                total_score += round_score
        
        return total_score / failure_rounds if failure_rounds > 0 else 1.0
    
    def find_convergence_round(self, threshold: float = 0.001) -> Optional[int]:
        """Encontra a rodada onde o modelo convergiu (mudanças < threshold)"""
        for i in range(1, len(self.rounds_data)):
            if abs(self.rounds_data[i].convergence_rate) < threshold:
                return i + 1
        return None
    
    def export_to_excel(self, output_dir: str = "node_failure_tests/results") -> str:
        """Exporta todas as métricas para um arquivo Excel"""
        
        # Cria o diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Nome do arquivo com timestamp
        filename = f"{self.experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(output_dir, filename)
        
        # Calcula métricas finais
        end_time = datetime.now().isoformat()
        average_accuracy = sum(r.global_accuracy for r in self.rounds_data) / len(self.rounds_data)
        final_accuracy = self.rounds_data[-1].global_accuracy if self.rounds_data else 0.0
        convergence_round = self.find_convergence_round()
        total_failures = sum(len(r.failed_clients) for r in self.rounds_data)
        resilience_score = self.calculate_resilience_score()
        
        # Cria o objeto de métricas do experimento
        experiment_metrics = ExperimentMetrics(
            experiment_id=self.experiment_id,
            start_time=self.start_time,
            end_time=end_time,
            total_rounds=len(self.rounds_data),
            scenarios_tested=self.scenarios_tested,
            average_accuracy=average_accuracy,
            final_accuracy=final_accuracy,
            convergence_round=convergence_round,
            total_failures=total_failures,
            resilience_score=resilience_score,
            rounds=self.rounds_data
        )
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # Aba 1: Resumo do Experimento
            summary_data = {
                'Métrica': [
                    'ID do Experimento',
                    'Nome do Experimento', 
                    'Início',
                    'Fim',
                    'Duração Total (min)',
                    'Total de Rodadas',
                    'Cenários Testados',
                    'Acurácia Média',
                    'Acurácia Final',
                    'Rodada de Convergência',
                    'Total de Falhas',
                    'Score de Resiliência'
                ],
                'Valor': [
                    experiment_metrics.experiment_id,
                    self.experiment_name,
                    experiment_metrics.start_time,
                    experiment_metrics.end_time,
                    round((datetime.fromisoformat(experiment_metrics.end_time) - 
                          datetime.fromisoformat(experiment_metrics.start_time)).total_seconds() / 60, 2),
                    experiment_metrics.total_rounds,
                    ', '.join(experiment_metrics.scenarios_tested),
                    round(experiment_metrics.average_accuracy, 4),
                    round(experiment_metrics.final_accuracy, 4),
                    experiment_metrics.convergence_round or 'Não convergiu',
                    experiment_metrics.total_failures,
                    round(experiment_metrics.resilience_score, 4)
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Aba 2: Métricas por Rodada
            rounds_data = []
            for round_metrics in self.rounds_data:
                round_dict = asdict(round_metrics)
                # Converte listas para strings para melhor visualização
                round_dict['failed_clients'] = str(round_dict['failed_clients'])
                round_dict['slow_clients'] = str(round_dict['slow_clients'])
                round_dict['response_times'] = str([round(t, 2) for t in round_dict['response_times']])
                round_dict['client_contributions'] = str(round_dict['client_contributions'])
                rounds_data.append(round_dict)
            
            rounds_df = pd.DataFrame(rounds_data)
            rounds_df.to_excel(writer, sheet_name='Métricas por Rodada', index=False)
            
            # Aba 3: Análise de Falhas
            failure_analysis = []
            for round_metrics in self.rounds_data:
                if round_metrics.failed_clients or round_metrics.slow_clients:
                    failure_analysis.append({
                        'Rodada': round_metrics.round_number,
                        'Cenário': round_metrics.scenario_name or 'N/A',
                        'Clientes Falharam': len(round_metrics.failed_clients),
                        'Clientes Lentos': len(round_metrics.slow_clients),
                        'Taxa de Disponibilidade': round_metrics.responding_clients / round_metrics.total_clients,
                        'Timeouts': round_metrics.timeout_count,
                        'Tempo Médio (s)': round(round_metrics.avg_response_time, 2),
                        'Acurácia': round(round_metrics.global_accuracy, 4),
                        'Impacto na Convergência': round(round_metrics.convergence_rate, 6)
                    })
            
            if failure_analysis:
                failure_df = pd.DataFrame(failure_analysis)
                failure_df.to_excel(writer, sheet_name='Análise de Falhas', index=False)
            
            # Aba 4: Estatísticas por Cenário
            scenario_stats = {}
            for round_metrics in self.rounds_data:
                scenario = round_metrics.scenario_name or 'baseline'
                if scenario not in scenario_stats:
                    scenario_stats[scenario] = {
                        'rounds': 0,
                        'avg_accuracy': 0.0,
                        'avg_response_time': 0.0,
                        'total_failures': 0,
                        'total_timeouts': 0
                    }
                
                stats = scenario_stats[scenario]
                stats['rounds'] += 1
                stats['avg_accuracy'] += round_metrics.global_accuracy
                stats['avg_response_time'] += round_metrics.avg_response_time
                stats['total_failures'] += len(round_metrics.failed_clients)
                stats['total_timeouts'] += round_metrics.timeout_count
            
            # Calcula médias
            scenario_summary = []
            for scenario, stats in scenario_stats.items():
                rounds = stats['rounds']
                scenario_summary.append({
                    'Cenário': scenario,
                    'Rodadas': rounds,
                    'Acurácia Média': round(stats['avg_accuracy'] / rounds, 4),
                    'Tempo Resposta Médio (s)': round(stats['avg_response_time'] / rounds, 2),
                    'Total de Falhas': stats['total_failures'],
                    'Total de Timeouts': stats['total_timeouts'],
                    'Falhas por Rodada': round(stats['total_failures'] / rounds, 2)
                })
            
            scenario_df = pd.DataFrame(scenario_summary)
            scenario_df.to_excel(writer, sheet_name='Estatísticas por Cenário', index=False)
        
        print(f"📁 Métricas exportadas para: {filepath}")
        return filepath
    
    def export_to_json(self, output_dir: str = "node_failure_tests/results") -> str:
        """Exporta as métricas para JSON (para análises programáticas)"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{self.experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Prepara os dados para serialização JSON
        export_data = {
            'experiment_id': self.experiment_id,
            'experiment_name': self.experiment_name,
            'start_time': self.start_time,
            'end_time': datetime.now().isoformat(),
            'total_rounds': len(self.rounds_data),
            'scenarios_tested': self.scenarios_tested,
            'resilience_score': self.calculate_resilience_score(),
            'rounds': [asdict(round_data) for round_data in self.rounds_data]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Dados JSON exportados para: {filepath}")
        return filepath
