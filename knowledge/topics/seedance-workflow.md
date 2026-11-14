---
title: Seedance 영상 제작 워크플로우
tags: [AI, Seedance, 워크플로우, 프롬프트, 가이드]
created: 2026-11-08
updated: 2026-11-08
---

# Seedance 영상 제작 워크플로우

## Step 1. 머릿속 영상을 글로 정리

만들고 싶은 영상을 먼저 구체적으로 정리:

- 누가/무엇이 나오는지 (피사체)
- 어떤 동작을 하는지
- 어디에서 (배경/환경)
- 어떤 분위기인지 (밝은/어두운/시네마틱)
- 몇 초짜리인지

## Step 2. 워크플로우 선택

| 상황 | 사용할 기능 |
|---|---|
| 아이디어만 있고 소스 없음 | **Text-to-Video** |
| 참고 이미지가 있음 | **Image-to-Video** |
| 시작/끝 장면이 정해져 있음 | **First & Last Frame** |
| 기존 영상을 수정하고 싶음 | **Video Edit** |
| 기존 영상을 더 길게 만들고 싶음 | **Video Extend** |

## Step 3. 영어 프롬프트 작성 (핵심!)

한국어로 구상 → 영어로 변환이 가장 좋다. 특히 Seedance 1.0은 한국어 네이티브 지원이 불확실하므로 영어 필수.

### 프롬프트 구조

```
[피사체 + 동작], [장면/환경], [스타일], [카메라], [네거티브]
```

### 나쁜 프롬프트 vs 좋은 프롬프트

```
❌ A woman drinking coffee

✅ A young woman in a beige sweater slowly lifts a steaming latte
to her lips in a cozy cafe with warm morning light streaming through
the window. Soft bokeh background, slow dolly in, cinematic color
grading, shallow depth of field. No text, no watermark.
```

### 차이점

- 피사체 구체화: "woman" → "young woman in a beige sweater"
- 동작 상세화: "drinking" → "slowly lifts a steaming latte to her lips"
- 환경 묘사: 없음 → "cozy cafe with warm morning light streaming through the window"
- 카메라/스타일: 없음 → "slow dolly in, cinematic color grading, shallow depth of field"
- 네거티브: 없음 → "No text, no watermark"

## Step 4. 저비용 테스트 → 반복 개선

1. **1.0 Fast + 480p + 4초**로 먼저 테스트 (크레딧 최소 소모)
2. 결과 확인 → 프롬프트 수정
3. 만족스러우면 해상도 올리거나 길이 늘리기
4. 필요하면 상위 모델(2.0/2.5)로 전환

## Step 5. 후처리

- 결과가 90%만 맞으면 → **Video Edit**으로 부분 수정
- 더 길게 필요하면 → **Video Extend**로 연장
- 여러 클립 합치기 → CapCut 등 외부 편집기 활용

## 실전 팁

1. **한 번에 완벽한 결과를 기대하지 말 것** — 3~5회 반복이 정상
2. **프롬프트에 "하지 말 것"도 적기** — `No text, no subtitle, no jumpcut`
3. **참조 이미지가 있으면 적극 활용** — 텍스트만보다 결과가 훨씬 정확함
4. **Claude에게 한국어로 설명 → 영어 프롬프트 변환 요청** 가능
