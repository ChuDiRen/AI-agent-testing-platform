import type { Metadata } from "next";
import "./globals.css";
import { Inter } from "next/font/google";
import React from "react";
import { NuqsAdapter } from "nuqs/adapters/next/app";
import { I18nProvider } from "@/contexts/I18nContext";

const inter = Inter({
  subsets: ["latin"],
  preload: true,
  display: "swap",
});

export const metadata: Metadata = {
  title: "AI 智能体聊天",
  description: "基于 LangChain 的 AI 智能体聊天界面",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <NuqsAdapter>
          <I18nProvider>{children}</I18nProvider>
        </NuqsAdapter>
      </body>
    </html>
  );
}
