# GUIA DE USO - Testes de Falha de Nós

## 🚀 Como executar os testes

### No Windows (PowerShell):
```powershell
cd node_failure_tests
.\run_tests.ps1
```

### No Linux/Mac (Bash):
```bash
cd node_failure_tests
chmod +x run_tests.sh
./run_tests.sh
```

### Manualmente com Docker:
```powershell
# TESTE COMPLETO - Todos os 7 cenários (30-45 min)
docker-compose -f docker-compose-test.yml up --build

# TESTE RÁPIDO - Apenas um cenário (2-5 min)
docker-compose -f docker-compose-test.yml run test-orchestrator python node_failure_tests/run_single_scenario.py

# TESTE AVANÇADO - Todos os 7 cenários + análise comparativa (45-60 min)
docker-compose -f docker-compose-test.yml run test-orchestrator python -c "
import sys
sys.path.append('/app/node_failure_tests')
from test_orchestrator import TestOrchestrator
from failure_simulator import FailureScenario, FailureType
import time

CLIENT_ENDPOINTS = ['http://client-1:5000/fit', 'http://client-2:5000/fit', 'http://client-3:5000/fit']
orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=10)

print('🚀 TESTE AVANÇADO - Análise Completa de Resiliência')
print('⏱️  Duração estimada: 45-60 minutos')
print('📊 Executa todos os 7 cenários + análise comparativa')
print('=' * 80)
print()

# Todos os cenários de teste
scenarios = [
    ('baseline', 'Baseline sem falhas', None, [], 0.0, 10, 0.0),
    ('single_failure', 'Falha de um nó por 3 rodadas', FailureType.TOTAL_FAILURE, [0], 1.0, 3, 0.0),
    ('multiple_failure', 'Falha de múltiplos nós por 2 rodadas', FailureType.TOTAL_FAILURE, [0,1], 1.0, 2, 0.0),
    ('network_instability', 'Instabilidade de rede (30%)', FailureType.NETWORK_TIMEOUT, [0,1,2], 0.3, 5, 0.1),
    ('slow_clients', 'Clientes lentos (80%)', FailureType.SLOW_RESPONSE, [1,2], 0.8, 6, 0.0),
    ('cascading_failure', 'Falha em cascata (20% -> 5%)', FailureType.TOTAL_FAILURE, [0,1,2], 0.2, 8, 0.05),
    ('intermittent_failure', 'Falhas intermitentes (40% -> 30%)', FailureType.NETWORK_TIMEOUT, [0,1,2], 0.4, 7, 0.3)
]

results = []
start_time_total = time.time()

for i, (name, desc, ftype, clients, prob, duration, recovery) in enumerate(scenarios, 1):
    print(f'🧪 [{i}/7] Executando cenário: {name.upper()}')
    print(f'    📋 Descrição: {desc}')
    print(f'    ⏱️  Tempo estimado: ~6-9 minutos')
    print()
    
    start_time = time.time()
    
    try:
        if ftype is None:
            print('    🎯 Executando baseline (sem falhas)...')
            result = orchestrator.run_scenario_test(None, f'advanced_test_{name}')
        else:
            print(f'    💥 Executando cenário: {ftype.name}')
            scenario = FailureScenario(name, desc, ftype, clients, prob, duration, recovery)
            result = orchestrator.run_scenario_test(scenario, f'advanced_test_{name}')
        
        duration_min = (time.time() - start_time) / 60
        results.append((name, desc, duration_min, 'SUCCESS'))
        print(f'    ✅ Cenário {name} concluído em {duration_min:.1f} minutos')
    except Exception as e:
        duration_min = (time.time() - start_time) / 60
        results.append((name, desc, duration_min, f'ERROR: {str(e)}'))
        print(f'    ❌ Erro no cenário {name}: {str(e)}')
    
    print('=' * 80)
    if i < len(scenarios):
        print('⏳ Aguardando 5 segundos antes do próximo cenário...')
        time.sleep(5)
    print()

# Executa análise comparativa automática
print('📊 EXECUTANDO ANÁLISE COMPARATIVA AUTOMÁTICA...')
try:
    import subprocess
    subprocess.run(['python', '/app/node_failure_tests/analyze_results.py'], check=True)
    print('✅ Análise automática concluída!')
except Exception as e:
    print(f'⚠️  Análise automática falhou: {e}')

total_time = (time.time() - start_time_total) / 60
success_count = sum(1 for _, _, _, status in results if status == 'SUCCESS')

print()
print('🎉 TESTE AVANÇADO FINALIZADO!')
print('=' * 80)
print('📊 RESUMO EXECUTIVO:')

for name, desc, duration, status in results:
    if status == 'SUCCESS':
        print(f'    ✅ {name}: {desc} ({duration:.1f} min)')
    else:
        print(f'    ❌ {name}: {status}')

print()
print(f'    📈 Taxa de Sucesso: {success_count}/{len(scenarios)} ({(success_count/len(scenarios)*100):.1f}%)')
print(f'    ⏱️  Tempo Total: {total_time:.1f} minutos')
print(f'    📁 Arquivos gerados: {success_count * 2} (Excel + JSON)')
print()
print('📈 PRÓXIMOS PASSOS:')
print('    1. Abra os arquivos Excel em node_failure_tests/results/')
print('    2. Compare os scores de resiliência entre cenários')
print('    3. Analise gráficos gerados automaticamente')
print('    4. Execute: python analyze_results.py para nova análise')
print()
print('🏆 PARABÉNS! Análise completa de resiliência finalizada!')
"

# TESTE MÉDIO - 3 cenários principais (15-20 min)
docker-compose -f docker-compose-test.yml run test-orchestrator python -c "
import sys
sys.path.append('/app/node_failure_tests')
from test_orchestrator import TestOrchestrator
from failure_simulator import FailureScenario, FailureType
import time

CLIENT_ENDPOINTS = ['http://client-1:5000/fit', 'http://client-2:5000/fit', 'http://client-3:5000/fit']
orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=8)

print('🚀 TESTE MÉDIO - 3 Cenários Principais')
print('⏱️  Duração estimada: 15-20 minutos')
print()

# Executa 3 cenários principais - CORRIGIDO
scenarios = [
    ('baseline', 'Baseline sem falhas', None, [], 0.0, 8, 0.0),
    ('single_failure', 'Falha de um nó', FailureType.TOTAL_FAILURE, [0], 1.0, 3, 0.0),
    ('network_issues', 'Instabilidade de rede', FailureType.NETWORK_TIMEOUT, [0,1,2], 0.3, 5, 0.1)
]

for i, (name, desc, ftype, clients, prob, duration, recovery) in enumerate(scenarios, 1):
    print(f'🧪 [{i}/3] Executando: {name.upper()}')
    start_time = time.time()
    
    if ftype is None:
        # Executa baseline sem cenário de falha
        orchestrator.run_scenario_test(None, f'medium_test_{name}')
    else:
        # Executa cenário com falhas
        scenario = FailureScenario(name, desc, ftype, clients, prob, duration, recovery)
        orchestrator.run_scenario_test(scenario, f'medium_test_{name}')
    
    print(f'✅ Concluído em {(time.time()-start_time)/60:.1f} min')
    if i < len(scenarios): time.sleep(2)
"

# Teste personalizado específico
docker-compose -f docker-compose-test.yml run test-orchestrator python -c "
from node_failure_tests.test_orchestrator import TestOrchestrator
from node_failure_tests.failure_simulator import FailureScenario, FailureType

CLIENT_ENDPOINTS = ['http://client-1:5000/fit', 'http://client-2:5000/fit', 'http://client-3:5000/fit']
orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=8)

# Exemplo: Cenário de rede instável
cenario = FailureScenario(
    name='rede_instavel',
    description='Rede instável com timeouts frequentes',
    failure_type=FailureType.NETWORK_TIMEOUT,
    affected_clients=[0, 1, 2],
    failure_probability=0.4,
    duration_rounds=6
)

orchestrator.run_scenario_test(cenario, 'teste_rede_instavel')
"
```

