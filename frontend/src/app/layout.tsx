import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "UNION GROWTH OS — Plataforma Autônoma de Crescimento Empresarial",
  description:
    "Workspace executivo de crescimento empresarial com IA, CRM, Marketing, SEO, Automações Python 24/7 e Analytics.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="min-h-screen ug-bg text-[var(--ug-text-primary)] antialiased">
        {children}
      </body>
    </html>
  );
}
