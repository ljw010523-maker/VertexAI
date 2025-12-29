/**
 * 개별 메시지 컴포넌트 (타이핑 효과 적용)
 */

'use client';

import type { Message } from '@/types/chat';
import { useTypingEffect } from '@/hooks/useTypingEffect';

interface MessageProps {
  message: Message;
  typingSpeed?: number;
  showTypingEffect?: boolean;
}

export default function MessageComponent({
  message,
  typingSpeed = 30,
  showTypingEffect = false,
}: MessageProps) {
  const isUser = message.role === 'user';
  const { displayedText, isTyping } = useTypingEffect(
    message.content,
    showTypingEffect && !isUser ? typingSpeed : 0
  );

  // 타이핑 효과 사용 여부에 따라 표시할 텍스트 결정
  const displayContent = showTypingEffect && !isUser ? displayedText : message.content;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fadeIn`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-3 shadow-md ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-white text-gray-900 border border-gray-200'
        }`}
      >
        <div className="text-xs font-semibold mb-2 opacity-70">
          {isUser ? '나' : '🤖 AI'}
        </div>
        <div className="whitespace-pre-wrap leading-relaxed">
          {displayContent}
          {isTyping && (
            <span className="inline-block w-2 h-4 ml-1 bg-gray-400 animate-pulse" />
          )}
        </div>
        <div className="text-xs mt-2 opacity-60">
          {message.timestamp.toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
}
