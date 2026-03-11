# Proposta de Arquitetura Otimizada: Reconstrução de Expert Advisors (EX5)

## Análise do Workflow Proposto Original

### Workflow Original
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 1. Extrator     │───▶│ 2. Profiler      │───▶│ 3. IA Analysis  │───▶│ 4. Comparação   │
│    Python EX5   │    │    MQL5 (1 sem)  │    │    JSON + CSV   │    │    & Ajustes    │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 1. Avaliação de Eficiência e Viabilidade

### 1.1 Problemas Críticos Identificados

| Aspecto | Problema | Severidade |
|---------|----------|------------|
| **Extração EX5** | Formato EX5 é bytecode MQL5 customizado com ofuscação - decompilação completa é **tecnicamente impossível** desde builds modernos | CRÍTICA |
| **Profiler 1 semana** | Tempo excessivo; mercado muda; não captura comportamento em todos os regimes | ALTA |
| **Dependência IA** | IA não pode reconstruir lógica que não está nos metadados; gera código "inspirado" não equivalente | ALTA |
| **Validação** | Sem ground truth para comparar comportamento | MÉDIA |

### 1.2 Realidade Técnica do Formato EX5

Segundo análises da comunidade de engenharia reversa [^3^][^18^]:

- **EX4/EX5** usam formato binário customizado executado em VM do MetaTrader
- **MetaEditor** e **Terminal.exe** possuem anti-debugging ativo
- Desde **MT4 Build 500+** e **MT5**, decompilação total é **impossível**
- Arquivos protegidos via **MQL5 Cloud Protector** são compilados para código nativo

> ⚠️ **Conclusão**: O workflow original parte de premissa tecnicamente inviável para decompilação completa.

---

## 2. Gargalos e Dependências Problemáticas

### 2.1 Gargalos Identificados

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GARGALOS DO WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [EX5 File] ──▶ [Python Extractor] ──▶ ⚠️ GARGALO #1: Extração limitada    │
│                      │                                                      │
│                      ▼                                                      │
│              [Metadados incompletos] ──▶ ⚠️ GARGALO #2: Informação          │
│                      │                         insuficiente para IA          │
│                      ▼                                                      │
│  [MT5 Profiler] ──▶ ⚠️ GARGALO #3: 1 semana de coleta                        │
│                      │                         (tempo excessivo)             │
│                      ▼                                                      │
│  [CSV Comportamental] ──▶ ⚠️ GARGALO #4: Dados sem contexto semântico        │
│                      │                                                      │
│                      ▼                                                      │
│  [IA Generativa] ──▶ ⚠️ GARGALO #5: Gera código aproximado, não equivalente  │
│                      │                                                      │
│                      ▼                                                      │
│  [Novo EA] ──▶ ⚠️ GARGALO #6: Validação impossível (sem código original)     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Dependências Problemáticas

| Dependência | Problema | Mitigação Proposta |
|-------------|----------|-------------------|
| ChatGPT/Claude/Gemini | Não têm acesso ao código-fonte real | Usar IA apenas para **assistência**, não geração principal |
| MT5 Profiler 1 semana | Janela temporal insuficiente para todos os regimes | Combinar **backtest histórico** + **análise estática** |
| Python puro para EX5 | Limitado sem engenharia reversa avançada | Adotar **Ghidra/IDA** para análise profunda |
| Comparação comportamental | Sem métricas definidas | Estabelecer **métricas quantitativas** de equivalência |

---

## 3. Automações Adicionais Sugeridas

### 3.1 Automações de Pipeline

```yaml
# pipeline_config.yaml
automations:
  pre_analysis:
    - checksum_verification:    # Verifica integridade do EX5
    - entropy_analysis:         # Detecta ofuscação/criptografia
    - string_extraction:        # Extrai strings legíveis
    
  static_analysis:
    - import_table_extraction:  # APIs MQL5 utilizadas
    - function_signature_detection:  # Assinaturas de funções
    - constant_extraction:      # Parâmetros hardcoded
    
  dynamic_analysis:
    - sandboxed_backtest:       # Execução em ambiente isolado
    - behavior_logging:         # Log de chamadas de trading
    - performance_profiling:    # Métricas de execução
    
  reconstruction:
    - template_generation:      # Gera template baseado em padrões
    - parameter_inference:      # Inferência de parâmetros via ML
    - code_assist_suggestions:  # Sugestões de implementação
    
  validation:
    - behavioral_equivalence:   # Teste de equivalência comportamental
    - statistical_comparison:   # Comparação estatística de resultados
    - regression_testing:       # Testes de regressão automatizados
```

