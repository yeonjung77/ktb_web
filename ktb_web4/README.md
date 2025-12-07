# 카카오부트캠프 개인프로젝트

##### 프로젝트 제목 : AI 패션 인사이트 커뮤니티

FastAPI로 만든 커뮤니티 백엔드와 패션 리서치용 Chat & Report을 구현한 프로젝트입니다.
로컬 LLM(Ollama)으로 댓글 욕설 필터와 패션 리포트 기반 질의응답을 처리합니다.

## 1. 폴더 구조 (간단 버전)

```text
ktb_web4/
├── BE/                # 백엔드 (FastAPI, 모델, 라우터 등)
│   ├── controllers/
│   ├── routes/
│   ├── models/
│   ├── faiss_index/
│   ├── database.py
│   ├── schemas.py
│   └── sof_langchain.py
├── FE/                # 프론트엔드 (HTML/JS)
│   └── static/
├── main.py            # FastAPI 엔트리포인트 (BE/FE 모두 연결)
├── requirements.txt
└── 기타 테스트/엑셀 파일 등
```

## 2. 설치

```bash
cd ktb_web4
pip install -r requirements.txt
```

```bash
ollama pull llama3
```

## 3. 서버 실행

```bash
uvicorn main:app --reload
```

- 접속: `http://localhost:8000/`
  - 로그인/회원가입, 게시글 목록/상세, 댓글 작성, Chat & Report 화면 사용 가능
- API 문서:
  - Swagger: `http://localhost:8000/docs`

## 4. 기본 사용 흐름

1. 브라우저에서 `http://localhost:8000/` 접속
2. 회원가입 후 로그인 (기본 계정도 제공)
3. 게시글 목록에서:
   - 새 게시글 작성, 상세 조회, 댓글 작성/수정/삭제 가능
4. `Chat & Report` 버튼:
   - SoF 리포트 기반 패션 Q&A 및 대화 요약 리포트 생성

---

## 주요 기능

- 회원 관리
  - 회원가입 (`POST /auth/signup`)
  - 로그인 (`POST /auth/login`)
  - 프로필 수정 (`PUT /profile/update`)
  - 비밀번호 변경 (`PUT /password/update`)
  - 회원 탈퇴 (`DELETE /profile/delete`)
- 게시글
  - 게시글 목록 조회 (`GET /posts`)
  - 게시글 상세 조회 (`GET /posts/{post_id}`)
  - 게시글 작성 (`POST /posts/create`)
  - 게시글 수정 (`PUT /posts/{post_id}/edit`)
- 댓글 및 AI 필터링
  - 게시글별 댓글 CRUD 엔드포인트 (작성/수정 시 Ollama 기반 욕설/혐오 발언 필터 적용)
  - 일반 댓글 API (`POST /comments`) 에서도 Ollama 기반 욕설/혐오 발언 필터 적용
- 패션 리서치 챗봇 (ChatReport)
  - SoF(State of Fashion) 2021–2025 리포트 기반 질의응답 (`POST /chat_report/chat`)
  - 대화 이력으로부터 인사이트 리포트 생성 (`POST /chat_report/report`)
- 테스트 케이스
  - `testcases.xlsx`

## 환경 요구사항

- Python 3.10 이상 (PEP 604 `|` 타입 힌트 사용)
- pip (또는 uv / pipx 등)
- (권장) 가상환경 도구: `venv` 또는 `conda`
- 로컬 LLM 실행용:
  - [Ollama](https://ollama.com/) 설치 (macOS / Windows / Linux)
  - LLM 모델 : `llama3`


### 내부 LLM 연동 구조

- 패션 리서치 챗봇 및 리포트
  - 구현 파일: `sof_langchain.py`
  - FAISS + BM25로 SoF 문서를 검색한 뒤, 검색된 문맥과 함께 Ollama `/api/chat` 엔드포인트에 요청을 보냅니다.
  - 환경변수:
    - `OLLAMA_HOST` : Ollama 서버 주소 (기본 `http://localhost:11434`)
    - `SOF_LLM_MODEL` : 챗봇/리포트에 사용할 모델 (`llama3`)

- 댓글 욕설/혐오 발언 필터
  - 구현 파일: `models/comment_model.py`
  - Ollama `/api/generate` 엔드포인트에 간단한 프롬프트를 보내 `ALLOW` / `BLOCK` 결정을 받습니다.
  - 환경변수:
    - `OLLAMA_HOST` : 동일하게 사용
    - `OLLAMA_MODERATION_MODEL` : 필터용 모델 (`llama3`)


## 폴더 구조 개요

```text
ktb_web4/
├── BE/                          # 백엔드 (FastAPI, 도메인/AI 로직)
│   ├── controllers/             # 비즈니스 로직 (Controller 계층)
│   ├── routes/                  # FastAPI 라우터 정의
│   ├── models/                  # 도메인/AI/유저 관련 모델
│   ├── faiss_index/             # SoF 벡터 인덱스
│   ├── database.py              # (필요 시) DB 설정
│   ├── schemas.py               # 공용 Pydantic 스키마
│   └── sof_langchain.py         # SoF 리서치용 벡터 검색 + Ollama 연동
├── FE/
│   └── static/                  # 프론트엔드 정적 파일 (HTML/JS/CSS)
├── main.py                      # FastAPI 엔트리포인트 (BE + FE 연결)
├── requirements.txt             # Python 의존성 목록
└── testcases_ktb_web4.csv       # 수동 테스트 케이스 정리
```
