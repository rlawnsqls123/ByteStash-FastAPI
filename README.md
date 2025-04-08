
# ByteStash API - Docker Compose 기반 인프라 프로젝트

전체 구성은 인증된 사용자만 API 접근이 가능하고, UI를 통해 스니펫을 조회/관리할 수 있도록 설계됨.

---
# 주요 포인트
- /snippets 등 FastAPI 엔드포인트에는 X-API-Key 인증 필요 → Nginx에서 자동 주입
- 인증 실패 시 403 반환
- UI 상에서 계정 생성 및 Snippet 관리 가능

---
# 사용법
```
git clone https://github.com/your-id/ByteStashAPI.git
cd ByteStashAPI
docker-compose up --build -d
```
- API: http://localhost:8082/api/docs
- UI: http://localhost:5050
- Reverse Proxy (인증 자동): http://localhost:8081/api/docs
# 디렉토리 구조
```
ByteStashAPI/
├── api/                # FastAPI 서버
│   ├── main.py
│   ├── database.py
│   └── models.py
├── nginx/              # Nginx 프록시 설정
│   └── default.conf
├── .env                # API_KEY, DB_PATH 설정
├── docker-compose.yml  # 전체 서비스 정의
├── snippets.db         # SQLite DB (읽기 전용)
```
# 인증 및 보안
### Nginx 설정 (default.conf)
```
location /api/ {
  proxy_pass http://fastapi:8080/;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-API-Key "my-secret-api-key-1234";
}
```
### FastAPI .env
```
API_KEY=my-secret-api-key-1234
DB_PATH=file:./snippets.db?mode=ro
```
### 환경 변수 설정
- API_KEY : Nginx에서 주입되는 키와 동일해야 함
- DB_PATH: SQLite DB를 읽기 전용으로 마운트

### 명령어 모음
```
docker-compose logs -f nginx-proxy         # Nginx 로그 확인
docker-compose exec -it fastapi bash       # FastAPI 디버깅 접속
docker ps                                  # 컨테이너 상태 확인
```
# 개발자 정보
- Author: rlawnsqls123
- Email: rlawnsqls123@naver.com
- GitHub: https://github.com/rlawnsqls123

# 개선 예정 항목
- PostgreSQL로 DB 이전
- JWT 인증으로 보안 강화
- 관리자용 Snippet 관리 전용 페이지 추가
- GitHub Actions 기반 CI/CD 자동화

# License
MIT License

