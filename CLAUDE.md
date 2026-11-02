# KUKARO-SEARCH - Knowledge Base

이 프로젝트는 지식 베이스(Knowledge Base)로 사용됩니다.

## 프로젝트 구조

```
knowledge/          - 지식 문서 저장소
  topics/           - 주제별 문서
  references/       - 참고 자료
  notes/            - 메모 및 노트
search-index/       - 검색 인덱스 (자동 생성)
```

## 규칙

- 모든 지식 문서는 Markdown 형식으로 작성
- 문서 파일명은 영문 kebab-case 사용 (예: `my-topic.md`)
- 각 문서는 YAML frontmatter 포함 (title, tags, created, updated)
- 한국어로 작성하되, 기술 용어는 원어 병기 가능
