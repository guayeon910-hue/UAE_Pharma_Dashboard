# 팀원 프론트엔드 (싱가포르) → 사우디 프로그램 이식 — 완전 설계 문서

## 1. 프로젝트 개요

| 항목 | 팀원 (소스) | 나 (타겟) |
|------|------------|----------|
| **폴더** | `1st_logic_initial-main` | `saudi-pharma-crawler` |
| **국가** | 🇸🇬 싱가포르 | 🇸🇦 사우디아라비아 |
| **통화** | SGD (싱가포르 달러) | SAR (사우디 리얄) |
| **대상 약품** | 동일 8개 | 동일 8개 |
| **배포** | Render (`sg-analysis-dashboard.onrender.com`) | 유사 구조 |
| **백엔드** | FastAPI (`server.py` 57KB) | FastAPI (`server.py` 103KB) |
| **프론트엔드** | `index.html` 24KB + `style.css` 68KB + `app.js` 100KB | `index.html` 32KB + `style.css` 66KB + `app.js` 95KB |

> [!IMPORTANT]
> **목표**: 팀원의 UI/UX(레이아웃, 여백, 창 크기, 색상, 폰트, 모달, 애니메이션)를 **픽셀 수준으로 동일**하게 복제하되, 데이터 바인딩과 텍스트만 사우디 맥락으로 교체합니다.

---

## 2. 스크린샷 분석 — UI 구조 완전 해부

### 2.1 전체 레이아웃 (2-Column Dashboard Grid)

```
┌──────────────────────────────────────────────────────────────────┐
│  [로고]  한국유나이티드제약(주) 해외 영업·마케팅 대시보드    🇸🇬 SG  │  ← topbar (height: 66px)
├────────────────────────────┬─────────────────────────────────────┤
│  01  수출가격 전략          │  02  바이어 발굴                     │
│                            │                                     │
│  [품목 드롭다운] [분석실행]  │  [보고서 드롭다운] [바이어 발굴 실행]  │
│  ▸ 신약 직접 분석           │                                     │
│  ────────────────          │  기업 평가 기준 (체크박스 ×5)          │
│  품목 선택                  │  [전체 해제]  [↓ 최종 보고서 다운로드]  │
│  [보고서 드롭다운]          │                                     │
│  [공공] [민간] [AI가격분석]  │  Top 10                             │
│  ────────────────          │  1. FARMABIOS                       │
│  ┌저가진입┐┌기준가┐┌프리미엄┐│  2. Aarti Pharmalabs Limited        │
│  │ 9.83  ││14.34 ││19.69  ││  3. Swati Spentose Pvt Ltd         │
│  │ USD   ││ USD  ││ USD   ││  ...                                │
│  │7.74SGD││11.29 ││15.50  ││  8. HANGZHOU PHARMCO CO LTD        │
│  └───────┘└──────┘└───────┘│                                     │
├────────────────────────────┴─────────────────────────────────────┤
│                                                   [보고서 탭] ← floating btn │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 CSS 핵심 치수 (팀원 코드에서 추출)

| 요소 | CSS | 값 |
|------|-----|-----|
| **상단바 높이** | `--topbar-h` | `66px` |
| **메인 패딩** | `.main padding` | `16px 28px 28px` |
| **최대 너비** | `.main max-width` | `1440px` |
| **그리드 비율** | `.dashboard-grid grid-template-columns` | `1fr 1.45fr` |
| **그리드 갭** | `.dashboard-grid gap` | `16px` |
| **그리드 높이** | `.dashboard-grid height` | `calc(100vh - 66px - 44px)` |
| **컬럼 카드** | `.col-left, .col-right border-radius` | `20px` |
| **셀렉터 카드** | `.selector-card border-radius / padding` | `16px / 12px 16px` |
| **프로세스 헤더** | `.process-header padding` | `13px 20px` |
| **프로세스 넘버** | `.process-num` | `11px / 900 / navy bg / 8px radius / 5px 11px padding` |
| **버튼 (분석실행)** | `.btn-analyze padding / radius` | `10px 26px / 10px` |
| **3열 가격카드** | `.p2-three-col gap` | `10px`, 각 `.p2-col border-radius: 14px` |
| **가격 폰트** | `.p2-col-price font-size / weight` | `22px / 900` |
| **바이어 리스트** | `.p3-list-row padding / radius` | `8px 12px / 8px` |
| **플로팅 보고서 버튼** | `.rep-float radius / shadow` | `999px / 0 4px 20px rgba(23,63,120,.35)` |
| **보고서 패널** | `.rep-panel width / max-height / radius` | `380px / 60vh / 16px` |
| **모달 오버레이** | `.buyer-modal-overlay background` | `rgba(0,0,0,.45)` |
| **모달 본체** | `.buyer-modal max-width / radius / padding` | `620px / 12px / 28px` |

### 2.3 색상 토큰 (CSS 변수 — 그대로 복제)

```css
:root {
  --navy:    #173f78;    /* 주 색상 */
  --navy2:   #224f91;    /* hover */
  --orange:  #f0a13a;    /* 강조 / 저가진입 */
  --green:   #2d9870;    /* 성공 / 프리미엄 */
  --blue:    #3a82f0;    /* 링크 */
  --red:     #c8564d;    /* 에러 */
  --warn:    #c98b28;    /* 경고 */
  --text:    #1e2d45;    /* 본문 */
  --muted:   #6b7d96;    /* 보조 텍스트 */
  --card:    #ffffff;    /* 카드 배경 */
  --inner:   #f4f6fa;    /* 내부 블록 */
  --shell:   #f8f5f0;    /* 페이지 배경 */
}
```

### 2.4 폰트 스택

```css
font-family: "Pretendard", "Noto Sans KR", "SF Pro Text", system-ui, sans-serif;
```

---

## 3. 컴포넌트별 이식 맵핑

### 3.1 상단바 (Topbar)

| 싱가포르 (원본) | 사우디 (타겟) |
|---------------|-------------|
| 🇸🇬 Singapore | 🇸🇦 Saudi Arabia |
| `SG` 라벨 | `SA` 라벨 |
| 타이틀 동일 유지 | 타이틀 동일 유지 |
| 로고 이미지 `/static/images/logo.png` | 동일 로고 사용 |

### 3.2 왼쪽 컬럼 — 01 수출가격 전략

#### 품목 드롭다운 (`#product-select`)

