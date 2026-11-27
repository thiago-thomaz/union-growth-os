# FASE 23 — ESTRATÉGIA DE PRODUTO & ARQUITETURA ("THE AUTONOMOUS BUSINESS GROWTH PLATFORM")

## 1. Posicionamento Central
Transformar o **UNION GROWTH OS** de uma coleção de 27 módulos técnicos em um **Copiloto e Gerente Digital de Crescimento Empresarial**, guiado por resultados financeiros reais e zero complexidade técnica para o empreendedor no modo padrão.

---

## 2. Os 7 Pilares Arquiteturais da Fase 23

### Pilar 1 — AI Growth Command Center (`Início`)
- Ao abrir o sistema, o usuário responde em até 10 segundos a 5 perguntas de negócio:
  1. **Como está minha empresa?** → **Business Health (12 dimensões)** com origem explícita (`REAL`, `ESTIMATIVA`, `SANDBOX`, `NÃO DISPONÍVEL`).
  2. **Qual a nota atual e o que está travando?** → **Growth Score Documentado (0–100)** mostrando componentes, pesos exatos, dados usados, limitações atuais e ações práticas para subir a nota.
  3. **Onde posso ganhar dinheiro ou corrigir gargalos?** → **Opportunity Radar Real** varrendo SEO, Concorrentes, Conteúdo, Leads, Campanhas, Produtos, Vendas, Retenção, Upsell, Automação e Canais.
  4. **O que a IA recomenda hoje e esta semana?** → **AI CEO Briefing (Diário + Semanal)** e **Executive Action Center** com ações de 1 clique (*O que fazer, por que, impacto, tempo, risco, custo R$ 0*).
  5. **Como resolvo algo em linguagem natural?** → **ASK UNION**, copiloto estruturado conectado ao estado real da empresa que classifica intenção, monta plano e gera ações rastreáveis e auditáveis.

### Pilar 2 — Zero Complexidade (`Modo Simples` vs. `Modo Avançado`)
- Preferência persistida em banco (`Tenant.ui_mode`: `"SIMPLE"` | `"ADVANCED"`) e `localStorage`.
- **Modo Simples (padrão amigável para leigos)**: oculta ruído técnico, jargões de engenharia, logs brutos e parâmetros de API; prioriza *Início (Command Center + ASK UNION)*, *Onboarding Inteligente*, *Marca*, *Campanhas/Conteúdo*, *CRM Simplificado* e *Aprovações*.
- **Modo Avançado**: libera todos os painéis técnicos, engines multimotor, logs imutáveis, webhooks, regras avançadas de automação e diagnósticos detalhados — sem quebrar nada do Modo Simples.

### Pilar 3 — Business Onboarding Inteligente (6 Etapas Recuperáveis)
Fluxo progressivo sem obrigar dezenas de formulários no dia 1:
1. **Sua Empresa** (nome, segmento, descrição, país, público, produtos/serviços)
2. **Sua Marca** (identidade, tom de voz, cores, logo, diferenciais, posicionamento)
3. **Seus Objetivos** (gerar leads, aumentar vendas, tráfego, SEO, retenção, conteúdo, automação)
4. **Plano de Crescimento** (estratégia automática personalizada persistida)
5. **Primeiras Ações** (execução imediata assistida / aprovável)
6. **Conexões** (integrações progressivas e opcionais, com Modo Assistido preservado)

### Pilar 4 — Brand Intelligence Hub Central (Jasper IQ + Canva Brand Kit)
Central única (`Gestão → Identidade & Marca`) com:
- Identidade visual (nome, logo, paleta primária/secundária, tipografia/fontes).
- Identidade verbal (tom de voz, proposta de valor, diferenciais, persona, posicionamento, exemplos, termos permitidos e termos proibidos).
- **Versionamento (`BrandVersionRecord`)**, pré-visualização ao vivo e **Detector Automático de Inconsistências** varrendo campanhas, copies, artigos SEO e Content Factory em tempo real.

### Pilar 5 — Equipe de 12 Agentes Coordenados (`AI Team`) + Arquitetura Resiliente de Provedores
- Incorporação explícita do **12º especialista (`AGENT_12_DATA_ANALYST` — AI Data Analyst)** ao registro oficial de agentes (`orchestrator.py` + `ai_engines_hub.py`).
- Reforço no `AIRouter` com **cache TTL em memória**, **circuit breaker por provedor** e **backoff em falhas transitórias** sem jamais violar `FREE_ONLY` nem tentar contornar cotas `HTTP 402` ou chaves inválidas.

### Pilar 6 — Automation Builder Conversacional Nativo Python (ZERO n8n)
- O usuário descreve em português simples o que deseja automatizar (ex.: *"Quando entrar um lead, quero que a IA analise e me avise"*, *"Leads sem resposta em 3 dias recebam follow-up"*, *"Relatório toda segunda-feira"*).
- Motor Python (`phase23_growth_platform.py`) interpreta gatilho, condição, ação, dependências, risco e custo (R$ 0,00), permite **Simular (Dry-Run)** e ativa regra persistida no PostgreSQL + `APScheduler` somente após aprovação humana explícita.

### Pilar 7 — Disciplina Absoluta de Dados, Custos e Segurança
- Proibição permanente de inventar métricas, simular envio OAuth sem credencial, expor tokens em URL ou gerar custos pagos automáticos (`FREE_ONLY`).
- Todo dado não disponível retorna explicitamente `"NAO_DISPONIVEL"`; metas e hipóteses levam selo `"ESTIMATIVA"`; fluxos financeiros de teste usam `"SANDBOX"`.
