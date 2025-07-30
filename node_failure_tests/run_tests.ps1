# node_failure_tests/run_tests.ps1
# Script PowerShell para executar os testes de falha de nós

Write-Host "🚀 Sistema de Testes de Falha de Nós - Federated Learning" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green

# Verifica se o Docker está rodando
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker não está rodando. Inicie o Docker Desktop primeiro." -ForegroundColor Red
    exit 1
}

# Cria diretório de resultados se não existir
if (!(Test-Path "results")) {
    New-Item -ItemType Directory -Path "results" | Out-Null
}

Write-Host ""
Write-Host "Selecione o tipo de teste:"
Write-Host "1) Execução completa (todos os cenários)"
Write-Host "2) Teste único (cenário específico)"  
Write-Host "3) Apenas baseline (sem falhas)"
Write-Host "4) Análise de resultados existentes"
Write-Host ""

$choice = Read-Host "Digite sua opção (1-4)"

switch ($choice) {
    "1" {
        Write-Host "🧪 Executando todos os cenários de teste..." -ForegroundColor Yellow
        Write-Host "⏳ Isso pode levar 30-45 minutos..." -ForegroundColor Yellow
        
        # Para containers existentes
        docker-compose -f docker-compose-test.yml down
        
        # Inicia os testes
        docker-compose -f docker-compose-test.yml up --build
        
        Write-Host "✅ Testes completos finalizados!" -ForegroundColor Green
        Write-Host "📁 Verifique os resultados em: .\results\" -ForegroundColor Cyan
    }
    
    "2" {
        Write-Host "🎯 Executando teste de cenário único..." -ForegroundColor Yellow
        
        # Para containers existentes
        docker-compose -f docker-compose-test.yml down
        
        # Executa cenário único
        docker-compose -f docker-compose-test.yml run test-orchestrator python node_failure_tests/run_single_scenario.py
        
        Write-Host "✅ Teste único finalizado!" -ForegroundColor Green
    }
    
    "3" {
        Write-Host "📊 Executando baseline (sem falhas)..." -ForegroundColor Yellow
        
        # Para containers existentes
        docker-compose -f docker-compose-test.yml down
        
        # Script Python para baseline
        $baselineScript = @"
import sys
import os
sys.path.append('/app')
from node_failure_tests.test_orchestrator import TestOrchestrator
import time

CLIENT_ENDPOINTS = ['http://client-1:5000/fit', 'http://client-2:5000/fit', 'http://client-3:5000/fit']
orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=10)
timestamp = time.strftime('%Y%m%d_%H%M%S')
orchestrator.run_baseline_training(f'baseline_{timestamp}')
"@
        
        # Salva script temporário
        $baselineScript | Out-File -FilePath "temp_baseline.py" -Encoding UTF8
        
        # Executa baseline
        docker-compose -f docker-compose-test.yml run -v "${PWD}:/app/temp" test-orchestrator python /app/temp/temp_baseline.py
        
        # Remove arquivo temporário
        Remove-Item "temp_baseline.py" -ErrorAction SilentlyContinue
        
        Write-Host "✅ Baseline finalizado!" -ForegroundColor Green
    }
    
    "4" {
        Write-Host "📈 Executando análise de resultados..." -ForegroundColor Yellow
        
        # Verifica se requirements.txt existe
        if (!(Test-Path "requirements.txt")) {
            Write-Host "❌ Arquivo requirements.txt não encontrado!" -ForegroundColor Red
            exit 1
        }
        
        # Instala dependências se necessário
        Write-Host "Instalando dependências de análise..." -ForegroundColor Yellow
        pip install matplotlib seaborn pandas
        
        # Executa análise
        python analyze_results.py
        
        Write-Host "✅ Análise finalizada!" -ForegroundColor Green
    }
    
    default {
        Write-Host "❌ Opção inválida!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "• Verifique os arquivos Excel gerados em .\results\" -ForegroundColor White
Write-Host "• Execute 'python analyze_results.py' para análises visuais" -ForegroundColor White  
Write-Host "• Consulte README.md para interpretação dos resultados" -ForegroundColor White
