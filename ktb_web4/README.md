# ktb_web4

FastAPI 기반 커뮤니티 백엔드와 패션 리서치용 챗봇(SoF 리포트 기반)을 구현한 학습용 프로젝트입니다.  
Route–Controller–Model 구조와 벡터 검색, 로컬 LLM(Ollama) 연동을 연습하는 데 초점을 두었습니다.

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
  - 게시글별 댓글 CRUD 엔드포인트
  - 일반 댓글 API (`POST /comments`) 에서 Ollama 기반 욕설/혐오 발언 필터 적용
- 패션 리서치 챗봇 (ChatReport)
  - SoF(State of Fashion) 2021–2025 리포트 기반 질의응답 (`POST /chat_report/chat`)
  - 대화 이력으로부터 인사이트 리포트 생성 (`POST /chat_report/report`)
- 테스트 케이스
  - `testcases_ktb_web4.csv`에 기능별 수동 테스트 케이스 정리

## 환경 요구사항

- Python 3.10 이상 (PEP 604 `|` 타입 힌트 사용)
- pip (또는 uv / pipx 등)
- (권장) 가상환경 도구: `venv` 또는 `conda`
- 로컬 LLM 실행용:
  - [Ollama](https://ollama.com/) 설치 (macOS / Windows / Linux)
  - SoF 리서치/댓글 필터링에 사용할 LLM 모델 (기본: `llama3`)

## 설치 및 의존성 설치

```bash
git clone <이 레포지토리 URL>
cd ktb_web4

# (선택) 가상환경 생성
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Python 패키지 설치
pip install -r requirements.txt
```

`requirements.txt`에는 FastAPI, LangChain 커뮤니티, FAISS, Sentence Transformers 등 이 프로젝트에 필요한 패키지가 정의되어 있습니다.

## 로컬 LLM(Ollama) 준비

이 프로젝트에서 사용하는 LLM은 클라우드 API(Groq 등)가 아니라 **로컬에서 실행되는 Ollama** 입니다.  
따라서 Python 패키지 설치만으로는 챗봇/리포트 기능이 동작하지 않으며, 아래 작업이 추가로 필요합니다.

1. Ollama 설치 및 실행
   - https://ollama.com/download 에서 OS에 맞는 Ollama를 설치 후 실행합니다.
   - 기본 설정에서는 `http://localhost:11434` 에서 API가 열립니다.

2. 사용할 모델 다운로드
   - 터미널에서 다음 명령을 실행합니다.
   - 기본값은 `llama3` 입니다.
   ```bash
   ollama pull llama3
   ```

3. `.env` (선택) 설정
   - 프로젝트 루트에 `.env` 파일을 만들고, 필요하다면 다음 값을 조정할 수 있습니다.
   ```bash
   # 패션 리서치/리포트용 LLM
   OLLAMA_HOST=http://localhost:11434
   SOF_LLM_MODEL=llama3

   # 댓글 욕설/혐오 발언 필터용 LLM (기본값도 llama3)
   OLLAMA_MODERATION_MODEL=llama3
   ```
   - 설정하지 않으면 위 값들이 기본값으로 사용됩니다.

### 내부 LLM 연동 구조

- 패션 리서치 챗봇 및 리포트
  - 구현 파일: `sof_langchain.py`
  - FAISS + BM25로 SoF 문서를 검색한 뒤, 검색된 문맥과 함께 Ollama `/api/chat` 엔드포인트에 요청을 보냅니다.
  - 환경변수:
    - `OLLAMA_HOST` : Ollama 서버 주소 (기본 `http://localhost:11434`)
    - `SOF_LLM_MODEL` : 챗봇/리포트에 사용할 모델 이름 (기본 `llama3`)

- 댓글 욕설/혐오 발언 필터
  - 구현 파일: `models/comment_model.py`
  - Ollama `/api/generate` 엔드포인트에 간단한 프롬프트를 보내 `ALLOW` / `BLOCK` 결정을 받습니다.
  - 환경변수:
    - `OLLAMA_HOST` : 동일하게 사용
    - `OLLAMA_MODERATION_MODEL` : 필터용 모델 이름 (기본 `llama3`)

Ollama가 실행 중이 아니거나 모델이 준비되지 않은 경우, 관련 엔드포인트는 5xx 계열 HTTP 오류와 함께 한국어 에러 메시지를 반환합니다.

## 서버 실행 방법

가상환경 및 패키지 설치, Ollama 준비가 끝났다면, 아래 명령으로 서버를 실행합니다.

```bash
uvicorn main:app --reload
```

- 기본 접속 URL: `http://localhost:8000/`
  - `GET /` : `static/index.html` 을 반환하며, 로그인 화면과 간단한 프론트엔드가 포함되어 있습니다.
- API 문서:
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

## 주요 엔드포인트 요약

### 인증 / 회원

- `POST /auth/signup` : 회원가입
- `POST /auth/login` : 로그인
- `PUT /profile/update` : 프로필 수정
- `DELETE /profile/delete` : 회원 탈퇴
- `PUT /password/update` : 비밀번호 변경

### 게시글 / 댓글

- `GET /posts` : 게시글 목록
- `GET /posts/{post_id}` : 게시글 상세
- `POST /posts/create` : 게시글 작성
- `PUT /posts/{post_id}/edit` : 게시글 수정
- `POST /posts/{post_id}/comments` : 특정 게시글에 댓글 작성
- `PUT /posts/{post_id}/comments/{comment_id}` : 댓글 수정
- `DELETE /posts/{post_id}/comments/{comment_id}` : 댓글 삭제
- `POST /comments` : 일반 댓글 작성 + Ollama 기반 욕설/혐오 발언 필터

### 패션 리서치 챗봇 (ChatReport)

- `POST /chat_report/chat`
  - Body 예시:
    ```json
    {
      "question": "2024년 글로벌 패션 소비 트렌드가 어떻게 변하고 있는지 알려줘"
    }
    ```
  - Response 예시:
    ```json
    {
      "answer": "..."
    }
    ```

- `POST /chat_report/report`
  - Body 예시:
    ```json
    {
      "history": [
        { "role": "user", "content": "럭셔리 시장 전망이 궁금해" },
        { "role": "assistant", "content": "..." }
      ]
    }
    ```
  - Response 예시:
    ```json
    {
      "report": "..."
    }
    ```

## 폴더 구조 개요

```text
ktb_web4/
├── main.py                # FastAPI 앱 엔트리포인트
├── database.py            # SQLite DB 설정
├── controllers/           # 비즈니스 로직 (Controller 계층)
├── routes/                # FastAPI 라우터 정의
├── models/                # 도메인/AI 관련 모델 (예: 댓글 필터링)
├── schemas.py             # 공용 Pydantic 스키마
├── sof_langchain.py       # SoF 리서치용 벡터 검색 + Ollama 연동
├── faiss_index/           # 미리 생성된 SoF 벡터 인덱스
├── static/                # 프론트엔드 정적 파일 (index.html 등)
├── requirements.txt       # Python 의존성 목록
└── testcases_ktb_web4.csv # 수동 테스트 케이스 정리
```

## 테스트

자동화된 테스트 코드는 포함되어 있지 않으며,  
`testcases_ktb_web4.csv`에 정의된 케이스를 기준으로 수동으로 API를 호출해 검증할 수 있습니다.

- 추천 도구:
  - Swagger UI (`/docs`), Postman, 혹은 VS Code REST Client

## 기타

- 이 프로젝트는 학습/연습용으로 작성되었으며, 실서비스에 적용할 경우
  - 인증/인가 (JWT 등)
  - DB 마이그레이션/스키마 관리
  - 로깅/모니터링
  - 비동기 작업 처리
  - 모델/프롬프트 보안 및 검증
  등을 추가로 고려해야 합니다.

