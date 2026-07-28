#!/usr/bin/env python3
import argparse
import base64
import hashlib
import hmac
import json
import sys
import time
import urllib.parse
import urllib.request


def build_signed_url(webhook: str, secret: str | None) -> str:
    if not secret:
        return webhook
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    sign = base64.b64encode(
        hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
    ).decode()
    sign = urllib.parse.quote_plus(sign)
    sep = '&' if '?' in webhook else '?'
    return f"{webhook}{sep}timestamp={timestamp}&sign={sign}"


def main() -> int:
    parser = argparse.ArgumentParser(description='Send DingTalk custom robot webhook message')
    parser.add_argument('--webhook', required=True, help='Full DingTalk webhook URL')
    parser.add_argument('--secret', help='Optional SEC... signing secret')
    parser.add_argument('--text', required=True, help='Text content to send')
    args = parser.parse_args()

    url = build_signed_url(args.webhook, args.secret)
    payload = json.dumps({
        'msgtype': 'text',
        'text': {'content': args.text},
    }, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode('utf-8', 'ignore')
        print(body)
        data = json.loads(body)
        return 0 if data.get('errcode') == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
