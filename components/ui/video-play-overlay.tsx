'use client';

import Image from 'next/image';
import { Play } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VideoPlayOverlayProps {
  coverImageUrl?: string;
  coverAlt: string;
  ariaLabel: string;
  onClick: () => void;
  className?: string;
  imageSizes?: string;
}

export function VideoPlayOverlay({
  coverImageUrl,
  coverAlt,
  ariaLabel,
  onClick,
  className,
  imageSizes = '(max-width: 1024px) 100vw, 60vw',
}: VideoPlayOverlayProps) {
  return (
    <button
      type="button"
      className={cn(
        'group relative block w-full overflow-hidden bg-black text-left',
        className,
      )}
      onClick={onClick}
      aria-label={ariaLabel}
    >
      {coverImageUrl ? (
        <Image
          src={coverImageUrl}
          alt={coverAlt}
          fill
          sizes={imageSizes}
          className="object-cover transition-transform duration-500 ease-out group-hover:scale-[1.02]"
        />
      ) : (
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_20%,rgba(96,165,250,0.34),transparent_38%),radial-gradient(circle_at_82%_78%,rgba(59,130,246,0.2),transparent_42%),linear-gradient(135deg,#020617_0%,#0f172a_45%,#111827_100%)]" />
      )}

      <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(2,6,23,0.14)_0%,rgba(2,6,23,0.34)_52%,rgba(2,6,23,0.58)_100%)] transition-opacity duration-300 group-hover:opacity-90" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.05),transparent_40%)] opacity-55 transition-opacity duration-300 group-hover:opacity-75" />

      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative flex h-14 w-14 items-center justify-center rounded-full border border-white/28 bg-black/18 text-white/82 shadow-[0_10px_28px_rgba(2,6,23,0.28)] backdrop-blur-sm transition-all duration-300 group-hover:scale-[1.03] group-hover:border-white/42 group-hover:bg-black/24 group-hover:text-white/92">
          <div className="absolute inset-1 rounded-full border border-white/10" />
          <Play className="relative ml-0.5 h-5 w-5 fill-current" strokeWidth={1.8} />
        </div>
      </div>
    </button>
  );
}
