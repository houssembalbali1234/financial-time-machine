import type { Metadata } from "next";
import { Bricolage_Grotesque, IBM_Plex_Sans } from "next/font/google";
import "./globals.css";

// Titres : une grotesque expressive. Texte : IBM Plex Sans, qui existe aussi en arabe.
const bricolage = Bricolage_Grotesque({
  variable: "--font-bricolage",
  subsets: ["latin"],
});

const plex = IBM_Plex_Sans({
  variable: "--font-plex",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Financial Time Machine",
  description: "Voyez l'effet de vos décisions financières avant de les prendre.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="fr" className={`${bricolage.variable} ${plex.variable} h-full antialiased`}>
      <body className="min-h-full">{children}</body>
    </html>
  );
}