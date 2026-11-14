#!/usr/bin/env python3
"""
전국 클라이밍 암장 정보 크롤러
- 네이버 지도 instant-search API로 전국 암장 검색
- 각 암장의 상세 정보 (영업시간, 연락처, 주소, 편의시설 등) 수집
- knowledge/climbing-gyms/ 에 Markdown 파일로 저장
"""

import os
import re
import json
import time
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

# ── 설정 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "knowledge" / "climbing-gyms"
DATA_DIR = PROJECT_ROOT / "scripts" / "data"
SEARCH_DELAY = 2.5        # 검색 API 호출 간 딜레이 (초)
DETAIL_DELAY = 2.5         # 상세 페이지 호출 간 딜레이 (초)
MAX_RETRIES = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": "https://map.naver.com/",
}

MOBILE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                  "Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

# 전국 주요 도시/지역 좌표 (위도, 경도)
# 촘촘하게 배치하여 누락 최소화
REGION_COORDS = [
    # 서울
    ("서울 강남", 37.4979, 127.0276),
    ("서울 강북", 37.5665, 126.9780),
    ("서울 강서", 37.5509, 126.8495),
    ("서울 강동", 37.5301, 127.1238),
    ("서울 노원", 37.6542, 127.0568),
    ("서울 마포", 37.5663, 126.9014),
    # 경기
    ("수원", 37.2636, 127.0286),
    ("성남", 37.4200, 127.1267),
    ("용인", 37.2411, 127.1776),
    ("고양", 37.6584, 126.8320),
    ("안양", 37.3943, 126.9568),
    ("부천", 37.5034, 126.7660),
    ("안산", 37.3219, 126.8309),
    ("화성", 37.1994, 126.8313),
    ("남양주", 37.6360, 127.2163),
    ("의정부", 37.7381, 127.0337),
    ("시흥", 37.3800, 126.8031),
    ("파주", 37.7590, 126.7803),
    ("김포", 37.6153, 126.7156),
    ("광주시", 37.4295, 127.2550),
    ("하남", 37.5393, 127.2148),
    ("이천", 37.2720, 127.4349),
    ("양주", 37.7855, 127.0458),
    ("구리", 37.5943, 127.1295),
    ("오산", 37.1498, 127.0698),
    ("평택", 36.9922, 127.1128),
    ("동탄", 37.2000, 127.0740),
    # 인천
    ("인천 남동", 37.4488, 126.7317),
    ("인천 부평", 37.5074, 126.7219),
    ("인천 연수", 37.4101, 126.6783),
    # 대전
    ("대전 서구", 36.3553, 127.3835),
    ("대전 유성", 36.3624, 127.3561),
    # 세종
    ("세종", 36.4801, 127.2590),
    # 충남
    ("천안", 36.8151, 127.1139),
    ("아산", 36.7898, 127.0018),
    ("서산", 36.7849, 126.4503),
    ("당진", 36.8897, 126.6292),
    # 충북
    ("청주", 36.6424, 127.4890),
    ("충주", 36.9910, 127.9259),
    # 대구
    ("대구 중구", 35.8714, 128.6014),
    ("대구 수성", 35.8583, 128.6308),
    ("대구 달서", 35.8299, 128.5326),
    # 경북
    ("포항", 36.0190, 129.3435),
    ("구미", 36.1196, 128.3444),
    ("경주", 35.8562, 129.2247),
    ("안동", 36.5684, 128.7296),
    # 부산
    ("부산 서면", 35.1580, 129.0596),
    ("부산 해운대", 35.1631, 129.1636),
    ("부산 사하", 35.1046, 128.9741),
    ("부산 동래", 35.2050, 129.0841),
    # 울산
    ("울산 남구", 35.5384, 129.3114),
    ("울산 중구", 35.5690, 129.3324),
    # 경남
    ("창원", 35.2280, 128.6811),
    ("김해", 35.2341, 128.8896),
    ("진주", 35.1800, 128.1076),
    ("양산", 35.3350, 129.0372),
    ("거제", 34.8806, 128.6211),
    # 광주
    ("광주 서구", 35.1525, 126.8895),
    ("광주 북구", 35.1744, 126.9120),
    # 전남
    ("여수", 34.7604, 127.6622),
    ("순천", 34.9506, 127.4873),
    ("목포", 34.8118, 126.3922),
    # 전북 (전주)
    ("전주", 35.8242, 127.1480),
    ("익산", 35.9483, 126.9577),
    ("군산", 35.9676, 126.7369),
    # 강원
    ("춘천", 37.8813, 127.7298),
    ("원주", 37.3422, 127.9202),
    ("강릉", 37.7519, 128.8760),
    ("속초", 38.2070, 128.5918),
    ("동해", 37.5247, 129.1143),
    # 제주
    ("제주시", 33.4996, 126.5312),
    ("서귀포", 33.2541, 126.5601),
]

