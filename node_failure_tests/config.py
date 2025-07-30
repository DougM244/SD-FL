# node_failure_tests/config.py

"""
Configurações para os testes de falha de nós
Modifique este arquivo para personalizar os testes
"""

# Configurações de rede
CLIENT_ENDPOINTS = [
    "http://client-1:5000/fit",
    "http://client-2:5000/fit", 
    "http://client-3:5000/fit",
]

# Configurações de treinamento
NUM_ROUNDS = 10
MIN_TIMEOUT = 10        # Timeout mínimo em segundos
MAX_TIMEOUT = 180       # Timeout máximo em segundos
ALPHA = 0.125          # Fator de ponderação para média de RTT
BETA = 0.25            # Fator de ponderação para desvio de RTT

# Configurações de exportação
RESULTS_DIR = "results"
EXPORT_JSON = True     # Se deve exportar JSON além do Excel
EXPORT_GRAPHS = True   # Se deve gerar gráficos automáticos

# Configurações de cenários customizados
CUSTOM_SCENARIOS = [
    {
        "name": "light_failure",
        "description": "Falha leve - apenas 1 cliente lento ocasionalmente",
        "failure_type": "SLOW_RESPONSE",
        "affected_clients": [0],
        "failure_probability": 0.3,
        "duration_rounds": 4,
        "recovery_probability": 0.4
    },
    {
        "name": "heavy_failure", 
        "description": "Falha pesada - múltiplos clientes falhando",
        "failure_type": "TOTAL_FAILURE",
        "affected_clients": [0, 1, 2],
        "failure_probability": 0.6,
        "duration_rounds": 6,
        "recovery_probability": 0.1
    }
]

# Configurações de análise
RESILIENCE_THRESHOLDS = {
    "excellent": 0.8,
    "good": 0.6,
    "moderate": 0.4
}

CONVERGENCE_THRESHOLD = 0.001  # Threshold para detectar convergência

# Configurações de visualização
GRAPH_SETTINGS = {
    "figure_size": (12, 8),
    "dpi": 300,
    "style": "seaborn",
    "color_palette": "husl"
}