### 3.2 Scripts de Automação

| Script | Função | Gatilho |
|--------|--------|---------|
| `ex5_analyzer.py` | Análise inicial do binário | On file upload |
| `behavior_capture.mq5` | Script injetável para logging | On MT5 attach |
| `backtest_runner.py` | Orquestra backtests automatizados | Scheduled/On demand |
| `equivalence_tester.py` | Compara comportamento original vs reconstruído | Post-reconstruction |
| `report_generator.py` | Gera relatórios de análise | Pipeline completion |

---

## 4. Arquitetura Otimizada e Realista

### 4.1 Arquitetura Proposta: "EA Reconstruction Pipeline v2"

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CAMADA DE INGESTÃO                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │   EX5 File   │  │   EX4 File   │  │   DLL Aux    │  │   Config     │                │
│  │   (Target)   │  │  (Opcional)  │  │  (Opcional)  │  │   (JSON)     │                │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                │
└─────────┼─────────────────┼─────────────────┼─────────────────┼────────────────────────┘
          │                 │                 │                 │
          ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           CAMADA DE ANÁLISE ESTÁTICA                                    │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                      ANÁLISE MULTI-FERRAMENTA                                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│  │  │   Ghidra    │  │  Python     │  │   YARA      │  │  Strings    │            │   │
│  │  │  (Deep)     │  │  (Utils)    │  │  (Rules)    │  │  (Extract)  │            │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │   │
│  │         └─────────────────┴─────────────────┴─────────────────┘                 │   │
│  │                                    │                                            │   │
│  │                                    ▼                                            │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐   │   │
│  │  │              EXTRACTED KNOWLEDGE BASE (JSON)                            │   │   │
│  │  │  {                                                                        │   │   │
│  │  │    "metadata": { "magic", "version", "timestamp", ... },                │   │   │
│  │  │    "imports": [ "OrderSend", "iMA", "iRSI", ... ],                      │   │   │
│  │  │    "strings": [ "StopLoss", "TakeProfit", "Signal", ... ],              │   │   │
│  │  │    "constants": { "period": 14, "deviation": 2.0, ... },                │   │   │
│  │  │    "indicators": [ { "type": "MA", "period": 20 }, ... ],               │   │   │
│  │  │    "patterns": [ "martingale", "grid", "scalping", ... ]                 │   │   │
│  │  │  }                                                                        │   │   │
│  │  └─────────────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          CAMADA DE ANÁLISE DINÂMICA                                     │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐                    │
│  │    BACKTEST HISTÓRICO        │  │    SANDBOX EXECUTION         │                    │
│  │    (Múltiplos regimes)       │  │    (Behavior Capture)        │                    │
│  │                              │  │                              │                    │
│  │  • 5+ anos de dados          │  │  • Order flow logging        │                    │
│  │  • Múltiplos timeframes      │  │  • Signal decision tree      │                    │
│  │  • Métricas de performance   │  │  • Risk management actions   │                    │
│  │  • Drawdown analysis         │  │  • Entry/exit patterns       │                    │
│  └──────────────┬───────────────┘  └──────────────┬───────────────┘                    │
│                 │                                 │                                     │
│                 └────────────────┬────────────────┘                                     │
│                                  ▼                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │              BEHAVIORAL PROFILE (CSV/JSON)                                       │  │
│  │  {                                                                               │  │
│  │    "trade_patterns": { "frequency", "avg_hold_time", "win_rate", ... },        │  │
│  │    "risk_profile": { "max_drawdown", "position_sizing", "stop_patterns" },     │  │
│  │    "indicator_usage": { "signals", "confirmations", "filters" },               │  │
│  │    "market_conditions": { "trending", "ranging", "volatile" }                   │  │
│  │  }                                                                               │  │
│  └─────────────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      CAMADA DE RECONSTRUÇÃO ASSISTIDA                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                    KNOWLEDGE-DRIVEN GENERATION                                   │   │
│  │                                                                                  │   │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │   │
│  │  │   Pattern    │───▶│   Template   │───▶│   Human      │───▶│   Generated  │  │   │
│  │  │   Matcher    │    │   Engine     │    │   Review     │    │   MQL5 Code  │  │   │
│  │  └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘  │   │
│  │         │                  │                   │                   │           │   │
│  │         └──────────────────┴───────────────────┴───────────────────┘           │   │
│  │                                    │                                            │   │
│  │                                    ▼                                            │   │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐   │   │
│  │  │  IA ASSISTÊNCIA (NÃO GERAÇÃO PRINCIPAL)                                  │   │   │
│  │  │  • Sugere implementações baseadas em padrões detectados                 │   │   │
│  │  │  • Explica funções MQL5 equivalentes                                    │   │   │
│  │  │  • Ajuda em otimização de parâmetros                                    │   │   │
│  │  │  • Gera documentação técnica                                            │   │   │
│  │  └─────────────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        CAMADA DE VALIDAÇÃO                                              │
│  ┌──────────────────────────┐  ┌──────────────────────────┐  ┌────────────────────────┐ │
│  │   EQUIVALÊNCIA           │  │   REGRESSÃO              │  │   PERFORMANCE          │ │
│  │   COMPORTAMENTAL         │  │   TESTS                  │  │   METRICS              │ │
│  │                          │  │                          │  │                        │ │
│  │ • Same trade sequence    │  │ • Edge cases             │  │ • Sharpe ratio         │ │
│  │ • Same signal timing     │  │ • Error handling         │  │ • Max drawdown         │ │
│  │ • Same risk behavior     │  │ • Recovery scenarios     │  │ • Win rate             │ │
│  └────────────┬─────────────┘  └────────────┬─────────────┘  └────────────┬───────────┘ │
│               │                             │                             │             │
│               └─────────────────────────────┼─────────────────────────────┘             │
│                                             ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                    VALIDATION REPORT                                             │   │
│  │  {                                                                               │   │
│  │    "equivalence_score": 0.87,  # 0-1                                            │   │
│  │    "confidence_level": "high",  # low/medium/high                               │   │
│  │    "recommendation": "APPROVED_WITH_REVIEW",                                    │   │
│  │    "manual_review_required": [ "position_sizing", "slippage_handling" ]         │   │
│  │  }                                                                               │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Componentes da Arquitetura

