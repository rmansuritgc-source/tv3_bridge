
from flask import Flask, Response, request
import requests
from urllib.parse import urljoin

app = Flask(__name__)

TARGET_URL = "https://live.irib.ir/live/smil:tv3.smil/playlist.m3u8"
HEADERS = {
    "Referer": "https://tv3.ir/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

@app.route('/')
def proxy_master():
    try:
        r = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        lines = r.text.split('\n')
        new_lines = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                absolute_url = urljoin(TARGET_URL, line)
                new_lines.append(f"/sub?url={absolute_url}")
            else:
                new_lines.append(line)
        return Response('\n'.join(new_lines), mimetype="application/vnd.apple.mpegurl")
    except Exception as e:
        return Response(str(e), status=500)

@app.route('/sub')
def proxy_sub():
    url = request.args.get('url')
    try:
        r = requests.get(url, headers=HEADERS, stream=True, timeout=10)
        
        # رفع باگ: اگر فایل قطعه ویدیویی (.ts) است، آن را مستقیماً و بدون تغییر استریم کن
        if '.ts' in url or r.headers.get('Content-Type') in ['video/mp2t', 'video/MP2T']:
            return Response(r.iter_content(chunk_size=1024*1024), content_type='video/MP2T')
            
        # اگر فایل لیست پخش است، آن را بازنویسی کن
        lines = r.text.split('\n')
        new_lines = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                absolute_url = urljoin(url, line)
                new_lines.append(f"/sub?url={absolute_url}")
            else:
                new_lines.append(line)
        return Response('\n'.join(new_lines), mimetype="application/vnd.apple.mpegurl")
    except Exception as e:
        return Response(str(e), status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