# ── 유틸리티 ──────────────────────────────────────────

def slugify(text: str) -> str:
    """한글/영문 텍스트를 파일명용 slug로 변환"""
    # 공백, 특수문자를 하이픈으로
    text = re.sub(r'[^\w가-힣a-zA-Z0-9]', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text.lower()


class CurlResponse:
    """curl 응답을 requests.Response처럼 사용"""
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def json(self):
        return json.loads(self.text)


def safe_request(url, headers=None, max_retries=MAX_RETRIES, delay=DETAIL_DELAY):
    """curl을 사용한 HTTP GET (네이버 차단 우회)"""
    use_headers = headers or HEADERS
    for attempt in range(max_retries):
        try:
            cmd = ["curl", "-s", "-w", "\n%{http_code}", url]
            for k, v in use_headers.items():
                cmd.extend(["-H", f"{k}: {v}"])
            cmd.extend(["--max-time", "15"])
            result = subprocess.run(cmd, capture_output=True, timeout=20)
            output = result.stdout.decode("utf-8", errors="replace")
            # 마지막 줄이 HTTP status code
            lines = output.rsplit("\n", 1)
            if len(lines) == 2:
                body, status_str = lines
                status_code = int(status_str.strip()) if status_str.strip().isdigit() else 0
            else:
                body = output
                status_code = 0

            if status_code == 200:
                return CurlResponse(body, 200)
            if status_code in (429, 400, 403):
                wait = delay * (attempt + 2)
                print(f"  [WAIT] HTTP {status_code}, {wait:.0f}s wait...")
                time.sleep(wait)
                continue
            print(f"  [WARN] HTTP {status_code} for {url[:80]}")
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"  [WARN] request fail ({attempt+1}/{max_retries}): {e}")
        time.sleep(delay)
    return None


# ── 1단계: 검색 ──────────────────────────────────────

def search_climbing_gyms(query: str, lat: float, lng: float) -> list[dict]:
    """네이버 지도 instant-search API로 암장 검색 (페이징 포함)"""
    all_places = []
    start = 1
    while True:
        url = (
            f"https://map.naver.com/p/api/search/instant-search"
            f"?query={quote(query)}&coords={lat},{lng}&start={start}"
        )
        resp = safe_request(url, headers=HEADERS, delay=SEARCH_DELAY)
        if not resp:
            break
        try:
            data = resp.json()
        except (json.JSONDecodeError, KeyError):
            break
        places = data.get("place", []) or []
        if not places:
            break
        all_places.extend(places)
        if len(places) < 10:
            break
        start += 10
        time.sleep(SEARCH_DELAY)

    # 암벽등반/클라이밍 카테고리만 필터
    results = []
    for p in all_places:
        ctg = p.get("ctg", "")
        title = p.get("title", "")
        # 암벽등반 카테고리이거나, 이름에 클라이밍/볼더링/암장 포함
        if ("암벽" in ctg or "클라이밍" in ctg or
            "클라이밍" in title or "볼더링" in title or
                "climbing" in title.lower() or "보울더" in title):
                results.append({
                    "id": p.get("id"),
                    "name": p.get("title"),
                    "address": p.get("roadAddress") or p.get("jibunAddress", ""),
                    "category": ctg,
                    "x": p.get("x"),
                    "y": p.get("y"),
                    "review_count": p.get("review", {}).get("count", "0"),
                })
        return results
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  [WARN] 검색 파싱 실패: {e}")
        return []


def collect_all_gyms() -> dict[str, dict]:
    """전국 좌표를 순회하며 모든 암장 수집 (중복 제거)"""
    all_gyms = {}  # id -> gym info
    queries = ["클라이밍", "볼더링", "클라이밍짐", "암벽등반"]

    total = len(REGION_COORDS) * len(queries)
    count = 0

    for region_name, lat, lng in REGION_COORDS:
        for query in queries:
            count += 1
            print(f"[{count}/{total}] {region_name} - '{query}' 검색 중...")
            results = search_climbing_gyms(query, lat, lng)
            new_count = 0
            for gym in results:
                gid = gym["id"]
                if gid not in all_gyms:
                    all_gyms[gid] = gym
                    new_count += 1
            if new_count:
                print(f"  → {new_count}개 신규 발견 (총 {len(all_gyms)}개)")
            time.sleep(SEARCH_DELAY)

    return all_gyms


