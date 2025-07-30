# node_failure_tests/run_single_scenario.py

"""
Script para executar um único cenário de teste de falha
Útil para testes rápidos e depuração
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_orchestrator import TestOrchestrator
from failure_simulator import FailureScenario, FailureType

def main():
    """Executa um único cenário de teste"""
    
    # Configuração dos endpoints
    CLIENT_ENDPOINTS = [
        "http://client-1:5000/fit",
        "http://client-2:5000/fit",
        "http://client-3:5000/fit",
    ]
    
    # Cria o orquestrador
    orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=8)
    
    # Define um cenário customizado para teste rápido
    test_scenario = FailureScenario(
        name="quick_test",
        description="Teste rápido com falha de um nó",
        failure_type=FailureType.TOTAL_FAILURE,
        affected_clients=[0],  # Apenas o primeiro cliente
        failure_probability=1.0,
        duration_rounds=3
    )
    
    print("🧪 Executando cenário de teste único")
    print(f"Cenário: {test_scenario.name}")
    print(f"Descrição: {test_scenario.description}")
    
    # Executa o teste
    orchestrator.run_scenario_test(test_scenario, "single_test")
    
    print("✅ Teste concluído!")

if __name__ == '__main__':
    main()
