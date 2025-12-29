/**
 * 메인 채팅 페이지 (개선 버전)
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import MessageComponent from '@/components/Message';
import ChatInput from '@/components/ChatInput';
import SettingsPanel from '@/components/SettingsPanel';
import AiLogo from '@/components/AiLogo';
import { sendMessage } from '@/lib/api';
import type { Message, ChatSettings } from '@/types/chat';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [latestMessageId, setLatestMessageId] = useState<string | null>(null);

  const [settings, setSettings] = useState<ChatSettings>({
    userId: 'user123',
    useContext: true,
    contextLimit: 10,
    typingSpeed: 30,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 메시지 목록 끝으로 스크롤
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 메시지 전송 핸들러
  const handleSendMessage = async (content: string) => {
    // 사용자 메시지 추가
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 백엔드 API 호출
      const response = await sendMessage(
        settings.userId,
        content,
        settings.useContext,
        settings.contextLimit
      );

      // AI 응답 추가
      const aiMessageId = (Date.now() + 1).toString();
      const aiMessage: Message = {
        id: aiMessageId,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setLatestMessageId(aiMessageId); // 최신 메시지에만 타이핑 효과 적용
    } catch (error) {
      console.error('메시지 전송 실패:', error);

      // 에러 메시지 추가
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '죄송합니다. 메시지 전송에 실패했습니다. 백엔드 서버가 실행 중인지 확인해주세요.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // 대화 초기화
  const handleClearChat = () => {
    if (confirm('대화를 초기화하시겠습니까?')) {
      setMessages([]);
      setLatestMessageId(null);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-gray-100">
      {/* 헤더 */}
      <header className="bg-white shadow-md px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center text-white shadow-lg">
            <AiLogo className="w-9 h-9 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-800">Vertex AI</h1>
            <p className="text-xs text-gray-500">
              {settings.useContext
                ? `컨텍스트 ${settings.contextLimit}개 활성화`
                : '컨텍스트 비활성화'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleClearChat}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="대화 초기화"
          >
            🗑️ 초기화
          </button>
          <button
            onClick={() => setIsSettingsOpen(true)}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
            title="설정"
          >
            ⚙️ 설정
          </button>
        </div>
      </header>

      {/* 메시지 목록 */}
      <main className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-6xl mb-4">💬</div>
                <p className="text-xl text-gray-600 mb-2">
                  안녕하세요! 무엇을 도와드릴까요?
                </p>
                <p className="text-sm text-gray-400">
                  아래에 메시지를 입력해주세요.
                </p>
                <div className="mt-6 flex flex-wrap gap-2 justify-center">
                  <button
                    onClick={() => handleSendMessage('아침 추천')}
                    className="px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-shadow text-sm text-gray-700"
                  >
                    아침 추천
                  </button>
                  <button
                    onClick={() => handleSendMessage('점심 추천')}
                    className="px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-shadow text-sm text-gray-700"
                  >
                    점심 추천
                  </button>
                  <button
                    onClick={() => handleSendMessage('저녁 추천')}
                    className="px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-shadow text-sm text-gray-700"
                  >
                    저녁 추천
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <MessageComponent
                  key={message.id}
                  message={message}
                  typingSpeed={settings.typingSpeed}
                  showTypingEffect={message.id === latestMessageId}
                />
              ))}
              {isLoading && (
                <div className="flex justify-start mb-4 animate-fadeIn">
                  <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-md">
                    <div className="flex gap-2 items-center">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-100"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-200"></div>
                      <span className="text-sm text-gray-500 ml-2">
                        AI가 생각 중...
                      </span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </main>

      {/* 입력창 */}
      <div className="border-t bg-white shadow-lg">
        <div className="max-w-4xl mx-auto">
          <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </div>
      </div>

      {/* 설정 패널 */}
      <SettingsPanel
        settings={settings}
        onSettingsChange={setSettings}
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
}
