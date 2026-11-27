export type UIMode = "SIMPLE" | "ADVANCED";

/**
 * Seleciona linguagem acessível para empreendedores (Modo Simples) ou técnica detalhada (Modo Avançado).
 */
export function uiCopy(mode: UIMode, simpleText: string, advancedText: string): string {
  return mode === "SIMPLE" ? simpleText : advancedText;
}

const SIMPLE_TERM_REPLACEMENTS: [RegExp, string][] = [
  [/\bWebhook\b/gi, "Conectar ferramenta externa"],
  [/\bWebhooks\b/gi, "Conexões externas"],
  [/\bRate limit\b/gi, "Limite de solicitações"],
  [/\bProvider\b/gi, "Serviço de IA"],
  [/\bProviders\b/gi, "Serviços de IA"],
  [/\bTrigger\b/gi, "Quando essa automação deve começar"],
  [/\bDry-Run\b/gi, "Simular antes de ativar"],
  [/\bPayload\b/gi, "Dados enviados"],
];

/**
 * Traduz termos técnicos pontuais em textos informativos quando em Modo Simples,
 * mantendo exatamente o significado real sem simplificação enganosa.
 */
export function simplifyTechnicalText(text: string, mode: UIMode): string {
  if (!text || mode === "ADVANCED") return text;
  let out = text;
  for (const [pattern, replacement] of SIMPLE_TERM_REPLACEMENTS) {
    out = out.replace(pattern, replacement);
  }
  return out;
}
