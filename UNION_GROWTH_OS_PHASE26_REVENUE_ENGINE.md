# UNION GROWTH OS — FASE 26: REVENUE ENGINE & CRM EVOLUTION

**Versão:** `2.3.0 — FASE 26`  

## 1. Fluxo Completo do Revenue Engine
1. **Captura & Qualificação LGPD (`POST /api/v1/crm/leads`)**: pontua lead automaticamente (`0–100`) e agenda primeiro contato comercial no CRM.
2. **CRM Revenue Intelligence (`GET /api/v1/growth-os/revenue-intelligence`)**: destaca leads quentes não contatados (`score >= 65`), negócios estagnados e taxa de conversão ponderada.
3. **Smart Follow-up Consultivo LGPD (`POST /api/v1/crm/leads/{lead_id}/smart-followup`)**:
   - Bloqueia imediatamente contatos marcados com **`opt_out`** (LGPD compliance obrigatório).
   - Gera rascunho consultivo contextualizado à empresa ativa e cria atividade `FOLLOW_UP`.
   - Sem canal conectado (`WhatsApp` / `SMTP`), retorna `PREPARED_MANUAL_COPY_NO_CHANNEL_CONNECTED` e exibe botão **Copiar Texto** na UI — **zero envio externo falso**.
   - Quando canal conectado, enfileira `ApprovalRequest` antes de qualquer disparo externo.
4. **Movimentação Inteligente no Pipeline (`POST /api/v1/crm/deals/{deal_id}/move-stage`)**:
   - Atualiza `stage` (`NEW_LEAD` → `QUALIFICATION` → `PROPOSAL` → `NEGOTIATION` → `CLOSED_WON` / `CLOSED_LOST`), transição automática de `status` (`OPEN`/`WON`/`LOST`) e recalcula `probability_pct` rotulando explicitamente `probability_origin: "ESTIMATED"` no Kanban DS 4.0 e API.
5. **Propostas Comerciais PDF & 3 Unidades (`MultiBusinessAndProposalsWorkspace.tsx`)**: mantém fluxo seguro via Blob URL e aprovação do proprietário.
