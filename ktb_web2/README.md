FastAPI	파이썬으로 개발함
파이썬 기반의 고성능 비동기 웹 프레임워크로, REST API 개발에 적합
pyproject.toml	Python 프로젝트의 의존성과 설정을 통합 관리하는 표준 설정 파일
Gunicorn	fastapi 운영
Python 웹 애플리케이션을 실제 서버 환경에서 실행시키는 WSGI 서버
HTTP Message	클라이언트와 서버가 주고받는 메세지
클라이언트와 서버 간 요청(Request)과 응답(Response)을 담는 메시지 구조
HTTP Request Method	서버에 요청의 의도를 알리는 방식 (GET, POST, PUT, DELETE 등)
HTTP Status Code	상태 코드 (200 : 성공,,,)
요청 처리 결과를 숫자로 표현한 코드 (200 OK, 404 Not Found 등)
HTTP URL	인터넷 자원의 위치를 나타내는 주소
Query string	url 뒷부분에 key, value
URL 끝에 ?key=value 형식으로 데이터를 전달하는 문자열
Path Variable	URL 경로 중 일부를 변수로 사용하여 데이터 전달 (/users/{id} 등)
JSON	데이터 형식
데이터를 구조적으로 표현하는 경량 포맷 (JavaScript Object Notation)
REST API	자원을 HTTP 방식으로 주고받는 규칙 기반의 API 설계 방식
디자인패턴	반복되는 문제를 해결하기 위한 소프트웨어 설계의 일반화된 해법
Database	데이터 저장, 관리
데이터를 체계적으로 저장하고 관리하는 시스템
SQL	데이터베이스 관리 언어
관계형 데이터베이스를 조작하기 위한 표준 언어
데이터 정의어	테이블 구조를 생성·변경·삭제하는 명령어 (CREATE, ALTER 등)
데이터 조작어	데이터 삽입·조회·수정·삭제를 수행하는 명령어 (INSERT, SELECT 등)
데이터 제어어	데이터 접근 권한이나 트랜잭션을 제어하는 명령어 (GRANT, COMMIT 등)
JOIN	여러 테이블을 공통 컬럼으로 연결하여 데이터를 조회하는 연산
정규화	데이터를 규칙있게 정리해서 중복을 줄임
암호화	중요한 데이터를 숨김
bcrypt	비밀번호를 암호화해서 저장하는 방식
stateful	서버가 누가 누구인지 상태를 기억
stateless	서버가 누가 누구인지를 기억하지 않음
connectionless	요청할때만 잠깐 연결
인증·인가	인증 : 누구인가? 인가 : 권한이 있는 사람인가?
쿠키	브라우저가 잠깐 저장하는 작은 정보
세션	사용자 로그인 정보
프레임워크	개발 구조, 뼈대
라이브러리	도구 모음
API	프로그램끼리 연결하는 도구
페이징	데이터가 많을 때 페이지를 나눔
HTTPS	더 안전한 HTTP
댓글 필터링	욕설/혐오 댓글 차단용 AI
POST /comments	{ "content": "댓글 내용", "post_id": 1(optional) } 형태로 호출
Ollama 모델	기본 모델은 llama3, 환경변수 OLLAMA_MODERATION_MODEL로 변경 가능
필요 환경	Ollama가 로컬에서 실행 중이어야 하며 기본 주소는 http://localhost:11434
