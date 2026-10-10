// Original cartoon of Handsome Dan, Yale's bulldog mascot, used as the chat helper's avatar.
// Drawn as inline SVG so it stays crisp at any size and needs no image download.

import { useId } from 'react'

const NAVY = '#00356B'
const FUR = '#F4EEE3'
const SHADE = '#E3D5C0'
const PATCH = '#C9A27A'
const INK = '#2A2522'

export default function HandsomeDan({ size = 48, className }: { size?: number; className?: string }) {
  const clipId = useId() // unique per avatar, since several can be on the page at once
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 100 100"
      role="img"
      aria-label="Handsome Dan, the Yale bulldog"
    >
      <defs>
        <clipPath id={clipId}>
          <circle cx="50" cy="50" r="50" />
        </clipPath>
      </defs>
      <g clipPath={`url(#${clipId})`}>
        <rect width="100" height="100" fill={NAVY} />
        {/* sweater with a block Y */}
        <path d="M6 104 Q10 80 50 78 Q90 80 94 104 Z" fill="#0A4A8F" />
        <path d="M20 85 Q50 75 80 85" fill="none" stroke="#FFFFFF" strokeWidth="3" />
        <text x="50" y="96" textAnchor="middle" fontFamily="Georgia, serif" fontWeight="700" fontSize="12" fill="#FFFFFF">
          Y
        </text>
        {/* folded "rose" ears */}
        <path d="M27 25 Q12 18 9 34 Q16 30 24 35 Z" fill={PATCH} stroke={INK} strokeWidth="1.6" strokeLinejoin="round" />
        <path d="M73 25 Q88 18 91 34 Q84 30 76 35 Z" fill={PATCH} stroke={INK} strokeWidth="1.6" strokeLinejoin="round" />
        {/* broad head with heavy jowls hanging past the chin */}
        <path
          d="M50 19 C70 19 84 28 86 46 C88 58 88 68 82 76 C78 81 72 80 68 77 C62 81 56 82 50 82 C44 82 38 81 32 77 C28 80 22 81 18 76 C12 68 12 58 14 46 C16 28 30 19 50 19 Z"
          fill={FUR}
          stroke={INK}
          strokeWidth="1.8"
        />
        {/* eye patch */}
        <path d="M57 34 Q72 30 77 42 Q76 53 63 52 Q56 45 57 34 Z" fill={PATCH} opacity="0.85" />
        {/* brow wrinkles */}
        <path d="M36 28 Q50 23 64 28" fill="none" stroke={INK} strokeWidth="1.4" strokeLinecap="round" />
        <path d="M40 33 Q50 29 60 33" fill="none" stroke={INK} strokeWidth="1.2" strokeLinecap="round" />
        <path d="M46 38 Q50 36 54 38" fill="none" stroke={INK} strokeWidth="1.1" strokeLinecap="round" />
        {/* eyes, set wide */}
        <circle cx="35" cy="45" r="5" fill={INK} />
        <circle cx="66" cy="44" r="5" fill={INK} />
        <circle cx="36.6" cy="43.4" r="1.6" fill="#FFFFFF" />
        <circle cx="67.6" cy="42.4" r="1.6" fill="#FFFFFF" />
        {/* wide muzzle and flat nose */}
        <path d="M24 62 Q26 50 50 50 Q74 50 76 62 Q76 74 50 74 Q24 74 24 62 Z" fill={SHADE} />
        <path d="M41 53 Q50 49 59 53 Q60 58 50 60 Q40 58 41 53 Z" fill={INK} />
        <path d="M50 60 L50 64" stroke={INK} strokeWidth="1.4" strokeLinecap="round" />
        {/* droopy jowl line and underbite */}
        <path d="M27 63 Q38 72 50 64 Q62 72 73 63" fill="none" stroke={INK} strokeWidth="1.8" strokeLinecap="round" />
        <path d="M38 70 Q50 78 62 70 Q58 67 50 68 Q42 67 38 70 Z" fill="#B5544A" stroke={INK} strokeWidth="1.4" strokeLinejoin="round" />
        <path d="M41.5 70 L43.5 65.5 L45.5 70.8 Z M58.5 70 L56.5 65.5 L54.5 70.8 Z" fill="#FFFFFF" stroke={INK} strokeWidth="0.8" strokeLinejoin="round" />
        {/* cheek blush */}
        <circle cx="22" cy="58" r="3.6" fill="#F2B8A8" opacity="0.6" />
        <circle cx="78" cy="58" r="3.6" fill="#F2B8A8" opacity="0.6" />
      </g>
      <circle cx="50" cy="50" r="48.5" fill="none" stroke="#FFFFFF" strokeWidth="3" />
    </svg>
  )
}