| Componente | Tecnologia | Função |
|------------|------------|--------|
| **Static Analyzer** | Ghidra + Python | Análise profunda do binário EX5 |
| **Pattern Matcher** | Python + YARA | Identifica padrões de trading conhecidos |
| **Backtest Engine** | MT5 Strategy Tester | Execução histórica controlada |
| **Behavior Logger** | MQL5 Script | Captura comportamento em runtime |
| **Template Engine** | Jinja2 + Python | Gera templates MQL5 estruturados |
| **AI Assistant** | Claude/GPT-4 API | Assistência contextual (não geração principal) |
| **Validator** | Python + MT5 | Validação automatizada de equivalência |

---

## 5. Avaliação de Alternativas de Ferramentas

### 5.1 Comparação: Python Puro vs Ghidra/IDA

| Critério | Python Puro | Ghidra | IDA Pro |
|----------|-------------|--------|---------|
| **Custo** | Gratuito | Gratuito | $$$ (Licença) |
| **Curva de aprendizado** | Baixa | Alta | Alta |
| **Análise EX5** | Superficial | Profunda | Profunda |
| **Decompilação** | ❌ Não | ⚠️ Limitada | ⚠️ Limitada |
| **Automação** | ✅ Excelente | ✅ Boa (headless) | ⚠️ Média |
| **Extensibilidade** | ✅ Alta | ✅ Alta (Java/Python) | ⚠️ Média |
| **Comunidade** | Grande | Crescente | Estabelecida |

### 5.2 Recomendação de Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────────┐
│                    STACK RECOMENDADO                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ANÁLISE ESTÁTICA                                               │
│  ├── Ghidra (primário) - Análise profunda de binários          │
│  ├── Python + pwntools - Extração de strings/básica            │
│  └── YARA - Detecção de padrões                                 │
│                                                                 │
│  ANÁLISE DINÂMICA                                               │
│  ├── MT5 Strategy Tester - Backtests controlados               │
│  ├── MQL5 Behavior Logger - Captura de comportamento           │
│  └── Docker + MT5 - Sandboxing isolado                         │
│                                                                 │
│  ORQUESTRAÇÃO                                                   │
│  ├── Python + Prefect/Airflow - Pipeline automation            │
│  ├── FastAPI - API de serviços                                 │
│  └── PostgreSQL/MongoDB - Armazenamento de análises            │
│                                                                 │
│  IA ASSISTÊNCIA                                                 │
│  ├── Claude API - Análise contextual e sugestões               │
│  └── LangChain - Orquestração de prompts                       │
│                                                                 │
│  VALIDAÇÃO                                                      │
│  ├── pytest + hypothesis - Testes automatizados                │
│  ├── MQL5 Unit Tests - Testes no código gerado                 │
│  └── Custom equivalence metrics - Métricas de equivalência     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Por que Ghidra é Essencial

