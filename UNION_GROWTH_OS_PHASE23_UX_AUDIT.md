# FASE 23 — AUDITORIA INDEPENDENTE DE UX, NAVEGAÇÃO & ARQUITETURA DE INTERFACE

**Alvo Auditado**: `UNION GROWTH OS` (`c29ae155d0e1829efe55846a34fc9aa8edfb83b9` em produção e código-fonte `frontend/src/` + `backend/app/`)  
**Referências de Comparação**: Linear, Notion, HubSpot, Stripe, Amplitude, Jasper, Canva, Intercom.

---

## 1. O Que Já Funciona Bem (Preservar Integralmente)
1. **Arquitetura de 6 Áreas na Navegação (`navigation.ts`)**: `Início`, `Meu Trabalho`, `Comercial`, `Marketing`, `Inteligência Artificial`, `Gestão` (+ `Todos os recursos`). Sem duplicidade de rotas principais.
2. **Command Palette (`Ctrl+K` / `CommandCenter.tsx`)**, **Drawer de Ajuda**, **Tema Dark/Light**, **Meu Trabalho Unificado (`MyWorkHub.tsx`)** e **Orientação Contextual (`AreaContextGuide.tsx`)** entregues nas Fases 22 / 22.1.
3. **Personalização real da Fábrica de Conteúdo** recém-corrigida no commit `c29ae15` (agora respeita marca, domínio, nicho, persona, oferta e campanha do tenant ativo).

---

## 2. Gargalos de Experiência & Complexidade Ainda Encontrados na Auditoria Independente

| Área Auditada | Problema Identificado na Experiência Atual | Impacto para o Empreendedor Leigo | Solução Arquitetural na Fase 23 |
|---|---|---|---|
| **Início (`HomeWorkspace.tsx`)** | Exibe saudação, checklist longo de 8 itens técnicos ("motores e agentes", "automações 24/7"), até 5 alertas e 4 KPIs numéricos soltos. Não responde em 5 segundos *saúde em 12 dimensões*, *Growth Score explicado*, *Opportunity Radar* nem permite pedir em português *"Quero vender mais"*. | Usuário não sabe qual é o diagnóstico geral da empresa nem por onde agir primeiro. | Substituir o topo do `Início` pelo **AI Growth Command Center**: **ASK UNION**, **Growth Score 0–100 transparente**, **Business Health (12 pilares reais/estimados)**, **AI CEO Briefing** e **Opportunity Radar + Executive Actions**. |
| **Separação de Perfis (`UX`)** | O usuário leigo vê submenus técnicos (`Auditoria & Logs`, `Modelos & Provedores`, `Experimentos ICE`, `Piloto 7 Dias`) com a mesma ênfase de tarefas simples do dia a dia. | Sobrecarga cognitiva ("30 ferramentas ao mesmo tempo"). | Criar **Modo Simples** vs. **Modo Avançado** persistente no cabeçalho e banco (`ui_mode`). No Modo Simples, exibir apenas ações orientadas a objetivo em linguagem cotidiana. |
| **Onboarding Inicial** | O `Configurações & Planos` tem formulário de 5 campos de empresa, mas falta um fluxo progressivo de **6 etapas** (*Empresa → Marca → Objetivos → Plano IA → Primeiras Ações → Conexões*). | Empreendedor não recebe um "primeiro plano de crescimento pronto" logo após entrar. | Implementar **Business Onboarding Progressivo (6 Etapas)** salvável, editável e retomável a qualquer momento. |
| **Gestão de Marca** | Marca está espalhada entre `Configurações` (5 campos) e `Personas` (`Marketing`), sem tom de voz, fontes, diferenciais, termos proibidos, preview ou detector de inconsistências. | Textos e campanhas podem sair sem tom consistente entre SEO, Copy e Redes. | Criar **Brand Intelligence Center** em `Gestão` com versionamento, visualização ao vivo e **auditoria de consistência** sobre campanhas e conteúdos. |
| **Automações (`IA`)** | Aba `Automações 24/7` exibe regras pré-semeadas técnicas (`cron`), sem opção para o empresário pedir automações por frase natural. | Leigo não consegue criar regras como *"Quando entrar lead, analisar e avisar"*. | Adicionar **Conversational Automation Builder** (linguagem natural → workflow legível → simulação dry-run → aprovação). |
| **Analytics & Atribuição** | Métricas comerciais, financeiras e de marketing ficam separadas em sub-abas distintas (`Financeiro`, `Relatórios`, `CRM`, `Marketing`) sem funil integrado e sem visão transparente de atribuição por canal. | Difícil saber de onde vêm leads e vendas sem abrir 4 telas. | Criar visão unificada **Analytics & Attribution** dentro de `Gestão → Relatórios & Analytics`, separando `REAL` / `ESTIMATIVA` / `NÃO DISPONÍVEL`. |
| **Equipe de Agentes** | `orchestrator.py` tinha `11` agentes registrados enquanto `ai_engines_hub.py` listava `12` (`AGENT_12_CRM`); faltava o `AI Data Analyst` pedido na arquitetura alvo. | Lacuna analítica dedicada no catálogo de especialistas. | Padronizar os **12 Agentes Especializados** incluindo `AGENT_12_DATA_ANALYST` com metadados humanos e técnicos unificados. |
| **Responsividade & CI/CD** | Validação responsiva anterior cobria 4 viewports (`1920`, `1366`, `768`, `390`), faltando `1024x768` e `360x800`; `.github/workflows/ci-cd.yml` usa `v4/v5` em Node 20. | Necessário garantir ausência de corte/overflow em notebooks 1024px e Android 360px, e atualizar pipeline CI/CD. | Validar **todos os 6 viewports** (`1920`, `1366`, `1024`, `768`, `390`, `360`) + atualizar pipeline + teste explícito de rate-limit. |
