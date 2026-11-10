import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "UNION GROWTH OS — AI Business & Marketing Director",
  description: "Central Autônoma de Inteligência Empresarial, Marketing, SEO, Social Media, Creative Studio, Copywriting, Growth e CRM.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="min-h-screen bg-[#070b14] text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}

