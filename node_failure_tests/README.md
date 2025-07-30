# node_failure_tests/README.md

# Testes de Falha de Nós - Federated Learning

Este módulo implementa testes abrangentes de falha de nós para o sistema de Federated Learning, com exportação automática de métricas para Excel.

## 📁 Estrutura dos Arquivos

```
node_failure_tests/
├── failure_simulator.py          # Simulador de falhas de nós
├── metrics_collector.py          # Coletor e exportador de métricas
├── test_orchestrator.py          # Orquestrador principal de testes
├── run_single_scenario.py        # Script para testes únicos
├── docker-compose-test.yml       # Docker Compose para testes
├── Dockerfile.test-orchestrator  # Dockerfile para orquestrador de testes
├── requirements.txt              # Dependências específicas
├── results/                      # Diretório para resultados (Excel/JSON)
└── README.md                     # Este arquivo
```

## 🎯 Tipos de Falhas Testadas

### 1. **Falha Total (TOTAL_FAILURE)**
- Nó completamente indisponível
- Simula falha de hardware/software
- Cliente não responde às requisições

### 2. **Timeout de Rede (NETWORK_TIMEOUT)**
- Simula problemas de conectividade
- Requisições excedem o tempo limite
- Instabilidade intermitente da rede

### 3. **Resposta Lenta (SLOW_RESPONSE)**
- Cliente responde, mas muito lentamente
- Simula sobrecarga ou recursos limitados
- Pode afetar a convergência do modelo

### 4. **Serviço Indisponível (SERVICE_UNAVAILABLE)**
- Erros temporários do serviço
- Falhas intermitentes com recuperação
- Simula restart de serviços

### 5. **Falha Parcial (PARTIAL_FAILURE)**
- Combinação de diferentes tipos de falha
- Simula cenários complexos do mundo real
- Falhas em cascata

## 📊 Cenários de Teste Predefinidos

### 1. **single_node_failure**
- **Descrição**: Falha de um único nó
- **Duração**: 3 rodadas
- **Clientes afetados**: 1
- **Tipo**: Falha total

### 2. **multiple_node_failure**
- **Descrição**: Falha de múltiplos nós simultaneamente
- **Duração**: 2 rodadas
- **Clientes afetados**: 2
- **Tipo**: Falha total

### 3. **network_instability**
- **Descrição**: Instabilidade de rede com timeouts
- **Duração**: 5 rodadas
- **Clientes afetados**: Todos
- **Probabilidade**: 30% por rodada

### 4. **slow_clients**
- **Descrição**: Clientes com resposta lenta
- **Duração**: 4 rodadas
- **Clientes afetados**: 2
- **Probabilidade**: 80% por rodada

### 5. **cascading_failure**
- **Descrição**: Falha em cascata
- **Duração**: 6 rodadas
- **Clientes afetados**: Todos
- **Probabilidade**: 20% por rodada
- **Recuperação**: 5% por rodada

### 6. **intermittent_failure**
- **Descrição**: Falhas intermitentes com recuperação
- **Duração**: 8 rodadas
- **Clientes afetados**: Todos
- **Probabilidade**: 40% por rodada
- **Recuperação**: 30% por rodada

## 📈 Métricas Coletadas

### Por Rodada:
- **Timestamp** da rodada
- **Cenário ativo** (se houver)
- **Número de clientes** respondendo/total
- **Lista de clientes** com falha/lentos
- **Tempos de resposta** individuais e estatísticas
- **Contagem de timeouts**
- **Acurácia e perda** do modelo global
- **Taxa de convergência**
- **Tempo de agregação**
- **Contribuições por cliente** (número de amostras)

### Por Experimento:
- **Score de resiliência** (0.0 a 1.0)
- **Rodada de convergência**
- **Acurácia média/final**
- **Total de falhas**
- **Estatísticas por cenário**

## 🚀 Como Executar

### Opção 1: Todos os Cenários (Recomendado)
```bash
# Com Docker Compose
cd node_failure_tests
docker-compose -f docker-compose-test.yml up

# Localmente (após instalar dependências)
python test_orchestrator.py
```

### Opção 2: Cenário Único (Para Testes Rápidos)
```bash
python run_single_scenario.py
```

### Opção 3: Baseline (Sem Falhas)
```python
from test_orchestrator import TestOrchestrator

orchestrator = TestOrchestrator(CLIENT_ENDPOINTS)
orchestrator.run_baseline_training("my_baseline")
```

## 📋 Pré-requisitos

### Dependências Python:
```bash
pip install -r requirements.txt
```

### Serviços Necessários:
- 3 clientes FL rodando (portas 5000 em containers)
- Acesso à rede Docker `fl-network`

## 📁 Resultados Exportados

### Arquivo Excel (.xlsx)
Contém 4 abas:

1. **Resumo**: Métricas gerais do experimento
2. **Métricas por Rodada**: Dados detalhados de cada rodada
3. **Análise de Falhas**: Foco nas rodadas com falhas
4. **Estatísticas por Cenário**: Comparação entre cenários

### Arquivo JSON (.json)
- Dados estruturados para análises programáticas
- Mesmas métricas do Excel em formato JSON
- Útil para ferramentas de visualização

### Localização:
```
node_failure_tests/results/
├── baseline_no_failures_YYYYMMDD_HHMMSS.xlsx
├── test_single_node_failure_YYYYMMDD_HHMMSS.xlsx
├── test_multiple_node_failure_YYYYMMDD_HHMMSS.xlsx
└── ...
```

## 🎛️ Configurações Avançadas

### Personalizar Cenários:
```python
from failure_simulator import FailureScenario, FailureType

custom_scenario = FailureScenario(
    name="custom_test",
    description="Meu teste personalizado",
    failure_type=FailureType.SLOW_RESPONSE,
    affected_clients=[0, 1],
    failure_probability=0.5,
    duration_rounds=5,
    recovery_probability=0.2
)

orchestrator.run_scenario_test(custom_scenario)
```

### Modificar Parâmetros:
```python
# Número de rodadas
orchestrator = TestOrchestrator(endpoints, num_rounds=15)

# Timeouts
orchestrator.MIN_TIMEOUT = 5
orchestrator.MAX_TIMEOUT = 60
```

## 📊 Interpretando os Resultados

### Score de Resiliência:
- **0.8 - 1.0**: Excelente resiliência
- **0.6 - 0.8**: Boa resiliência  
- **0.4 - 0.6**: Resiliência moderada
- **0.0 - 0.4**: Baixa resiliência

### Análise Recomendada:
1. Compare acurácia final entre cenários
2. Observe tempo de convergência
3. Analise impacto de diferentes tipos de falha
4. Verifique recuperação após falhas
5. Compare com baseline (sem falhas)

## 🔧 Solução de Problemas

### Erro "Cliente não respondeu":
- Verifique se os containers estão rodando
- Confirme conectividade de rede
- Ajuste timeouts se necessário

### Arquivos Excel não gerados:
- Instale `openpyxl`: `pip install openpyxl`
- Verifique permissões do diretório `results/`

### Falhas não simuladas:
- Confirme que o cenário foi iniciado corretamente
- Verifique logs do `failure_simulator`
- Ajuste probabilidades se necessário

## 🤝 Contribuindo

Para adicionar novos tipos de falha:

1. Adicione ao enum `FailureType`
2. Implemente lógica em `should_client_fail()`
3. Adicione cenários em `get_predefined_scenarios()`
4. Documente o novo tipo de falha

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs detalhados
2. Consulte este README
3. Analise os arquivos de exemplo
4. Teste com cenário único primeiro
