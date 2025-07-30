# node_failure_tests/analyze_results.py

"""
Script para análise e visualização dos resultados dos testes de falha
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import glob
from typing import List, Dict
import numpy as np

class ResultsAnalyzer:
    """Analisador de resultados dos testes de falha de nós"""
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = results_dir
        self.experiments = []
        self.load_experiments()
    
    def load_experiments(self):
        """Carrega todos os experimentos JSON do diretório de resultados"""
        json_files = glob.glob(os.path.join(self.results_dir, "*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    experiment = json.load(f)
                    experiment['filename'] = os.path.basename(json_file)
                    self.experiments.append(experiment)
            except Exception as e:
                print(f"Erro ao carregar {json_file}: {e}")
        
        print(f"Carregados {len(self.experiments)} experimentos")
    
    def compare_accuracy_across_scenarios(self):
        """Compara a acurácia final entre diferentes cenários"""
        scenario_data = {}
        
        for exp in self.experiments:
            exp_name = exp['experiment_name']
            if exp['rounds']:
                final_accuracy = exp['rounds'][-1]['global_accuracy']
                scenario_data[exp_name] = final_accuracy
        
        # Cria gráfico
        plt.figure(figsize=(12, 6))
        scenarios = list(scenario_data.keys())
        accuracies = list(scenario_data.values())
        
        bars = plt.bar(scenarios, accuracies)
        plt.title('Acurácia Final por Cenário de Teste', fontsize=14)
        plt.xlabel('Cenário')
        plt.ylabel('Acurácia Final')
        plt.xticks(rotation=45, ha='right')
        
        # Adiciona valores nas barras
        for bar, acc in zip(bars, accuracies):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{acc:.3f}', ha='center', va='bottom')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'accuracy_comparison.png'), dpi=300)
        plt.show()
        
        return scenario_data
    
    def plot_resilience_scores(self):
        """Plota os scores de resiliência de cada experimento"""
        resilience_data = {}
        
        for exp in self.experiments:
            exp_name = exp['experiment_name']
            resilience_data[exp_name] = exp.get('resilience_score', 0.0)
        
        plt.figure(figsize=(12, 6))
        scenarios = list(resilience_data.keys())
        scores = list(resilience_data.values())
        
        # Cores baseadas no score (verde = melhor, vermelho = pior)
        colors = ['green' if s >= 0.8 else 'orange' if s >= 0.6 else 'red' for s in scores]
        
        bars = plt.bar(scenarios, scores, color=colors, alpha=0.7)
        plt.title('Score de Resiliência por Cenário', fontsize=14)
        plt.xlabel('Cenário')
        plt.ylabel('Score de Resiliência (0.0 - 1.0)')
        plt.xticks(rotation=45, ha='right')
        
        # Adiciona linha de referência
        plt.axhline(y=0.8, color='green', linestyle='--', alpha=0.5, label='Excelente (≥0.8)')
        plt.axhline(y=0.6, color='orange', linestyle='--', alpha=0.5, label='Bom (≥0.6)')
        plt.axhline(y=0.4, color='red', linestyle='--', alpha=0.5, label='Moderado (≥0.4)')
        
        # Adiciona valores nas barras
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'resilience_scores.png'), dpi=300)
        plt.show()
        
        return resilience_data
    
    def plot_convergence_analysis(self):
        """Analisa a convergência do modelo ao longo das rodadas"""
        plt.figure(figsize=(15, 10))
        
        # Plot para cada experimento
        for i, exp in enumerate(self.experiments):
            if not exp['rounds']:
                continue
                
            rounds = [r['round_number'] for r in exp['rounds']]
            accuracies = [r['global_accuracy'] for r in exp['rounds']]
            
            plt.subplot(2, 2, (i % 4) + 1)
            plt.plot(rounds, accuracies, marker='o', linewidth=2, markersize=4)
            plt.title(f"{exp['experiment_name']}", fontsize=12)
            plt.xlabel('Rodada')
            plt.ylabel('Acurácia')
            plt.grid(True, alpha=0.3)
            plt.ylim(0, 1)
        
        plt.suptitle('Convergência da Acurácia ao Longo das Rodadas', fontsize=16)
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'convergence_analysis.png'), dpi=300)
        plt.show()
    
    def analyze_failure_impact(self):
        """Analisa o impacto das falhas na performance"""
        impact_data = []
        
        for exp in self.experiments:
            if not exp['rounds']:
                continue
                
            exp_name = exp['experiment_name']
            
            for round_data in exp['rounds']:
                failed_count = len(round_data['failed_clients'])
                slow_count = len(round_data['slow_clients'])
                total_affected = failed_count + slow_count
                availability = round_data['responding_clients'] / round_data['total_clients']
                
                impact_data.append({
                    'experiment': exp_name,
                    'round': round_data['round_number'],
                    'failed_clients': failed_count,
                    'slow_clients': slow_count,
                    'total_affected': total_affected,
                    'availability': availability,
                    'accuracy': round_data['global_accuracy'],
                    'avg_response_time': round_data['avg_response_time']
                })
        
        df = pd.DataFrame(impact_data)
        
        # Gráfico de dispersão: Disponibilidade vs Acurácia
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        scatter = plt.scatter(df['availability'], df['accuracy'], 
                            c=df['total_affected'], cmap='Reds', alpha=0.6)
        plt.xlabel('Disponibilidade dos Clientes')
        plt.ylabel('Acurácia do Modelo')
        plt.title('Impacto da Disponibilidade na Acurácia')
        plt.colorbar(scatter, label='Clientes Afetados')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        # Boxplot da acurácia por número de clientes afetados
        df_grouped = df.groupby('total_affected')['accuracy'].apply(list).to_dict()
        box_data = [accuracies for affected, accuracies in df_grouped.items()]
        box_labels = list(df_grouped.keys())
        
        plt.boxplot(box_data, labels=box_labels)
        plt.xlabel('Número de Clientes Afetados')
        plt.ylabel('Acurácia')
        plt.title('Distribuição da Acurácia por Nível de Falha')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.results_dir, 'failure_impact.png'), dpi=300)
        plt.show()
        
        return df
    
    def generate_summary_report(self):
        """Gera um relatório resumido dos resultados"""
        print("\n" + "="*60)
        print("RELATÓRIO RESUMIDO DOS TESTES DE FALHA DE NÓS")
        print("="*60)
        
        if not self.experiments:
            print("❌ Nenhum experimento encontrado!")
            return
        
        # Estatísticas gerais
        total_rounds = sum(exp['total_rounds'] for exp in self.experiments)
        avg_resilience = np.mean([exp.get('resilience_score', 0) for exp in self.experiments])
        
        print(f"\n📊 ESTATÍSTICAS GERAIS:")
        print(f"   • Total de experimentos: {len(self.experiments)}")
        print(f"   • Total de rodadas: {total_rounds}")
        print(f"   • Score médio de resiliência: {avg_resilience:.3f}")
        
        # Ranking de cenários por resiliência
        scenario_scores = [(exp['experiment_name'], exp.get('resilience_score', 0)) 
                          for exp in self.experiments]
        scenario_scores.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n🏆 RANKING POR RESILIÊNCIA:")
        for i, (name, score) in enumerate(scenario_scores, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"   {emoji} {i}. {name}: {score:.3f}")
        
        # Análise de convergência
        converged_experiments = []
        for exp in self.experiments:
            if exp.get('convergence_round'):
                converged_experiments.append((exp['experiment_name'], exp['convergence_round']))
        
        if converged_experiments:
            print(f"\n📈 CONVERGÊNCIA:")
            for name, round_num in converged_experiments:
                print(f"   • {name}: Rodada {round_num}")
        else:
            print(f"\n📈 CONVERGÊNCIA: Nenhum experimento convergiu no tempo limite")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        
        best_scenario = scenario_scores[0] if scenario_scores else None
        worst_scenario = scenario_scores[-1] if scenario_scores else None
        
        if best_scenario and best_scenario[1] >= 0.8:
            print(f"   ✅ Sistema demonstra boa resiliência no cenário '{best_scenario[0]}'")
        
        if worst_scenario and worst_scenario[1] < 0.6:
            print(f"   ⚠️  Sistema apresenta baixa resiliência no cenário '{worst_scenario[0]}'")
            print(f"       Considere implementar mecanismos adicionais de tolerância a falhas")
        
        if avg_resilience >= 0.7:
            print(f"   ✅ Sistema geral tem boa tolerância a falhas")
        else:
            print(f"   ⚠️  Sistema precisa melhorar a tolerância a falhas")
        
        print("\n" + "="*60)
    
    def export_consolidated_report(self):
        """Exporta um relatório consolidado em Excel"""
        if not self.experiments:
            return
        
        filename = f"consolidated_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.results_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # Resumo dos experimentos
            summary_data = []
            for exp in self.experiments:
                summary_data.append({
                    'Experimento': exp['experiment_name'],
                    'Rodadas': exp['total_rounds'],
                    'Cenários Testados': ', '.join(exp.get('scenarios_tested', [])),
                    'Acurácia Final': exp['rounds'][-1]['global_accuracy'] if exp['rounds'] else 0,
                    'Score Resiliência': exp.get('resilience_score', 0),
                    'Rodada Convergência': exp.get('convergence_round', 'N/A'),
                    'Total Falhas': sum(len(r['failed_clients']) for r in exp['rounds'])
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Resumo Experimentos', index=False)
            
            # Dados consolidados de todas as rodadas
            all_rounds = []
            for exp in self.experiments:
                for round_data in exp['rounds']:
                    round_entry = round_data.copy()
                    round_entry['experiment'] = exp['experiment_name']
                    round_entry['failed_clients_count'] = len(round_data['failed_clients'])
                    round_entry['slow_clients_count'] = len(round_data['slow_clients'])
                    all_rounds.append(round_entry)
            
            rounds_df = pd.DataFrame(all_rounds)
            if not rounds_df.empty:
                # Remove colunas de lista para Excel
                cols_to_remove = ['failed_clients', 'slow_clients', 'response_times', 'client_contributions']
                rounds_df = rounds_df.drop(columns=[col for col in cols_to_remove if col in rounds_df.columns])
                rounds_df.to_excel(writer, sheet_name='Todas as Rodadas', index=False)
        
        print(f"📊 Relatório consolidado exportado: {filepath}")
        return filepath

def main():
    """Executa análise completa dos resultados"""
    analyzer = ResultsAnalyzer()
    
    if not analyzer.experiments:
        print("❌ Nenhum resultado encontrado para análise!")
        print("Execute primeiro os testes com test_orchestrator.py")
        return
    
    print("🔍 Iniciando análise dos resultados...")
    
    # Análises
    analyzer.compare_accuracy_across_scenarios()
    analyzer.plot_resilience_scores()
    analyzer.plot_convergence_analysis()
    analyzer.analyze_failure_impact()
    
    # Relatório
    analyzer.generate_summary_report()
    analyzer.export_consolidated_report()
    
    print("\n✅ Análise completa! Verifique os gráficos e relatórios gerados.")

if __name__ == '__main__':
    main()
