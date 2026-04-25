import type { Metadata } from "next";
import { Inter, Syncopate } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const syncopate = Syncopate({ 
  weight: ['400', '700'], 
  subsets: ["latin"], 
  variable: "--font-syncopate" 
});

export const metadata: Metadata = {
  title: "Aventador Scrollytelling",
  description: "Interactive WebGL/Canvas Experience",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${syncopate.variable} antialiased font-inter`}>
        {children}
      </body>
    </html>
  );
}
