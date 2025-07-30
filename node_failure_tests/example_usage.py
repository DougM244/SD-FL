# node_failure_tests/example_usage.py

"""
Exemplo de como usar o sistema de testes de falha de nós programaticamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_orchestrator import TestOrchestrator
from failure_simulator import FailureScenario, FailureType
from metrics_collector import MetricsCollector
from analyze_results import ResultsAnalyzer
import config

def exemplo_teste_customizado():
    """Exemplo de como criar e executar um teste customizado"""
    
    print("🧪 Exemplo: Teste Customizado")
    print("=" * 50)
    
    # Cria orquestrador com configurações personalizadas
    orchestrator = TestOrchestrator(
        client_endpoints=config.CLIENT_ENDPOINTS,
        num_rounds=8  # Teste mais curto
    )
    
    # Define um cenário específico para nosso caso de uso
    cenario_personalizado = FailureScenario(
        name="teste_personalizado",
        description="Teste específico para nossa aplicação",
        failure_type=FailureType.NETWORK_TIMEOUT,
        affected_clients=[0, 2],  # Apenas clientes 1 e 3
        failure_probability=0.5,   # 50% de chance por rodada
        duration_rounds=5,         # Dura 5 rodadas
        recovery_probability=0.2   # 20% de chance de recuperação
    )
    
    # Executa o teste
    print(f"Executando cenário: {cenario_personalizado.name}")
    orchestrator.run_scenario_test(cenario_personalizado, "meu_experimento_customizado")
    
    print("✅ Teste customizado concluído!")

def exemplo_comparacao_multiplos_cenarios():
    """Exemplo de como comparar múltiplos cenários"""
    
    print("\n🔬 Exemplo: Comparação de Múltiplos Cenários")
    print("=" * 50)
    
    orchestrator = TestOrchestrator(config.CLIENT_ENDPOINTS, num_rounds=6)
    
    # Lista de cenários para comparar
    cenarios_teste = [
        FailureScenario(
            name="cenario_A",
            description="Cenário A: Falha rápida e recuperação",
            failure_type=FailureType.TOTAL_FAILURE,
            affected_clients=[0],
            failure_probability=1.0,
            duration_rounds=2,
            recovery_probability=0.8
        ),
        FailureScenario(
            name="cenario_B", 
            description="Cenário B: Falha prolongada",
            failure_type=FailureType.TOTAL_FAILURE,
            affected_clients=[0],
            failure_probability=1.0,
            duration_rounds=4,
            recovery_probability=0.1
        ),
        FailureScenario(
            name="cenario_C",
            description="Cenário C: Múltiplas falhas intermitentes",
            failure_type=FailureType.SERVICE_UNAVAILABLE,
            affected_clients=[0, 1, 2],
            failure_probability=0.4,
            duration_rounds=6,
            recovery_probability=0.3
        )
    ]
    
    resultados = []
    
    # Executa baseline primeiro
    print("Executando baseline...")
    orchestrator.run_baseline_training("baseline_comparacao")
    baseline_path = orchestrator.metrics_collector.export_to_excel()
    
    # Executa cada cenário
    for i, cenario in enumerate(cenarios_teste, 1):
        print(f"\nExecutando cenário {i}/{len(cenarios_teste)}: {cenario.name}")
        orchestrator.run_scenario_test(cenario, f"comparacao_{cenario.name}")
        resultado_path = orchestrator.metrics_collector.export_to_excel()
        resultados.append(resultado_path)
    
    print(f"\n✅ Comparação concluída!")
    print(f"📁 Baseline: {baseline_path}")
    for i, path in enumerate(resultados):
        print(f"📁 Cenário {cenarios_teste[i].name}: {path}")

def exemplo_analise_automatica():
    """Exemplo de como fazer análise automática dos resultados"""
    
    print("\n📊 Exemplo: Análise Automática")
    print("=" * 50)
    
    # Cria analisador
    analyzer = ResultsAnalyzer("results")
    
    if not analyzer.experiments:
        print("❌ Nenhum resultado encontrado!")
        print("Execute primeiro alguns testes para gerar dados.")
        return
    
    # Análises automáticas
    print("Gerando comparação de acurácia...")
    accuracy_data = analyzer.compare_accuracy_across_scenarios()
    
    print("Gerando scores de resiliência...")
    resilience_data = analyzer.plot_resilience_scores()
    
    print("Analisando convergência...")
    analyzer.plot_convergence_analysis()
    
    print("Analisando impacto de falhas...")
    failure_impact_df = analyzer.analyze_failure_impact()
    
    # Relatório resumido
    analyzer.generate_summary_report()
    
    # Exporta relatório consolidado
    consolidated_path = analyzer.export_consolidated_report()
    print(f"📊 Relatório consolidado: {consolidated_path}")

def exemplo_teste_especifico_para_producao():
    """Exemplo de teste específico para validar sistema em produção"""
    
    print("\n🏭 Exemplo: Teste para Produção")
    print("=" * 50)
    
    orchestrator = TestOrchestrator(config.CLIENT_ENDPOINTS, num_rounds=12)
    
    # Cenário que simula condições reais de produção
    cenario_producao = FailureScenario(
        name="simulacao_producao",
        description="Simula condições reais: falhas ocasionais, rede instável",
        failure_type=FailureType.PARTIAL_FAILURE,
        affected_clients=list(range(len(config.CLIENT_ENDPOINTS))),
        failure_probability=0.15,  # 15% chance - mais realista
        duration_rounds=12,        # Todo o experimento
        recovery_probability=0.25  # 25% chance de recuperação
    )
    
    print("🎯 Executando simulação de produção...")
    print("   • Falhas ocasionais (15% chance por rodada)")
    print("   • Todos os clientes podem ser afetados")
    print("   • Recuperação automática (25% chance)")
    print("   • Duração: 12 rodadas")
    
    orchestrator.run_scenario_test(cenario_producao, "validacao_producao")
    
    # Análise específica para produção
    metrics = orchestrator.metrics_collector
    
    # Verifica se o sistema atende critérios mínimos
    if len(metrics.rounds_data) > 0:
        acuracia_final = metrics.rounds_data[-1].global_accuracy
        score_resiliencia = metrics.calculate_resilience_score()
        
        print(f"\n📋 Resultados da Validação:")
        print(f"   • Acurácia final: {acuracia_final:.4f}")
        print(f"   • Score de resiliência: {score_resiliencia:.4f}")
        
        # Critérios de aprovação
        aprovado = True
        
        if acuracia_final < 0.85:
            print("   ⚠️  Acurácia abaixo do esperado (< 85%)")
            aprovado = False
            
        if score_resiliencia < 0.7:
            print("   ⚠️  Resiliência abaixo do esperado (< 70%)")
            aprovado = False
        
        if aprovado:
            print("   ✅ Sistema APROVADO para produção!")
        else:
            print("   ❌ Sistema REPROVADO - necessita melhorias")
    
    # Exporta resultados
    result_path = metrics.export_to_excel()
    print(f"📁 Relatório detalhado: {result_path}")

def main():
    """Executa todos os exemplos"""
    
    print("🚀 Exemplos de Uso - Sistema de Testes de Falha de Nós")
    print("=" * 60)
    
    print("\nEscolha qual exemplo executar:")
    print("1) Teste customizado simples")
    print("2) Comparação de múltiplos cenários")
    print("3) Análise automática (requer resultados existentes)")
    print("4) Teste específico para produção")
    print("5) Executar todos os exemplos")
    
    try:
        escolha = input("\nDigite sua escolha (1-5): ").strip()
        
        if escolha == "1":
            exemplo_teste_customizado()
        elif escolha == "2":
            exemplo_comparacao_multiplos_cenarios()
        elif escolha == "3":
            exemplo_analise_automatica()
        elif escolha == "4":
            exemplo_teste_especifico_para_producao()
        elif escolha == "5":
            exemplo_teste_customizado()
            exemplo_comparacao_multiplos_cenarios()
            exemplo_analise_automatica()
            exemplo_teste_especifico_para_producao()
        else:
            print("❌ Escolha inválida!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Execução interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
    
    print("\n🎉 Exemplos concluídos!")
    print("📚 Consulte GUIA_DE_USO.md para mais informações.")

if __name__ == '__main__':
    main()
