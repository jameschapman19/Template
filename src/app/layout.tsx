import type { Metadata } from "next";
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import theme from '@/components/ThemeRegistry/theme';
import ResponsiveAppBar from '@/components/Header';
import Footer from '@/components/Footer';
import meta from "@/content/metadata.json";

export const metadata: Metadata = {
  title: meta.title,
  description: meta.description,
};

export default function RootLayout(props: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
      <ThemeProvider theme={theme}>
        <CssBaseline />
          <ResponsiveAppBar/>
        {props.children}
          <Footer/>
      </ThemeProvider>
      </body>
    </html>
  );
}