### Localmente (após instalar dependências):
```bash
cd node_failure_tests
pip install -r requirements.txt

# Certifique-se que os clientes estão rodando primeiro
python test_orchestrator.py
```

## 📊 Resultados gerados

Todos os resultados são salvos em `node_failure_tests/results/`:

### Arquivos Excel (.xlsx):
- **baseline_no_failures_YYYYMMDD_HHMMSS.xlsx** - Execução sem falhas
- **test_single_node_failure_YYYYMMDD_HHMMSS.xlsx** - Teste com falha de 1 nó
- **test_multiple_node_failure_YYYYMMDD_HHMMSS.xlsx** - Teste com falha de múltiplos nós
- **test_network_instability_YYYYMMDD_HHMMSS.xlsx** - Teste de instabilidade de rede
- **test_slow_clients_YYYYMMDD_HHMMSS.xlsx** - Teste com clientes lentos
- **test_cascading_failure_YYYYMMDD_HHMMSS.xlsx** - Teste de falha em cascata
- **test_intermittent_failure_YYYYMMDD_HHMMSS.xlsx** - Teste de falhas intermitentes

Cada arquivo Excel contém 4 abas:
1. **Resumo** - Métricas gerais do experimento
2. **Métricas por Rodada** - Dados detalhados de cada rodada
3. **Análise de Falhas** - Foco nas rodadas com problemas
4. **Estatísticas por Cenário** - Comparação entre diferentes cenários

