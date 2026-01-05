"""
RAG (Retrieval-Augmented Generation) 서비스
LangChain + Chroma + Gemini Embeddings 사용
"""

import os
from typing import List, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.utils.config import settings


class RAGService:
    """문서 기반 검색 증강 생성 서비스"""

    def __init__(self):
        """RAG 서비스 초기화"""
        self.embeddings = None
        self.vectorstore = None
        self.is_initialized = False

        # 설정
        self.persist_directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "chroma_db"
        )
        self.chunk_size = 512
        self.chunk_overlap = 50

    def initialize(self):
        """임베딩 모델 및 벡터 DB 초기화"""
        if self.is_initialized:
            return

        try:
            # Gemini 임베딩 모델 (100+ 언어 지원)
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=settings.GEMINI_API_KEY
            )

            # Chroma 벡터 DB
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )

            self.is_initialized = True
            print(f"[OK] RAG 서비스 초기화 완료 (DB: {self.persist_directory})")

        except Exception as e:
            print(f"[ERROR] RAG 서비스 초기화 실패: {e}")
            self.is_initialized = False

    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None):
        """
        문서 추가 (자동으로 청크 분할)

        Args:
            texts: 문서 텍스트 리스트
            metadatas: 문서 메타데이터 (파일명, 날짜 등)
        """
        if not self.is_initialized:
            self.initialize()

        # 텍스트 분할기 (긴 문서를 작은 청크로)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # Document 객체 생성
        documents = [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(texts, metadatas or [{}] * len(texts))
        ]

        # 청크 분할
        chunks = text_splitter.split_documents(documents)

        # 벡터 DB에 추가
        self.vectorstore.add_documents(chunks)

        print(f"[OK] {len(texts)}개 문서를 {len(chunks)}개 청크로 분할하여 추가")

    def search(self, query: str, k: int = 3) -> List[str]:
        """
        의미 기반 검색 (다국어 지원)

        Args:
            query: 검색 질문 (한국어, 영어, 혼용 모두 가능)
            k: 반환할 문서 개수

        Returns:
            관련 문서 텍스트 리스트
        """
        if not self.is_initialized:
            self.initialize()

        if not self.vectorstore:
            return []

        try:
            # 유사도 검색
            docs = self.vectorstore.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            print(f"[ERROR] 검색 실패: {e}")
            return []

    def search_with_scores(self, query: str, k: int = 3) -> List[tuple]:
        """
        유사도 점수와 함께 검색

        Returns:
            (문서 텍스트, 유사도 점수) 튜플 리스트
        """
        if not self.is_initialized:
            self.initialize()

        if not self.vectorstore:
            return []

        try:
            docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=k)
            return [(doc.page_content, score) for doc, score in docs_with_scores]
        except Exception as e:
            print(f"[ERROR] 검색 실패: {e}")
            return []

    def clear_database(self):
        """벡터 DB 초기화 (모든 문서 삭제)"""
        if self.is_initialized and self.vectorstore:
            self.vectorstore.delete_collection()
            print("[OK] 벡터 DB 초기화 완료")

    def get_document_count(self) -> int:
        """저장된 문서 청크 개수"""
        if not self.is_initialized or not self.vectorstore:
            return 0

        try:
            return self.vectorstore._collection.count()
        except:
            return 0


# 싱글톤 인스턴스
rag_service = RAGService()
