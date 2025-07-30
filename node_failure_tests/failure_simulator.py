# node_failure_tests/failure_simulator.py

import random
import time
import threading
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

class FailureType(Enum):
    """Tipos de falhas que podem ser simuladas"""
    NETWORK_TIMEOUT = "network_timeout"
    SERVICE_UNAVAILABLE = "service_unavailable"
    SLOW_RESPONSE = "slow_response"
    PARTIAL_FAILURE = "partial_failure"
    TOTAL_FAILURE = "total_failure"

@dataclass
class FailureScenario:
    """Define um cenário de falha"""
    name: str
    description: str
    failure_type: FailureType
    affected_clients: List[int]  # Índices dos clientes afetados
    failure_probability: float  # Probabilidade de falha (0.0 a 1.0)
    duration_rounds: int  # Número de rodadas que a falha persiste
    recovery_probability: float = 0.1  # Probabilidade de recuperação por rodada

class NodeFailureSimulator:
    """Simula falhas de nós durante o treinamento federado"""
    
    def __init__(self, client_endpoints: List[str]):
        self.client_endpoints = client_endpoints
        self.num_clients = len(client_endpoints)
        self.failed_clients = set()
        self.slow_clients = set()
        self.current_scenario = None
        self.scenario_remaining_rounds = 0
        
    def get_predefined_scenarios(self) -> List[FailureScenario]:
        """Retorna cenários de falha predefinidos"""
        scenarios = [
            FailureScenario(
                name="single_node_failure",
                description="Falha de um único nó",
                failure_type=FailureType.TOTAL_FAILURE,
                affected_clients=[0],
                failure_probability=1.0,
                duration_rounds=3
            ),
            FailureScenario(
                name="multiple_node_failure",
                description="Falha de múltiplos nós simultaneamente",
                failure_type=FailureType.TOTAL_FAILURE,
                affected_clients=[0, 1],
                failure_probability=1.0,
                duration_rounds=2
            ),
            FailureScenario(
                name="network_instability",
                description="Instabilidade de rede com timeouts aleatórios",
                failure_type=FailureType.NETWORK_TIMEOUT,
                affected_clients=list(range(self.num_clients)),
                failure_probability=0.3,
                duration_rounds=5
            ),
            FailureScenario(
                name="slow_clients",
                description="Clientes com resposta lenta",
                failure_type=FailureType.SLOW_RESPONSE,
                affected_clients=[1, 2],
                failure_probability=0.8,
                duration_rounds=4
            ),
            FailureScenario(
                name="cascading_failure",
                description="Falha em cascata - um nó falha e depois outros",
                failure_type=FailureType.PARTIAL_FAILURE,
                affected_clients=list(range(self.num_clients)),
                failure_probability=0.2,
                duration_rounds=6,
                recovery_probability=0.05
            ),
            FailureScenario(
                name="intermittent_failure",
                description="Falhas intermitentes com recuperação",
                failure_type=FailureType.SERVICE_UNAVAILABLE,
                affected_clients=list(range(self.num_clients)),
                failure_probability=0.4,
                duration_rounds=8,
                recovery_probability=0.3
            )
        ]
        return scenarios
    
    def start_scenario(self, scenario: FailureScenario):
        """Inicia um cenário de falha"""
        self.current_scenario = scenario
        self.scenario_remaining_rounds = scenario.duration_rounds
        print(f"🎭 Iniciando cenário de falha: {scenario.name}")
        print(f"   Descrição: {scenario.description}")
        print(f"   Duração: {scenario.duration_rounds} rodadas")
    
    def should_client_fail(self, client_index: int, round_num: int) -> Tuple[bool, str]:
        """
        Determina se um cliente deve falhar nesta rodada
        Retorna: (deve_falhar, motivo_da_falha)
        """
        if not self.current_scenario or self.scenario_remaining_rounds <= 0:
            return False, ""
        
        if client_index not in self.current_scenario.affected_clients:
            return False, ""
        
        # Verifica se o cliente já está em falha
        if client_index in self.failed_clients:
            # Chance de recuperação
            if random.random() < self.current_scenario.recovery_probability:
                self.failed_clients.discard(client_index)
                self.slow_clients.discard(client_index)
                print(f"🔄 Cliente {client_index + 1} se recuperou da falha")
                return False, ""
            return True, f"Cliente ainda em falha ({self.current_scenario.failure_type.value})"
        
        # Verifica se deve falhar agora
        if random.random() < self.current_scenario.failure_probability:
            failure_type = self.current_scenario.failure_type
            
            if failure_type == FailureType.TOTAL_FAILURE:
                self.failed_clients.add(client_index)
                return True, "Total failure - client completely unavailable"
            
            elif failure_type == FailureType.NETWORK_TIMEOUT:
                return True, "Network timeout - request will timeout"
            
            elif failure_type == FailureType.SLOW_RESPONSE:
                self.slow_clients.add(client_index)
                return True, "Slow response - client will respond very slowly"
            
            elif failure_type == FailureType.SERVICE_UNAVAILABLE:
                return True, "Service unavailable - temporary service error"
            
            elif failure_type == FailureType.PARTIAL_FAILURE:
                if random.random() < 0.7:  # 70% chance de falha total, 30% de lentidão
                    self.failed_clients.add(client_index)
                    return True, "Partial failure - total unavailability"
                else:
                    self.slow_clients.add(client_index)
                    return True, "Partial failure - slow response"
        
        return False, ""
    
    def get_failure_delay(self, client_index: int) -> float:
        """Retorna o delay adicional para clientes lentos"""
        if client_index in self.slow_clients:
            return random.uniform(10.0, 30.0)  # 10-30 segundos de delay extra
        return 0.0
    
    def update_round(self):
        """Atualiza o estado do simulador para a próxima rodada"""
        if self.scenario_remaining_rounds > 0:
            self.scenario_remaining_rounds -= 1
            
        if self.scenario_remaining_rounds == 0 and self.current_scenario:
            print(f"✅ Cenário de falha '{self.current_scenario.name}' concluído")
            self.current_scenario = None
            self.failed_clients.clear()
            self.slow_clients.clear()
    
    def get_status_summary(self) -> Dict:
        """Retorna um resumo do status atual das falhas"""
        return {
            "active_scenario": self.current_scenario.name if self.current_scenario else None,
            "remaining_rounds": self.scenario_remaining_rounds,
            "failed_clients": list(self.failed_clients),
            "slow_clients": list(self.slow_clients),
            "total_clients": self.num_clients,
            "available_clients": self.num_clients - len(self.failed_clients)
        }