Baseado em pesquisas [^12^][^14^][^15^]:

1. **ProgramAPI**: Permite análise programática de binários
2. **PCode**: Representação intermediária independente de arquitetura
3. **Decompiler**: Gera pseudocódigo C para análise
4. **Headless Mode**: Automação via linha de comando
5. **Extensões**: BTIGhidra para inferência de tipos [^14^]
6. **ghidriff**: Diffing de binários para comparação [^12^]

---

## 6. Escalabilidade e Batch Processing

### 6.1 Arquitetura para Múltiplos EAs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BATCH PROCESSING SYSTEM                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     JOB QUEUE (Redis/RabbitMQ)                       │   │
│  │  [EA_1] [EA_2] [EA_3] [EA_4] ... [EA_n]                             │   │
│  └────────────────────────┬────────────────────────────────────────────┘   │
│                           │                                                 │
│           ┌───────────────┼───────────────┐                                 │
│           ▼               ▼               ▼                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │  Worker 1   │  │  Worker 2   │  │  Worker N   │  (Horizontal scaling)   │
│  │  (Docker)   │  │  (Docker)   │  │  (Docker)   │                         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                         │
│         │                │                │                                 │
│         └────────────────┴────────────────┘                                 │
│                          │                                                  │
│                          ▼                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              SHARED STORAGE (S3/MinIO + PostgreSQL)                  │   │
│  │  • EX5 files  • Analysis results  • Generated code  • Reports        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Configuração de Escalabilidade

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  analyzer_worker:
    image: ea-reconstruction-analyzer:latest
    deploy:
      replicas: 5
      resources:
        limits:
          cpus: '4'
          memory: 8G
    environment:
      - GHIDRA_MAX_RAM=6G
      - MT5_WINE_PREFIX=/mt5
      
  backtest_worker:
    image: ea-reconstruction-backtest:latest
    deploy:
      replicas: 10
      resources:
        limits:
          cpus: '2'
          memory: 4G
    environment:
      - MT5_TIMEOUT=3600
      
  validation_worker:
    image: ea-reconstruction-validator:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### 6.3 Métricas de Escalabilidade

| Métrica | Target | Estratégia |
|---------|--------|------------|
| Throughput | 50 EAs/dia | Workers paralelos |
| Latency (análise) | < 30 min/EA | Cache de análises Ghidra |
| Latency (backtest) | < 2h/EA | Múltiplos timeframes simultâneos |
| Storage | < 100MB/EA | Compressão + retenção seletiva |

---

## 7. Versionamento e Documentação

### 7.1 Estrutura de Versionamento

```
ea-reconstruction-repo/
├── 📁 input/
│   └── 📁 ex5_files/
│       ├── EA_Original_v1.0.ex5
│       └── EA_Original_v1.1.ex5
│
├── 📁 analysis/
│   ├── 📁 static/
│   │   ├── EA_v1.0_ghidra_project/
│   │   ├── EA_v1.0_metadata.json
│   │   └── EA_v1.0_patterns.yaml
│   └── 📁 dynamic/
│       ├── EA_v1.0_behavior_profile.csv
│       └── EA_v1.0_backtest_results/
│
├── 📁 reconstruction/
│   ├── 📁 templates/
│   │   └── scalping_template_v2.mq5
│   ├── 📁 generated/
│   │   ├── EA_Reconstructed_v1.0.mq5
│   │   └── EA_Reconstructed_v1.0.ex5
│   └── 📁 validation/
│       ├── equivalence_report.json
│       └── diff_analysis.html
│
├── 📁 docs/
│   ├── 📄 ARCHITECTURE.md
│   ├── 📄 METHODOLOGY.md
│   ├── 📄 EA_v1.0_ANALYSIS_REPORT.md
│   └── 📄 CHANGELOG.md
│
└── 📁 pipeline/
    ├── 📄 config.yaml
    └── 📁 scripts/
```

