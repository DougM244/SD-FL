#!/bin/bash

# node_failure_tests/run_tests.sh
# Script para executar os testes de falha de nós

echo "🚀 Sistema de Testes de Falha de Nós - Federated Learning"
echo "======================================================"

# Verifica se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Inicie o Docker primeiro."
    exit 1
fi

# Cria diretório de resultados se não existir
mkdir -p results

echo ""
echo "Selecione o tipo de teste:"
echo "1) Execução completa (todos os cenários)"
echo "2) Teste único (cenário específico)"
echo "3) Apenas baseline (sem falhas)"
echo "4) Análise de resultados existentes"
echo ""
read -p "Digite sua opção (1-4): " choice

case $choice in
    1)
        echo "🧪 Executando todos os cenários de teste..."
        echo "⏳ Isso pode levar 30-45 minutos..."
        
        # Para containers existentes
        docker-compose -f docker-compose-test.yml down
        
        # Inicia os testes
        docker-compose -f docker-compose-test.yml up --build
        
        echo "✅ Testes completos finalizados!"
        echo "📁 Verifique os resultados em: ./results/"
        ;;
        
    2)
        echo "🎯 Executando teste de cenário único..."
        
        # Para containers existentes  
        docker-compose -f docker-compose-test.yml down
        
        # Modifica o comando para executar cenário único
        export TEST_COMMAND="python node_failure_tests/run_single_scenario.py"
        docker-compose -f docker-compose-test.yml run test-orchestrator $TEST_COMMAND
        
        echo "✅ Teste único finalizado!"
        ;;
        
    3)
        echo "📊 Executando baseline (sem falhas)..."
        
        # Para containers existentes
        docker-compose -f docker-compose-test.yml down
        
        # Executa apenas baseline
        export TEST_COMMAND="python -c \"
from node_failure_tests.test_orchestrator import TestOrchestrator
CLIENT_ENDPOINTS = ['http://client-1:5000/fit', 'http://client-2:5000/fit', 'http://client-3:5000/fit']
orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=10)
orchestrator.run_baseline_training('baseline_$(date +%Y%m%d_%H%M%S)')
\""
        docker-compose -f docker-compose-test.yml run test-orchestrator bash -c "$TEST_COMMAND"
        
        echo "✅ Baseline finalizado!"
        ;;
        
    4)
        echo "📈 Executando análise de resultados..."
        
        if [ ! -f "requirements.txt" ]; then
            echo "❌ Arquivo requirements.txt não encontrado!"
            exit 1
        fi
        
        # Instala dependências se necessário
        echo "Instalando dependências de análise..."
        pip install matplotlib seaborn pandas
        
        # Executa análise
        python analyze_results.py
        
        echo "✅ Análise finalizada!"
        ;;
        
    *)
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac

echo ""
echo "📋 Próximos passos:"
echo "• Verifique os arquivos Excel gerados em ./results/"
echo "• Execute 'python analyze_results.py' para análises visuais"
echo "• Consulte README.md para interpretação dos resultados"
