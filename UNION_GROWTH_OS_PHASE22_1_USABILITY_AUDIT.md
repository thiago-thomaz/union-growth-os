# FASE 22.1 — AUDITORIA REAL DE USABILIDADE & FRICÇÃO POR PERFIL DE USUÁRIO

**Sistema Auditado**: `UNION GROWTH OS` (`https://automacao.projetosunion.cloud`)  
**Ambiente de Teste Seguro**: Execuções de escrita realizadas exclusivamente no tenant isolado `QA_AUTOMATED_TENANT`, preservando intactos os dados reais do Tenant 1 (`UNION GROWTH OS`), sem pagamentos live, sem anúncios pagos e sem publicações externas automáticas reais (`FREE_ONLY` preservado).  
**Executor**: Chrome Headless via CDP ([`scripts/phase22_1_usability_flows.py`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/scripts/phase22_1_usability_flows.py))  
**Evidência Baseline (ANTES)**: [`phase22_1_flows_before.json`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/phase22_1_flows_before.json)

---

## 1. Perfis Simulados e Problemas Reais Encontrados (ANTES das Melhorias)

### Perfil 1 — Iniciante (não conhece o sistema)
- **O que trava o usuário hoje**:
  1. **Fluxo 1 (`Configurações & Planos` — FAIL)**: Ao clicar no passo *"Configure sua empresa"* / *"Configure sua marca e identidade"* do Onboarding no `Início`, a tela `Configurações & Planos` exibia apenas Autonomia, Planos SaaS e *"Criar Nova Empresa no Grupo"*. **Não existia formulário para editar Nome da Empresa, Nome da Marca, Domínio, Nicho ou Público-Alvo da empresa atual**, apesar do backend (`PUT /api/v1/tenants/current`) já suportar esses campos!
  2. **Envios silenciosos em formulários**: Em Campanhas (`Marketing`), Personas (`Marketing`), Calendário (`Calendário & Redes`), Leads (`CRM`) e Propostas (`Multinegócio`), clicar no botão de envio com campos obrigatórios vazios retornava sem nenhuma mensagem orientativa (`if (!campName) return;`), deixando o iniciante sem saber por que nada aconteceu.
  3. **Campos sem `<label>` visível**: Diversos campos dependiam apenas de `placeholder` (ao digitar ou quando já havia valor padrão como `"15000"` em Valor Estimado do Lead ou `"5000"` em Orçamento da Campanha, o usuário iniciante não sabia o significado do número).

### Perfil 2 — Intermediário (conhece gestão/marketing, não a plataforma)
- **O que trava o usuário hoje**:
  1. **BUG REAL na busca do CRM (`Comercial -> Leads & CRM` — FAIL)**: O campo `"Buscar lead por nome, empresa ou status..."` filtrava erroneamente por `l.name`, `l.company` e `l.status`, enquanto a API entrega `l.full_name`, `l.company_name` e `l.qualification_status`. Na prática, buscar qualquer lead por nome ou empresa zerava a lista!
  2. **Canal oculto em Nova Campanha (`Marketing -> Campanhas & Personas`)**: O envio usava um canal padrão fixo (`Organic SEO + LinkedIn`) sem exibir seletor de canal no formulário de criação.
  3. **Integrações multi-campo (`Gestão -> Integrações` — PARTIAL)**: Integrações que exigem 2 credenciais (ex.: `Google Analytics 4 (GA4)` pedindo `property_id` e `service_account_json_or_oauth_token`) renderizavam apenas **1 input genérico** que replicava o mesmo texto para as duas chaves. Além disso, o badge técnico `PENDING_CREDENTIALS` assustava o usuário sem explicar que o **Modo Assistido** continua funcionando normalmente.
  4. **Espaços vazios sem instrução**: Cartões sem dados (como Personas ICP em tenants novos) exibiam áreas vazias sem `EmptyState` explicativo.

### Perfil 3 — Avançado (usa automações e agentes de IA)
- **O que trava o usuário hoje**:
  1. **Configuração de IA sem assistente guiado direto em `Visão & Agentes` (`PARTIAL`)**: Para inserir ou testar uma chave do Gemini (`FREE_ONLY`), o usuário precisava navegar para `Modelos & Provedores -> 2. Provedores -> 10. Testes`, onde havia rótulos técnicos como `Classe: GeminiProvider`, `VERIFIED_FREE` e `text_generation`.
  2. **Falta de indicação de dependência de credencial por agente**: Cada card de agente precisava explicitar claramente se roda 100% nativo, se usa Gemini opcional ou se depende de OAuth para envio externo (Modo Assistido).

---

## 2. Resumo Quantitativo Observado no Baseline (`--mode before`)

| Fluxo | Resultado Antes | Cliques | Tempo (ms) | Achados Comprovados no Baseline |
|---|---:|---:|---:|---|
| **F1. Configurar empresa e marca** | **FAIL** | 2 | `1897.8` | Ausência total de campos de edição de empresa/marca/nicho na tela de Configurações |
| **F2. Configurar agentes** | **PARTIAL** | 2 | `1872.8` | Sem Assistente Guiado passo-a-passo nem badge de dependência de credencial por agente |
| **F3. Conectar integrações** | **PARTIAL** | 3 | `3415.4` | GA4 exibia `1` input único para `2` chaves; badge técnico `PENDING_CREDENTIALS`; sem nota de Modo Assistido |
| **F4. Criar campanha** | **FAIL** | 4 | `4892.8` | Validação vazia silenciosa (`empty_validation_feedback: false`), sem seletor de canal, input de filtro confundindo fluxo |
| **F5. Criar conteúdo** | **FAIL** | 2 | `3626.7` | Validação vazia silenciosa e ausência de atalho direto entre Post Individual e Fábrica de 30 peças |
| **F6. Capturar e acompanhar lead** | **FAIL** | 3 | `5410.1` | Busca do CRM retornando vazio por usar `l.name` ao invés de `l.full_name`; campo `"15000"` sem `<label>` |
| **F7. Criar proposta e venda** | **FAIL** | 2 | `4454.2` | Jargões `Setup`, `MRR`, `PENDING_APPROVAL`, validação silenciosa e ausência de guia de etapas |
| **F8. Consultar resultados e IA** | **PASS** | 3 | `2662.8` | Painel Início e Relatórios funcionais, porém beneficiados por Orientação Contextual unificada nas 6 áreas |

**Evidências Visuais BEFORE Salvas**: [`01_fluxo1_empresa_marca.png`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/01_fluxo1_empresa_marca.png), [`03_fluxo3_integracoes.png`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/03_fluxo3_integracoes.png), [`04_fluxo4_criar_campanha.png`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/04_fluxo4_criar_campanha.png), [`06_fluxo6_capturar_lead_crm.png`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/06_fluxo6_capturar_lead_crm.png), [`07_fluxo7_proposta_venda.png`](file:///c:/Users/Thiago%20Thomaz/OneDrive/Documentos/AntiGravity - Projetos/2027/Marketing Digital automático/union-growth-os/UNION_GROWTH_OS_PHASE22_1_EVIDENCE/before/07_fluxo7_proposta_venda.png).
