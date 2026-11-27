# UNION GROWTH OS — FASE 26: MARKETING ENGINE

**Versão:** `2.3.0 — FASE 26`  

## 1. Arquitetura do Motor de Marketing (`MarketingAndSEOWorkspace.tsx`)
- **Campanhas & Personas**: definição de ICP, proposta de valor e campanhas multicanal com rastreio de orçamento planejado × gasto real × receita atribuída.
- **Fábrica de Conteúdo (30 Peças Contextuais/Lote)**: consome diretamente `brand_name`, `domain`, `niche`, `target_audience`, persona e campanha ativa. Inclui barra de **Contexto usado na criação dos conteúdos** e modal DS 4.0 **Pacote de Publicação Assistida (1 Clique)** para distribuir em qualquer canal sem OAuth conectado.
- **Estúdio Criativo Local (PNG Pillow) & Copywriter A/B**: gera artes reais localmente sem gasto de créditos pagos e variantes AIDA/PAS/BAB/FAB revisáveis antes de uso.
- **Centro de Crescimento (`GrowthExecutionCenter.tsx`)**: integra estratégia comercial em 4 horizontes (`Hoje`, `7d`, `30d`, `90d`) acionando geração de lote de conteúdo ou campanha sob governança de autonomia.
