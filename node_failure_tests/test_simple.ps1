# Script simplificado para testes de falha de nos
Write-Host "Sistema de Testes de Falha de Nos - Federated Learning" -ForegroundColor Green

# Verifica Docker
try {
    docker info > $null
    Write-Host "Docker detectado" -ForegroundColor Green
} catch {
    Write-Host "Docker nao esta rodando. Inicie o Docker primeiro." -ForegroundColor Red
    exit 1
}

# Cria diretorio de resultados
if (!(Test-Path "results")) {
    New-Item -ItemType Directory -Path "results" > $null
}

Write-Host ""
Write-Host "Opcoes de teste:"
Write-Host "1) Teste unico (rapido)"
Write-Host "2) Todos os cenarios" 
Write-Host "3) Apenas baseline"

$choice = Read-Host "Digite sua opcao (1-3)"

switch ($choice) {
    "1" {
        Write-Host "Executando teste unico..." -ForegroundColor Yellow
        docker-compose -f docker-compose-test.yml down
        docker-compose -f docker-compose-test.yml run test-orchestrator python node_failure_tests/run_single_scenario.py
    }
    "2" {
        Write-Host "Executando todos os cenarios..." -ForegroundColor Yellow
        docker-compose -f docker-compose-test.yml down  
        docker-compose -f docker-compose-test.yml up --build
    }
    "3" {
        Write-Host "Executando baseline..." -ForegroundColor Yellow
        docker-compose -f docker-compose-test.yml down
        docker-compose -f docker-compose-test.yml run test-orchestrator python -c "
from test_orchestrator import TestOrchestrator
CLIENT_ENDPOINTS = ['http://client-1:5000/fit', 'http://client-2:5000/fit', 'http://client-3:5000/fit']  
orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=6)
orchestrator.run_baseline_training('baseline_test')
"
    }
    default {
        Write-Host "Opcao invalida!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Teste concluido! Verifique os resultados em ./results/" -ForegroundColor Green
