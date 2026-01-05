"""
문서 관리 API 엔드포인트 (RAG용)

이 파일이 하는 일:
1. POST /api/documents/upload - 텍스트를 벡터 DB에 추가
2. POST /api/documents/upload-file - 파일을 업로드하여 벡터 DB에 추가
3. GET /api/documents/count - 저장된 문서 개수 확인
4. DELETE /api/documents/clear - 벡터 DB 초기화
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.rag_service import rag_service
from app.utils.file_parser import FileParser


# ========================================
# APIRouter 생성
# ========================================
router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# ========================================
# 요청/응답 모델
# ========================================
class DocumentUploadRequest(BaseModel):
    """문서 업로드 요청"""

    texts: List[str] = Field(
        ...,
        description="추가할 문서 텍스트 리스트",
        examples=[["회사 정책: 연차는 입사일 기준으로 부여됩니다."]],
    )

    metadatas: Optional[List[dict]] = Field(
        default=None,
        description="각 문서의 메타데이터 (파일명, 날짜 등)",
        examples=[[{"source": "company_policy.txt", "date": "2024-01-01"}]],
    )

    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "회사 정책: 연차는 입사일 기준으로 부여됩니다.",
                    "근무 시간: 오전 9시 ~ 오후 6시",
                ],
                "metadatas": [
                    {"source": "hr_policy.txt"},
                    {"source": "work_hours.txt"},
                ],
            }
        }


class DocumentUploadResponse(BaseModel):
    """문서 업로드 응답"""

    success: bool = Field(..., description="업로드 성공 여부")
    message: str = Field(..., description="결과 메시지")
    document_count: int = Field(..., description="현재 저장된 총 문서 개수")


class DocumentCountResponse(BaseModel):
    """문서 개수 응답"""

    count: int = Field(..., description="저장된 문서 청크 개수")
    message: str


# ========================================
# 문서 업로드 엔드포인트
# ========================================
@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    summary="문서 업로드",
    description="텍스트 문서를 벡터 DB에 추가합니다. (다국어 지원)",
)
async def upload_documents(request: DocumentUploadRequest):
    """
    문서를 벡터 DB에 추가

    - 긴 문서는 자동으로 500자 청크로 분할됨
    - 한국어, 영어, 베트남어 등 100+ 언어 지원
    - 검색 시 언어가 달라도 의미 기반으로 검색 가능
    """
    try:
        # RAG 서비스 초기화
        if not rag_service.is_initialized:
            rag_service.initialize()

        if not rag_service.is_initialized:
            raise HTTPException(
                status_code=500, detail="RAG 서비스 초기화에 실패했습니다."
            )

        # 문서 추가
        rag_service.add_documents(
            texts=request.texts, metadatas=request.metadatas
        )

        # 현재 저장된 문서 개수
        doc_count = rag_service.get_document_count()

        return DocumentUploadResponse(
            success=True,
            message=f"{len(request.texts)}개의 문서가 추가되었습니다.",
            document_count=doc_count,
        )

    except Exception as e:
        print(f"[ERROR] 문서 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"문서 업로드 실패: {str(e)}")


# ========================================
# 문서 개수 조회 엔드포인트
# ========================================
@router.get(
    "/count",
    response_model=DocumentCountResponse,
    summary="문서 개수 조회",
    description="벡터 DB에 저장된 문서 청크 개수를 반환합니다.",
)
async def get_document_count():
    """저장된 문서 청크 개수 조회"""
    try:
        # RAG 서비스 초기화
        if not rag_service.is_initialized:
            rag_service.initialize()

        count = rag_service.get_document_count()

        return DocumentCountResponse(
            count=count, message=f"현재 {count}개의 문서 청크가 저장되어 있습니다."
        )

    except Exception as e:
        print(f"[ERROR] 문서 개수 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"문서 개수 조회 실패: {str(e)}")


# ========================================
# 벡터 DB 초기화 엔드포인트
# ========================================
@router.delete(
    "/clear",
    summary="벡터 DB 초기화",
    description="저장된 모든 문서를 삭제합니다. (주의: 복구 불가)",
)
async def clear_documents():
    """벡터 DB의 모든 문서 삭제"""
    try:
        if not rag_service.is_initialized:
            rag_service.initialize()

        rag_service.clear_database()

        return {"success": True, "message": "모든 문서가 삭제되었습니다."}

    except Exception as e:
        print(f"[ERROR] 벡터 DB 초기화 실패: {e}")
        raise HTTPException(status_code=500, detail=f"벡터 DB 초기화 실패: {str(e)}")


# ========================================
# 파일 업로드 엔드포인트
# ========================================
@router.post(
    "/upload-file",
    response_model=DocumentUploadResponse,
    summary="파일 업로드",
    description="PDF, Word, Excel 등의 파일을 업로드하여 벡터 DB에 추가합니다.",
)
async def upload_file(files: List[UploadFile] = File(...)):
    """
    파일 업로드 및 벡터 DB 저장

    지원 형식:
    - PDF (.pdf)
    - Word (.docx, .doc)
    - Excel (.xlsx, .xls)
    - PowerPoint (.pptx, .ppt)
    - HTML (.html, .htm)
    - Text (.txt, .md, .csv)

    다국어 지원: 한국어, 영어, 베트남어 등 100+ 언어
    """
    try:
        # RAG 서비스 초기화
        if not rag_service.is_initialized:
            rag_service.initialize()

        if not rag_service.is_initialized:
            raise HTTPException(
                status_code=500, detail="RAG 서비스 초기화에 실패했습니다."
            )

        uploaded_files = []
        failed_files = []

        # 각 파일 처리
        for file in files:
            try:
                # 파일 내용 읽기
                file_content = await file.read()

                # 파일 파싱 (텍스트 추출)
                text = FileParser.parse_file(file.filename, file_content)

                if not text.strip():
                    failed_files.append(
                        {"filename": file.filename, "reason": "추출된 텍스트가 없습니다"}
                    )
                    continue

                # 벡터 DB에 추가
                metadata = {
                    "source": file.filename,
                    "content_type": file.content_type or "unknown",
                }

                rag_service.add_documents(texts=[text], metadatas=[metadata])

                uploaded_files.append(file.filename)
                print(f"[OK] 파일 업로드 성공: {file.filename}")

            except ValueError as e:
                # 파일 파싱 실패 (지원하지 않는 형식 등)
                failed_files.append({"filename": file.filename, "reason": str(e)})
                print(f"[ERROR] 파일 파싱 실패: {file.filename} - {e}")

            except Exception as e:
                # 기타 오류
                failed_files.append({"filename": file.filename, "reason": str(e)})
                print(f"[ERROR] 파일 처리 실패: {file.filename} - {e}")

        # 현재 저장된 문서 개수
        doc_count = rag_service.get_document_count()

        # 응답 메시지 생성
        if uploaded_files and not failed_files:
            message = f"{len(uploaded_files)}개 파일이 성공적으로 업로드되었습니다."
        elif uploaded_files and failed_files:
            message = f"{len(uploaded_files)}개 성공, {len(failed_files)}개 실패"
        else:
            message = f"모든 파일 업로드 실패 ({len(failed_files)}개)"

        response = DocumentUploadResponse(
            success=len(uploaded_files) > 0,
            message=message,
            document_count=doc_count,
        )

        # 실패한 파일 정보 추가
        if failed_files:
            response_dict = response.model_dump()
            response_dict["failed_files"] = failed_files
            return response_dict

        return response

    except Exception as e:
        print(f"[ERROR] 파일 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")
