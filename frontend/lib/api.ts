/**
 * 백엔드 API 호출 함수
 */

import type { ChatRequest, ChatResponse } from '@/types/chat';

// 백엔드 API 주소
const API_BASE_URL = 'http://localhost:8000';

/**
 * 채팅 메시지 전송
 */
export async function sendMessage(
  userId: string,
  message: string,
  useContext: boolean = true,
  contextLimit: number = 10
): Promise<ChatResponse> {
  const requestData: ChatRequest = {
    user_id: userId,
    message: message,
    use_context: useContext,
    context_limit: contextLimit,
  };

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestData),
  });

  if (!response.ok) {
    throw new Error(`API 호출 실패: ${response.status}`);
  }

  const data: ChatResponse = await response.json();
  return data;
}

/**
 * 채팅 기록 조회
 */
export async function getChatHistory(
  userId: string,
  limit: number = 10
): Promise<any> {
  const response = await fetch(
    `${API_BASE_URL}/api/chat/history/${userId}?limit=${limit}`
  );

  if (!response.ok) {
    throw new Error(`기록 조회 실패: ${response.status}`);
  }

  return await response.json();
}

/**
 * 채팅 기록 삭제
 */
export async function deleteChatLog(logId: number): Promise<any> {
  const response = await fetch(
    `${API_BASE_URL}/api/chat/history/${logId}`,
    {
      method: 'DELETE',
    }
  );

  if (!response.ok) {
    throw new Error(`기록 삭제 실패: ${response.status}`);
  }

  return await response.json();
}

/**
 * 파일 업로드 (RAG 문서 추가)
 */
export async function uploadFiles(files: File[]): Promise<any> {
  const formData = new FormData();

  // 여러 파일을 동일한 필드명으로 추가
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await fetch(`${API_BASE_URL}/api/documents/upload-file`, {
    method: 'POST',
    body: formData,
    // Content-Type을 명시하지 않으면 브라우저가 자동으로 multipart/form-data로 설정
  });

  if (!response.ok) {
    throw new Error(`파일 업로드 실패: ${response.status}`);
  }

  return await response.json();
}