| 싱가포르 value | 사우디 value |
|-----------|----------|
| `SG_sereterol_activair` | `SA_sereterol_activair` |
| `SG_omethyl_omega3_2g` | `SA_omethyl_omega3_2g` |
| `SG_hydrine_hydroxyurea_500` | `SA_hydrine_hydroxyurea_500` |
| `SG_gadvoa_gadobutrol_604` | `SA_gadvoa_gadobutrol_604` |
| `SG_rosumeg_combigel` | `SA_rosumeg_combigel` |
| `SG_atmeg_combigel` | `SA_atmeg_combigel` |
| `SG_ciloduo_cilosta_rosuva` | `SA_ciloduo_cilosta_rosuva` |
| `SG_gastiin_cr_mosapride` | `SA_gastiin_cr_mosapride` |

> [!NOTE]
> 약품 8개는 동일. **value 접두어만 `SG_` → `SA_`**, 나머지 라벨과 INN은 그대로 유지.

#### 통화 표기

| 싱가포르 | 사우디 |
|---------|-------|
| `SGD` / `USD` | `SAR` / `USD` |
| `#p2c-sub-agg`: `7.74 SGD` | → `X.XX SAR` |
| 환율: `SGD/KRW`, `SGD/USD` | → `SAR/KRW`, `SAR/USD` |

#### 가격 카드 3열 (저가진입 / 기준가 / 프리미엄)

- UI 구조: **완전 동일** (`.p2-three-col` 3열 그리드, 상단 색대: orange / navy / green)
- 데이터: `사우디 server.py`의 `/api/p2/pipeline` 결과를 바인딩
- 통화 라벨만 `SGD` → `SAR`로 교체

### 3.3 오른쪽 컬럼 — 02 바이어 발굴

| 요소 | 변경 사항 |
|------|----------|
| 보고서 드롭다운 | 사우디 보고서 목록 연동 |
| 바이어 발굴 실행 | 사우디 `/api/buyers/pipeline` 호출 |
| 기업 평가 기준 5개 | 동일 유지 (매출규모, 파이프라인, 제조소 보유, 수입 경험, 약국체인 운영) |
| Top 10 리스트 | 사우디 바이어 데이터 렌더링 |
| 최종 보고서 다운로드 | `/api/report/combined` 호출 |

### 3.4 플로팅 보고서 패널 (우하단)

- **위치**: `position: fixed; bottom: 2rem; right: 2rem; z-index: 8000;`
- **버튼**: navy 원형 (`border-radius: 999px`) "보고서 탭" 라벨
- **패널**: 380px 너비, 60vh 최대 높이, 보고서 목록 + PDF 다운로드/삭제
- 변경 없음 — UI 구조 그대로 복사, PDF 경로만 사우디 서버 연동

