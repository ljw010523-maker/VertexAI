"""
보안 필터링 서비스

이 파일이 하는 일:
1. PII (개인정보) 감지 및 마스킹
   - 이메일 주소
   - 전화번호 (한국 형식)
   - 주민등록번호
   - 카드번호
2. 금지 키워드 차단
3. 민감한 정보 로깅 방지
"""

import re
from typing import Tuple, List
from dataclasses import dataclass


# ========================================
# 필터링 결과 데이터 클래스
# ========================================
@dataclass
class FilterResult:
    """
    필터링 결과

    Attributes:
    - is_filtered: 필터링 여부 (True면 차단)
    - masked_text: 마스킹된 텍스트
    - detected_items: 감지된 항목 목록
    - reason: 필터링 이유
    """
    is_filtered: bool
    masked_text: str
    detected_items: List[str]
    reason: str = ""


# ========================================
# 정규표현식 패턴 정의
# ========================================
class Patterns:
    """PII 감지용 정규표현식 패턴"""

    # 이메일 (example@domain.com)
    EMAIL = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )

    # 전화번호 (한국)
    # 예: 010-1234-5678, 01012345678, 02-123-4567
    PHONE = re.compile(
        r'\b(?:010|011|016|017|018|019)-?\d{3,4}-?\d{4}\b|'  # 휴대폰
        r'\b0\d{1,2}-?\d{3,4}-?\d{4}\b'  # 일반전화
    )

    # 주민등록번호 (123456-1234567 또는 1234561234567)
    SSN = re.compile(
        r'\b\d{6}-?\d{7}\b'
    )

    # 카드번호 (1234-5678-9012-3456 또는 16자리 연속)
    CARD = re.compile(
        r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
    )

    # IP 주소 (192.168.0.1)
    IP_ADDRESS = re.compile(
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    )


# ========================================
# 금지 키워드 리스트
# ========================================
BLOCKED_KEYWORDS = [
    # 악성 키워드
    "해킹",
    "크랙",
    "불법",
    "도용",

    # 민감한 시스템 정보 (예시)
    "관리자 비밀번호",
    "DB 접속정보",
    "API 키",

    # 회사별로 추가 가능
    # "경쟁사 기밀",
    # "내부 자료",
]


# ========================================
# 보안 필터 클래스
# ========================================
class SecurityFilter:
    """보안 필터링 처리 클래스"""

    def __init__(self):
        """초기화"""
        self.blocked_keywords = BLOCKED_KEYWORDS


    def filter_message(self, text: str) -> FilterResult:
        """
        메시지 필터링 (메인 함수)

        Parameters:
        - text: 검사할 텍스트

        Returns:
        - FilterResult: 필터링 결과
        """
        detected_items = []

        # ========================================
        # 1. 금지 키워드 체크
        # ========================================
        for keyword in self.blocked_keywords:
            if keyword.lower() in text.lower():
                return FilterResult(
                    is_filtered=True,
                    masked_text=text,
                    detected_items=[keyword],
                    reason=f"금지된 키워드가 포함되어 있습니다: {keyword}"
                )


        # ========================================
        # 2. PII 감지 및 마스킹
        # ========================================
        masked_text = text

        # 이메일 마스킹
        emails = Patterns.EMAIL.findall(text)
        if emails:
            detected_items.extend([f"이메일: {email}" for email in emails])
            masked_text = Patterns.EMAIL.sub("[이메일]", masked_text)

        # 전화번호 마스킹
        phones = Patterns.PHONE.findall(text)
        if phones:
            detected_items.extend([f"전화번호: {phone}" for phone in phones])
            masked_text = Patterns.PHONE.sub("[전화번호]", masked_text)

        # 주민등록번호 마스킹
        ssns = Patterns.SSN.findall(text)
        if ssns:
            detected_items.extend([f"주민번호: {ssn}" for ssn in ssns])
            masked_text = Patterns.SSN.sub("[주민번호]", masked_text)

        # 카드번호 마스킹
        cards = Patterns.CARD.findall(text)
        if cards:
            detected_items.extend([f"카드번호: {card}" for card in cards])
            masked_text = Patterns.CARD.sub("[카드번호]", masked_text)

        # IP 주소 마스킹 (선택적)
        ips = Patterns.IP_ADDRESS.findall(text)
        if ips:
            detected_items.extend([f"IP주소: {ip}" for ip in ips])
            masked_text = Patterns.IP_ADDRESS.sub("[IP주소]", masked_text)


        # ========================================
        # 3. 결과 반환
        # ========================================
        if detected_items:
            return FilterResult(
                is_filtered=False,  # PII는 마스킹만 하고 차단하지 않음
                masked_text=masked_text,
                detected_items=detected_items,
                reason=f"개인정보 {len(detected_items)}건 마스킹됨"
            )
        else:
            return FilterResult(
                is_filtered=False,
                masked_text=text,
                detected_items=[],
                reason=""
            )


    def add_blocked_keyword(self, keyword: str):
        """금지 키워드 추가"""
        if keyword not in self.blocked_keywords:
            self.blocked_keywords.append(keyword)
            print(f"[OK] 금지 키워드 추가: {keyword}")


    def remove_blocked_keyword(self, keyword: str):
        """금지 키워드 제거"""
        if keyword in self.blocked_keywords:
            self.blocked_keywords.remove(keyword)
            print(f"[OK] 금지 키워드 제거: {keyword}")


# ========================================
# 전역 필터 인스턴스
# ========================================
security_filter = SecurityFilter()


# ========================================
# 테스트 함수
# ========================================
def test_filter():
    """필터링 테스트"""
    test_messages = [
        "안녕하세요, 이메일은 test@example.com입니다.",
        "전화번호는 010-1234-5678이에요.",
        "주민번호 123456-1234567 알려드립니다.",
        "카드번호는 1234-5678-9012-3456입니다.",
        "해킹 방법을 알려주세요.",
        "IP는 192.168.0.1입니다.",
        "안전한 메시지입니다.",
    ]

    print("=" * 50)
    print("[보안 필터링 테스트]")
    print("=" * 50)

    for msg in test_messages:
        result = security_filter.filter_message(msg)
        print(f"\n원본: {msg}")
        print(f"필터링: {result.is_filtered}")
        print(f"마스킹: {result.masked_text}")
        if result.detected_items:
            print(f"감지: {', '.join(result.detected_items)}")
        if result.reason:
            print(f"이유: {result.reason}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    test_filter()
