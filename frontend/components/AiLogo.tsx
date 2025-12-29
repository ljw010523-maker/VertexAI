/**
 * AI 로고 컴포넌트 (SVG)
 */

'use client';

interface AiLogoProps {
  className?: string;
}

export default function AiLogo({ className = '' }: AiLogoProps) {
  return (
    <svg
      className={className}
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* 배경 원 */}
      <circle cx="20" cy="20" r="20" fill="currentColor" fillOpacity="0.1" />

      {/* 중앙 다이아몬드 */}
      <path
        d="M20 8L26 14L20 20L14 14L20 8Z"
        fill="currentColor"
        fillOpacity="0.8"
      />

      {/* 하단 다이아몬드 */}
      <path
        d="M20 20L26 26L20 32L14 26L20 20Z"
        fill="currentColor"
        fillOpacity="0.6"
      />

      {/* 연결선 */}
      <line
        x1="20"
        y1="8"
        x2="20"
        y2="32"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeOpacity="0.4"
      />

      {/* 좌측 점 */}
      <circle cx="10" cy="20" r="2" fill="currentColor" fillOpacity="0.7" />

      {/* 우측 점 */}
      <circle cx="30" cy="20" r="2" fill="currentColor" fillOpacity="0.7" />

      {/* 좌측 연결선 */}
      <line
        x1="10"
        y1="20"
        x2="14"
        y2="20"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeOpacity="0.4"
      />

      {/* 우측 연결선 */}
      <line
        x1="26"
        y1="20"
        x2="30"
        y2="20"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeOpacity="0.4"
      />
    </svg>
  );
}