### 3.5 모달 (팝업 창)

| 모달 | 크기 | 용도 |
|------|------|------|
| **P2 역산 편집** | `width: 470px; max-width: 95vw; padding: 22px 24px` | 가격 옵션 편집 |
| **바이어 상세** | `max-width: 620px; max-height: 88vh; padding: 28px` | 바이어 기업 상세 |

---

## 4. 백엔드 API 매핑 (JS → server.py)

### 4.1 팀원 `app.js`가 호출하는 API 목록 vs 사우디 `server.py` 대응

| 팀원 JS 호출 | 사우디 서버 엔드포인트 | 상태 |
|-------------|---------------------|------|
| `GET /api/exchange` | ❌ 신규 필요 (SAR/KRW 환율) | **구현 필요** |
| `GET /api/macro` | ❌ 신규 필요 (사우디 거시지표) | **구현 필요** |
| `GET /api/news` | ❌ 신규 필요 (사우디 제약 뉴스) | **구현 필요** |
| `POST /api/pipeline/{key}` | ✅ 동일 구조 존재 | 그대로 사용 |
| `GET /api/pipeline/{key}/status` | ✅ 동일 구조 존재 | 그대로 사용 |
| `GET /api/pipeline/{key}/result` | ✅ 동일 구조 존재 | 그대로 사용 |
| `POST /api/pipeline/custom` | ❌ 확인 필요 | **구현 필요** |
| `GET /api/pipeline/custom/status` | ❌ 확인 필요 | **구현 필요** |
| `GET /api/pipeline/custom/result` | ❌ 확인 필요 | **구현 필요** |
| `POST /api/p2/pipeline` | ✅ `run_public_pipeline` / `run_private_pipeline` 존재 | 연동 필요 |
| `GET /api/p2/pipeline/status` | ❌ 확인 필요 | **구현 필요** |
| `GET /api/p2/pipeline/result` | ❌ 확인 필요 | **구현 필요** |
| `POST /api/p2/upload` | ❌ 신규 필요 | **구현 필요** |
| `POST /api/p2/report` | ❌ 확인 필요 | **구현 필요** |
| `POST /api/buyers/pipeline` (P3) | ✅ 유사 엔드포인트 존재 확인 필요 | 연동 필요 |
| `GET /api/report/download` | ✅ 존재 | 그대로 사용 |
| `GET /api/report/combined` | ❌ 확인 필요 | **구현 필요** |
| `GET /api/settings/keys/status` | ❌ 확인 필요 | **구현 필요** |
| `GET /api/health` | ✅ 존재 확인 필요 | 확인 |

> [!WARNING]
> 사우디 `server.py`는 이미 103KB로 팀원보다 훨씬 크고 기능이 더 많습니다(Phase 3 빈틈분석, Phase 5 경쟁사 역추적 등). 따라서 **누락된 API만 추가 구현**하고, 기존 사우디 고유 기능은 절대 건드리지 않습니다.

### 4.2 사우디 데이터 구조 (dashboard_data.json)

```json
{
  "product_id": "SFDA_1807245616",
  "trade_name": "0.9% W/V SODIUM CHLORIDE B.P",
  "price": 0.75,
  "confidence": 0.9105,
  "outlier": false,
  "inn_name": null,
  "inn_match": "none",
  "dosage_form": "injection",
  "anomaly_reason": null,
  "page": 1
}
```

→ 팀원 JS에서 테이블/카드에 바인딩할 때 이 필드명 그대로 사용 가능.

---

## 5. 파일별 이식 작업 목록

### 5.1 `index.html` — 변경 포인트

| 라인 | 싱가포르 원본 | 사우디 변경 |
|------|-------------|-----------|
| 6 | `<title>싱가포르 수출 적합성 분석</title>` | `<title>사우디 수출 적합성 분석 — UPharma Export AI</title>` |
| 21 | `🇸🇬` | `🇸🇦` |
| 22 | `Singapore` | `Saudi Arabia` |
| 50-58 | `SG_xxx` option values | `SA_xxx` option values |
| 121 | `SGD` 통화 라벨 | `SAR` |
| 전체 | `SGD` 텍스트 | `SAR` 텍스트 |

### 5.2 `style.css` — 변경 포인트

**변경 없음.** CSS는 팀원 파일을 **100% 그대로 복사합니다.** 색상 토큰, 레이아웃 치수, 반응형 브레이크포인트, 애니메이션 전부 동일하게 유지합니다.

