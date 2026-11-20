# PHASE 19 — UNION AI ENGINE HUB REPORT
## Central Multimotor de Inteligência Artificial com Google Gemini Prioritário, Governança de Custos (`FREE_ONLY` & `OWNER_APPROVED`), AI Router, Image Studio e Video Studio

---

### 1. Auditoria Inicial
- **Repositório:** `https://github.com/thiago-thomaz/union-growth-os` (branch `main`)
- **Domínio Oficial de Produção:** `https://automacao.projetosunion.cloud`
- **Infraestrutura:** VPS `72.62.13.62`, Coolify (`swpy83sa5wshb558fadlrzwc`), Docker, PostgreSQL 16, FastAPI (Python 3.12), APScheduler (100% nativo, zero n8n) e Next.js 15.
- **Preservação Integral:** Todas as funcionalidades das Fases 1 a 18.1 (11 agentes + CRM Intelligence, 3 Unidades de Negócio, 5 Gavetas Financeiras Fase 18.1, 32 automações nativas, Content Factory 30D, Propostas, Contratos, Pagamentos e LGPD) foram preservadas sem reconstrução ou perda de dados.

---

### 2. Arquitetura do UNION AI ENGINE HUB
A Fase 19 implementa uma camada centralizada e multi-tenant de roteamento, governança, credenciais e execução de Inteligência Artificial (`backend/app/services/ai_engines_hub.py`), composta por:
1. **Abstração de Provedores Independentes (`BaseAIProvider`)**: Declaração explícita e individual das 7 capacidades (`text_generation`, `structured_generation`, `image_generation`, `image_analysis`, `video_generation`, `audio_generation`, `audio_transcription`).
2. **Central de Credenciais de IA (`AICredentialRecord`)**: Criptografia Fernet em repouso (`encrypt_secret` / `decrypt_secret`), mascaramento obrigatório (`mask_secret`), isolamento por `tenant_id` e zero exposição em logs, relatórios, frontend ou GitHub.
3. **AI Router (`AIRouter`)**: Seleção automática baseada em 10 critérios (preferência do proprietário, capacidade real do modelo, disponibilidade, cota conhecida, limite configurado, política de custo `FREE_ONLY` vs `OWNER_APPROVED`, latência, qualidade, restrição da tarefa e cadeia de fallback).
4. **Motor de Campanhas (`AICampaignPackageRecord`)**: Suporte a `GERAR CAMPANHA COMPLETA` (25 itens estruturados) e `GERAR PEÇA INDIVIDUAL` (`POST`, `IMAGE`, `VIDEO`, `COPY`, `EMAIL`, `ARTICLE`, `LANDING_PAGE`, `CAROUSEL`, `AD`, `SCRIPT`, `SEO`, `CTA`).
5. **AI Image Studio & AI Video Studio (`AIMediaGenerationRecord`)**: Verificação prévia obrigatória de suporte do modelo/API e separação estrita entre prompt/roteiro/storyboard e mídia efetivamente renderizada.

---

### 3. Provedores Implementados (`PROVIDER_CLASSES`)

| Provedor (`provider_key`) | Classe Python | Classificação Padrão | Status Inicial | Observações de Cota e Limitações |
| :--- | :--- | :--- | :--- | :--- |
| `gemini` | `GeminiProvider` | `VERIFIED_FREE` (Texto) / `PAID` (Imagen/Veo) | Prioritário Padrão | Cota gratuita oficial no Google AI Studio (15 RPM / 1.500 RPD) para modelos Flash de texto/multimodais. Imagen 3 e Veo 2 exigem billing pago. |
| `openai` | `OpenAIProvider` | `PAID` | Disponível | Exige créditos pré-pagos na OpenAI Platform. Não possui cota gratuita permanente. |
| `anthropic` | `AnthropicProvider` | `PAID` | Disponível | Exige créditos pagos no Anthropic Console. Suporta apenas texto, JSON e análise de imagem (não gera imagem/vídeo/áudio). |
| `groq` | `GroqProvider` | `VERIFIED_FREE` | Fallback Prioritário | Possui plano gratuito oficial no Groq Cloud (30 RPM / 14.400 RPD) para modelos de texto Llama 3.3. Não gera imagens ou vídeos. |
| `openrouter` | `OpenRouterProvider` | `VERIFIED_FREE` (sufixo `:free`) | Fallback Secundário | Gratuito apenas para modelos com sufixo `:free` (20 RPM / 200 RPD). Modelos sem `:free` são pagos. |
| `openai_compatible` | `GenericOpenAICompatibleProvider` | `UNKNOWN_COST` | Desativado até configurar URL | Exige endpoint Base URL explícito. Bloqueado em `FREE_ONLY` até declaração formal do proprietário. |

