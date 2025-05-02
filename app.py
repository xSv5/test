from flask import Flask, request, Response
import requests

app = Flask(__name__)
TARGET_URL = 'https://xsv4mailsender.pythonanywhere.com/verify'

@app.route('/verify', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy():
    resp = requests.request(
        method=request.method,
        url=TARGET_URL,
        headers={k: v for k, v in request.headers if k.lower() != 'host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )
    excluded = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(k, v) for k, v in resp.raw.headers.items() if k.lower() not in excluded]
    return Response(resp.content, resp.status_code, headers)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
