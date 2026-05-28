import teamEn from '@/Content/Team/members.en.json';
import teamZh from '@/Content/Team/members.zh.json';

export interface TeamMember {
  id: string;
  order: number;
  name: string;
  role: string;
  image: string;
  highlight: string;
  bio: string[];
}

export function getTeamMembers(locale: string): TeamMember[] {
  const members = locale === 'zh' ? teamZh : teamEn;
  return [...members].sort((a, b) => a.order - b.order);
}