---

### 4. Modelos e Capacidades Declaradas Individualmente

| Modelo (`model_id`) | Provedor | Modalidade | `text_gen` | `struct_gen` | `image_gen` | `image_analysis` | `video_gen` | Classificação de Custo |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `gemini-2.5-flash` | `gemini` | `MULTIMODAL` | Sim | Sim | **Não** | Sim | **Não** | `VERIFIED_FREE` |
| `gemini-2.0-flash` | `gemini` | `MULTIMODAL` | Sim | Sim | **Não** | Sim | **Não** | `VERIFIED_FREE` |
| `gemini-1.5-flash` | `gemini` | `MULTIMODAL` | Sim | Sim | **Não** | Sim | **Não** | `VERIFIED_FREE` |
| `imagen-3.0-generate-002` | `gemini` | `IMAGE` | Não | Não | **Sim** | Não | Não | `PAID` (Requer Billing) |
| `veo-2.0-generate-001` | `gemini` | `VIDEO` | Não | Não | Não | Não | **Sim** | `PAID` (Requer Billing) |
| `gpt-4o-mini` | `openai` | `MULTIMODAL` | Sim | Sim | **Não** | Sim | **Não** | `PAID` |
| `gpt-4o` | `openai` | `MULTIMODAL` | Sim | Sim | **Não** | Sim | **Não** | `PAID` |
| `dall-e-3` | `openai` | `IMAGE` | Não | Não | **Sim** | Não | Não | `PAID` |
| `claude-3-7-sonnet-latest` | `anthropic` | `TEXT` | Sim | Sim | **Não** | Sim | **Não** | `PAID` |
| `llama-3.3-70b-versatile` | `groq` | `TEXT` | Sim | Sim | **Não** | Não | **Não** | `VERIFIED_FREE` |
| `google/gemini-2.0-flash-exp:free` | `openrouter` | `TEXT` | Sim | Sim | **Não** | Sim | **Não** | `VERIFIED_FREE` |
| `custom-openai-model` | `openai_compatible` | `TEXT` | Sim | Sim | **Não** | Não | **Não** | `UNKNOWN_COST` |

---

### 5. Integração Google Gemini, Geração de Texto, Imagens e Vídeo
- **Google Gemini (`GeminiProvider`)**: Conecta via interface oficial `https://generativelanguage.googleapis.com/v1beta`, suportando descoberta dinâmica de modelos (`GET /v1beta/models`), geração de texto (`generateContent`), geração estruturada JSON (`responseMimeType: "application/json"`), retry controlado com backoff exponencial para erros transitórios (`502/503/504`) e parada imediata em erros de autenticação/cota (`400/401/403/429`).
- **AI Image Studio**:
  - Separa `PROMPT_ONLY` (geração gratuita de prompt técnico detalhado via modelo de texto `gemini-2.5-flash`, com `image_generated: false`) de `GENERATE_IMAGE` (que exige modelo com capacidade real de `image_generation` como `imagen-3.0-generate-002` ou `dall-e-3`).
  - Bloqueia com `BLOCKED_CAPABILITY` qualquer tentativa de gerar imagem usando um modelo puramente textual.
  - Em modo `FREE_ONLY`, bloqueia `imagen-3.0-generate-002` e `dall-e-3` com `BLOCKED_FREE_ONLY`, informando claramente que esses modelos exigem faturamento ativo no provedor.
- **AI Video Studio**:
  - Separa estritamente `SCRIPT_ONLY`, `STORYBOARD_ONLY`, `PIPELINE_ASSEMBLED_VIDEO`, `RENDERED_VIDEO`, `PROVIDER_GENERATED_VIDEO` e `WAITING_PROCESSING`.
  - Quando gera roteiro e storyboard com `gemini-2.5-flash`, retorna `delivery_stage: "STORYBOARD_ONLY"` e `video_effectively_generated: false`, nunca declarando vídeo gerado quando apenas um roteiro foi produzido.

---

