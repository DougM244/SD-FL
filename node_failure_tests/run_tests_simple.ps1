# node_failure_tests/run_tests_simple.ps1
# Script PowerShell simplificado para executar os testes

Write-Host "🚀 Sistema de Testes de Falha de Nós - Federated Learning" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green

# Verifica Docker
try {
    docker info | Out-Null
    Write-Host "✅ Docker detectado" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker não está rodando. Inicie o Docker Desktop primeiro." -ForegroundColor Red
    exit 1
}

# Cria diretório de resultados
if (!(Test-Path "results")) {
    New-Item -ItemType Directory -Path "results" | Out-Null
    Write-Host "📁 Diretório 'results' criado" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Selecione o tipo de teste:"
Write-Host "1) Teste único (rápido - 1 cenário)"
Write-Host "2) Execução completa (todos os cenários)"
Write-Host "3) Apenas baseline (sem falhas)"
Write-Host ""

$choice = Read-Host "Digite sua opção (1-3)"

if ($choice -eq "1") {
    Write-Host "🎯 Executando teste único..." -ForegroundColor Yellow
    docker-compose -f docker-compose-test.yml down
    docker-compose -f docker-compose-test.yml run test-orchestrator python node_failure_tests/run_single_scenario.py
    Write-Host "✅ Teste único finalizado!" -ForegroundColor Green
}
elseif ($choice -eq "2") {
    Write-Host "🧪 Executando todos os cenários..." -ForegroundColor Yellow
    Write-Host "⏳ Isso pode levar 30-45 minutos..." -ForegroundColor Yellow
    docker-compose -f docker-compose-test.yml down
    docker-compose -f docker-compose-test.yml up --build
    Write-Host "✅ Testes completos finalizados!" -ForegroundColor Green
}
elseif ($choice -eq "3") {
    Write-Host "📊 Executando baseline..." -ForegroundColor Yellow
    docker-compose -f docker-compose-test.yml down
    docker-compose -f docker-compose-test.yml run test-orchestrator python -c "
import sys
sys.path.append('/app')
from node_failure_tests.test_orchestrator import TestOrchestrator
import time
CLIENT_ENDPOINTS = ['http://client-1:5000/fit', 'http://client-2:5000/fit', 'http://client-3:5000/fit']
orchestrator = TestOrchestrator(CLIENT_ENDPOINTS, num_rounds=8)
orchestrator.run_baseline_training('baseline_' + str(int(time.time())))
"
    Write-Host "✅ Baseline finalizado!" -ForegroundColor Green
}
else {
    Write-Host "❌ Opção inválida!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "• Verifique os arquivos Excel em .\results\" -ForegroundColor White
Write-Host "• Execute 'python analyze_results.py' para gráficos" -ForegroundColor White
