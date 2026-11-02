---
title: Seedance (씨댄스) 완전 가이드
tags: [AI, Seedance, 영상생성, 가이드, 레퍼런스]
created: 2026-11-03
updated: 2026-11-03
---

# 🎬 Seedance (씨댄스) 완전 가이드

> ByteDance가 만든 AI 영상 생성 모델. 텍스트/이미지/비디오/오디오를 조합해 최대 30초 영상을 만든다.

---

## 목차

1. [한눈에 보기](#한눈에-보기)
2. [시작하기 (Quick Start)](#시작하기)
3. [6가지 워크플로우](#6가지-워크플로우)
4. [프롬프트 작성법](#프롬프트-작성법)
5. [프롬프트 예시 모음](#프롬프트-예시-모음)
6. [API 코드 레시피](#api-코드-레시피)
7. [캐릭터 일관성 워크플로우](#캐릭터-일관성-워크플로우)
8. [가격표](#가격표)
9. [팁과 주의사항](#팁과-주의사항)

---

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| **최대 길이** | 30초 (연장 2회 추가 가능) |
| **참조 입력** | 이미지 30장 + 비디오 10개 + 오디오 10개 |
| **해상도** | 480p, 720p (네이티브) / 1080p, 4K (업스케일) |
| **화면비** | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9, 9:21 |
| **오디오** | 자동 생성 + 립싱크 |
| **언어** | 한국어 포함 10개+ (영어 프롬프트 권장) |

---

## 시작하기

### 방법 1: 웹 플랫폼 (비개발자 추천)

**Dreamina** — 가장 쉬운 시작점
1. Dreamina 가입 (무료 일일 크레딧 제공)
2. Seedance 2.5 모델 선택
3. 프롬프트 입력 + 참조 자료 업로드
4. 화면비/해상도/길이 설정
5. 생성 (1~3분 소요) → 다운로드

### 방법 2: Together AI API (개발자 추천)

```bash
# 1. SDK 설치
pip install together          # Python
npm install together-ai       # Node.js

# 2. API 키 설정
export TOGETHER_API_KEY=your_key_here
```

**첫 영상 만들기 (Python):**

```python
import time
from together import Together

client = Together()

# 영상 생성 요청
job = client.videos.create(
    prompt="A cinematic slow-motion shot of a cyberpunk city in the rain, neon lights reflecting on puddles",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="5",
)

# 결과 대기
while True:
    status = client.videos.retrieve(job.id)
    if status.status == "completed":
        print(f"완성! → {status.outputs.video_url}")
        break
    elif status.status == "failed":
        print(f"실패: {status.error}")
        break
    time.sleep(15)
```

### 방법 3: MuAPI (고급 기능, 1080p/4K 필요 시)

```bash
pip install seedance-2-api
```

```python
from seedance_api import SeedanceAPI

api = SeedanceAPI()  # 환경변수 MUAPI_API_KEY 필요

result = api.text_to_video(
    prompt="A majestic eagle soaring over snow-capped Himalayas",
    aspect_ratio="16:9",
    duration=5,
)
video = api.wait_for_completion(result['request_id'])
print(video.get("output", {}).get("video"))
```

---

## 6가지 워크플로우

### ① 텍스트 → 비디오

텍스트만으로 영상 생성. 가장 기본.

```python
job = client.videos.create(
    prompt="프롬프트 여기에",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="5",
)
```

### ② 이미지 → 비디오

정지 이미지를 움직이는 영상으로.

```python
job = client.videos.create(
    prompt="카메라가 천천히 줌인하며 피사체가 고개를 든다",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="5",
    media={
        "frame_images": [
            {"input_image": "https://이미지URL", "frame": "first"}
        ],
    },
)
```

### ③ 키프레임 전환 (First & Last Frame)

시작과 끝 이미지를 지정하면 자연스럽게 전환.

```python
job = client.videos.create(
    prompt="Smooth cinematic transition with natural motion.",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="5",
    media={
        "frame_images": [
            {"input_image": "https://시작이미지", "frame": "first"},
            {"input_image": "https://끝이미지", "frame": "last"},
        ],
    },
)
```

### ④ 복합 참조 (Omni Reference)

이미지+비디오+오디오를 모두 참조. `frame_images`와 동시 사용 불가.

```python
job = client.videos.create(
    prompt="A person dances on a neon-lit stage with dynamic camera motion.",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="6",
    media={
        "reference_images": ["https://캐릭터.png", "https://의상.png"],
        "reference_videos": [{"video": "https://댄스참조.mp4"}],
        "reference_audios": ["https://음악.mp3"],
    },
)
```

### ⑤ 비디오 편집 (Video Edit)

기존 영상의 특정 부분만 수정. MuAPI 전용.

```bash
curl -X POST "https://api.muapi.ai/api/v1/seedance-2.5-video-edit" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "prompt": "낮 장면을 비 오는 블루아워로 변경, 피사체와 카메라 움직임은 유지",
    "video": "https://원본영상.mp4",
    "generate_audio": true,
    "duration": 8,
    "aspect_ratio": "16:9"
  }'
```

### ⑥ 비디오 연장 (Video Extend)

영상 끝에서 이어서 생성. 최대 2회 연장.

```bash
curl -X POST "https://api.muapi.ai/api/v1/seedance-2.5-video-extend" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "prompt": "카메라가 계속 전진하며 빛나는 도시 입구로 진입",
    "video": "https://원본영상.mp4",
    "duration": 5,
    "generate_audio": true
  }'
```

---

## 프롬프트 작성법

### 핵심 원칙

> 정지 이미지 캡션이 아니라 **촬영 브리프**처럼 쓴다.

### 5요소 분할법 (권장)

```
피사체/동작  →  장소/환경  →  스타일  →  카메라  →  오디오
```

### 구조화 포맷 (30초 영상용)

```
[목적] 실사 30초 제품 광고, 16:9, 원테이크

[참조 지시] 제품 형태/로고/색상 유지; 배경 제외

[장면 분할]
0-10초: [구체적 행동]
10-20초: [구체적 행동]
20-30초: [구체적 행동]

[카메라] 핸드헬드, 부드러운 모션, 얕은 포커스 풀
[스타일] 다큐멘터리 리얼리즘, 35mm 필름 그레인
[물리] 사실적 무게감, 액체 출렁임
[제외] 자막 없음, 배경음악 없음, 점프컷 없음
```

### 작성 체크리스트

- [ ] **구체적인가?** — "사람이 걷는다" ✗ → "정장 남성이 빗속에서 우산 없이 느리게 걷는다" ✓
- [ ] **카메라 지시가 있는가?** — 돌리, 팬, 줌, 틸트, 크레인, 핸드헬드 등
- [ ] **분위기/조명이 있는가?** — golden hour, neon-lit, overcast, dramatic shadows
- [ ] **시간 흐름이 있는가?** — 정적 묘사 대신 시간에 따른 변화 기술
- [ ] **불필요한 것을 제외했는가?** — 네거티브로 원치 않는 요소 차단
- [ ] **영어로 작성했는가?** — 한국어도 되지만 영어가 더 안정적

---

## 프롬프트 예시 모음

### 시네마틱 자연

```
Aerial drone shot slowly descending through morning fog over a dense
bamboo forest. Golden sunlight filters through the canopy, creating
volumetric light rays. Camera gently rotates as it descends. Bird
songs and rustling leaves in the background.
```

### 제품 광고 (커피)

```
[목적] 실사 15초 커피 광고, 9:16

[장면 분할]
0-5초: 원두가 컵에 쏟아지는 클로즈업, 증기 피어오름
5-10초: 바리스타가 라떼아트 완성, 카메라 천천히 줌아웃
10-15초: 완성된 커피와 제품 패키지, 따뜻한 조명

[카메라] 스무스 돌리, 얕은 심도
[스타일] 따뜻한 톤, 자연광
[제외] 텍스트 없음, 워터마크 없음
```

### 사이버펑크 액션

```
A cinematic slow-motion shot of a cyberpunk city in the rain. Neon
lights reflect on wet asphalt puddles. A hooded figure walks through
the frame, camera tracking from the side. Dramatic synth music pulses
in the background. 8k resolution, shallow depth of field.
```

### 판타지 배틀

```
A small cute cartoon kitten general in golden armor stands on a cliff,
commanding an army of mice charging below. Epic ancient war atmosphere,
dramatic clouds over snowy mountains. Camera slowly pushes in on the
kitten's determined face.
```

### Before/After (키프레임용)

```
Smooth cinematic transition from abandoned, overgrown building to
fully restored modern architecture. Natural lighting shifts from
overcast to golden hour. Camera position remains fixed.
```

### 비디오 편집

```
Turn the sunny afternoon into a rainy blue-hour scene while preserving
the subject and camera movement. Add reflections on the ground and
moody atmospheric haze.
```

---

## API 코드 레시피

### TypeScript — 텍스트→비디오

```typescript
import Together from "together-ai";

const together = new Together();

async function generateVideo(prompt: string) {
  const job = await together.videos.create({
    prompt,
    model: "ByteDance/Seedance-2.5",
    resolution: "720p",
    seconds: "5",
  });

  while (true) {
    const status = await together.videos.retrieve(job.id);
    if (status.status === "completed") return status.outputs.video_url;
    if (status.status === "failed") throw new Error(JSON.stringify(status.error));
    await new Promise(r => setTimeout(r, 15000));
  }
}

// 사용
const url = await generateVideo("A cat sitting on a windowsill watching rain");
console.log(url);
```

### cURL — 빠른 테스트

```bash
# 생성 요청
curl -X POST "https://api.together.xyz/v2/videos" \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ByteDance/Seedance-2.5",
    "prompt": "A cinematic shot of ocean waves crashing on rocks at sunset",
    "resolution": "720p",
    "seconds": "5"
  }'

# 결과 확인 (JOB_ID를 위 응답의 id로 교체)
curl "https://api.together.xyz/v2/videos/JOB_ID" \
  -H "Authorization: Bearer $TOGETHER_API_KEY"
```

### Python — 이미지→비디오 + 오디오 참조

```python
job = client.videos.create(
    prompt="The character raps energetically, bobbing with the beat.",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="10",
    media={
        "reference_images": ["https://래퍼이미지.png"],
        "reference_audios": ["https://랩오디오.mp3"],
    },
)
```

### MuAPI — 1080p/4K 생성

```bash
# 1080p 텍스트→비디오
curl -X POST "https://api.muapi.ai/api/v1/seedance-2.5-text-to-video-1080p" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_KEY" \
  -d '{
    "prompt": "A majestic eagle soaring over snow-capped Himalayas",
    "aspect_ratio": "16:9",
    "duration": 5,
    "seed": 42
  }'
```

---

## 캐릭터 일관성 워크플로우

여러 영상에서 **같은 캐릭터**를 유지하려면 캐릭터 시트를 먼저 만든다.

```python
from seedance_api import SeedanceAPI
api = SeedanceAPI()

# 1단계: 캐릭터 시트 생성 (사진 1~3장)
char = api.create_character(
    images_list=["https://인물사진.jpg"],
    outfit_description="cyberpunk jacket with neon accents, glowing visor",
)
sheet = api.wait_for_completion(char["request_id"])
sheet_url = sheet["outputs"][0]

# 2단계: 시트 기반으로 영상 생성 (일관된 캐릭터)
video1 = api.consistent_video(
    sheet_url=sheet_url,
    prompt="The character rides a motorcycle through a neon city at night",
    aspect_ratio="16:9",
    duration=5,
)

video2 = api.consistent_video(
    sheet_url=sheet_url,
    prompt="The character draws a weapon in slow motion, dramatic lighting",
    aspect_ratio="16:9",
    duration=5,
    extra_images=["https://배경.jpg"],  # 추가 참조 가능
)
```

> 캐릭터 시트 비용: $0.18/장 (고정)

---

## 가격표

### Together AI

| 해상도 | 초당 가격 | 5초 영상 |
|---|---|---|
| 480p | $0.115 | $0.575 |
| 720p | $0.249 | $1.245 |

### MuAPI

| 해상도 | 생성 (초당) | 편집/연장 (초당) | 5초 영상 |
|---|---|---|---|
| 480p | $0.17 | $0.11 | $0.85 |
| 720p | $0.34 | $0.22 | $1.70 |
| 1080p | $0.85 | $0.55 | $4.25 |
| 4K | $1.70 | $1.11 | $8.50 |

> Spicy 변형: 위 가격 +10%

### 웹 플랫폼 (Dreamina)

| 플랜 | 월 가격 | 크레딧 | 대략 영상 수 |
|---|---|---|---|
| Mini | $14.9/월 | 3,000/월 | ~86편 |
| Standard | $29.9/월 | — | — |
| Plus | $59.9/월 | — | — |
| Pro | $99.9/월 | 26,000/월 | ~743편 |

---

## 팁과 주의사항

### 잘 되는 것

- 시네마틱 자연/도시 풍경
- 제품 광고 숏폼
- 댄스/모션 영상
- 캐릭터 기반 시리즈
- 분위기 전환 편집

### 주의할 점

| 항목 | 내용 |
|---|---|
| **프롬프트 언어** | 영어가 가장 안정적. 한국어도 가능하나 품질 차이 있음 |
| **frame_images vs reference** | 동시 사용 불가. 둘 중 하나만 선택 |
| **1080p/4K** | Together AI는 720p까지만. 1080p 이상은 MuAPI 사용 |
| **생성 시간** | 보통 1~3분. 30초 영상은 더 오래 걸림 |
| **IP 주의** | 타인 얼굴/음성/상표 무단 사용 금지 |
| **상업 이용** | 유료 플랜에서 가능. 무료 크레딧 결과물은 제한 있을 수 있음 |
| **시드 고정** | `seed` 값 고정하면 유사한 결과 재현 가능 |

### 관련 링크

| 리소스 | URL |
|---|---|
| Together AI 문서 | https://docs.together.ai/docs/seedance2.5-quickstart |
| GitHub SDK (Python) | https://github.com/SamurAIGPT/Seedance-2.5-API |
| ComfyUI 노드 | https://github.com/Anil-matcha/seedance2.5-comfyui |
| MCP 서버 | https://github.com/Anil-matcha/seedance-2.5-mcp |
| 프롬프트 모음 | https://github.com/Anil-matcha/awesome-seedance-2.5-api-prompts |
