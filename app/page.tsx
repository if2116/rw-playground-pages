import { redirect } from 'next/navigation';

const basePath = process.env.NEXT_PUBLIC_BASE_PATH || process.env.NEXT_BASE_PATH || '';

export default function RootPage() {
  redirect(`${basePath}/zh`);
}