### Arquivos JSON (.json):
- Mesmos dados em formato estruturado para análises programáticas

## 📈 Como analisar os resultados

### 1. Análise Visual Automática:
```bash
python analyze_results.py
```
Gera gráficos e relatórios automáticos.

### 2. Análise Manual dos Excel:
- Abra os arquivos Excel gerados
- Compare a aba "Resumo" entre diferentes cenários
- Observe a coluna "Score de Resiliência" (0.0 = ruim, 1.0 = excelente)
- Analise "Acurácia Final" para ver impacto nas performance

### 3. Métricas importantes:

**Score de Resiliência:**
- 0.8-1.0: 🟢 Excelente tolerância a falhas
- 0.6-0.8: 🟡 Boa tolerância a falhas
- 0.4-0.6: 🟠 Tolerância moderada
- 0.0-0.4: 🔴 Baixa tolerância a falhas

**Rodada de Convergência:**
- Indica quando o modelo estabilizou
- Valores menores = convergência mais rápida

**Acurácia Final:**
- Compare entre cenários
- Queda significativa indica problemas com falhas

## 🎯 Cenários testados

### **Teste Completo (Todos os Cenários)**
Quando você executa `docker-compose -f docker-compose-test.yml up --build`, os seguintes cenários são testados automaticamente:

1. **Baseline** - Sem falhas (referência)
   - 10 rodadas normais para estabelecer performance base
   - Score de resiliência = 1.0 (perfeito)

2. **Single Node Failure** - 1 cliente falha por 3 rodadas
   - Cliente 1 fica totalmente indisponível
   - Testa capacidade de continuar com 2/3 clientes
   - Recuperação automática após 3 rodadas

3. **Multiple Node Failure** - 2 clientes falham por 2 rodadas
   - Clientes 1 e 2 falham simultaneamente
   - Sistema opera apenas com 1/3 clientes
   - Cenário extremo de resiliência

4. **Network Instability** - Timeouts aleatórios (30% chance/rodada)
   - Simula problemas de conectividade
   - Todos os clientes podem ser afetados
   - Falhas intermitentes por 5 rodadas

5. **Slow Clients** - 2 clientes lentos (80% chance/rodada)
   - Clientes 2 e 3 respondem lentamente
   - Adiciona 10-30 segundos de delay
   - Testa tolerância a latência alta

