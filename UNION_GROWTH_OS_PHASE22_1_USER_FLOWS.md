# FASE 22.1 — AUDITORIA & VALIDAÇÃO DOS 8 FLUXOS PRINCIPAIS DE USUÁRIO

**Ambiente Testado**: Produção (`https://automacao.projetosunion.cloud`)  
**Tenant Isolado de Teste**: `QA_AUTOMATED_TENANT` (Tenant 1 real `UNION GROWTH OS` 100% preservado)  
**Executor**: Chrome Headless via CDP ([`scripts/phase22_1_usability_flows.py`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/scripts/phase22_1_usability_flows.py))  
**Fontes Brutas**: [`phase22_1_flows_before.json`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/phase22_1_flows_before.json) | [`phase22_1_flows_after.json`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/after/phase22_1_flows_after.json)

---

## Quadro Comparativo Geral (ANTES vs. DEPOIS)

| Fluxo | Perfil Principal | Etapas (Antes → Depois) | Cliques (Antes → Depois) | Tempo ms (Antes → Depois) | Status Antes | Status Depois |
|---|---:|---:|---:|---:|---|---|
| **F1. Configurar empresa e marca** | Iniciante | `2 → 3` | `2 → 5` (salvamento real) | `1897.8 → 4077.4` | **FAIL** | **PASS** |
| **F2. Configurar agentes** | Avançado / Iniciante | `3 → 3` | `2 → 3` | `1872.8 → 4103.1` | **PARTIAL** | **PASS** |
| **F3. Conectar integrações** | Intermediário | `3 → 3` | `3 → 3` | `3415.4 → 2917.1` | **PARTIAL** | **PASS** |
| **F4. Criar campanha** | Iniciante | `4 → 4` | `4 → 4` | `4892.8 → 4391.5` | **FAIL** | **PASS** |
| **F5. Criar conteúdo** | Iniciante | `3 → 3` | `2 → 2` | `3626.7 → 3471.2` | **FAIL** | **PASS** |
| **F6. Capturar e acompanhar lead** | Intermediário | `6 → 6` | `3 → 3` | `5410.1 → 6435.4` | **FAIL** | **PASS** |
| **F7. Criar proposta e acompanhar venda** | Intermediário / Diretor | `5 → 5` | `2 → 2` | `4454.2 → 3166.8` | **FAIL** | **PASS** |
| **F8. Consultar resultados e execuções da IA** | Todos | `3 → 3` | `3 → 3` | `2662.8 → 6243.7` | **PASS** | **PASS** |

---

## Detalhamento Fluxo a Fluxo

### Fluxo 1 — Configurar empresa e marca (`Gestão -> Configurações & Planos`)
- **Etapas**: `3` (`Gestão` -> `Configurações & Planos` -> preencher e salvar formulário **"1. Identidade da Empresa & Marca Ativa"**).
- **Dificuldades ANTES**: `hasBrandField: false`, `hasNicheField: false`, `hasContextGuide: false`, `inputsCount: 1`, `brand_saved: false`. Usuário iniciante não tinha nenhum campo para editar a empresa ativa.
- **Resultado DEPOIS**: `hasBrandField: true`, `hasNicheField: true`, `hasContextGuide: true`, `inputsCount: 6`, `brand_saved: true` via `PUT /api/v1/tenants/current`.
- **Evidências**: [Antes](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/01_fluxo1_empresa_marca.png) | [Depois](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/after/01_fluxo1_empresa_marca.png)

### Fluxo 2 — Configurar agentes (`Inteligência Artificial -> Visão & Agentes`)
- **Etapas**: `3` (`Inteligência Artificial` -> `Visão & Agentes` -> percorrer Assistente Guiado de Configuração de IA / verificar dependência de credencial e botão de rotina segura).
- **Dificuldades ANTES**: `hasWizard: false`, `hasCredentialDependencyPerAgent: false`, `hasSafeTestButton: false`.
- **Resultado DEPOIS**: `hasWizard: true`, `hasCredentialDependencyPerAgent: true`, `hasPlainLanguageExplain: true`, `hasSafeTestButton: true`, `exposesJargonByDefault: false`. Bloqueios reais por cota (`HTTP 402`) e política `FREE_ONLY` continuam exibidos com honestidade.
- **Evidências**: [Antes](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/02_fluxo2_configurar_agentes.png) | [Depois](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/after/02_fluxo2_configurar_agentes.png)

