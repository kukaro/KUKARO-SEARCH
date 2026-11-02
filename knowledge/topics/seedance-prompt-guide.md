---
title: Seedance 프롬프트 작성법
tags: [AI, Seedance, 프롬프트, 가이드]
created: 2026-11-03
updated: 2026-11-03
---

# Seedance 프롬프트 작성법

## 프롬프트 구조 원칙

Seedance 프롬프트는 **정지 이미지 캡션이 아니라 짧은 촬영 브리프**처럼 작성해야 한다.
모델이 피사체와 움직임, 카메라를 파악할 수 있도록 서술한다.

## 6요소 순서 (선택 요소 생략 가능)

1. **피사체와 동작** (Subject & Action)
2. **장면과 환경** (Scene & Environment)
3. **비주얼 스타일** (Visual Style)
4. **카메라 움직임/컷** (Camera Movement or Cuts)
5. **오디오** (Audio)
6. **네거티브 프롬프트** (Negative Prompts)

## 구조화 프롬프트 포맷

```
[목적] 실사 30초 제품 광고, 16:9, 원테이크

[참조 지시] 제품 형태/로고/색상 유지; 배경 제외

[장면 분할]
0-10초: [구체적 행동]
10-20초: [구체적 행동]
20-30초: [구체적 행동]

[카메라 스타일] 핸드헬드, 부드러운 모션, 얕은 포커스 풀

[비주얼 미학] 다큐멘터리 리얼리즘, 자연스러운 피부 질감, 35mm 필름 그레인

[물리] 사실적 무게감, 액체 출렁임

[네거티브] 자막 없음, 배경음악 없음, 점프컷 없음, 로고 변경 없음
```

## 대안 구조: 5분할 방식

Seedance 2.5는 장문 서술보다 **피사체/동작/장소/스타일/카메라**로 분할 기술할 때 더 안정적이다.

## 타임스탬프 기반 접근

강력한 프롬프트는 정지 이미지가 아닌 **타이밍이 있는 장면**으로 서술한다:

```
피사체 + 동작 + 타이밍 + 카메라 움직임 + 조명 + 참조 규칙 + 네거티브 제약
```

## 프롬프트 예시

### 텍스트→비디오 (기본)
```
A small cute cartoon kitten general in golden armor stands on a cliff,
commanding an army of mice charging below. Epic ancient war atmosphere,
dramatic clouds over snowy mountains.
```

### 시네마틱 도시
```
A cinematic slow-motion shot of a cyberpunk city in the rain, neon lights
reflecting on puddles, 8k resolution
```

### 비디오 편집
```
Turn the sunny afternoon into a rainy blue-hour scene while preserving
the subject and camera movement
```

### 비디오 연장
```
Continue the camera move forward into the glowing city entrance
```

### 제품 광고 (구조화)
```
[목적] 실사 15초 커피 광고, 9:16, 세로형

[참조 지시] 제품 패키지 디자인 유지, 로고 선명하게

[장면 분할]
0-5초: 원두가 컵에 쏟아지는 클로즈업, 증기 피어오름
5-10초: 바리스타가 라떼아트 완성, 카메라 천천히 줌아웃
10-15초: 완성된 커피와 제품 패키지, 따뜻한 조명

[카메라] 스무스 돌리, 얕은 심도
[스타일] 따뜻한 톤, 자연광, 고급스러운 분위기
[네거티브] 텍스트 없음, 워터마크 없음
```

## 프롬프트 작성 팁

1. **구체적으로** — "사람이 걷는다" 대신 "정장 입은 남성이 빗속에서 우산 없이 느리게 걷는다"
2. **카메라 지시 포함** — 돌리, 팬, 줌, 틸트, 크레인 등 명시
3. **분위기/조명 서술** — "golden hour", "neon-lit", "overcast" 등
4. **불필요한 요소 제외** — 네거티브 프롬프트로 원치 않는 요소 차단
5. **시간 흐름 서술** — 정적 묘사 대신 시간에 따른 변화를 기술
6. **영어 프롬프트 권장** — 한국어도 지원하나 영어가 더 안정적