6. **Cascading Failure** - Falhas progressivas (20% chance, recuperação 5%)
   - Falhas se espalham gradualmente
   - Baixa probabilidade de recuperação
   - Simula cenários de falha em cascata

7. **Intermittent Failure** - Falhas intermitentes (40% chance, recuperação 30%)
   - Clientes entram e saem de falha
   - Alta probabilidade de recuperação
   - Ambiente instável mas recuperável

### **Duração Estimada por Cenário:**
- Baseline: ~3-5 minutos
- Single/Multiple failure: ~4-6 minutos cada
- Network/Slow/Cascading/Intermittent: ~5-8 minutos cada
- **Total**: 30-45 minutos

### **Cenários Personalizados Rápidos:**
Para testes mais rápidos, use cenários personalizados com menos rodadas:

## 🔧 Personalizando testes

### Criar cenário customizado:
```python
from failure_simulator import FailureScenario, FailureType
from test_orchestrator import TestOrchestrator

# Define cenário customizado
meu_cenario = FailureScenario(
    name="meu_teste",
    description="Meu teste personalizado",
    failure_type=FailureType.SLOW_RESPONSE,
    affected_clients=[0, 2],  # Clientes 1 e 3
    failure_probability=0.6,  # 60% chance por rodada
    duration_rounds=5,        # Dura 5 rodadas
    recovery_probability=0.1  # 10% chance de recuperação por rodada
)

# Executa teste
CLIENT_ENDPOINTS = ["http://client-1:5000/fit", "http://client-2:5000/fit", "http://client-3:5000/fit"]
orchestrator = TestOrchestrator(CLIENT_ENDPOINTS)
orchestrator.run_scenario_test(meu_cenario, "meu_experimento")
```

### Modificar parâmetros:
```python
# Mais rodadas
orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=20)

# Timeouts diferentes
orchestrator.MIN_TIMEOUT = 5   # Mínimo 5 segundos
orchestrator.MAX_TIMEOUT = 120 # Máximo 2 minutos
```

## 📋 Interpretação dos resultados

### O que procurar:

**✅ Sistema resiliente:**
- Score de resiliência > 0.7
- Acurácia final próxima ao baseline
- Convergência em número similar de rodadas
- Recuperação rápida após falhas

**⚠️ Sistema com problemas:**
- Score de resiliência < 0.5
- Queda significativa na acurácia final
- Não converge ou demora muito
- Performance degrada muito com falhas

### Recomendações baseadas nos resultados:

**Se resilience score < 0.6:**
- Implementar timeouts adaptativos mais inteligentes
- Adicionar cache de modelos anteriores
- Melhorar algoritmo de agregação para lidar com menos clientes
- Considerar técnicas como dropout de clientes planejado

**Se acurácia final cai > 10% com falhas:**
- Implementar pesos adaptativos baseados na confiabilidade histórica
- Adicionar validação cruzada entre clientes
- Considerar técnicas de ensemble models

**Se não converge com falhas:**
- Ajustar taxa de aprendizado dinamicamente
- Implementar early stopping inteligente
- Adicionar checkpoints e rollback automático

## 🆘 Solução de problemas

### "Cliente não respondeu":
1. Verifique se containers estão rodando: `docker ps`
2. Verifique logs: `docker logs client-1`
3. Teste conectividade: `docker exec test-orchestrator ping client-1`

### "Arquivos Excel não gerados":
1. Instale openpyxl: `pip install openpyxl`
2. Verifique permissões da pasta results
3. Verifique espaço em disco

### "Falhas não sendo simuladas":
1. Verifique logs do simulador
2. Confirme que cenário foi iniciado
3. Ajuste probabilidades se necessário

### "Erro de importação":
1. Instale dependências: `pip install -r requirements.txt`
2. Verifique versões do Python (requer 3.8+)
3. Configure PYTHONPATH se necessário
