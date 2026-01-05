/**
 * 메인 채팅 페이지 (사이드바 중심 UI)
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import MessageComponent from '@/components/Message';
import ChatInput from '@/components/ChatInput';
import Sidebar from '@/components/Sidebar';
import AiLogo from '@/components/AiLogo';
import { sendMessage } from '@/lib/api';
import type { Message, ChatSettings } from '@/types/chat';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
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

  // 화면 크기에 따라 사이드바 자동 조절
  useEffect(() => {
    const handleResize = () => {
      // lg 이하 화면에서는 사이드바 닫기
      if (window.innerWidth < 1024) {
        setIsSidebarOpen(false);
      } else {
        setIsSidebarOpen(true);
      }
    };

    // 초기 실행
    handleResize();

    // 리사이즈 이벤트 리스너 추가
    window.addEventListener('resize', handleResize);

    // 클린업
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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
        content:
          '죄송합니다. 메시지 전송에 실패했습니다. 백엔드 서버가 실행 중인지 확인해주세요.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // 새 대화 시작
  const handleNewChat = () => {
    if (
      messages.length === 0 ||
      confirm('새 대화를 시작하시겠습니까? 현재 대화는 저장되지 않습니다.')
    ) {
      setMessages([]);
      setLatestMessageId(null);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      {/* 좌측 사이드바 */}
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        onNewChat={handleNewChat}
        userId={settings.userId}
        settings={settings}
        onSettingsChange={setSettings}
      />

      {/* 메인 채팅 영역 */}
      <div
        className={`flex-1 flex flex-col transition-all duration-300 ${
          isSidebarOpen ? 'ml-64' : 'ml-0 lg:ml-16'
        }`}
      >
        {/* 헤더 */}
        <header className="bg-white border-b px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            {/* 모바일 메뉴 버튼 */}
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden text-gray-600 hover:text-gray-800 p-2"
            >
              ☰
            </button>
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
        </header>

        {/* 메시지 목록 */}
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto h-full">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <p className="text-2xl text-gray-800 mb-3">

                    Hello! How can I help you?
                  </p>
                  <p className="text-sm text-gray-500">
                    아래에 메시지를 입력해주세요.
                  </p>
                  <div className="mt-6 flex flex-wrap gap-2 justify-center">
                    <button
                      onClick={() => handleSendMessage('오늘 날씨')}
                      className="px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-shadow text-sm text-gray-700"
                    >
                      오늘 날씨
                    </button>
                    <button
                      onClick={() =>
                        handleSendMessage('인기 급상승')
                      }
                      className="px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-shadow text-sm text-gray-700"
                    >
                      인기 급상승
                    </button>
                    <button
                      onClick={() => handleSendMessage('RAG가 뭐야?')}
                      className="px-4 py-2 bg-white rounded-lg shadow hover:shadow-md transition-shadow text-sm text-gray-700"
                    >
                      RAG 설명
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
      </div>
    </div>
  );
}
