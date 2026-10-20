"""Sube el episodio a YouTube (YouTube Data API v3): video, miniatura y subtítulos.

Credenciales por variables de entorno (en GitHub: Settings → Secrets → Actions):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

Uso:
  python -m md.upload_youtube build/<slug> [--privacy private|unlisted|public] [--publish-at 2026-11-01T15:00:00Z]

Por defecto sube como PRIVADO para revisarlo antes de publicarlo.
"""
import argparse
import json
import os
from pathlib import Path


def client():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], client_id=os.environ["YT_CLIENT_ID"],
                        client_secret=os.environ["YT_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token",
                        scopes=["https://www.googleapis.com/auth/youtube.upload",
                                "https://www.googleapis.com/auth/youtube.force-ssl"])
    return build("youtube", "v3", credentials=creds)


def main():
    from googleapiclient.http import MediaFileUpload
    ap = argparse.ArgumentParser()
    ap.add_argument("build_dir")
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    ap.add_argument("--publish-at", help="programar publicación (RFC3339, requiere privacy=private)")
    a = ap.parse_args()
    d = Path(a.build_dir)
    meta = json.loads((d / "youtube.json").read_text())
    slug = d.name
    yt = client()
    status = {"privacyStatus": a.privacy, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}
    if a.publish_at:
        status["publishAt"] = a.publish_at
    body = {"snippet": {"title": meta["title"][:100], "description": meta["description"][:5000],
                        "tags": meta.get("tags", []), "categoryId": meta.get("categoryId", "27"),
                        "defaultLanguage": "es", "defaultAudioLanguage": meta.get("defaultAudioLanguage", "es-419")},
            "status": status}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(d / f"{slug}.mp4"), chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        st, resp = req.next_chunk()
        if st:
            print(f"subiendo… {int(st.progress() * 100)}%", flush=True)
    vid = resp["id"]
    print("video:", f"https://youtu.be/{vid}")
    try:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(d / "thumbnail.jpg"))).execute()
    except Exception as e:  # requiere canal verificado
        print("miniatura no aplicada:", e)
    srt = d / f"{slug}.es.srt"
    if srt.exists():
        yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "es", "name": "Español"}},
                             media_body=MediaFileUpload(str(srt), mimetype="application/octet-stream")).execute()
        print("subtítulos cargados")
    (d / "youtube_result.json").write_text(json.dumps({"id": vid, "url": f"https://youtu.be/{vid}"}))


if __name__ == "__main__":
    main()