### 6. AI Router, Modos `FREE_ONLY` / `OWNER_APPROVED`, Fallback e Honestidade Estrita
- **Modo `FREE_ONLY` (Padrão)**: Somente permite modelos com `cost_tier == "VERIFIED_FREE"` ou expressamente autorizados pelo proprietário como gratuitos (`owner_permitted_free == True`). Motores `PAID` ou `UNKNOWN_COST` são bloqueados com `BLOCKED_FREE_ONLY`. Quando a cota gratuita se esgota, o sistema **jamais** migra para um motor pago sem autorização.
- **Modo `OWNER_APPROVED`**: Permite motores pagos somente quando autorizados pelo proprietário (`owner_approved_paid == True`) e dentro dos limites diários/mensais configurados.
- **Fallback Inteligente e Rastreável**: Se o provedor primário falhar temporariamente, o `AIRouter` consulta a cadeia de fallback (`["gemini", "groq", "openrouter"]`), valida capacidade, custo e limites de cada candidato, executa o fallback autorizado e grava um registro auditável em `ai_fallback_records` e `ai_engine_executions`.
- **Proibição de Simulação**: Se nenhum provedor real compatível/autorizado estiver disponível (ou se a API Key ainda não tiver sido inserida), o roteador retorna a falha real (`PENDING_API_KEY`, `BLOCKED_FREE_ONLY`, `BLOCKED_CAPABILITY`, `BLOCKED_LIMIT`), não gera cobranças e **não apresenta texto de template como se fosse resposta de LLM real**.

---

### 7. Banco de Dados e Migrations Compatíveis (PostgreSQL 16)
Foram adicionadas 7 novas tabelas multi-tenant em `backend/app/models/entities.py` criadas de forma não-destrutiva:
1. `ai_provider_records` (`AIProviderRecord`)
2. `ai_model_records` (`AIModelRecord`)
3. `ai_credential_records` (`AICredentialRecord`)
4. `ai_engine_configurations` (`AIEngineConfigurationRecord`)
5. `ai_engine_executions` (`AIEngineExecutionRecord`)
6. `ai_fallback_records` (`AIFallbackRecord`)
7. `ai_campaign_packages` (`AICampaignPackageRecord`) e `ai_media_generations` (`AIMediaGenerationRecord`)

---

### 8. Testes Automatizados (Unitários, Integração e Regressão)
- **Nota de Transparência sobre Mocks:** Na suíte automatizada (`test_43_phase19_union_ai_engine_hub_complete_suite` em `backend/tests/test_union_growth_os.py`), foram utilizados mocks controlados (`monkeypatch`) para testar a lógica de resposta da API Gemini e o fallback para Groq sem consumir cota externa durante o CI/CD. O teste real contra a API externa do Google Gemini em produção aguarda a inserção da chave `GEMINI_API_KEY` do proprietário na Central de Credenciais do menu `25 UNION AI ENGINE HUB`.
- **Cenários Testados e Aprovados:**
  - Overview inicial (`gemini` prioritário, `gemini-2.5-flash`, `FREE_ONLY`, 6 provedores, 12 agentes).
  - Credencial ausente/inválida (`INVALID_CREDENTIALS`), salvamento criptografado com Fernet e mascaramento.
  - Credencial válida e modelo inexistente (`MODEL_NOT_FOUND`) com mock de teste unitário.
  - Bloqueio de motores pagos (`openai:gpt-4o`, `anthropic:claude-3-7-sonnet-latest`) e custo desconhecido (`openai_compatible`) em `FREE_ONLY`.
  - Bloqueio de capacidade incompatível (`BLOCKED_CAPABILITY` ao pedir `image_generation` para modelo de texto).
  - Geração de texto, geração estruturada JSON, `GERAR CAMPANHA COMPLETA` (25 itens) e `GERAR PEÇA INDIVIDUAL`.
  - `AI IMAGE STUDIO` (`PROMPT_ONLY` com `image_generated=False` vs bloqueio de `Imagen 3` pago em `FREE_ONLY`).
  - `AI VIDEO STUDIO` (`STORYBOARD_ONLY` com `video_effectively_generated=False` vs bloqueio de `Veo 2` pago em `FREE_ONLY`).
  - Fallback inteligente (`Gemini -> Groq`) com persistência em `AIFallbackRecord`.
  - Bloqueio por limite configurável (`BLOCKED_LIMIT`) e separação de custos em `AI USAGE & COSTS`.

---

### 9. Credenciais Necessárias e Próximos Passos para o Proprietário
1. **Para ativar a geração real gratuita com Google Gemini em produção:**
   - Obtenha uma chave gratuita no Google AI Studio: `https://aistudio.google.com/apikey`
   - Acesse `https://automacao.projetosunion.cloud` → Menu **`25 🧠 UNION AI ENGINE HUB`** → Aba **`2. Provedores`** → Cole a chave no cartão **Google Gemini (Motor Prioritário)** e clique em **`CONFIGURAR GEMINI`** e depois em **`TESTAR MOTOR`**.
2. **Para ativar o fallback gratuito secundário (Groq Cloud):**
   - Obtenha uma chave gratuita em `https://console.groq.com/keys` e salve no cartão **Groq Cloud LPU**.
