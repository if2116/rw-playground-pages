import type { Metadata } from 'next';
import { NextIntlClientProvider } from 'next-intl';
import { setRequestLocale } from 'next-intl/server';
import { Header, Footer } from '@/components/layout';
import { FloatingCTA } from '@/components/floating-cta';

export const dynamicParams = false;

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'zh' }];
}

export const metadata: Metadata = {
  title: 'RWAI Arena - Real-World AI Best Practices',
  description: 'Find the best AI solutions for your real-world business scenarios. Verified, open-source, production-ready.',
};

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const messages = (await import(`../../locales/${locale}.json`)).default;

  return (
    <NextIntlClientProvider locale={locale} messages={messages}>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
        <FloatingCTA locale={locale} />
      </div>
    </NextIntlClientProvider>
  );
}
