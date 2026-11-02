---
title: Seedance API Quick Start
tags: [AI, Seedance, API, 개발, QuickStart]
created: 2026-11-03
updated: 2026-11-03
---

# Seedance API Quick Start

## 플랫폼별 API 선택

| 플랫폼 | 모델 ID | 베이스 URL |
|---|---|---|
| Together AI | `ByteDance/Seedance-2.5` | `https://api.together.xyz/v2/videos` |
| MuAPI | 라우트별 상이 | `https://api.muapi.ai/api/v1` |

## Together AI — Quick Start

### 1. 설치

```bash
# Python
pip install together

# Node.js
npm install together-ai
```

### 2. 인증

```bash
export TOGETHER_API_KEY=your_api_key_here
```

### 3. 핵심 워크플로우

```
요청 전송 → Job ID 수신 → 상태 폴링 → 비디오 URL 획득
```

### 4. Python — 텍스트→비디오

```python
import time
from together import Together

client = Together()

job = client.videos.create(
    prompt="A small cute cartoon kitten general in golden armor stands on a cliff, commanding an army of mice charging below.",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="5",
)

print(f"Job ID: {job.id}")

while True:
    status = client.videos.retrieve(job.id)
    print(f"Status: {status.status}")

    if status.status == "completed":
        print(f"Video URL: {status.outputs.video_url}")
        break
    elif status.status == "failed":
        print(f"Error: {status.error}")
        break

    time.sleep(15)
```

### 5. TypeScript — 텍스트→비디오

```typescript
import Together from "together-ai";

const together = new Together();

async function main() {
  const job = await together.videos.create({
    prompt: "A cinematic slow-motion shot of a cyberpunk city in the rain",
    model: "ByteDance/Seedance-2.5",
    resolution: "720p",
    seconds: "5",
  });

  console.log(`Job ID: ${job.id}`);

  while (true) {
    const status = await together.videos.retrieve(job.id);
    if (status.status === "completed") {
      console.log(`Video URL: ${status.outputs.video_url}`);
      break;
    } else if (status.status === "failed") {
      console.log(`Error: ${JSON.stringify(status.error)}`);
      break;
    }
    await new Promise((resolve) => setTimeout(resolve, 15000));
  }
}

main();
```

### 6. cURL — 텍스트→비디오

```bash
curl -X POST "https://api.together.xyz/v2/videos" \
  -H "Authorization: Bearer $TOGETHER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ByteDance/Seedance-2.5",
    "prompt": "A cinematic shot of a cyberpunk city in the rain",
    "resolution": "720p",
    "seconds": "5"
  }'
```

### 7. 이미지→비디오 (첫 프레임)

```python
job = client.videos.create(
    prompt="A black cat curiously gazes up at the sky. Camera slowly rises.",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="5",
    media={
        "frame_images": [
            {
                "input_image": "https://example.com/cat.png",
                "frame": "first",
            }
        ],
    },
)
```

### 8. 첫+마지막 프레임 키프레임

```python
job = client.videos.create(
    prompt="Smooth cinematic transition with natural motion.",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="5",
    media={
        "frame_images": [
            {"input_image": "https://example.com/start.png", "frame": "first"},
            {"input_image": "https://example.com/end.png", "frame": "last"},
        ],
    },
)
```

### 9. 참조 기반 생성

```python
job = client.videos.create(
    prompt="A person dances on a neon-lit stage with dynamic camera motion.",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="6",
    media={
        "reference_images": [
            "https://example.com/character.png",
            "https://example.com/outfit.png",
        ],
        "reference_videos": [
            {"video": "https://example.com/dance-style.mp4"},
        ],
    },
)
```

### 10. 오디오 기반 생성

```python
job = client.videos.create(
    prompt="The character raps energetically into a microphone, bobbing with the beat.",
    model="ByteDance/Seedance-2.5",
    resolution="720p",
    seconds="10",
    media={
        "reference_images": [
            "https://example.com/rapper.png",
        ],
        "reference_audios": [
            "https://example.com/rap-audio.mp3",
        ],
    },
)
```

## Together AI — 파라미터 레퍼런스

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---|---|---|---|---|
| `prompt` | string | O | — | 2~10,000자 |
| `model` | string | O | — | `ByteDance/Seedance-2.5` |
| `resolution` | string | X | `720p` | `480p` 또는 `720p` |
| `seconds` | string | X | `5` | 4~30 (정수) |
| `media` | object | X | — | frame_images, reference_images, reference_videos, reference_audios |

### 입력 모드 (상호 배타적)

- **텍스트→비디오**: media 없음
- **이미지→비디오**: `frame_images` 최대 2개만
- **참조 기반**: `reference_images`(최대 30) + `reference_videos`(최대 10)
- **오디오 기반**: 위 + `reference_audios`(최대 10)

