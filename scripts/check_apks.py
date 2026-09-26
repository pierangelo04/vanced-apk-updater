#!/usr/bin/env python3
"""Controlla aggiornamenti APK su LeeAPK per YouTube Vanced e YouTube Music Premium.

Confronta versione+build con state.json e stampa su stdout un JSON con
gli eventuali aggiornamenti (inclusi i link diretti agli APK).
Uso: python3 check_apks.py [--state PATH] [--out PATH]
"""

import argparse
import json
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

APPS = {
    "vanced": {
        "label": "YouTube Vanced",
        "page": "https://leeapk.com/youtube-vanced-mod-apk/",
    },
    "music": {
        "label": "YouTube Music Premium",
        "page": "https://leeapk.com/youtube-music-premium-mod-apk/",
    },
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_app(key: str, cfg: dict) -> dict:
    html = fetch(cfg["page"])
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    title = m.group(1).strip() if m else ""
    ver = re.search(r"v(\d+\.\d+\.\d+)", title)
    version = ver.group(1) if ver else None
    build = None
    m2 = re.search(r"Build\s+(\d+)", title)
    if m2:
        build = m2.group(1)
    else:
        m3 = re.search(r'"softwareVersion"\s*:\s*"[^"]*?(\d{6,})', html)
        if m3:
            build = m3.group(1)
    if not version:
        raise RuntimeError(f"versione non trovata nella pagina {cfg['page']}")

    m = re.search(r'href="(https://leeapk\.com/[^"]+/download/)"', html)
    if not m:
        raise RuntimeError(f"pagina di download non trovata per {key}")
    dl_html = fetch(m.group(1))
    m = re.search(r'href="(https://cloud\.droidapks\.com/[^"]+?\.apk\?token=[^"]+)"', dl_html)
    if not m:
        raise RuntimeError(f"link APK diretto non trovato per {key}")
    apk_url = m.group(1)
    filename = apk_url.split("?")[0].rsplit("/", 1)[-1]
    return {
        "key": key,
        "label": cfg["label"],
        "version": version,
        "build": build,
        "apk_url": apk_url,
        "filename": filename,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="state.json")
    args = ap.parse_args()

    try:
        state = json.load(open(args.state, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}

    checked, updates = {}, []
    for key, cfg in APPS.items():
        try:
            info = parse_app(key, cfg)
        except Exception as exc:  # noqa: BLE001 - riporto l'errore nel JSON
            checked[key] = {"error": str(exc)}
            continue
        checked[key] = {"version": info["version"], "build": info["build"]}
        prev = state.get(key, {})
        if prev.get("version") != info["version"] or prev.get("build") != info["build"]:
            updates.append(info)

    out = {"updates": updates, "checked": checked}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
