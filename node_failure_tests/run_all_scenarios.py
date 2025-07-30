#!/usr/bin/env python3
# node_failure_tests/run_all_scenarios.py
"""
Script principal para executar TESTE COMPLETO com todos os 7 cenários
Este é o teste mais abrangente do sistema (30-45 minutos)
"""

import sys
import os
import time
from datetime import datetime

# Adiciona os caminhos necessários
sys.path.append('/app')
sys.path.append('/app/node_failure_tests')

from test_orchestrator import TestOrchestrator
from failure_simulator import FailureScenario, FailureType

def main():
    print("🚀 TESTE COMPLETO - ANÁLISE ABRANGENTE DE RESILIÊNCIA")
    print("=" * 80)
    print("⏱️  Duração estimada: 30-45 minutos")
    print("📊 Executa todos os 7 cenários de falha automaticamente")
    print("📁 Gera 14 arquivos de resultado (Excel + JSON)")
    print("🎯 Análise comparativa completa de resiliência")
    print("=" * 80)
    print()

    # Configuração dos endpoints dos clientes
    CLIENT_ENDPOINTS = [
        'http://client-1:5000/fit',
        'http://client-2:5000/fit', 
        'http://client-3:5000/fit'
    ]
    
    # Inicializa o orquestrador de testes
    orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=10)
    
    # Define todos os cenários de teste
    scenarios = [
        {
            'name': 'baseline',
            'description': 'Baseline sem falhas (referência)',
            'scenario': None,
            'expected_resilience': 1.0,
            'expected_accuracy': '>0.85'
        },
        {
            'name': 'single_node_failure',
            'description': 'Falha de um nó por 3 rodadas',
            'scenario': FailureScenario(
                name='single_failure',
                description='Cliente 1 falha completamente',
                failure_type=FailureType.TOTAL_FAILURE,
                affected_clients=[0],
                failure_probability=1.0,
                duration_rounds=3,
                recovery_probability=0.0
            ),
            'expected_resilience': '>0.7',
            'expected_accuracy': '>0.80'
        },
        {
            'name': 'multiple_node_failure',
            'description': 'Falha de múltiplos nós por 2 rodadas',
            'scenario': FailureScenario(
                name='multiple_failure',
                description='Clientes 1 e 2 falham simultaneamente',
                failure_type=FailureType.TOTAL_FAILURE,
                affected_clients=[0, 1],
                failure_probability=1.0,
                duration_rounds=2,
                recovery_probability=0.0
            ),
            'expected_resilience': '>0.6',
            'expected_accuracy': '>0.75'
        },
        {
            'name': 'network_instability',
            'description': 'Instabilidade de rede (30% chance/rodada)',
            'scenario': FailureScenario(
                name='network_instability',
                description='Timeouts aleatórios em todos os clientes',
                failure_type=FailureType.NETWORK_TIMEOUT,
                affected_clients=[0, 1, 2],
                failure_probability=0.3,
                duration_rounds=5,
                recovery_probability=0.1
            ),
            'expected_resilience': '>0.65',
            'expected_accuracy': '>0.78'
        },
        {
            'name': 'slow_clients',
            'description': 'Clientes lentos (80% chance/rodada)',
            'scenario': FailureScenario(
                name='slow_clients',
                description='Clientes 2 e 3 respondem lentamente',
                failure_type=FailureType.SLOW_RESPONSE,
                affected_clients=[1, 2],
                failure_probability=0.8,
                duration_rounds=6,
                recovery_probability=0.0
            ),
            'expected_resilience': '>0.55',
            'expected_accuracy': '>0.75'
        },
        {
            'name': 'cascading_failure',
            'description': 'Falha em cascata (20% chance, recuperação 5%)',
            'scenario': FailureScenario(
                name='cascading_failure',
                description='Falhas progressivas se espalhando',
                failure_type=FailureType.TOTAL_FAILURE,
                affected_clients=[0, 1, 2],
                failure_probability=0.2,
                duration_rounds=8,
                recovery_probability=0.05
            ),
            'expected_resilience': '>0.45',
            'expected_accuracy': '>0.70'
        },
        {
            'name': 'intermittent_failure',
            'description': 'Falhas intermitentes (40% chance, recuperação 30%)',
            'scenario': FailureScenario(
                name='intermittent_failure',
                description='Clientes entram/saem de falha',
                failure_type=FailureType.NETWORK_TIMEOUT,
                affected_clients=[0, 1, 2],
                failure_probability=0.4,
                duration_rounds=7,
                recovery_probability=0.3
            ),
            'expected_resilience': '>0.50',
            'expected_accuracy': '>0.72'
        }
    ]
    
    # Executa todos os cenários
    results = []
    start_time_total = time.time()
    
    for i, scenario_config in enumerate(scenarios, 1):
        print(f"🧪 [{i}/{len(scenarios)}] EXECUTANDO: {scenario_config['name'].upper()}")
        print(f"    📋 Descrição: {scenario_config['description']}")
        print(f"    🎯 Resiliência esperada: {scenario_config['expected_resilience']}")
        print(f"    📊 Acurácia esperada: {scenario_config['expected_accuracy']}")
        print(f"    ⏱️  Tempo estimado: ~4-7 minutos")
        print()
        
        start_time = time.time()
        
        try:
            if scenario_config['scenario'] is None:
                print("    🎯 Executando baseline (sem falhas)...")
                result = orchestrator.run_scenario_test(None, f"complete_test_{scenario_config['name']}")
            else:
                print(f"    💥 Executando cenário: {scenario_config['scenario'].failure_type.name}")
                result = orchestrator.run_scenario_test(
                    scenario_config['scenario'], 
                    f"complete_test_{scenario_config['name']}"
                )
            
            duration_min = (time.time() - start_time) / 60
            
            # Extrai métricas do resultado
            final_accuracy = result.get('summary', {}).get('final_accuracy', 0)
            resilience_score = result.get('summary', {}).get('resilience_score', 0)
            
            results.append({
                'name': scenario_config['name'],
                'description': scenario_config['description'],
                'duration_min': duration_min,
                'status': 'SUCCESS',
                'final_accuracy': final_accuracy,
                'resilience_score': resilience_score,
                'expected_resilience': scenario_config['expected_resilience'],
                'expected_accuracy': scenario_config['expected_accuracy']
            })
            
            print(f"    ✅ SUCESSO! Cenário {scenario_config['name']} concluído em {duration_min:.1f} minutos")
            print(f"    📊 Acurácia final: {final_accuracy:.3f} ({final_accuracy*100:.1f}%)")
            print(f"    🛡️  Score resiliência: {resilience_score:.3f}")
            
        except Exception as e:
            duration_min = (time.time() - start_time) / 60
            results.append({
                'name': scenario_config['name'],
                'description': scenario_config['description'],
                'duration_min': duration_min,
                'status': f'ERROR: {str(e)}',
                'final_accuracy': 0,
                'resilience_score': 0,
                'expected_resilience': scenario_config['expected_resilience'],
                'expected_accuracy': scenario_config['expected_accuracy']
            })
            print(f"    ❌ ERRO no cenário {scenario_config['name']}: {str(e)}")
        
        print("    " + "=" * 76)
        
        # Pausa entre cenários (exceto no último)
        if i < len(scenarios):
            print("    ⏳ Aguardando 5 segundos antes do próximo cenário...")
            time.sleep(5)
        
        print()
    
    # Resumo final
    total_time = (time.time() - start_time_total) / 60
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    
    print()
    print("🎉 TESTE COMPLETO FINALIZADO!")
    print("=" * 80)
    print("📊 RESUMO EXECUTIVO DETALHADO:")
    print()
    
    # Resultados por cenário
    for result in results:
        if result['status'] == 'SUCCESS':
            grade = get_resilience_grade(result['resilience_score'])
            print(f"    ✅ {result['name'].upper()}: {result['description']}")
            print(f"       ⏱️  Duração: {result['duration_min']:.1f} min")
            print(f"       🛡️  Resiliência: {result['resilience_score']:.3f} ({grade})")
            print(f"       📊 Acurácia: {result['final_accuracy']:.3f} ({result['final_accuracy']*100:.1f}%)")
            print()
        else:
            print(f"    ❌ {result['name'].upper()}: {result['status']}")
            print()
    
    # Estatísticas gerais
    successful_results = [r for r in results if r['status'] == 'SUCCESS']
    if successful_results:
        avg_resilience = sum(r['resilience_score'] for r in successful_results) / len(successful_results)
        avg_accuracy = sum(r['final_accuracy'] for r in successful_results) / len(successful_results)
        
        print("📈 ESTATÍSTICAS GERAIS:")
        print(f"    📈 Taxa de Sucesso: {success_count}/{len(scenarios)} ({(success_count/len(scenarios)*100):.1f}%)")
        print(f"    ⏱️  Tempo Total: {total_time:.1f} minutos")
        print(f"    🛡️  Resiliência Média: {avg_resilience:.3f} ({get_resilience_grade(avg_resilience)})")
        print(f"    📊 Acurácia Média: {avg_accuracy:.3f} ({avg_accuracy*100:.1f}%)")
        print(f"    📁 Arquivos Gerados: {success_count * 2} (Excel + JSON)")
    
    print()
    print("📈 PRÓXIMOS PASSOS:")
    print("    1. 📂 Abra os arquivos Excel em node_failure_tests/results/")
    print("    2. 📊 Compare os scores de resiliência entre cenários")
    print("    3. 📈 Analise gráficos e métricas detalhadas")
    print("    4. 🔍 Execute: python analyze_results.py para análise avançada")
    print()
    
    # Classificação final do sistema
    if successful_results:
        if avg_resilience >= 0.8:
            classification = "🟢 SISTEMA ALTAMENTE RESILIENTE"
            recommendation = "Excelente tolerância a falhas. Sistema pronto para produção."
        elif avg_resilience >= 0.6:
            classification = "🟡 SISTEMA MODERADAMENTE RESILIENTE"
            recommendation = "Boa tolerância com algumas melhorias recomendadas."
        elif avg_resilience >= 0.4:
            classification = "🟠 SISTEMA COM VULNERABILIDADES"
            recommendation = "Requer melhorias antes de ambientes críticos."
        else:
            classification = "🔴 SISTEMA CRÍTICO"
            recommendation = "Necessita revisão arquitetural urgente."
        
        print(f"🏷️  CLASSIFICAÇÃO FINAL: {classification}")
        print(f"💡 RECOMENDAÇÃO: {recommendation}")
    
    print()
    print("🏆 PARABÉNS! Análise completa de resiliência do sistema finalizada!")
    print("=" * 80)

def get_resilience_grade(score):
    """Converte score de resiliência em nota"""
    if score >= 0.9:
        return "A+ (Excelente)"
    elif score >= 0.8:
        return "A (Muito Bom)"
    elif score >= 0.7:
        return "B+ (Bom)"
    elif score >= 0.6:
        return "B (Satisfatório)"
    elif score >= 0.5:
        return "C+ (Regular)"
    elif score >= 0.4:
        return "C (Fraco)"
    elif score >= 0.3:
        return "D (Ruim)"
    else:
        return "F (Crítico)"

if __name__ == "__main__":
    main()
