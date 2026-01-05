/**
 * 좌측 사이드바 컴포넌트 (ChatGPT 스타일 - 모든 기능 통합)
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { uploadFiles, getChatHistory, deleteChatLog } from '@/lib/api';
import type { ChatSettings } from '@/types/chat';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onNewChat: () => void;
  userId: string;
  settings: ChatSettings;
  onSettingsChange: (settings: ChatSettings) => void;
}

interface HistoryItem {
  id: number;
  user_id: string;
  message: string;
  response: string;
  filtered: boolean;
  created_at: string;
}

type ActiveSection = 'none' | 'upload' | 'history' | 'settings';

export default function Sidebar({
  isOpen,
  onToggle,
  onNewChat,
  userId,
  settings,
  onSettingsChange,
}: SidebarProps) {
  const [activeSection, setActiveSection] = useState<ActiveSection>('none');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 섹션 토글
  const toggleSection = (section: ActiveSection) => {
    if (activeSection === section) {
      setActiveSection('none');
    } else {
      setActiveSection(section);
      if (section === 'history') {
        loadHistory();
      }
    }
  };

  // 히스토리 불러오기
  const loadHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const response = await getChatHistory(userId, 50);
      setHistory(response.history || []);
    } catch (err) {
      console.error('히스토리 로드 실패:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // 히스토리 삭제
  const handleDeleteHistory = async (logId: number) => {
    if (!confirm('이 채팅 기록을 삭제하시겠습니까?')) return;
    try {
      await deleteChatLog(logId);
      setHistory((prev) => prev.filter((item) => item.id !== logId));
    } catch (err) {
      console.error('삭제 실패:', err);
      alert('채팅 기록 삭제에 실패했습니다.');
    }
  };

  // 파일 선택
  const handleFileSelect = (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    const newFiles = Array.from(fileList);
    setSelectedFiles((prev) => [...prev, ...newFiles]);
    setUploadStatus('');
  };

  // 파일 업로드
  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    setUploadStatus('');

    try {
      const result = await uploadFiles(selectedFiles);
      setUploadStatus(
        `✅ ${selectedFiles.length}개 파일 업로드 완료! (총 ${result.document_count}개 문서)`
      );
      setSelectedFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('업로드 실패:', error);
      setUploadStatus('❌ 업로드 실패');
    } finally {
      setIsUploading(false);
    }
  };

  // 파일 제거
  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  // 파일 크기 포맷
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <>
      {/* 모바일 오버레이 (lg 화면 이상에서는 숨김) */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={onToggle}
          aria-hidden="true"
        />
      )}

      {/* 사이드바 */}
      <div
        className={`fixed top-0 left-0 h-full bg-gray-900 text-white z-40 transition-all duration-300 flex flex-col overflow-hidden ${
          isOpen ? 'w-64' : 'w-0 lg:w-16'
        }`}
      >
        {/* 헤더 */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          {isOpen ? (
            <>
              <h2 className="text-lg font-bold">Vertex AI</h2>
              <button
                onClick={onToggle}
                className="text-gray-400 hover:text-white p-1"
                title="사이드바 닫기"
              >
                ✕
              </button>
            </>
          ) : (
            <button
              onClick={onToggle}
              className="hidden lg:block text-gray-400 hover:text-white p-1 w-full"
              title="사이드바 열기"
            >
              ☰
            </button>
          )}
        </div>

        {/* 내용 (사이드바 열렸을 때만 표시) */}
        {isOpen && (
          <div className="flex-1 overflow-y-auto">
            {/* 새 대화 버튼 */}
            <div className="p-4 border-b border-gray-700">
              <button
                onClick={onNewChat}
                className="w-full px-4 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors flex items-center gap-3"
              >
                <span className="text-xl">➕</span>
                <span className="text-sm font-medium">새 대화</span>
              </button>
            </div>

            {/* 메뉴 버튼들 */}
            <div className="p-4 space-y-2">
              <button
                onClick={() => toggleSection('upload')}
                className={`w-full px-4 py-2 rounded-lg transition-colors flex items-center justify-between text-sm ${
                  activeSection === 'upload'
                    ? 'bg-gray-800 text-white'
                    : 'hover:bg-gray-800'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span>📁</span>
                  <span>문서 업로드</span>
                </div>
                <span className="text-xs">
                  {activeSection === 'upload' ? '▼' : '▶'}
                </span>
              </button>

              {/* 문서 업로드 섹션 */}
              {activeSection === 'upload' && (
                <div className="ml-4 mt-2 p-3 bg-gray-800 rounded-lg space-y-3 animate-fadeIn">
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    onChange={(e) => handleFileSelect(e.target.files)}
                    className="hidden"
                    id="sidebar-file-upload"
                  />
                  <label
                    htmlFor="sidebar-file-upload"
                    className="block w-full px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-center text-xs cursor-pointer transition-colors"
                  >
                    📎 파일 선택
                  </label>

                  {selectedFiles.length > 0 && (
                    <>
                      <div className="space-y-1 max-h-40 overflow-y-auto">
                        {selectedFiles.map((file, index) => (
                          <div
                            key={index}
                            className="bg-gray-700 rounded p-2 flex items-center justify-between text-xs"
                          >
                            <div className="flex-1 min-w-0 truncate">
                              {file.name}
                            </div>
                            <button
                              onClick={() => handleRemoveFile(index)}
                              className="text-red-400 hover:text-red-300 ml-2"
                            >
                              ✕
                            </button>
                          </div>
                        ))}
                      </div>
                      <button
                        onClick={handleUpload}
                        disabled={isUploading}
                        className="w-full px-3 py-2 bg-blue-600 hover:bg-blue-500 rounded text-xs font-medium disabled:opacity-50 transition-colors"
                      >
                        {isUploading ? '업로드 중...' : '업로드'}
                      </button>
                    </>
                  )}

                  {uploadStatus && (
                    <div className="text-xs text-gray-300 break-words">
                      {uploadStatus}
                    </div>
                  )}
                </div>
              )}

              <button
                onClick={() => toggleSection('history')}
                className={`w-full px-4 py-2 rounded-lg transition-colors flex items-center justify-between text-sm ${
                  activeSection === 'history'
                    ? 'bg-gray-800 text-white'
                    : 'hover:bg-gray-800'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span>📜</span>
                  <span>채팅 기록</span>
                </div>
                <span className="text-xs">
                  {activeSection === 'history' ? '▼' : '▶'}
                </span>
              </button>

              {/* 채팅 기록 섹션 */}
              {activeSection === 'history' && (
                <div className="ml-4 mt-2 p-3 bg-gray-800 rounded-lg animate-fadeIn max-h-96 overflow-y-auto">
                  {isLoadingHistory ? (
                    <div className="text-xs text-gray-400 text-center py-4">
                      로딩 중...
                    </div>
                  ) : history.length === 0 ? (
                    <div className="text-xs text-gray-400 text-center py-4">
                      저장된 채팅 기록이 없습니다
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {history.map((item) => (
                        <div
                          key={item.id}
                          className="bg-gray-700 rounded p-2 hover:bg-gray-600 transition-colors"
                        >
                          <div className="flex justify-between items-start mb-1">
                            <div className="text-xs font-medium text-gray-200 line-clamp-1 flex-1">
                              {item.message}
                            </div>
                            <button
                              onClick={() => handleDeleteHistory(item.id)}
                              className="text-red-400 hover:text-red-300 text-xs ml-2"
                              title="삭제"
                            >
                              🗑️
                            </button>
                          </div>
                          <div className="text-xs text-gray-400">
                            {new Date(item.created_at).toLocaleString('ko-KR', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <button
                onClick={() => toggleSection('settings')}
                className={`w-full px-4 py-2 rounded-lg transition-colors flex items-center justify-between text-sm ${
                  activeSection === 'settings'
                    ? 'bg-gray-800 text-white'
                    : 'hover:bg-gray-800'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span>⚙️</span>
                  <span>설정</span>
                </div>
                <span className="text-xs">
                  {activeSection === 'settings' ? '▼' : '▶'}
                </span>
              </button>

              {/* 설정 섹션 */}
              {activeSection === 'settings' && (
                <div className="ml-4 mt-2 p-3 bg-gray-800 rounded-lg space-y-4 animate-fadeIn">
                  {/* 사용자 ID */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">
                      사용자 ID
                    </label>
                    <input
                      type="text"
                      value={settings.userId}
                      onChange={(e) =>
                        onSettingsChange({ ...settings, userId: e.target.value })
                      }
                      className="w-full px-3 py-2 bg-gray-700 text-white rounded text-xs"
                    />
                  </div>

                  {/* 컨텍스트 사용 */}
                  <div className="flex items-center justify-between">
                    <label className="text-xs text-gray-400">
                      대화 컨텍스트
                    </label>
                    <input
                      type="checkbox"
                      checked={settings.useContext}
                      onChange={(e) =>
                        onSettingsChange({
                          ...settings,
                          useContext: e.target.checked,
                        })
                      }
                      className="w-4 h-4"
                    />
                  </div>

                  {/* 컨텍스트 개수 */}
                  {settings.useContext && (
                    <div>
                      <label className="block text-xs text-gray-400 mb-1">
                        컨텍스트 개수: {settings.contextLimit}
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="20"
                        value={settings.contextLimit}
                        onChange={(e) =>
                          onSettingsChange({
                            ...settings,
                            contextLimit: parseInt(e.target.value),
                          })
                        }
                        className="w-full"
                      />
                    </div>
                  )}

                  {/* 타이핑 속도 */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">
                      타이핑 속도: {settings.typingSpeed}ms
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      step="10"
                      value={settings.typingSpeed}
                      onChange={(e) =>
                        onSettingsChange({
                          ...settings,
                          typingSpeed: parseInt(e.target.value),
                        })
                      }
                      className="w-full"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      {settings.typingSpeed === 0
                        ? '타이핑 효과 없음'
                        : '타이핑 효과 있음'}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
