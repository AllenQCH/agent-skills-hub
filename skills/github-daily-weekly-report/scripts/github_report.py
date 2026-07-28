#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from collections import Counter, defaultdict

API = 'https://api.github.com'


def load_token():
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return token.strip()
    hermes_home = os.environ.get('HERMES_HOME') or os.path.expanduser('~/.hermes')
    env_path = os.path.join(hermes_home, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('GITHUB_TOKEN='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    return None


def gh_get(path, token, params=None):
    url = API + path
    if params:
        from urllib.parse import urlencode
        url += '?' + urlencode(params)
    req = urllib.request.Request(url, headers={
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'Hermes-GitHub-Report/1.0'
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def parse_iso(s):
    if not s:
        return None
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))


def in_window(ts, start, end):
    if not ts:
        return False
    return start <= ts <= end


def summarize_repo(repo, token, start, end):
    owner, name = repo.split('/', 1)
    pulls = gh_get(f'/repos/{owner}/{name}/pulls', token, {
        'state': 'all', 'sort': 'updated', 'direction': 'desc', 'per_page': 100
    })
    issues = gh_get(f'/repos/{owner}/{name}/issues', token, {
        'state': 'all', 'since': start.isoformat().replace('+00:00', 'Z'), 'per_page': 100
    })
    runs = gh_get(f'/repos/{owner}/{name}/actions/runs', token, {'per_page': 50}).get('workflow_runs', [])
    releases = gh_get(f'/repos/{owner}/{name}/releases', token, {'per_page': 20})

    pr_opened = []
    pr_merged = []
    pr_open_backlog = []
    author_counter = Counter()
    for pr in pulls:
        author = (pr.get('user') or {}).get('login') or 'unknown'
        created = parse_iso(pr.get('created_at'))
        merged = parse_iso(pr.get('merged_at'))
        updated = parse_iso(pr.get('updated_at'))
        if in_window(created, start, end):
            pr_opened.append(pr)
            author_counter[author] += 1
        if in_window(merged, start, end):
            pr_merged.append(pr)
            author_counter[author] += 1
        if pr.get('state') == 'open' and updated and updated >= start:
            pr_open_backlog.append(pr)

    issue_opened = []
    issue_closed = []
    risk_issues = []
    for it in issues:
        if 'pull_request' in it:
            continue
        created = parse_iso(it.get('created_at'))
        closed = parse_iso(it.get('closed_at'))
        if in_window(created, start, end):
            issue_opened.append(it)
            author = (it.get('user') or {}).get('login') or 'unknown'
            author_counter[author] += 1
        if in_window(closed, start, end):
            issue_closed.append(it)
        labels = {x.get('name', '').lower() for x in it.get('labels', [])}
        if it.get('state') == 'open' and labels.intersection({'p0', 'p1', 'priority:high', 'high', 'critical', 'bug'}):
            risk_issues.append(it)

    failed_runs = []
    failed_by_name = Counter()
    for run in runs:
        updated = parse_iso(run.get('updated_at'))
        if run.get('conclusion') == 'failure' and in_window(updated, start, end):
            failed_runs.append(run)
            failed_by_name[run.get('name') or 'unnamed-workflow'] += 1

    new_releases = []
    for rel in releases:
        published = parse_iso(rel.get('published_at'))
        if in_window(published, start, end):
            new_releases.append(rel)

    return {
        'repo': repo,
        'pr_opened': pr_opened,
        'pr_merged': pr_merged,
        'pr_open_backlog': pr_open_backlog[:5],
        'issue_opened': issue_opened,
        'issue_closed': issue_closed,
        'risk_issues': risk_issues[:5],
        'failed_runs': failed_runs[:5],
        'failed_by_name': failed_by_name,
        'new_releases': new_releases,
        'authors': author_counter,
    }


def render(mode, repos, start, end, reports):
    title = 'GitHub 日报' if mode == 'daily' else 'GitHub 周报'
    lines = [f'# {title}', f'> 时间窗口：{start.strftime("%Y-%m-%d %H:%M UTC")} ~ {end.strftime("%Y-%m-%d %H:%M UTC")}', f'> 仓库：{", ".join(repos)}', '']
    totals = defaultdict(int)
    all_authors = Counter()
    overall_risks = []
    for r in reports:
        totals['pr_opened'] += len(r['pr_opened'])
        totals['pr_merged'] += len(r['pr_merged'])
        totals['issue_opened'] += len(r['issue_opened'])
        totals['issue_closed'] += len(r['issue_closed'])
        totals['failed_runs'] += len(r['failed_runs'])
        totals['new_releases'] += len(r['new_releases'])
        all_authors.update(r['authors'])
        if r['failed_runs']:
            overall_risks.append(f"{r['repo']} 有 {len(r['failed_runs'])} 个失败 CI")
        if r['risk_issues']:
            overall_risks.append(f"{r['repo']} 有 {len(r['risk_issues'])} 个高优 open issue")
        if len(r['pr_open_backlog']) >= 5:
            overall_risks.append(f"{r['repo']} 活跃 open PR 较多，需关注积压")

    lines += [
        '## 总览',
        f'- 新开 PR：{totals["pr_opened"]}',
        f'- 合并 PR：{totals["pr_merged"]}',
        f'- 新增 Issue：{totals["issue_opened"]}',
        f'- 关闭 Issue：{totals["issue_closed"]}',
        f'- 失败 CI：{totals["failed_runs"]}',
        f'- 新 Release：{totals["new_releases"]}',
        ''
    ]

    lines.append('## 各仓库摘要')
    for r in reports:
        lines += [
            f'### {r["repo"]}',
            f'- PR：新开 {len(r["pr_opened"])}，合并 {len(r["pr_merged"])}，活跃 open {len(r["pr_open_backlog"])}',
            f'- Issue：新增 {len(r["issue_opened"])}，关闭 {len(r["issue_closed"])}，高优未关 {len(r["risk_issues"])}',
            f'- CI：失败 {len(r["failed_runs"])}',
            f'- Release：{len(r["new_releases"])}',
        ]
        if r['failed_by_name']:
            top_fail = ', '.join(f'{k} x{v}' for k, v in r['failed_by_name'].most_common(3))
            lines.append(f'- 重复失败 workflow：{top_fail}')
        if r['risk_issues']:
            lines.append('- 风险 issue：' + '；'.join(f"#{x['number']} {x['title']}" for x in r['risk_issues'][:3]))
        if r['pr_merged']:
            lines.append('- 关键合并：' + '；'.join(f"#{x['number']} {x['title']}" for x in r['pr_merged'][:3]))
        lines.append('')

    lines.append('## 活跃作者')
    if all_authors:
        for i, (name, count) in enumerate(all_authors.most_common(10), 1):
            lines.append(f'{i}. {name}：{count}')
    else:
        lines.append('- 无')
    lines.append('')

    lines.append('## 风险摘要')
    if overall_risks:
        for item in overall_risks[:10]:
            lines.append(f'- {item}')
    else:
        lines.append('- 本周期未见明显风险项')
    lines.append('')

    lines.append('## 建议关注')
    if totals['failed_runs']:
        lines.append('- 先处理失败的 workflow，避免 CI 红灯持续积压')
    if totals['issue_opened'] > totals['issue_closed']:
        lines.append('- 本周期 issue 净增，建议确认 backlog 是否在扩张')
    if totals['pr_opened'] > totals['pr_merged']:
        lines.append('- PR 打开多于合并，建议关注 review / merge 节奏')
    if not any([totals['failed_runs'], totals['issue_opened'] > totals['issue_closed'], totals['pr_opened'] > totals['pr_merged']]):
        lines.append('- 节奏健康，继续按当前方式推进')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['daily', 'weekly'], required=True)
    ap.add_argument('--repos', nargs='+', required=True)
    args = ap.parse_args()

    token = load_token()
    if not token:
        print('ERROR: missing GITHUB_TOKEN', file=sys.stderr)
        sys.exit(2)

    end = dt.datetime.now(dt.timezone.utc)
    delta = dt.timedelta(days=1 if args.mode == 'daily' else 7)
    start = end - delta

    reports = [summarize_repo(repo, token, start, end) for repo in args.repos]
    print(render(args.mode, args.repos, start, end, reports))


if __name__ == '__main__':
    main()