### 5.3 `app.js` — 변경 포인트

| 섹션 | 변경 내용 |
|------|---------|
| `INN_MAP` 상수 | 키 접두어 `SG_` → `SA_` |
| `TODO_LS_KEY` | `sg_upharma_todos_v1` → `sa_upharma_todos_v1` |
| `REPORTS_LS_KEY` | `sg_upharma_reports_v1` → `sa_upharma_reports_v1` |
| 환율 표시 | `SGD/KRW` → `SAR/KRW`, `SGD/USD` → `SAR/USD` |
| 통화 텍스트 | 모든 `SGD` → `SAR` |
| API 호출 경로 | 대부분 동일 (사우디 서버 구조 동일) |
| P2 시장 설명문 | 싱가포르 맥락 → 사우디 맥락 (NUPCO, SFDA 등) |

---

## 6. 구현 순서 (Phase)

### Phase 1: CSS 완전 복사
1. 팀원의 `style.css` (2275줄)을 사우디 `frontend/static/style.css`에 **덮어쓰기**
2. 주석 헤더만 "사우디 대시보드 스타일"로 변경

### Phase 2: HTML 구조 이식
1. 팀원의 `index.html` 골격을 사우디에 복사
2. 국가 플래그/라벨/타이틀 변경 (`🇸🇬` → `🇸🇦`, `SG` → `SA`)
3. 드롭다운 options value 접두어 변경 (`SG_` → `SA_`)
4. 통화 라벨 교체 (`SGD` → `SAR`)

### Phase 3: JavaScript 로직 이식
1. 팀원의 `app.js`를 사우디에 복사
2. `INN_MAP` 상수 키 변경
3. localStorage 키 변경
4. 통화/환율 관련 텍스트 교체
5. 사우디 서버 API 경로에 맞게 fetch URL 조정

### Phase 4: 백엔드 API 보강 *(선택)*
1. 사우디 `server.py`에 누락된 API 엔드포인트 추가
2. 환율 API (`SAR/KRW`), 신약 파이프라인, P2 파이프라인 상태/결과 등

### Phase 5: 검증
1. 로컬 서버 실행 및 화면 비교
2. 팀원 스크린샷과 나란히 놓고 여백/크기 검증

---

## 7. 사우디 크롤링 소스 (dashboard_sites.py) — 현재 상태

| key | 이름 | 도메인 | 카테고리 |
|-----|------|--------|----------|
| `sfda_api` | SFDA API | sfda.gov.sa | 공공조달 |
| `nupco` | NUPCO | nupco.com | 공공조달 |
| `sfda_companies` | SFDA Companies | sfda.gov.sa | 공공조달 |
| `sfda_drugs` | SFDA Drug List | sfda.gov.sa | 공공조달 |
| `nahdi_web` | Nahdi | nahdionline.com | 민간 |
| `whites_web` | Whites | whites.sa | 민간 |

→ 팀원 UI에서 사이트별 상태 표시 부분은 이 6개 소스를 반영합니다.

---

## 결정 사항 (확정)

> [!NOTE]
> 1. ✅ **환율 API**: 사우디 `server.py`에 `GET /api/exchange` (SAR/KRW, SAR/USD) 엔드포인트를 **yfinance로 추가 구현**합니다.
> 2. ✅ **신약 직접 분석**: 사우디 서버에 이미 동일 구조 존재. `runCustomPipeline()` → `/api/pipeline/{product_key}` 호출. **기존 사우디 코드 그대로 활용**, 프론트엔드 UI만 팀원 것과 동일하게 맞춤.
> 3. ✅ **P2 AI 가격분석**: 프론트엔드 껍데기(UI)만 팀원과 동일, **백엔드 로직은 기존 사우디** (`fob_private.py` / `run_public_pipeline` / `run_private_pipeline`) **그대로 사용**. 국가별 데이터가 다르므로 속 내용물은 사우디 전용.

## Verification Plan

### Manual Verification
1. 사우디 서버 로컬 실행 (`uvicorn frontend.server:app --port 8000`)
2. 팀원 스크린샷(위 4장)과 동일 화면을 1:1 비교
3. 모든 버튼 클릭 테스트 (분석 실행, AI 가격 분석, 바이어 발굴, 보고서 탭)
4. 3열 가격 카드의 여백·폰트·색상 일치 확인
5. 모달 팝업 크기·위치·트랜지션 확인
6. 반응형 테스트 (1200px, 860px, 720px 브레이크포인트)
