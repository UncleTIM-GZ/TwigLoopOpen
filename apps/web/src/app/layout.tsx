import type { Metadata } from "next";
import "./globals.css";
import { NavBar } from "@/components/nav-bar";
import { Footer } from "@/components/footer";
import { Providers } from "@/lib/providers";

export const metadata: Metadata = {
  title: "Twig Loop",
  description: "AI-native project collaboration platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" className="dark">
      <body className="antialiased bg-gray-950 text-gray-100">
        <Providers>
          <NavBar />
          <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
