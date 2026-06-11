import teamEn from '@/Content/Team/members.en.json';
import teamMedia from '@/Content/Team/members.media.json';
import teamZh from '@/Content/Team/members.zh.json';

export interface TeamMemberAvatar {
  fit?: 'cover' | 'contain';
  scale?: number;
  position?: string;
  origin?: string;
  background?: string;
}

export interface TeamMember {
  id: string;
  order: number;
  name: string;
  role: string;
  image: string;
  avatar?: TeamMemberAvatar;
  highlight: string;
  bio: string[];
}

type LocalizedTeamMember = Omit<TeamMember, 'image' | 'avatar'>;
type TeamMemberMedia = Pick<TeamMember, 'id' | 'image' | 'avatar'>;

const teamMediaById = new Map(
  (teamMedia as TeamMemberMedia[]).map((member) => [member.id, member])
);

export function getTeamMembers(locale: string): TeamMember[] {
  const members = (locale === 'zh' ? teamZh : teamEn) as LocalizedTeamMember[];
  return members
    .map((member) => {
      const media = teamMediaById.get(member.id);

      if (!media) {
        throw new Error(`Missing team media for member: ${member.id}`);
      }

      return {
        ...member,
        image: media.image,
        avatar: media.avatar,
      };
    })
    .sort((a, b) => a.order - b.order);
}