### 7.2 Esquema de Versionamento Semântico

```
Formato: [ORIGINAL_VERSION]-[RECONSTRUCTION_VERSION]

Exemplos:
├── EA_Original_v1.0 → EA_Rec_v1.0-1.0.0  (primeira reconstrução)
├── EA_Original_v1.0 → EA_Rec_v1.0-1.1.0  (ajuste de parâmetros)
├── EA_Original_v1.0 → EA_Rec_v1.0-2.0.0  (refatoração major)
└── EA_Original_v2.0 → EA_Rec_v2.0-1.0.0  (nova versão original)
```

### 7.3 Template de Documentação

```markdown
# Relatório de Reconstrução: [EA_NAME] v[VERSION]

## 1. Sumário Executivo
- **Data da Análise**: YYYY-MM-DD
- **Analista**: [Nome/IA]
- **Score de Equivalência**: X.XX/1.00
- **Status**: [APPROVED/APPROVED_WITH_REVIEW/REJECTED]

## 2. Análise Estática
### 2.1 Metadados Extraídos
### 2.2 APIs MQL5 Utilizadas
### 2.3 Padrões Detectados
### 2.4 Indicadores Identificados

## 3. Análise Dinâmica
### 3.1 Perfil de Trading
### 3.2 Métricas de Performance
### 3.3 Comportamento em Diferentes Regimes

## 4. Reconstrução
### 4.1 Template Utilizado
### 4.2 Parâmetros Inferidos
### 4.3 Decisões de Implementação

## 5. Validação
### 5.1 Testes de Equivalência
### 5.2 Diferenças Identificadas
### 5.3 Recomendações

## 6. Anexos
- Código fonte gerado
- Logs de execução
- Gráficos comparativos
```

---

## 8. Roadmap de Implementação

### Fase 1: Foundation (Semanas 1-4)
- [ ] Setup de infraestrutura (Ghidra, MT5, Docker)
- [ ] Desenvolvimento do extrator básico
- [ ] Implementação do behavior logger MQL5
- [ ] Pipeline de CI/CD básico

### Fase 2: Analysis Engine (Semanas 5-8)
- [ ] Integração Ghidra headless
- [ ] Sistema de pattern matching
- [ ] Automação de backtests
- [ ] Base de conhecimento de padrões

### Fase 3: Reconstruction (Semanas 9-12)
- [ ] Template engine
- [ ] Integração com IA assistiva
- [ ] Sistema de geração de código
- [ ] Primeiros casos de teste

### Fase 4: Validation (Semanas 13-16)
- [ ] Métricas de equivalência
- [ ] Testes de regressão
- [ ] Relatórios automatizados
- [ ] Otimização de performance

### Fase 5: Scale (Semanas 17-20)
- [ ] Arquitetura de workers
- [ ] Batch processing
- [ ] Monitoramento e alerting
- [ ] Documentação completa

---

## 9. Considerações Finais

### 9.1 Limitações Conhecidas

1. **Decompilação completa é impossível** - Aceitar que reconstrução é aproximada
2. **Comportamento em live pode diferir** - Sempre validar em conta demo
3. **EAs protegidos com Cloud Protector** - Requerem abordagem diferente (memory dump)
4. **Dependência de dados históricos** - Qualidade do backtest depende dos dados

### 9.2 Melhores Práticas

1. **Nunca confiar cegamente** - Sempre revisar código gerado
2. **Testar incrementalmente** - Validar cada componente isoladamente
3. **Documentar decisões** - Manter registro de escolhas de implementação
4. **Versionar tudo** - Código, configurações, resultados
5. **Automatizar validação** - Reduzir dependência de intervenção manual

### 9.3 Próximos Passos Recomendados

1. Prova de conceito com 3-5 EAs conhecidos
2. Definição de métricas de sucesso claras
3. Estabelecimento de baseline de performance
4. Iteração baseada em feedback

---

## Referências

- [^3^] Reverse Engineering StackExchange - EX5 decompilation methods
- [^12^] Ghidriff - Binary Diffing Engine
- [^14^] BTIGhidra - Binary Type Inference
- [^18^] MQL5 Forum - Protection from decompilation
- [^21^] MQL5 Articles - Risk Enforcement EA
- [^22^] MQL5 Articles - Custom Logging Framework
