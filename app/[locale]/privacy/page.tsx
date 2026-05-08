export default async function PrivacyPolicyPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
  const termsHref = `${basePath}/${locale}/terms`;

  return (
    <div className="flex min-h-[40vh] items-center justify-center bg-white px-6 py-24 text-center">
      <meta httpEquiv="refresh" content={`0;url=${termsHref}`} />
      <div>
        <h1 className="mb-3 text-2xl font-semibold text-slate-900">
          {locale === 'zh' ? '服务条款已更新' : 'Terms of Service Updated'}
        </h1>
        <p className="mb-6 text-slate-600">
          {locale === 'zh'
            ? '隐私政策、服务使用规则和免责声明已合并到服务条款页面。'
            : 'The privacy policy, service usage rules, and disclaimers have been consolidated into the Terms of Service page.'}
        </p>
        <a className="font-medium text-primary hover:underline" href={termsHref}>
          {locale === 'zh' ? '前往服务条款' : 'Go to Terms of Service'}
        </a>
      </div>
    </div>
  );
}
