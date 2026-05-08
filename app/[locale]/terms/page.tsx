import fs from 'node:fs/promises';
import path from 'node:path';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText } from 'lucide-react';
import { setRequestLocale } from 'next-intl/server';

export default async function TermsOfServicePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const isChina = locale === 'zh';
  const legalStatementPath = path.join(
    process.cwd(),
    'Content',
    'Legal',
    isChina ? 'legal-statement.zh.md' : 'legal-statement.en.md'
  );
  const legalStatement = await fs.readFile(legalStatementPath, 'utf8');

  return (
    <div className="w-full">
      <section className="relative overflow-hidden bg-slate-950 py-24 sm:py-32">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950" />
        <div className="absolute inset-0 opacity-40">
          <div className="absolute left-1/4 top-1/4 h-[600px] w-[600px] rounded-full bg-blue-600/20 blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 h-[500px] w-[500px] rounded-full bg-emerald-700/20 blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-6 inline-flex h-20 w-20 items-center justify-center rounded-full bg-blue-600/20">
              <FileText className="h-10 w-10 text-blue-400" />
            </div>
            <h1 className="mb-6 text-5xl font-bold tracking-normal text-white sm:text-6xl">
              {isChina ? '服务条款' : 'Terms of Service'}
            </h1>
            <p className="text-lg leading-relaxed text-slate-400">
              {isChina
                ? '欢迎使用 RWAI Arena。使用我们的服务即表示您同意以下条款、政策和声明。'
                : 'Welcome to RWAI Arena. By using our services, you agree to the following terms, policies, and statements.'}
            </p>
            <p className="mt-4 text-sm text-slate-500">
              {isChina ? '最后更新：2026年5月6日' : 'Last updated: May 6, 2026'}
            </p>
          </div>
        </div>
      </section>

      <section className="bg-white py-20 sm:py-24">
        <div className="mx-auto max-w-4xl px-6 lg:px-8">
          <article className="markdown-content legal-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{legalStatement}</ReactMarkdown>
          </article>
        </div>
      </section>

      <section className="border-t border-slate-200 bg-slate-50 py-12">
        <div className="mx-auto max-w-4xl px-6 text-center lg:px-8">
          <p className="mb-2 text-sm text-slate-600">
            {isChina ? '感谢您使用 RWAI Arena。' : 'Thank you for using RWAI Arena.'}
          </p>
          <p className="text-sm text-slate-500">
            {isChina
              ? '本条款最后更新于 2026年5月6日，并可能会不时更新。'
              : 'These terms were last updated on May 6, 2026, and may be updated from time to time.'}
          </p>
        </div>
      </section>
    </div>
  );
}
