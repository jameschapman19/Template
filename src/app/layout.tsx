import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from '@/theme';
import ResponsiveAppBar from '@/components/Header';
import Footer from '@/components/Footer';
import Copyright from '@/components/Copyright';
const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Base App",
  description: "Starter template for Next.js apps",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
      <ThemeProvider theme={theme}>
        {/* CssBaseline kickstart an elegant, consistent, and simple baseline to build upon. */}
        <CssBaseline />
          <ResponsiveAppBar/>
        {children}
          <Footer/>
          {/*<Copyright/>*/}
      </ThemeProvider>
      </body>
    </html>
  );
}