> **주의**: `frame_images`와 `reference_*`는 동시 사용 불가

## Together AI — 가격

| 해상도 | 초당 가격 |
|---|---|
| 480p | $0.115/초 |
| 720p | $0.249/초 |

---

## MuAPI — Quick Start

### 1. 설치

```bash
pip install seedance-2-api
```

### 2. 인증

```env
MUAPI_API_KEY=your_muapi_api_key_here
```

### 3. Python — 텍스트→비디오

```python
from seedance_api import SeedanceAPI

api = SeedanceAPI()

submission = api.text_to_video(
    prompt="A cinematic slow-motion shot of a cyberpunk city in the rain, neon lights reflecting on puddles, 8k resolution",
    aspect_ratio="16:9",
    duration=5,
)

result = api.wait_for_completion(submission['request_id'])
video_url = result.get("output", {}).get("video") or result.get("url")
print(f"Video: {video_url}")
```

### 4. cURL — 텍스트→비디오 (1080p)

```bash
curl -X POST "https://api.muapi.ai/api/v1/seedance-2.5-text-to-video-1080p" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
      "prompt": "A majestic eagle soaring over snow-capped Himalayas",
      "aspect_ratio": "16:9",
      "duration": 5,
      "seed": 42
  }'
```

### 5. 캐릭터 일관성 워크플로우

```python
from seedance_api import SeedanceAPI
api = SeedanceAPI()

# 1단계: 캐릭터 시트 생성 (1~3장 참조 사진)
char = api.create_character(
    images_list=["https://example.com/person.jpg"],
    outfit_description="cyberpunk jacket with neon accents",
)
sheet_result = api.wait_for_completion(char["request_id"])
sheet_url = sheet_result["outputs"][0]

# 2단계: 캐릭터 시트 기반 영상 생성
video = api.consistent_video(
    sheet_url=sheet_url,
    prompt="The character rides a motorcycle through a neon-lit city at night",
    aspect_ratio="16:9",
    duration=5,
)
result = api.wait_for_completion(video["request_id"])
print(f"Video: {result['outputs'][0]}")
```

## MuAPI — 라우트 매트릭스 (72개)

6개 워크플로우 × 3개 변형 × 4개 해상도 = 72개 라우트

**변형:**
- **Standard** — 기본 콘텐츠 안전 설정
- **Intl** — 국제 콘텐츠 정책
- **Spicy** — 완화된 안전, 대담한 스타일 (+10% 가격)

**해상도 접미사:** 없음(720p), `-480p`, `-1080p`, `-4k`

**예시:** `seedance-2.5-spicy-text-to-video-4k`

## MuAPI — 파라미터 레퍼런스

| 파라미터 | 타입 | 적용 대상 | 설명 |
|---|---|---|---|
| `prompt` | string | 전체 | 필수. 장면/모션/편집/연속 지시 |
| `image_url` | URL | I2V | 입력 이미지 1장 |
| `images_list` | URL[] | F&L/Omni | 키프레임 2장 또는 참조 최대 30장 |
| `videos_list` | URL[] | Omni | 참조 클립 최대 10개 |
| `audios_list` | URL[] | Omni | 참조 오디오 최대 10개 |
| `video` | URL | Edit/Extend | 소스 비디오 (30초 초과 시 트림) |
| `reference_images` | URL[] | Edit | 아이덴티티/스타일 참조, 최대 30장 |
| `reference_audios` | URL[] | Edit | 오디오 참조, 최대 10개 |
| `last_image` | URL | Extend | 연속 목표 프레임 |
| `generate_audio` | bool | Edit/Extend | 동기화 오디오 생성 (기본 true) |
| `aspect_ratio` | string | 전체 | 16:9, 9:16, 1:1, 4:3, 3:4, 21:9, 9:21 |
| `duration` | int | 전체 | 4~30초, 기본 5 |
| `seed` | int | 전체 | -1~4294967295, -1=랜덤 |
| `webhook_url` | URL | 전체 | 완료 웹훅 (선택) |

## MuAPI — 가격

| 해상도 | T2V/I2V/Keyframe/Omni | Edit/Extend |
|---|---|---|
| 480p | $0.17/초 | $0.1105/초 |
| 720p | $0.34/초 | $0.221/초 |
| 1080p | $0.85/초 | $0.5525/초 |
| 4K | $1.70/초 | $1.105/초 |

## 관련 리소스

- **GitHub SDK**: https://github.com/SamurAIGPT/Seedance-2.5-API
- **PyPI**: `pip install seedance-2-api`
- **Together AI 문서**: https://docs.together.ai/docs/seedance2.5-quickstart
- **ComfyUI 노드**: https://github.com/Anil-matcha/seedance2.5-comfyui
- **MCP 서버**: https://github.com/Anil-matcha/seedance-2.5-mcp
