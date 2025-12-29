/**
 * 설정 패널 컴포넌트
 */

'use client';

import type { ChatSettings } from '@/types/chat';

interface SettingsPanelProps {
  settings: ChatSettings;
  onSettingsChange: (settings: ChatSettings) => void;
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsPanel({
  settings,
  onSettingsChange,
  isOpen,
  onClose,
}: SettingsPanelProps) {
  if (!isOpen) return null;

  return (
    <>
      {/* 배경 오버레이 */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* 설정 패널 */}
      <div className="fixed right-0 top-0 h-full w-80 bg-white shadow-lg z-50 p-6 overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">설정</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div className="space-y-6">
          {/* 사용자 ID */}
          <div>
            <label className="block text-sm font-medium mb-2">
              사용자 ID
            </label>
            <input
              type="text"
              value={settings.userId}
              onChange={(e) =>
                onSettingsChange({ ...settings, userId: e.target.value })
              }
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="user123"
            />
          </div>

          {/* 컨텍스트 사용 */}
          <div>
            <label className="flex items-center gap-2">
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
              <span className="text-sm font-medium">
                이전 대화 컨텍스트 사용
              </span>
            </label>
            <p className="text-xs text-gray-500 mt-1 ml-6">
              AI가 이전 대화를 기억합니다
            </p>
          </div>

          {/* 컨텍스트 개수 */}
          <div>
            <label className="block text-sm font-medium mb-2">
              컨텍스트 개수: {settings.contextLimit}
            </label>
            <input
              type="range"
              min="1"
              max="50"
              value={settings.contextLimit}
              onChange={(e) =>
                onSettingsChange({
                  ...settings,
                  contextLimit: parseInt(e.target.value),
                })
              }
              disabled={!settings.useContext}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1</span>
              <span>50</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              최근 {settings.contextLimit}개 대화를 기억
            </p>
          </div>

          {/* 타이핑 속도 */}
          <div>
            <label className="block text-sm font-medium mb-2">
              타이핑 속도
            </label>
            <select
              value={settings.typingSpeed}
              onChange={(e) =>
                onSettingsChange({
                  ...settings,
                  typingSpeed: parseInt(e.target.value),
                })
              }
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={10}>매우 빠름</option>
              <option value={20}>빠름</option>
              <option value={30}>보통</option>
              <option value={50}>느림</option>
              <option value={0}>타이핑 효과 없음</option>
            </select>
          </div>

          {/* 설명 */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium mb-2 text-sm">💡 도움말</h3>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• 컨텍스트를 사용하면 AI가 이전 대화를 기억합니다</li>
              <li>• 컨텍스트 개수를 늘리면 더 오래 기억합니다</li>
              <li>• 타이핑 속도는 AI 응답이 나타나는 속도입니다</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}
