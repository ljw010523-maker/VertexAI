/**
 * 채팅 관련 타입 정의
 * 백엔드 API와 통신하는 데이터 구조
 */

// 백엔드로 보낼 채팅 요청
export interface ChatRequest {
  user_id: string;
  message: string;
  use_context?: boolean;
  context_limit?: number;
}

// 백엔드에서 받는 채팅 응답
export interface ChatResponse {
  response: string;
  filtered: boolean;
  log_id: number;
  timestamp: string;
}

// 화면에 표시할 메시지
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// 채팅 설정
export interface ChatSettings {
  userId: string;
  useContext: boolean;
  contextLimit: number;
  typingSpeed: number;
}
