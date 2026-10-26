
import type { Metadata } from "next";
import "./globals.css";
import { LanguageProvider } from "@/components/LanguageProvider";
import ConnectionStatus from "@/components/ConnectionStatus";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "CivicLens",
  description:
    "Report civic issues in your city and track them until they are fixed.",
};
type RootLayoutProps = {
  children: ReactNode;
};
export default function RootLayout({
  children,
}: RootLayoutProps) {
  return (
    <html
      lang="en"
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col">
        <LanguageProvider><ConnectionStatus />{children}</LanguageProvider>
      </body>
    </html>
  );
}
