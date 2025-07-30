#!/usr/bin/env python3
# node_failure_tests/run_advanced_test.py
"""
Script para executar teste avançado completo de resiliência
Executa todos os 7 cenários + análise comparativa automática
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_orchestrator import TestOrchestrator
from failure_simulator import FailureScenario, FailureType
import time
import subprocess

def main():
    CLIENT_ENDPOINTS = [
        'http://client-1:5000/fit', 
        'http://client-2:5000/fit', 
        'http://client-3:5000/fit'
    ]
    
    # Configuração avançada com mais rodadas para análise detalhada
    orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=10)

    print('🚀 TESTE AVANÇADO - Análise Completa de Resiliência')
    print('⏱️  Duração estimada: 45-60 minutos')
    print('📊 Executa todos os 7 cenários + análise comparativa')
    print('🎯 10 rodadas por cenário para análise estatística robusta')
    print('=' * 80)
    print()

    # Definição completa de todos os cenários
    scenarios = [
        {
            'name': 'baseline',
            'description': 'Baseline sem falhas (referência)',
            'scenario': None,
            'expected_accuracy': '90-92%',
            'expected_resilience': '1.0 (perfeito)'
        },
        {
            'name': 'single_failure',
            'description': 'Falha de um nó por 3 rodadas',
            'scenario': FailureScenario(
                'single_failure', 
                'Um cliente falha completamente por 3 rodadas',
                FailureType.TOTAL_FAILURE, 
                [0], 1.0, 3, 0.0
            ),
            'expected_accuracy': '88-91%',
            'expected_resilience': '0.8-0.9'
        },
        {
            'name': 'multiple_failure',
            'description': 'Falha de múltiplos nós por 2 rodadas',
            'scenario': FailureScenario(
                'multiple_failure',
                'Dois clientes falham simultaneamente por 2 rodadas',
                FailureType.TOTAL_FAILURE,
                [0, 1], 1.0, 2, 0.0
            ),
            'expected_accuracy': '85-88%',
            'expected_resilience': '0.6-0.8'
        },
        {
            'name': 'network_instability',
            'description': 'Instabilidade de rede (30% chance)',
            'scenario': FailureScenario(
                'network_instability',
                'Timeouts aleatórios em todos os clientes (30% por rodada)',
                FailureType.NETWORK_TIMEOUT,
                [0, 1, 2], 0.3, 5, 0.1
            ),
            'expected_accuracy': '87-90%',
            'expected_resilience': '0.7-0.9'
        },
        {
            'name': 'slow_clients',
            'description': 'Clientes lentos (80% chance)',
            'scenario': FailureScenario(
                'slow_clients',
                'Clientes 2 e 3 respondem lentamente (80% chance)',
                FailureType.SLOW_RESPONSE,
                [1, 2], 0.8, 6, 0.0
            ),
            'expected_accuracy': '86-89%',
            'expected_resilience': '0.6-0.8'
        },
        {
            'name': 'cascading_failure',
            'description': 'Falha em cascata (20% -> 5% recuperação)',
            'scenario': FailureScenario(
                'cascading_failure',
                'Falhas se espalham progressivamente com baixa recuperação',
                FailureType.TOTAL_FAILURE,
                [0, 1, 2], 0.2, 8, 0.05
            ),
            'expected_accuracy': '75-85%',
            'expected_resilience': '0.4-0.7'
        },
        {
            'name': 'intermittent_failure',
            'description': 'Falhas intermitentes (40% -> 30% recuperação)',
            'scenario': FailureScenario(
                'intermittent_failure',
                'Clientes entram e saem de falha frequentemente',
                FailureType.NETWORK_TIMEOUT,
                [0, 1, 2], 0.4, 7, 0.3
            ),
            'expected_accuracy': '83-87%',
            'expected_resilience': '0.6-0.8'
        }
    ]

    results = []
    start_time_total = time.time()

    # Executa cada cenário
    for i, scenario_config in enumerate(scenarios, 1):
        name = scenario_config['name']
        description = scenario_config['description']
        scenario = scenario_config['scenario']
        expected_acc = scenario_config['expected_accuracy']
        expected_res = scenario_config['expected_resilience']
        
        print(f'🧪 [{i}/7] Executando cenário: {name.upper()}')
        print(f'    📋 Descrição: {description}')
        print(f'    🎯 Acurácia esperada: {expected_acc}')
        print(f'    🛡️  Resiliência esperada: {expected_res}')
        print(f'    ⏱️  Tempo estimado: ~6-9 minutos')
        print()
        
        start_time = time.time()
        
        try:
            if scenario is None:
                print('    🎯 Executando baseline (sem falhas)...')
                result = orchestrator.run_scenario_test(None, f'advanced_test_{name}')
            else:
                print(f'    💥 Executando cenário: {scenario.failure_type.name}')
                result = orchestrator.run_scenario_test(scenario, f'advanced_test_{name}')
            
            duration_min = (time.time() - start_time) / 60
            results.append((name, description, duration_min, 'SUCCESS', expected_acc, expected_res))
            print(f'    ✅ Cenário {name} concluído em {duration_min:.1f} minutos')
        except Exception as e:
            duration_min = (time.time() - start_time) / 60
            results.append((name, description, duration_min, f'ERROR: {str(e)}', expected_acc, expected_res))
            print(f'    ❌ Erro no cenário {name}: {str(e)}')
        
        print('=' * 80)
        if i < len(scenarios):
            print('⏳ Aguardando 5 segundos antes do próximo cenário...')
            time.sleep(5)
        print()

    # Executa análise comparativa automática
    print('📊 EXECUTANDO ANÁLISE COMPARATIVA AUTOMÁTICA...')
    try:
        subprocess.run(['python', 'analyze_results.py'], check=True, cwd=os.path.dirname(os.path.abspath(__file__)))
        print('✅ Análise automática concluída!')
    except Exception as e:
        print(f'⚠️  Análise automática falhou: {e}')
        print('💡 Execute manualmente: python analyze_results.py')

    # Relatório final
    total_time = (time.time() - start_time_total) / 60
    success_count = sum(1 for _, _, _, status, _, _ in results if status == 'SUCCESS')

    print()
    print('🎉 TESTE AVANÇADO FINALIZADO!')
    print('=' * 80)
    print('📊 RESUMO EXECUTIVO:')
    print()

    for name, description, duration, status, expected_acc, expected_res in results:
        if status == 'SUCCESS':
            print(f'    ✅ {name.upper()}:')
            print(f'        📋 {description}')
            print(f'        ⏱️  Duração: {duration:.1f} min')
            print(f'        🎯 Acurácia esperada: {expected_acc}')
            print(f'        🛡️  Resiliência esperada: {expected_res}')
        else:
            print(f'    ❌ {name.upper()}: {status}')
        print()

    print('📈 ESTATÍSTICAS GERAIS:')
    print(f'    🎯 Taxa de Sucesso: {success_count}/{len(scenarios)} ({(success_count/len(scenarios)*100):.1f}%)')
    print(f'    ⏱️  Tempo Total: {total_time:.1f} minutos')
    print(f'    📁 Arquivos Excel: {success_count} gerados')
    print(f'    📄 Arquivos JSON: {success_count} gerados')
    print()
    
    print('📈 PRÓXIMOS PASSOS:')
    print('    1. 📊 Abra os arquivos Excel em node_failure_tests/results/')
    print('    2. 📈 Compare os scores de resiliência entre cenários')
    print('    3. 📉 Analise tendências de convergência e acurácia')
    print('    4. 🔍 Identifique pontos fracos do sistema')
    print('    5. 🛠️  Implemente melhorias baseadas nos resultados')
    print()
    
    if success_count == len(scenarios):
        print('🏆 PARABÉNS! Análise completa de resiliência finalizada com 100% de sucesso!')
        print('🎉 Seu sistema de Federated Learning demonstrou robustez em todos os cenários!')
    else:
        print('⚠️  Alguns cenários falharam. Revise os logs para identificar problemas.')
    
    print('=' * 80)

if __name__ == "__main__":
    main()
