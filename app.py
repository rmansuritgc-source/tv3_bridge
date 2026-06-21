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
                if not line.startswith('http'):
                    absolute_url = urljoin(TARGET_URL, line)
                    new_lines.append(f"/sub?url={absolute_url}")
                else:
                    new_lines.append(f"/sub?url={line}")
            else:
                new_lines.append(line)
        return Response('\n'.join(new_lines), content_type="application/vnd.apple.mpegurl")
    except Exception as e:
        return Response(str(e), status=500)

@app.route('/sub')
def proxy_sub():
    url = request.args.get('url')
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        lines = r.text.split('\n')
        new_lines = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                if not line.startswith('http'):
                    absolute_url = urljoin(url, line)
                    new_lines.append(absolute_url)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        return Response('\n'.join(new_lines), content_type="application/vnd.apple.mpegurl")
    except Exception as e:
        return Response(str(e), status=500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