### Fluxo 3 — Conectar integrações (`Gestão -> Integrações`)
- **Etapas**: `3` (`Gestão` -> `Integrações` -> inspecionar campos separados do GA4 e testar conexão real).
- **Dificuldades ANTES**: `gaInputs: 1` (um único campo para duas credenciais), `hasRawEnum: true` (`PENDING_CREDENTIALS`), `hasFriendlyStatus: false`, `hasHumanEmptyFallbackExplain: false`.
- **Resultado DEPOIS**: `gaInputs: 2` (campos separados rotulados), `hasHumanEmptyFallbackExplain: true` (**Modo Assistido** explicado em card próprio), `hasFriendlyStatus: true`, `hasRawEnum: false`, `honest_test_response: true`, tempo reduzido de `3415.4 ms` para `2917.1 ms`.
- **Evidências**: [Antes](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/03_fluxo3_integracoes.png) | [Depois](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/after/03_fluxo3_integracoes.png)

### Fluxo 4 — Criar campanha (`Marketing -> Campanhas & Personas`)
- **Etapas**: `4` (`Marketing` -> `Campanhas & Personas` -> validar feedback vazio -> selecionar canal e preencher `#ug-camp-name-input` -> confirmar persistência em tela).
- **Dificuldades ANTES**: `empty_validation_feedback: false` (retorno silencioso), `has_channel_selector: false`, `camp_persisted: false`.
- **Resultado DEPOIS**: `empty_validation_feedback: true` (alerta orientativo visível), `has_channel_selector: true` (`#ug-camp-channel-select`), `camp_persisted: true` com tempo reduzido de `4892.8 ms` para `4391.5 ms`.
- **Evidências**: [Antes](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/04_fluxo4_criar_campanha.png) | [Depois](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/after/04_fluxo4_criar_campanha.png)

### Fluxo 5 — Criar conteúdo (`Marketing -> Calendário & Redes` + `Fábrica de Conteúdo`)
- **Etapas**: `3` (`Calendário & Redes` -> preencher `#ug-cal-title-input` -> clicar em `Agendar no Calendário` e verificar persistência).
- **Dificuldades ANTES**: `post_persisted: false` por ausência de `<label>`/`id` claro e falta de validação orientativa.
- **Resultado DEPOIS**: `post_persisted: true` em `3471.2 ms` (`2` cliques), rótulos completos, exemplos reais nos campos e atalho direto para a Fábrica de 30 peças.
- **Evidências**: [Antes](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/05_fluxo5_criar_conteudo.png) | [Depois](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/after/05_fluxo5_criar_conteudo.png)

### Fluxo 6 — Capturar e acompanhar lead (`Comercial -> Leads & CRM`)
- **Etapas**: `6` (`Comercial` -> `Leads & CRM` -> preencher nome/empresa/valor/LGPD -> cadastrar -> pesquisar no filtro real do CRM).
- **Dificuldades ANTES**: `lead_persisted: false` e **bug real** no filtro do CRM (`lead_found_in_crm_search: false`, pois filtrava `l.name`/`l.company`/`l.status` em vez de `full_name`/`company_name`/`qualification_status`).
- **Resultado DEPOIS**: `lead_persisted: true` (`POST /api/v1/crm/leads 201 Created` confirmado nos logs do servidor) e `lead_found_in_crm_search: true`.
- **Evidências**: [Antes](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/06_fluxo6_capturar_lead_crm.png) | [Depois](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/after/06_fluxo6_capturar_lead_crm.png)

### Fluxo 7 — Criar proposta e acompanhar venda (`Comercial -> Propostas, Contratos & 3 Unidades`)
- **Etapas**: `5` (`Comercial` -> `Propostas` -> guia de 4 etapas -> preencher título/empresa -> gerar proposta -> acompanhar no funil comercial).
- **Dificuldades ANTES**: `prop_created: false`, jargões técnicos (`Setup`, `MRR`, `PENDING_APPROVAL`) sem explicação.
- **Resultado DEPOIS**: `prop_created: true` (`POST /api/v1/commercial/proposals 201 Created` confirmado nos logs), tradução completa para linguagem de negócio (`Implantação`, `Mensalidade`, `Aguardando Aprovação`, etapas do funil em português), tempo reduzido de `4454.2 ms` para `3166.8 ms`.
- **Evidências**: [Antes](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/07_fluxo7_proposta_venda.png) | [Depois](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/after/07_fluxo7_proposta_venda.png)

### Fluxo 8 — Consultar resultados e execuções da IA (`Início` + `Inteligência Artificial` + `Gestão -> Relatórios`)
- **Etapas**: `3` (`Início` com orientações contextuais -> `Inteligência Artificial` -> `Gestão / Relatórios`).
- **Resultado DEPOIS**: `hasContextGuide: true`, `showsResults: true`, `showsAIActivity: true`, `has_reports: true`, `status: PASS`.
- **Evidências**: [Antes](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/08_fluxo8_resultados_e_ia.png) | [Depois](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/after/08_fluxo8_resultados_e_ia.png)
