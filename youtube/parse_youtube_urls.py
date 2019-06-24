
import re
try:
    from urlib.parse import urlparse
except:
    from urlparse import urlparse
from urllib2 import unquote
from ural import normalize_url

def clean_url(url):
    if url.endswith("/live"):
        url = url[:-5]
    if url.endswith("youtube%5D"):
        url = url[:-10]
    elif url.endswith("%5D"):
        url = url[:-3]
    url = url.replace("?%26", "?")
    url = url.replace("?gl=FR&hl=fr", "")
    url = url.replace("?hl=fr&gl=FR", "")
    url = url.replace("?feature=fbr", "")
    url = url.replace("?hl=en", "")
    url = url.replace("/%E2%80%8Bwatch", "/watch")
    url = url.replace("/watch%20?", "/watch?")
    url = url.replace('youtu.be/channel/', 'youtube.com/channel/')
    url = url.replace('youtube.com/profile?user=', 'youtube.com/user/')
    return url

def parse_youtube_url(url):
    url = clean_url(url)
    u = normalize_url(url, strip_lang_subdomains=True, strip_trailing_slash=True)
    parsed = urlparse(url)
    # URL pattern youtu.be/VIDEO_ID
    if parsed.netloc == 'youtu.be':
        if "/" not in u:
            return "home", None
        url_id = u.split("/")[1]
        url_id = u.split("?")[0]
        url_id = u.split("%")[0]
        return "video", url_id
    # URL pattern youtube.googleapis.com/v/VIDEO_ID
    if parsed.netloc == 'youtube.googleapis.com':
        if "/v/" in u:
            url_id = u.split("/")[2]
        else:
            raise(Exception("Wrong url format %s" % u))
        return "video", url_id
    if parsed.netloc in ['img.youtube.com', 'gaming.youtube.com', 'music.youtube.com', 'studio.youtube.com']:
        return "irrelevant", None
    if parsed.netloc.endswith('youtube.com'):
        if u in ["youtube.com"] and not parsed.fragment:
            return "home", None
        stem0 = parsed.path.split("/")[1]
        stem1 = parsed.path.split("/")[2] if "/" in parsed.path.lstrip("/") else None
        queryargs = parsed.query.split("&")
        if stem0 in ["t", "yt", "results", "playlist", "artist", "channels", "audiolibrary", "feed", "intl", "musicpremium", "premium", "show", "watch_videos", "comment", "creators", "profile_redirector", "static", "view_play_list", "index"]:
            return "irrelevant", None
        # URL pattern youtube.com/channel/CHANNEL_ID
        if stem0 == "channel":
            return "channel", stem1
        # URL pattern youtube.com/user/USER_ID
        if stem0 in ["user", "c"]:
            return "user", stem1
        # URL pattern youtube.com/profile_videos?user=USER_ID
        if stem0 == "attribution_link":
            uarg = [arg for arg in queryargs if arg.startswith("u=")]
            if len(uarg):
                return parse_youtube_url("http://youtube.com" + unquote(uarg[0].split("=")[1]))
        if stem0 in ["profile_videos", "subscription_center"]:
            uarg = [arg for arg in queryargs if arg.startswith("user=") or arg.startswith("add_user=")]
            if len(uarg):
                return "user", uarg[0].split("=")[1]
        # URL pattern youtube.com/v/VIDEO_ID
        if stem0 in ["v", "embed", "video"]:
            return "video", stem1
        # URL pattern youtube.com/watch?v=VIDEO_ID
        if stem0 in ["watch", "redirect", "comment_servlet", "all_comments", "watch_popup"]:
            varg = [arg for arg in queryargs if arg.startswith("v=")]
            if len(varg):
                return "video", varg[0].split("=")[1]
            return "video", None
        if stem0 in ["edit", "swf"]:
            varg = [arg for arg in queryargs if arg.startswith("video_id=")]
            if len(varg):
                return "video", varg[0].split("=")[1]
            return "video", None
        # URL pattern youtube.com/#%2Fwatch%3Fv%3DVIDEO_ID
        if "v%3D" in parsed.query:
            fquery = unquote(parsed.query)
            queryargs = fquery.split("?")[1].split("&")
            varg = [arg for arg in queryargs if arg.startswith("v=")]
            if len(varg):
                return "video", varg[0].split("=")[1]
        if "v%3D" in parsed.fragment:
            fquery = unquote(parsed.fragment)
            queryargs = fquery.split("?")[1].split("&")
            varg = [arg for arg in queryargs if arg.startswith("v=")]
            if len(varg):
                return "video", varg[0].split("=")[1]
        if "continue=" in parsed.query:
            urlarg = [arg for arg in queryargs if arg.startswith("continue=")][0].split("=")[1]
            return parse_youtube_url(unquote(urlarg))
        if not stem1 and (not parsed.query or parsed.query in ["sub_confirmation=1"]) and not parsed.fragment:
            return "user", stem0
    return "error", None

def _extract_YT_video_id(u):
    l["yt_video_id"]  = [q.split("=")[1] for q in u.split("?")[-1].split("&") if q.startswith("v=")][0]
    pass

def _extract_YT_channel_id(u):
    u = u[12:]
    if u.startswith("channel/"):
        pass
    elif u.startswith("user/"):
        pass
    elif u.startswith("c/"):
        pass
    elif "?" not in u or "v=" not in u:
        pass
    pass

def get_channel_from_url(u):
    try:
        typ, uid = parse_youtube_url(u)
        if typ in ("irrelevant", "error"):
            return None
        if typ == "channel":
            return uid
        if typ == "user":
            return get_channel_from_user_id(uid)
        if typ == "video":
            return get_channel_from_video_id(uid)
        raise(Exception("ERROR: %s does not seem attachable to a YouTube channel" % u))
    except Exception as e:
        pass

def get_channel_from_user_id(uid):
    pass

def get_channel_from_video_id(vid):
    pass

if __name__ == "__main__":
    import csv
    import sys
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "youtube-inlinks.csv"
    csv_field = sys.argv[2] if len(sys.argv) > 2 else "youtube_url"
    with open(csv_file) as f:
        for l in csv.DictReader(f):
            try:
                url_type, url_id = parse_youtube_url(l[csv_field])
                print(l[csv_field], url_type, url_id)
            except Exception as e:
                print("ERROR %s: %s" % (type(e), e), l)
                exit(1)