# ── 2단계: 상세 정보 ─────────────────────────────────

def extract_apollo_state(html: str) -> dict | None:
    """HTML에서 __APOLLO_STATE__ JSON 추출"""
    match = re.search(r'window\.__APOLLO_STATE__\s*=\s*(\{.+?\})\s*;?\s*</script>', html, re.DOTALL)
    if not match:
        match = re.search(r'window\.__APOLLO_STATE__\s*=\s*(\{.+?\})\s*;\s*window\.', html, re.DOTALL)
    if not match:
        return None
    raw = match.group(1)
    # JSON 파싱 시 제어 문자 제거
    raw = re.sub(r'[\x00-\x1f]', '', raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 이스케이프 문제 보정 시도
        raw = raw.replace('\\"', '"').replace('\\\\', '\\')
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None


def parse_business_hours(html: str) -> list[dict]:
    """HTML에서 7일 영업시간 추출"""
    # WorkingHoursInfo 패턴 직접 매칭 (Apollo JSON 파싱 실패 시 폴백)
    pattern = (
        r'"WorkingHoursInfo","day":"([^"]*)",'
        r'"businessHours":\{"__typename":"StartEndTime","start":"([^"]*)","end":"([^"]*)"\},'
        r'"breakHours":\[([^\]]*)\]'
    )
    matches = re.findall(pattern, html)
    hours = []
    for day, start, end, breaks in matches:
        entry = {"day": day, "open": start, "close": end}
        if breaks:
            break_matches = re.findall(r'"start":"([^"]*)","end":"([^"]*)"', breaks)
            entry["break"] = [{"start": s, "end": e} for s, e in break_matches]
        hours.append(entry)
    return hours


def parse_detail_from_apollo(html: str) -> dict:
    """Apollo State에서 상세 정보 추출"""
    info = {}

    # PlaceDetailBase 키에서 데이터 추출
    # name
    m = re.search(r'"PlaceDetailBase:[^"]*":\{[^}]*"name":"([^"]*)"', html)
    if m:
        info["name"] = m.group(1)

    # roadAddress
    m = re.search(r'"roadAddress":"([^"]*)"', html)
    if m:
        info["road_address"] = m.group(1).replace("\\u002F", "/")

    # address (지번)
    m = re.search(r'"PlaceDetailBase[^"]*"[^}]*"address":"([^"]*)"', html)
    if m:
        info["jibun_address"] = m.group(1)

    # phone / virtualPhone
    m = re.search(r'"virtualPhone":"([^"]*)"', html)
    if m and m.group(1):
        info["phone"] = m.group(1)
    m2 = re.search(r'"phone":"([^"]+)"', html)
    if m2 and m2.group(1) != "null":
        info["phone_direct"] = m2.group(1)

    # category
    m = re.search(r'"category":"([^"]*)"', html)
    if m:
        info["category"] = m.group(1)

    # conveniences
    m = re.search(r'"conveniences":\[([^\]]*)\]', html)
    if m:
        info["conveniences"] = re.findall(r'"([^"]+)"', m.group(1))

    # 좌표
    m = re.search(r'"coordinate":\{"__typename":"Coordinate","x":"([^"]*)","y":"([^"]*)"', html)
    if m:
        info["longitude"] = m.group(1)
        info["latitude"] = m.group(2)

    # 리뷰 수
    m = re.search(r'"visitorReviewsTotal":(\d+)', html)
    if m:
        info["visitor_reviews"] = int(m.group(1))
    m = re.search(r'"cafeBlogReviewsTotal":(\d+)', html)
    if m:
        info["blog_reviews"] = int(m.group(1))

    # 영업시간
    info["business_hours"] = parse_business_hours(html)

    # 영업 상태 설명
    m = re.search(r'"businessStatusDescription":\{[^}]*"status":"([^"]*)"[^}]*"description":"([^"]*)"', html)
    if m:
        info["business_status"] = m.group(1)
        info["business_status_desc"] = m.group(2)

    # 자유 텍스트 (임시휴무 등)
    m = re.search(r'"freeText":"([^"]*)"', html)
    if m and m.group(1):
        info["notice"] = m.group(1).replace("\\n", "\n")

    # 네이버 블로그
    m = re.search(r'"naverBlog":"([^"]*)"', html)
    if m and m.group(1) != "null" and m.group(1):
        info["naver_blog"] = m.group(1).replace("\\u002F", "/")

    # talktalkUrl
    m = re.search(r'"talktalkUrl":"([^"]*)"', html)
    if m and m.group(1):
        info["talktalk_url"] = m.group(1).replace("\\u002F", "/")

    # 결제 정보
    m = re.search(r'"paymentInfo":\[([^\]]*)\]', html)
    if m:
        info["payment"] = re.findall(r'"([^"]+)"', m.group(1))

    # 홈페이지 URL
    m = re.search(r'"homepageUrl":\{"[^"]*":"[^"]*","url":"([^"]*)"', html)
    if m:
        info["homepage"] = m.group(1).replace("\\u002F", "/")

    # 예약 가능 여부
    if '"booking":true' in html:
        info["booking_available"] = True

    # 주차 정보
    m = re.search(r'"parkingInfo":\{[^}]*"parkingTypes":\[([^\]]*)\]', html)
    if m:
        info["parking"] = re.findall(r'"([^"]+)"', m.group(1))

    # 메뉴/가격 정보
    menu_pattern = r'"Menu:[^"]*":\{[^}]*"name":"([^"]*)"[^}]*"price":"([^"]*)"'
    menus = re.findall(menu_pattern, html)
    if menus:
        info["menus"] = [{"name": n, "price": p} for n, p in menus]

    # 설명
    m = re.search(r'"description":"([^"]{10,500})"', html)
    if m:
        desc = m.group(1).replace("\\n", "\n").replace("\\u002F", "/")
        if "클라이밍" in desc or "볼더링" in desc or "암벽" in desc:
            info["description"] = desc

    return info


def fetch_gym_detail(place_id: str) -> dict:
    """개별 암장 상세 정보 크롤링"""
    url = f"https://m.place.naver.com/place/{place_id}/home"
    resp = safe_request(url, headers=MOBILE_HEADERS, delay=DETAIL_DELAY)
    if not resp:
        return {}
    html = resp.text
    info = parse_detail_from_apollo(html)
    info["naver_place_url"] = f"https://map.naver.com/p/entry/place/{place_id}"
    info["place_id"] = place_id
    return info


# ── 3단계: Markdown 저장 ─────────────────────────────

DAY_ORDER = {"월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6}

def format_business_hours(hours: list[dict]) -> str:
    """영업시간을 Markdown 테이블로 포맷"""
    if not hours:
        return "영업시간 정보 없음"

    # 요일 순 정렬
    sorted_hours = sorted(hours, key=lambda h: DAY_ORDER.get(h["day"], 99))

    lines = ["| 요일 | 영업시간 | 휴식시간 |", "|------|----------|----------|"]
    for h in sorted_hours:
        breaks = ""
        if h.get("break"):
            breaks = ", ".join(f'{b["start"]}~{b["end"]}' for b in h["break"])
        lines.append(f'| {h["day"]} | {h["open"]} ~ {h["close"]} | {breaks or "-"} |')
    return "\n".join(lines)


def extract_region(address: str) -> str:
    """주소에서 지역 추출 (시/도 + 시/구)"""
    if not address:
        return "기타"
    parts = address.split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    return parts[0] if parts else "기타"


def save_gym_markdown(gym: dict, detail: dict):
    """암장 정보를 Markdown 파일로 저장"""
    name = detail.get("name") or gym.get("name", "Unknown")
    place_id = gym.get("id") or detail.get("place_id", "unknown")
    address = detail.get("road_address") or gym.get("address", "")
    region = extract_region(address)

    # 파일명 생성
    filename = f"{slugify(name)}-{place_id}.md"
    filepath = OUTPUT_DIR / filename

    now = datetime.now().strftime("%Y-%m-%d")

    # 태그 생성
    tags = ["클라이밍", "암장"]
    if "볼더링" in name:
        tags.append("볼더링")
    region_parts = region.split()
    tags.extend(region_parts)

    # Markdown 내용 구성
    lines = [
        "---",
        f'title: "{name}"',
        f'tags: [{", ".join(tags)}]',
        f'created: {now}',
        f'updated: {now}',
        f'place_id: "{place_id}"',
        f'region: "{region}"',
        "---",
        "",
        f"# {name}",
        "",
    ]

    # 기본 정보
    lines.append("## 기본 정보")
    lines.append("")
    lines.append(f"- **카테고리**: {detail.get('category', gym.get('category', '암벽등반'))}")
    lines.append(f"- **도로명 주소**: {detail.get('road_address', address)}")
    if detail.get("jibun_address"):
        lines.append(f"- **지번 주소**: {detail['jibun_address']}")
    if detail.get("phone"):
        lines.append(f"- **전화 (예약)**: {detail['phone']}")
    if detail.get("phone_direct"):
        lines.append(f"- **전화 (직통)**: {detail['phone_direct']}")
    if detail.get("longitude") and detail.get("latitude"):
        lines.append(f"- **좌표**: {detail['latitude']}, {detail['longitude']}")
    lines.append("")

    # 영업시간
    lines.append("## 영업시간")
    lines.append("")
    if detail.get("business_status_desc"):
        lines.append(f"**현재 상태**: {detail.get('business_status', '')} ({detail['business_status_desc']})")
        lines.append("")
    lines.append(format_business_hours(detail.get("business_hours", [])))
    lines.append("")
    if detail.get("notice"):
        lines.append(f"> **공지**: {detail['notice']}")
        lines.append("")

    # 가격/메뉴 정보
    if detail.get("menus"):
        lines.append("## 이용 요금")
        lines.append("")
        lines.append("| 항목 | 가격 |")
        lines.append("|------|------|")
        for menu in detail["menus"]:
            lines.append(f'| {menu["name"]} | {menu["price"]} |')
        lines.append("")

    # 편의시설
    if detail.get("conveniences"):
        lines.append("## 편의시설")
        lines.append("")
        lines.append(", ".join(detail["conveniences"]))
        lines.append("")

    # 결제 정보
    if detail.get("payment"):
        lines.append("## 결제 수단")
        lines.append("")
        lines.append(", ".join(detail["payment"]))
        lines.append("")

    # 주차 정보
    if detail.get("parking"):
        lines.append("## 주차")
        lines.append("")
        lines.append(", ".join(detail["parking"]))
        lines.append("")

    # 리뷰
    reviews = []
    if detail.get("visitor_reviews"):
        reviews.append(f"방문자 리뷰 {detail['visitor_reviews']}건")
    if detail.get("blog_reviews"):
        reviews.append(f"블로그 리뷰 {detail['blog_reviews']}건")
    if reviews:
        lines.append("## 리뷰")
        lines.append("")
        lines.append(", ".join(reviews))
        lines.append("")

    # 링크
    lines.append("## 링크")
    lines.append("")
    naver_url = detail.get("naver_place_url", f"https://map.naver.com/p/entry/place/{place_id}")
    lines.append(f"- **네이버 플레이스**: {naver_url}")
    if detail.get("homepage"):
        lines.append(f"- **홈페이지**: {detail['homepage']}")
    if detail.get("naver_blog"):
        lines.append(f"- **네이버 블로그**: {detail['naver_blog']}")
    if detail.get("booking_available"):
        lines.append(f"- **네이버 예약**: 가능")
    lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return filepath


# ── 4단계: 인덱스 생성 ───────────────────────────────

def generate_index(gyms_data: list[dict]):
    """전국 암장 인덱스 파일 생성"""
    now = datetime.now().strftime("%Y-%m-%d")

    # 지역별 그룹핑
    by_region = {}
    for g in gyms_data:
        region = g.get("region", "기타")
        by_region.setdefault(region, []).append(g)

    lines = [
        "---",
        'title: "전국 클라이밍 암장 목록"',
        "tags: [클라이밍, 암장, 인덱스]",
        f"created: {now}",
        f"updated: {now}",
        "---",
        "",
        "# 전국 클라이밍 암장 목록",
        "",
        f"총 **{len(gyms_data)}개** 암장 (업데이트: {now})",
        "",
    ]

    for region in sorted(by_region.keys()):
        gyms = sorted(by_region[region], key=lambda g: g.get("name", ""))
        lines.append(f"## {region} ({len(gyms)}개)")
        lines.append("")
        for g in gyms:
            name = g.get("name", "?")
            addr = g.get("address", "")
            fname = g.get("filename", "")
            hours_summary = g.get("hours_summary", "")
            line = f"- [{name}]({fname})"
            if hours_summary:
                line += f" — {hours_summary}"
            lines.append(line)
        lines.append("")

    index_path = OUTPUT_DIR / "_index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[INDEX] 인덱스 생성: {index_path}")


def summarize_hours(hours: list[dict]) -> str:
    """영업시간 요약 문자열"""
    if not hours:
        return ""
    times = set()
    for h in hours:
        times.add(f'{h["open"]}~{h["close"]}')
    if len(times) == 1:
        return f"매일 {times.pop()}"
    return f"{len(hours)}일 운영"


# ── 메인 실행 ────────────────────────────────────────

def main():
    print("=" * 60)
    print("[CLIMB] 전국 클라이밍 암장 정보 크롤러")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1) 전국 검색
    print("\n[1/3] 전국 암장 검색 중...")
    all_gyms = collect_all_gyms()
    print(f"\n[OK] 총 {len(all_gyms)}개 암장 발견")

    # 중간 저장
    raw_path = DATA_DIR / "gyms_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_gyms, f, ensure_ascii=False, indent=2)
    print(f"[SAVE] 원시 데이터 저장: {raw_path}")

    # 2) 상세 정보 수집
    print(f"\n[2/3] 각 암장 상세 정보 수집 중... ({len(all_gyms)}개)")
    gyms_data = []
    for i, (place_id, gym) in enumerate(all_gyms.items(), 1):
        name = gym.get("name", "?")
        print(f"  [{i}/{len(all_gyms)}] {name} (ID: {place_id})")
        detail = fetch_gym_detail(place_id)

        # Markdown 저장
        filepath = save_gym_markdown(gym, detail)

        gyms_data.append({
            "name": detail.get("name") or name,
            "region": extract_region(detail.get("road_address") or gym.get("address", "")),
            "address": detail.get("road_address") or gym.get("address", ""),
            "filename": filepath.name,
            "hours_summary": summarize_hours(detail.get("business_hours", [])),
        })

        time.sleep(DETAIL_DELAY)

    # 상세 데이터 저장
    detail_path = DATA_DIR / "gyms_detail.json"
    with open(detail_path, "w", encoding="utf-8") as f:
        json.dump(gyms_data, f, ensure_ascii=False, indent=2)

    # 3) 인덱스 생성
    print(f"\n[3/3] 인덱스 생성 중...")
    generate_index(gyms_data)

    print("\n" + "=" * 60)
    print(f"[OK] 완료! {len(gyms_data)}개 암장 정보 저장")
    print(f"[DIR] 저장 위치: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    # 이전 실행 데이터에서 이어서 할 수 있도록
    if "--resume" in sys.argv and (DATA_DIR / "gyms_raw.json").exists():
        print("[RESUME] 이전 검색 데이터에서 이어서 상세 수집...")
        with open(DATA_DIR / "gyms_raw.json", encoding="utf-8") as f:
            all_gyms = json.load(f)
        # 이미 저장된 파일 확인
        existing = {p.stem.split("-")[-1] for p in OUTPUT_DIR.glob("*.md") if p.name != "_index.md"}
        remaining = {k: v for k, v in all_gyms.items() if k not in existing}
        print(f"  기존 {len(existing)}개, 남은 {len(remaining)}개")

        gyms_data = []
        for i, (place_id, gym) in enumerate(remaining.items(), 1):
            name = gym.get("name", "?")
            print(f"  [{i}/{len(remaining)}] {name}")
            detail = fetch_gym_detail(place_id)
            filepath = save_gym_markdown(gym, detail)
            gyms_data.append({
                "name": detail.get("name") or name,
                "region": extract_region(detail.get("road_address") or gym.get("address", "")),
                "address": detail.get("road_address") or gym.get("address", ""),
                "filename": filepath.name,
                "hours_summary": summarize_hours(detail.get("business_hours", [])),
            })
            time.sleep(DETAIL_DELAY)

        # 기존 파일도 포함하여 인덱스 재생성
        for md_file in OUTPUT_DIR.glob("*.md"):
            if md_file.name == "_index.md":
                continue
            if md_file.stem.split("-")[-1] in existing:
                content = md_file.read_text(encoding="utf-8")
                m_name = re.search(r'^# (.+)$', content, re.MULTILINE)
                m_region = re.search(r'^region: "(.+)"$', content, re.MULTILINE)
                gyms_data.append({
                    "name": m_name.group(1) if m_name else md_file.stem,
                    "region": m_region.group(1) if m_region else "기타",
                    "address": "",
                    "filename": md_file.name,
                    "hours_summary": "",
                })

        generate_index(gyms_data)
        print(f"\n[OK] 완료!")
    else:
        main()
