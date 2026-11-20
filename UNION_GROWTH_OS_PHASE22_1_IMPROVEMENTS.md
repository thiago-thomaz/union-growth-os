# FASE 22.1 — MELHORIAS DE USABILIDADE, FLUXOS GUIADOS & CLAREZA OPERACIONAL

Este documento detalha cada otimização implementada para reduzir cliques desnecessários, eliminar envios silenciosos, corrigir bugs reais de interação e tornar os 8 fluxos principais autoexplicativos para usuários iniciantes, intermediários e avançados.

---

## 1. Orientação Contextual em Todas as 6 Áreas ([`AreaContextGuide.tsx`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/frontend/src/components/AreaContextGuide.tsx))
- Adicionado banner contextual recolhível no topo do workspace de cada área (`Início`, `Meu Trabalho`, `Comercial`, `Marketing`, `Inteligência Artificial`, `Gestão`) com persistência independente por área em `localStorage` (`ug_ctx_guide_<areaId>`).
- Responde objetivamente sem jargões técnicos:
  1. **O que você pode fazer aqui?**
  2. **Como começo & o que preencher?**
  3. **O que acontece depois?**
  4. **O que a IA pode fazer aqui?**
  5. **Depende da sua aprovação / credenciais?**
- Exibe **avisos reais honestos de dependência**:
  - Em `Marketing`: explica se redes sociais operam em **Modo Assistido (pacote 1-clique)** quando não há OAuth conectado.
  - Em `Inteligência Artificial`: indica se a chave gratuita do Google Gemini está conectada, aguardando ou bloqueada por cota (`HTTP 402`), mantendo a proteção `FREE_ONLY`.

---

## 2. Melhorias Específicas nos 8 Fluxos Principais

| Fluxo | Melhoria Implementada | Arquivo |
|---|---|---|
| **F1. Empresa & Marca** | Novo formulário **"1. Identidade da Empresa & Marca Ativa"** pré-preenchido (`Nome Oficial`, `Nome da Marca`, `Site/Domínio`, `Nicho`, `Público-Alvo`), validação de campos obrigatórios e salvamento direto em `PUT /api/v1/tenants/current`. | [`page.tsx`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/frontend/src/app/page.tsx) |
| **F2. Agentes & IA** | Novo **Assistente Guiado de Configuração de IA (3 Passos)** conectado a `/api/v1/ai-engine-hub/credentials`, `/test-connection` e `/tenants/current`; cards dos 11 agentes atualizados com **Qual problema resolve**, **O que executa**, **Dependência de credenciais**, filtro de busca, botão **"Executar Rotina Segura"** e link direto para **"Resultados"**. Trava `FREE_ONLY` preservada. | [`AITeamAndGovernanceView.tsx`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/frontend/src/components/AITeamAndGovernanceView.tsx) |
| **F3. Integrações** | Geração dinâmica de **1 input rotulado por credencial exigida** (ex.: GA4 agora exibe campos distintos para `PROPERTY ID` e `SERVICE ACCOUNT JSON OR OAUTH TOKEN`), status humanos via `StatusPill` (`Aguardando Conexão`, `Conectada`, `Falha na Conexão`), quadro explícito de **Modo Assistido** quando sem integração, escopos técnicos recolhíveis em `<details>` e validação com `showNotice`. | [`page.tsx`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/frontend/src/app/page.tsx) |
| **F4. Criar Campanha** | Adicionados `<label>` em todos os campos (`Nome da Campanha *`, `Canal Principal`, `Objetivo / Tipo`, `Orçamento Planejado (R$)`), novo seletor visível de **Canal Principal**, placeholders com exemplos reais, validação orientativa ao clicar vazio e `EmptyState` em Personas e Campanhas. | [`page.tsx`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/frontend/src/app/page.tsx) |
| **F5. Criar Conteúdo** | Rótulos claros em `Calendário & Redes`, exemplos em todos os inputs, tradução de `PENDING_CREDENTIALS` para `Modo Assistido (sem OAuth)`, validação de título vazio, `EmptyState` e navegação cruzada em 1 clique entre **Post Manual** e **Fábrica de Conteúdo (30 peças)**. | [`page.tsx`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/frontend/src/app/page.tsx) |
| **F6. Leads & CRM** | **Correção do BUG de busca**: filtro alterado de `l.name`/`l.company`/`l.status` para `l.full_name`, `l.company_name`, `l.email`, `l.qualification_status` e `l.pipeline_stage`; adicionados `<label>` em todos os campos (incluindo `Valor Estimado (R$)`), checkbox explícito de **Consentimento LGPD**, validação amigável e `EmptyState` com botão "Limpar busca". | [`page.tsx`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/frontend/src/app/page.tsx) |
| **F7. Proposta & Venda** | Guia de 4 etapas no Gerador de Propostas, `<label>` com exemplos, tradução de jargões (`Setup` -> `Implantação`, `MRR` -> `Mensalidade`, `PENDING_APPROVAL` -> `Aguardando Aprovação`, `ACCEPTED` -> `Aprovada & Fechada`), pipeline Kanban com etapas em português e estados vazios instrutivos; download **PDF Blob seguro** preservado sem token em URL. | [`page.tsx`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/frontend/src/app/page.tsx) |
| **F8. Resultados & IA** | Consolidação clara no `Início`, `Relatórios` visuais e histórico transparente em `Visão & Agentes` diferenciando execuções reais de bloqueios por cota/`FREE_ONLY`, com suporte completo ao Modo Claro WCAG (`globals.css`). | [`globals.css`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/frontend/src/app/globals.css) |

---

## 3. Hardening Adicional de Regressão (CI Backend)
- Adicionado `os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "2000")` no cabeçalho de teste em [`backend/tests/test_union_growth_os.py`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/backend/tests/test_union_growth_os.py#L14) para impedir falsos `HTTP 429` causados pela velocidade de execução em SSD Linux do GitHub Actions (>180 chamadas em <60s), **sem alterar a proteção real de `180/min` em produção** nem enfraquecer testes de brute-force (`test_24`).
