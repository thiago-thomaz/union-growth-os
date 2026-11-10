# Manual de Operações (OPERATIONS.md) — UNION GROWTH OS

## 1. Credenciais Executivas Iniciais

- **E-mail**: `admin@projetosunion.cloud`
- **Senha**: `UnionGrowth#2026!`
- **Papel**: `owner` (Acesso total multi-tenant e governança)

---

## 2. Níveis de Autonomia Operacional

O administrador pode configurar o nível de autonomia em **Configurações & Planos** (`PUT /api/v1/tenants/current`):

- **NÍVEL 1 — ASSISTIDO**: Os 11 agentes analisam, diagnosticam e geram recomendações; o usuário executa todas as ações.
- **NÍVEL 2 — SEMIAUTÔNOMO (Padrão)**: A IA prepara campanhas, artigos, copies, artes e calendário, solicitando aprovação humana na aba **Aprovações** antes de publicações externas ou gastos financeiros.
- **NÍVEL 3 — AUTÔNOMO**: A IA executa automaticamente as rotinas previamente autorizadas dentro dos limites de governança.

---

## 3. Operação da Central de Automações (APScheduler Python)

O agendador nativo roda dentro do servidor em nuvem, independente do computador local estar ligado:
- **07:00**: Pesquisa diária de tendências e oportunidades de conteúdo (`AGENT_04_SOCIAL`).
- **08:00**: Geração automática do **CEO DAILY BRIEFING** (`AGENT_01_CEO`).
- **08:30**: Verificação e qualificação de leads novos (`AGENT_08_SALES`).
- **19:00**: Análise diária de publicações e métricas (`AGENT_04_SOCIAL`).
- **Semanal**: Auditoria SEO (`AGENT_03_SEO`), Concorrentes (`AGENT_09_COMPETITIVE`) e ROI de Campanhas (`AGENT_02_CMO`).
- **Mensal**: Planejamento estratégico mensal (`AGENT_02_CMO`).
- **Tempo Real (Eventos)**: Qualificação imediata ao receber lead no CRM (`lead.created`), retry com backoff exponencial em falha de publicação (`publication.failed`), alerta de queda de indicador (`kpi.drop_detected`) e relatório de meta atingida (`goal.achieved`).

---

## 4. Como Ativar Cada Integração Externa

Acesse o menu **18. Integrações** no Painel Executivo. Para cada uma das 16 plataformas:
1. Verifique a lista de **Credenciais Necessárias** e o link **Onde Obter**.
2. Conceda os **Escopos Oficiais** listados no painel do provedor (Google Cloud, Meta for Developers, TikTok Developers, LinkedIn Developers, Pinterest, Mercado Pago ou SMTP).
3. Insira as credenciais (que serão criptografadas com **Fernet AES-128-CBC + HMAC-SHA256**) e clique em **Testar Conexão**.

