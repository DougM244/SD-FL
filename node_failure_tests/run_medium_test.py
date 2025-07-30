#!/usr/bin/env python3
"""
Script para executar teste médio com 3 cenários principais.
Duração estimada: 15-20 minutos
"""

import sys
import os
import time

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('/app')
sys.path.append('/app/node_failure_tests')

try:
    from test_orchestrator import TestOrchestrator
    from failure_simulator import FailureScenario, FailureType
except ImportError:
    try:
        from node_failure_tests.test_orchestrator import TestOrchestrator
        from node_failure_tests.failure_simulator import FailureScenario, FailureType
    except ImportError:
        print("❌ Erro: Não foi possível importar os módulos necessários")
        print("   Verifique se você está no diretório correto")
        sys.exit(1)

def main():
    print("🚀 TESTE MÉDIO - 3 Cenários Principais de Falha de Nós")
    print("⏱️  Duração estimada: 15-20 minutos")
    print("=" * 60)
    print()

    # Configuração dos endpoints dos clientes
    CLIENT_ENDPOINTS = [
        'http://client-1:5000/fit', 
        'http://client-2:5000/fit', 
        'http://client-3:5000/fit'
    ]
    
    # Inicializa o orchestrador
    orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=8)
    
    # Define os 3 cenários principais
    scenarios = [
        {
            'name': 'baseline',
            'description': 'Baseline sem falhas (referência)',
            'failure_type': FailureType.NO_FAILURE,
            'affected_clients': [],
            'failure_probability': 0.0,
            'duration_rounds': 8,
            'recovery_probability': 0.0
        },
        {
            'name': 'single_failure',
            'description': 'Falha de um nó por 3 rodadas',
            'failure_type': FailureType.TOTAL_FAILURE,
            'affected_clients': [0],
            'failure_probability': 1.0,
            'duration_rounds': 3,
            'recovery_probability': 0.0
        },
        {
            'name': 'network_issues',
            'description': 'Instabilidade de rede (30% falha)',
            'failure_type': FailureType.NETWORK_TIMEOUT,
            'affected_clients': [0, 1, 2],
            'failure_probability': 0.3,
            'duration_rounds': 5,
            'recovery_probability': 0.1
        }
    ]
    
    results_summary = []
    
    for i, scenario_config in enumerate(scenarios, 1):
        print(f"🧪 [{i}/3] Executando cenário: {scenario_config['name'].upper()}")
        print(f"   📝 Descrição: {scenario_config['description']}")
        print(f"   ⏱️  Tempo estimado: ~5-7 minutos")
        print()
        
        start_time = time.time()
        
        # Cria o cenário de falha
        scenario = FailureScenario(
            name=scenario_config['name'],
            description=scenario_config['description'],
            failure_type=scenario_config['failure_type'],
            affected_clients=scenario_config['affected_clients'],
            failure_probability=scenario_config['failure_probability'],
            duration_rounds=scenario_config['duration_rounds'],
            recovery_probability=scenario_config['recovery_probability']
        )
        
        # Executa o teste
        try:
            result = orchestrator.run_scenario_test(scenario, f'medium_test_{scenario_config["name"]}')
            end_time = time.time()
            
            duration_min = (end_time - start_time) / 60
            results_summary.append((scenario_config['name'], scenario_config['description'], duration_min))
            
            print(f"✅ Cenário {scenario_config['name']} concluído em {duration_min:.1f} minutos")
            
        except Exception as e:
            print(f"❌ Erro no cenário {scenario_config['name']}: {str(e)}")
            results_summary.append((scenario_config['name'], f"ERRO: {str(e)}", 0))
        
        print("=" * 60)
        
        if i < len(scenarios):
            print("⏸️  Aguardando 3 segundos antes do próximo cenário...")
            time.sleep(3)
        print()
    
    # Resumo final
    print("🎉 TESTE MÉDIO FINALIZADO!")
    print()
    print("📊 RESUMO DOS RESULTADOS:")
    total_time = sum(duration for _, _, duration in results_summary if isinstance(duration, (int, float)))
    
    for name, desc, duration in results_summary:
        if isinstance(duration, (int, float)) and duration > 0:
            print(f"   • {name}: {desc} ({duration:.1f} min)")
        else:
            print(f"   • {name}: {desc}")
    
    if total_time > 0:
        print(f"   • TEMPO TOTAL: {total_time:.1f} minutos")
    print()
    print("📁 Todos os resultados foram salvos em node_failure_tests/results/")
    print("📈 Execute: python analyze_results.py para análise automática")

if __name__ == "__main__":
    main()
