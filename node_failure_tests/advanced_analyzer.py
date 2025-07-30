#!/usr/bin/env python3
# node_failure_tests/advanced_analyzer.py
"""
Script de análise avançada dos resultados de teste de resiliência
Gera relatórios comparativos detalhados, gráficos e recomendações
"""

import pandas as pd
import matplotlib.pyplot as plt
import json
import os
import glob
from datetime import datetime
import numpy as np

class AdvancedResultsAnalyzer:
    def __init__(self, results_dir="results"):
        self.results_dir = results_dir
        self.excel_files = glob.glob(os.path.join(results_dir, "*.xlsx"))
        self.json_files = glob.glob(os.path.join(results_dir, "*.json"))
        
    def load_all_results(self):
        """Carrega todos os arquivos de resultado"""
        all_data = []
        
        for json_file in self.json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    # Extrai informações do nome do arquivo
                    filename = os.path.basename(json_file)
                    
                    # Melhora a extração do nome do cenário
                    if 'advanced_test_' in filename:
                        scenario_name = filename.replace('advanced_test_', '').split('_')[0]
                    elif 'medium_test_' in filename:
                        scenario_name = filename.replace('medium_test_', '').split('_')[0]
                    else:
                        scenario_name = filename.split('_')[0]
                    
                    data['scenario_name'] = scenario_name
                    data['filename'] = filename
                    all_data.append(data)
            except Exception as e:
                print(f"Erro ao carregar {json_file}: {e}")
        
        return all_data
    
    def calculate_advanced_metrics(self, data):
        """Calcula métricas de resiliência avançadas"""
        metrics = data.get('summary', {})
        rounds_data = data.get('rounds', [])
        
        # Métricas básicas
        final_accuracy = metrics.get('final_accuracy', 0)
        avg_accuracy = metrics.get('average_accuracy', 0)
        resilience_score = metrics.get('resilience_score', 0)
        convergence_round = metrics.get('convergence_round', len(rounds_data))
        
        # Métricas avançadas
        accuracy_variance = np.var([r.get('accuracy', 0) for r in rounds_data]) if rounds_data else 0
        recovery_time = self._calculate_recovery_time(rounds_data)
        stability_index = self._calculate_stability_index(rounds_data)
        degradation_rate = self._calculate_degradation_rate(rounds_data)
        
        return {
            'scenario': data.get('scenario_name', 'unknown'),
            'final_accuracy': final_accuracy,
            'average_accuracy': avg_accuracy,
            'resilience_score': resilience_score,
            'convergence_round': convergence_round,
            'accuracy_variance': accuracy_variance,
            'recovery_time': recovery_time,
            'stability_index': stability_index,
            'degradation_rate': degradation_rate,
            'total_rounds': len(rounds_data),
            'failed_rounds': sum(1 for r in rounds_data if r.get('failures', 0) > 0),
            'avg_response_time': np.mean([r.get('avg_response_time', 0) for r in rounds_data]) if rounds_data else 0
        }
    
    def _calculate_recovery_time(self, rounds_data):
        """Calcula tempo médio de recuperação após falhas"""
        recovery_times = []
        in_failure = False
        failure_start = 0
        
        for i, round_data in enumerate(rounds_data):
            failures = round_data.get('failures', 0)
            
            if failures > 0 and not in_failure:
                in_failure = True
                failure_start = i
            elif failures == 0 and in_failure:
                in_failure = False
                recovery_times.append(i - failure_start)
        
        return np.mean(recovery_times) if recovery_times else 0
    
    def _calculate_stability_index(self, rounds_data):
        """Calcula índice de estabilidade (0-1)"""
        if len(rounds_data) < 2:
            return 1.0
            
        accuracies = [r.get('accuracy', 0) for r in rounds_data]
        
        # Calcula coeficiente de variação
        mean_acc = np.mean(accuracies)
        std_acc = np.std(accuracies)
        
        if mean_acc == 0:
            return 0.0
            
        cv = std_acc / mean_acc
        stability = max(0, 1 - cv)
        return min(1, stability)
    
    def _calculate_degradation_rate(self, rounds_data):
        """Calcula taxa de degradação durante falhas"""
        if len(rounds_data) < 2:
            return 0.0
            
        accuracies = [r.get('accuracy', 0) for r in rounds_data]
        failures = [r.get('failures', 0) for r in rounds_data]
        
        degradations = []
        for i in range(1, len(rounds_data)):
            if failures[i] > 0:
                degradation = max(0, accuracies[i-1] - accuracies[i])
                degradations.append(degradation)
        
        return np.mean(degradations) if degradations else 0.0
    
    def generate_comprehensive_report(self):
        """Gera relatório comparativo abrangente"""
        all_data = self.load_all_results()
        
        if not all_data:
            print("❌ Nenhum arquivo de resultado encontrado!")
            return
        
        # Calcula métricas para todos os cenários
        metrics_list = []
        for data in all_data:
            metrics = self.calculate_advanced_metrics(data)
            metrics_list.append(metrics)
        
        # Cria DataFrame para análise
        df = pd.DataFrame(metrics_list)
        
        # Remove duplicatas (mantém o mais recente)
        df = df.drop_duplicates(subset=['scenario'], keep='last')
        
        # Gera relatório
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"comprehensive_analysis_{timestamp}.txt"
        report_path = os.path.join(self.results_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            self._write_comprehensive_report(f, df)
        
        print(f"📄 Relatório abrangente salvo em: {report_path}")
        
        # Gera gráficos avançados
        self.generate_advanced_charts(df, timestamp)
        
        return df
    
    def _write_comprehensive_report(self, f, df):
        """Escreve o relatório abrangente"""
        f.write("🚀 ANÁLISE ABRANGENTE DE RESILIÊNCIA - FEDERATED LEARNING\n")
        f.write("=" * 80 + "\n")
        f.write(f"📅 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"📊 Cenários analisados: {len(df)}\n\n")
        
        # Executive Summary
        self._write_executive_summary(f, df)
        
        # Ranking detalhado
        self._write_detailed_ranking(f, df)
        
        # Análise por categoria
        self._write_category_analysis(f, df)
        
        # Recomendações estratégicas
        self._write_strategic_recommendations(f, df)
        
        # Análise estatística
        self._write_statistical_analysis(f, df)
    
    def _write_executive_summary(self, f, df):
        """Escreve sumário executivo"""
        f.write("📋 SUMÁRIO EXECUTIVO\n")
        f.write("-" * 40 + "\n")
        
        # Métricas gerais
        avg_resilience = df['resilience_score'].mean()
        avg_accuracy = df['final_accuracy'].mean()
        best_scenario = df.loc[df['resilience_score'].idxmax(), 'scenario']
        worst_scenario = df.loc[df['resilience_score'].idxmin(), 'scenario']
        
        f.write(f"🎯 Resiliência Média do Sistema: {avg_resilience:.3f} ({self._get_resilience_grade(avg_resilience)})\n")
        f.write(f"📊 Acurácia Média: {avg_accuracy:.3f} ({avg_accuracy*100:.1f}%)\n")
        f.write(f"🏆 Melhor Cenário: {best_scenario.upper()}\n")
        f.write(f"⚠️  Cenário Mais Desafiador: {worst_scenario.upper()}\n\n")
        
        # Classificação geral do sistema
        if avg_resilience >= 0.8:
            classification = "🟢 SISTEMA ALTAMENTE RESILIENTE"
            desc = "Excelente tolerância a falhas em todos os cenários"
        elif avg_resilience >= 0.6:
            classification = "🟡 SISTEMA MODERADAMENTE RESILIENTE"
            desc = "Boa tolerância com algumas vulnerabilidades"
        elif avg_resilience >= 0.4:
            classification = "🟠 SISTEMA COM VULNERABILIDADES"
            desc = "Requer melhorias para ambientes críticos"
        else:
            classification = "🔴 SISTEMA CRÍTICO"
            desc = "Necessita revisão arquitetural urgente"
        
        f.write(f"🏷️  CLASSIFICAÇÃO: {classification}\n")
        f.write(f"💭 {desc}\n\n")
    
    def _write_detailed_ranking(self, f, df):
        """Escreve ranking detalhado"""
        f.write("🏆 RANKING DETALHADO DE RESILIÊNCIA\n")
        f.write("-" * 40 + "\n")
        
        df_sorted = df.sort_values('resilience_score', ascending=False)
        
        for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            grade = self._get_resilience_grade(row['resilience_score'])
            
            f.write(f"{medal} {row['scenario'].upper()}\n")
            f.write(f"   🛡️  Resiliência: {row['resilience_score']:.3f} ({grade})\n")
            f.write(f"   🎯 Acurácia: {row['final_accuracy']:.3f} ({row['final_accuracy']*100:.1f}%)\n")
            f.write(f"   📏 Estabilidade: {row['stability_index']:.3f}\n")
            f.write(f"   ⏱️  Convergência: Rodada {row['convergence_round']}\n\n")
    
    def _write_category_analysis(self, f, df):
        """Escreve análise por categoria de falha"""
        f.write("📊 ANÁLISE POR CATEGORIA DE FALHA\n")
        f.write("-" * 40 + "\n")
        
        categories = {
            'baseline': '🎯 Referência (Sem Falhas)',
            'single': '💥 Falha Única',
            'multiple': '💥💥 Falhas Múltiplas', 
            'network': '🌐 Problemas de Rede',
            'slow': '🐌 Performance Degradada',
            'cascading': '📉 Falha em Cascata',
            'intermittent': '🔄 Falhas Intermitentes'
        }
        
        for category, desc in categories.items():
            category_data = df[df['scenario'].str.contains(category, case=False)]
            if not category_data.empty:
                row = category_data.iloc[0]
                f.write(f"{desc}\n")
                f.write(f"   📋 Cenário: {row['scenario']}\n")
                f.write(f"   🛡️  Resiliência: {row['resilience_score']:.3f}\n")
                f.write(f"   🎯 Acurácia: {row['final_accuracy']:.3f}\n")
                f.write(f"   ⏱️  Recuperação: {row['recovery_time']:.1f} rodadas\n")
                f.write(f"   📊 Taxa Degradação: {row['degradation_rate']:.3f}\n\n")
    
    def _write_strategic_recommendations(self, f, df):
        """Escreve recomendações estratégicas"""
        f.write("💡 RECOMENDAÇÕES ESTRATÉGICAS\n")
        f.write("-" * 40 + "\n")
        
        baseline_score = df[df['scenario'] == 'baseline']['resilience_score'].iloc[0] if 'baseline' in df['scenario'].values else 1.0
        
        f.write("🔧 PRIORIDADES DE MELHORIA:\n\n")
        
        # Analisa cada cenário
        for _, row in df.iterrows():
            if row['scenario'] == 'baseline':
                continue
                
            resilience_drop = baseline_score - row['resilience_score']
            
            f.write(f"📌 {row['scenario'].upper()}:\n")
            
            if resilience_drop > 0.4:
                f.write("   🚨 PRIORIDADE CRÍTICA\n")
                f.write("   💡 Implementar redundância e cache distribuído\n")
                f.write("   💡 Adicionar sistema de detecção prévia de falhas\n")
            elif resilience_drop > 0.3:
                f.write("   ⚠️  PRIORIDADE ALTA\n")
                f.write("   💡 Otimizar algoritmo de agregação adaptativa\n")
                f.write("   💡 Implementar timeouts dinâmicos\n")
            elif resilience_drop > 0.2:
                f.write("   🟡 PRIORIDADE MÉDIA\n")
                f.write("   💡 Melhorar monitoramento e alertas\n")
                f.write("   💡 Implementar retry inteligente\n")
            elif resilience_drop > 0.1:
                f.write("   ✅ PRIORIDADE BAIXA\n")
                f.write("   💡 Monitorar tendências e otimizar configurações\n")
            else:
                f.write("   🏆 EXCELENTE - Manter configuração atual\n")
            
            f.write(f"   📉 Impacto na resiliência: -{resilience_drop:.3f}\n\n")
    
    def _write_statistical_analysis(self, f, df):
        """Escreve análise estatística"""
        f.write("📈 ANÁLISE ESTATÍSTICA DETALHADA\n")
        f.write("-" * 40 + "\n")
        
        f.write("📊 DISTRIBUIÇÃO DE MÉTRICAS:\n")
        f.write(f"   🛡️  Resiliência: μ={df['resilience_score'].mean():.3f} σ={df['resilience_score'].std():.3f}\n")
        f.write(f"   🎯 Acurácia: μ={df['final_accuracy'].mean():.3f} σ={df['final_accuracy'].std():.3f}\n")
        f.write(f"   📏 Estabilidade: μ={df['stability_index'].mean():.3f} σ={df['stability_index'].std():.3f}\n")
        f.write(f"   ⏱️  Recuperação: μ={df['recovery_time'].mean():.1f} σ={df['recovery_time'].std():.1f}\n\n")
        
        # Correlações
        f.write("🔗 CORRELAÇÕES ENTRE MÉTRICAS:\n")
        corr_res_acc = df['resilience_score'].corr(df['final_accuracy'])
        corr_res_stab = df['resilience_score'].corr(df['stability_index'])
        f.write(f"   Resiliência ↔ Acurácia: {corr_res_acc:.3f}\n")
        f.write(f"   Resiliência ↔ Estabilidade: {corr_res_stab:.3f}\n")
    
    def _get_resilience_grade(self, score):
        """Converte score em nota"""
        if score >= 0.9: return "A+"
        elif score >= 0.8: return "A"
        elif score >= 0.7: return "B+"
        elif score >= 0.6: return "B"
        elif score >= 0.5: return "C+"
        elif score >= 0.4: return "C"
        elif score >= 0.3: return "D"
        else: return "F"
    
    def generate_advanced_charts(self, df, timestamp):
        """Gera gráficos avançados"""
        try:
            plt.style.use('seaborn-v0_8')
        except:
            plt.style.use('default')
            
        fig = plt.figure(figsize=(20, 15))
        fig.suptitle('🚀 ANÁLISE ABRANGENTE DE RESILIÊNCIA - FEDERATED LEARNING', 
                    fontsize=20, fontweight='bold', y=0.98)
        
        # Gráfico 1: Radar Chart de Métricas
        ax1 = plt.subplot(3, 3, 1, projection='polar')
        self._create_radar_chart(ax1, df)
        
        # Gráfico 2: Heatmap de Correlações
        ax2 = plt.subplot(3, 3, 2)
        self._create_correlation_heatmap(ax2, df)
        
        # Gráfico 3: Scores de Resiliência
        ax3 = plt.subplot(3, 3, 3)
        self._create_resilience_bars(ax3, df)
        
        # Gráfico 4: Acurácia vs Estabilidade
        ax4 = plt.subplot(3, 3, 4)
        self._create_accuracy_stability_scatter(ax4, df)
        
        # Gráfico 5: Tempo de Recuperação
        ax5 = plt.subplot(3, 3, 5)
        self._create_recovery_time_chart(ax5, df)
        
        # Gráfico 6: Distribuição de Métricas
        ax6 = plt.subplot(3, 3, 6)
        self._create_metrics_distribution(ax6, df)
        
        # Gráfico 7: Performance Overview
        ax7 = plt.subplot(3, 3, (7, 9))
        self._create_performance_overview(ax7, df)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        chart_filename = f"comprehensive_analysis_{timestamp}.png"
        chart_path = os.path.join(self.results_dir, chart_filename)
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"📊 Gráficos abrangentes salvos em: {chart_path}")
        
        plt.close()
    
    def _create_radar_chart(self, ax, df):
        """Cria gráfico radar das métricas principais"""
        # Seleciona apenas alguns cenários representativos
        scenarios_to_plot = ['baseline', 'single', 'network', 'cascading']
        
        angles = np.linspace(0, 2 * np.pi, 4, endpoint=False).tolist()
        angles += angles[:1]  # Fecha o círculo
        
        ax.set_title('📊 Perfil de Métricas', y=1.08)
        
        for scenario in scenarios_to_plot:
            scenario_data = df[df['scenario'].str.contains(scenario, case=False)]
            if not scenario_data.empty:
                row = scenario_data.iloc[0]
                values = [
                    row['resilience_score'],
                    row['final_accuracy'], 
                    row['stability_index'],
                    1 - row['degradation_rate']  # Inverte para que maior seja melhor
                ]
                values += values[:1]  # Fecha o círculo
                
                ax.plot(angles, values, 'o-', linewidth=2, label=scenario.title())
                ax.fill(angles, values, alpha=0.25)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(['Resiliência', 'Acurácia', 'Estabilidade', 'Robustez'])
        ax.set_ylim(0, 1)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    
    def _create_correlation_heatmap(self, ax, df):
        """Cria heatmap de correlações"""
        metrics = ['resilience_score', 'final_accuracy', 'stability_index', 'recovery_time']
        corr_matrix = df[metrics].corr()
        
        im = ax.imshow(corr_matrix, cmap='RdBu', vmin=-1, vmax=1)
        ax.set_xticks(range(len(metrics)))
        ax.set_yticks(range(len(metrics)))
        ax.set_xticklabels(['Resiliência', 'Acurácia', 'Estabilidade', 'Recuperação'])
        ax.set_yticklabels(['Resiliência', 'Acurácia', 'Estabilidade', 'Recuperação'])
        ax.set_title('🔗 Correlações entre Métricas')
        
        # Adiciona valores na matriz
        for i in range(len(metrics)):
            for j in range(len(metrics)):
                text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black", fontweight='bold')
    
    def _create_resilience_bars(self, ax, df):
        """Cria gráfico de barras dos scores de resiliência"""
        df_sorted = df.sort_values('resilience_score', ascending=True)
        scenarios = df_sorted['scenario'].str.replace('_', ' ').str.title()
        colors = plt.cm.RdYlGn(df_sorted['resilience_score'])
        
        bars = ax.barh(scenarios, df_sorted['resilience_score'], color=colors)
        ax.set_xlabel('Score de Resiliência')
        ax.set_title('🛡️ Ranking de Resiliência')
        ax.set_xlim(0, 1)
        
        # Adiciona valores nas barras
        for bar, value in zip(bars, df_sorted['resilience_score']):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                   f'{value:.3f}', va='center', fontweight='bold')
    
    def _create_accuracy_stability_scatter(self, ax, df):
        """Cria scatter plot acurácia vs estabilidade"""
        scatter = ax.scatter(df['final_accuracy'], df['stability_index'], 
                           s=df['resilience_score']*300, alpha=0.7, 
                           c=df['resilience_score'], cmap='RdYlGn')
        
        ax.set_xlabel('Acurácia Final')
        ax.set_ylabel('Índice de Estabilidade')
        ax.set_title('🎯 Acurácia vs Estabilidade\n(Tamanho = Resiliência)')
        
        # Adiciona rótulos
        for _, row in df.iterrows():
            ax.annotate(row['scenario'][:4], 
                       (row['final_accuracy'], row['stability_index']),
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    def _create_recovery_time_chart(self, ax, df):
        """Cria gráfico de tempo de recuperação"""
        recovery_data = df[df['recovery_time'] > 0]
        
        if not recovery_data.empty:
            scenarios = recovery_data['scenario'].str.replace('_', ' ').str.title()
            bars = ax.bar(scenarios, recovery_data['recovery_time'], 
                         color='orange', alpha=0.7)
            ax.set_ylabel('Rodadas para Recuperação')
            ax.set_title('⏱️ Tempo de Recuperação')
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            for bar, value in zip(bars, recovery_data['recovery_time']):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                       f'{value:.1f}', ha='center', va='bottom')
        else:
            ax.text(0.5, 0.5, 'Nenhuma recuperação\nnecessária', 
                   transform=ax.transAxes, ha='center', va='center', fontsize=12)
            ax.set_title('⏱️ Tempo de Recuperação')
    
    def _create_metrics_distribution(self, ax, df):
        """Cria gráfico de distribuição das métricas"""
        metrics = ['resilience_score', 'final_accuracy', 'stability_index']
        data_to_plot = [df[metric] for metric in metrics]
        
        bp = ax.boxplot(data_to_plot, patch_artist=True, 
                       labels=['Resiliência', 'Acurácia', 'Estabilidade'])
        
        colors = ['lightblue', 'lightgreen', 'lightcoral']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_title('📊 Distribuição das Métricas')
        ax.set_ylabel('Score')
        ax.set_ylim(0, 1)
    
    def _create_performance_overview(self, ax, df):
        """Cria overview geral de performance"""
        scenarios = df['scenario'].str.replace('_', ' ').str.title()
        x_pos = np.arange(len(scenarios))
        
        width = 0.25
        
        bars1 = ax.bar(x_pos - width, df['resilience_score'], width, 
                      label='Resiliência', alpha=0.8, color='skyblue')
        bars2 = ax.bar(x_pos, df['final_accuracy'], width, 
                      label='Acurácia', alpha=0.8, color='lightgreen')
        bars3 = ax.bar(x_pos + width, df['stability_index'], width, 
                      label='Estabilidade', alpha=0.8, color='lightcoral')
        
        ax.set_xlabel('Cenários')
        ax.set_ylabel('Score')
        ax.set_title('📈 Overview Geral de Performance')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(scenarios, rotation=45, ha='right')
        ax.legend()
        ax.set_ylim(0, 1.1)
        
        # Adiciona valores nas barras
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{height:.2f}', ha='center', va='bottom', fontsize=8)

def main():
    print("🚀 Iniciando análise abrangente dos resultados...")
    
    analyzer = AdvancedResultsAnalyzer()
    
    if not analyzer.json_files:
        print("❌ Nenhum arquivo de resultado encontrado!")
        print("💡 Execute primeiro um teste para gerar resultados.")
        return
    
    print(f"📁 Encontrados {len(analyzer.json_files)} arquivos de resultado")
    
    # Gera análise abrangente
    df = analyzer.generate_comprehensive_report()
    
    if df is not None and not df.empty:
        print("\n✅ Análise abrangente concluída com sucesso!")
        print("📊 Verifique os arquivos gerados na pasta results/")
        print("🎯 Relatório detalhado e gráficos avançados disponíveis")
    else:
        print("❌ Falha na geração da análise")

if __name__ == "__main__":
    main()
