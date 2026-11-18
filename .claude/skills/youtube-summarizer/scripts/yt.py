#!/usr/bin/env python3
"""youtube-summarizer 보조 스크립트.

사용법:
  yt.py set <URL>      고정 URL 저장 (config.json)
  yt.py get            고정 URL 출력
  yt.py fetch [URL]    자막을 [mm:ss] 타임스탬프 형식으로 출력 (URL 생략 시 고정 URL 사용)
"""
import json
import re
import sys
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent / "config.json"


def load_config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"fixed_url": "", "languages": ["ko", "en"]}


def save_config(cfg):
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def video_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|live/|embed/)([A-Za-z0-9_-]{11})", url)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url
    sys.exit(f"오류: 유튜브 영상 ID를 찾을 수 없습니다: {url}")


def ts(seconds):
    s = int(seconds)
    h, m, s = s // 3600, s % 3600 // 60, s % 60
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def fetch(url, languages):
    vid = video_id(url)
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        sys.exit("오류: pip install youtube-transcript-api 를 먼저 실행하세요.")
    api = YouTubeTranscriptApi()
    try:
        try:
            transcript = api.fetch(vid, languages=languages)
        except Exception:
            # 지정 언어가 없으면 사용 가능한 첫 자막(자동 생성 포함)을 사용
            transcript = next(iter(api.list(vid))).fetch()
    except Exception as e:
        sys.exit(f"오류: 자막을 가져오지 못했습니다 ({type(e).__name__}). "
                 "자막이 없는 영상이거나 youtube.com 네트워크 접근이 막혀 있을 수 있습니다.")
    print(f"# video_id: {vid}\n# url: https://www.youtube.com/watch?v={vid}")
    for snip in transcript:
        text = snip.text.replace("\n", " ").strip()
        if text:
            print(f"[{ts(snip.start)}] {text}")


def main():
    args = sys.argv[1:]
    cfg = load_config()
    if not args:
        sys.exit(__doc__)
    cmd = args[0]
    if cmd == "set" and len(args) == 2:
        video_id(args[1])
        cfg["fixed_url"] = args[1]
        save_config(cfg)
        print(f"고정 URL 저장됨: {args[1]}")
    elif cmd == "get":
        print(cfg.get("fixed_url") or "(고정 URL 없음)")
    elif cmd == "fetch":
        url = args[1] if len(args) > 1 else cfg.get("fixed_url")
        if not url:
            sys.exit("오류: URL이 없습니다. 'yt.py set <URL>' 로 고정하거나 URL을 직접 넘기세요.")
        fetch(url, cfg.get("languages") or ["ko", "en"])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
