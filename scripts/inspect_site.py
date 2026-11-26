#!/usr/bin/env python3
"""What an agent without JavaScript gets from a site: raw HTML facts and service files.

Read-only. Standard library only. Usage:

    python3 inspect_site.py https://example.com [--page /work/case/] [--json]

It fetches the home page (and any --page) the way a plain HTTP agent would: no JavaScript,
no cookies. It reports what can be measured mechanically. It does not judge what an agent
would answer: that needs a real reader (see SKILL.md, step 2).
"""
import argparse
import json
import random
import re
import string
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

UA = 'Mozilla/5.0 (compatible; readable-by-agents/1.0)'
AI_BOTS = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-User', 'Claude-SearchBot',
           'PerplexityBot', 'Google-Extended', 'CCBot', 'Applebot-Extended', 'Bytespider']
PLACEHOLDERS = ['00:00:00', 'Loading…', 'Loading...', '{{', '}}', 'undefined', 'NaN', 'lorem ipsum']
# Links to documents in an online editor: fetch tools often get only the app shell, not the text.
# "Publish to the web" (/pub) and export links serve plain text or a file, so they are left out.
DOC_LINK = re.compile(r'https?://(docs|drive)\.google\.com/', re.I)
DOC_LINK_OK = re.compile(r'/pub(html)?\b|[?&]export=|/export\b', re.I)
SKIP_TAGS = {'script', 'style', 'svg', 'template', 'noscript'}
BLOCK_TAGS = {'p', 'div', 'section', 'article', 'main', 'header', 'footer', 'nav', 'aside', 'li', 'ul', 'ol',
              'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'tr', 'td', 'th', 'dt', 'dd', 'dl', 'figure',
              'figcaption', 'blockquote', 'table', 'form', 'dialog', 'hr'}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def fetch(url, ua=UA, follow=True, limit=8, accept='text/html,*/*;q=0.8'):
    """Return dict: status, url, chain, headers, body (str), error. Records each redirect hop."""
    opener = urllib.request.build_opener(NoRedirect)
    chain = []
    current = url
    for _ in range(limit):
        req = urllib.request.Request(current, headers={'User-Agent': ua, 'Accept': accept})
        try:
            resp = opener.open(req, timeout=20)
            status, headers, raw = resp.status, resp.headers, resp.read()
        except urllib.error.HTTPError as e:
            status, headers, raw = e.code, e.headers, e.read()
        except Exception as e:  # network errors, TLS, timeouts
            return {'status': None, 'url': current, 'chain': chain, 'headers': {}, 'body': '', 'error': str(e)}
        if status in (301, 302, 303, 307, 308) and follow and headers.get('Location'):
            nxt = urllib.parse.urljoin(current, headers['Location'])
            chain.append(f'{status} {current} -> {nxt}')
            current = nxt
            continue
        charset = headers.get_content_charset() or 'utf-8'
        return {'status': status, 'url': current, 'chain': chain, 'headers': dict(headers.items()),
                'body': raw.decode(charset, 'replace'), 'error': None}
    return {'status': None, 'url': current, 'chain': chain, 'headers': {}, 'body': '', 'error': 'too many redirects'}


class Page(HTMLParser):
    """Collects metadata and the visible text an HTML-to-text reader would get."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.links, self.jsonld_types, self.mailto, self.doc_links = {}, [], [], [], []
        self.lang, self.title, self._in_title = None, '', False
        self.skip, self.text, self.scripts, self.script_bytes = 0, [], 0, 0
        self.h1_pos = self.main_pos = None
        self._jsonld = False
        self.noscript = False
        self.comments = []
        # images: alt text is all a text reader learns about an image
        self.img_total, self.img_alt, self.img_alt_empty, self.img_no_alt = 0, 0, 0, 0

    def handle_comment(self, data):
        text = data.strip()
        # functional markers (Cloudflare email_off, conditional comments) are not notes
        if not text or text.startswith('[if') or text.startswith('<!') or text.lower().strip('/') == 'email_off':
            return
        self.comments.append(re.sub(r'\s+', ' ', text)[:120])

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
        elif tag == 'title':
            self._in_title = True
        elif tag == 'meta':
            key = a.get('name') or a.get('property')
            if key and 'content' in a:
                self.meta[key.lower()] = a['content']
        elif tag == 'link':
            self.links.append(a)
        elif tag == 'a':
            href = a.get('href') or ''
            if href.startswith('mailto:'):
                self.mailto.append(href)
            elif DOC_LINK.match(href) and not DOC_LINK_OK.search(href):
                self.doc_links.append(href)
        elif tag == 'script':
            self.scripts += 1
            self._jsonld = a.get('type') == 'application/ld+json'
        elif tag == 'noscript':
            self.noscript = True
        elif tag == 'img' and not self.skip:
            self.img_total += 1
            if 'alt' not in a:
                self.img_no_alt += 1
            elif (a.get('alt') or '').strip():
                self.img_alt += 1
            else:
                self.img_alt_empty += 1
        if tag == 'h1' and self.h1_pos is None:
            self.h1_pos = self.getpos()
        if tag == 'main' and self.main_pos is None:
            self.main_pos = self.getpos()
        if tag in SKIP_TAGS:
            self.skip += 1
        if tag in BLOCK_TAGS:
            self.text.append('\n')

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
        if tag in SKIP_TAGS and self.skip:
            self.skip -= 1
        if tag in BLOCK_TAGS:
            self.text.append('\n')

    def handle_data(self, data):
        if self._in_title:
            self.title += data
            return
        if self._jsonld:
            try:
                d = json.loads(data)
                for item in d if isinstance(d, list) else [d]:
                    t = item.get('@type') if isinstance(item, dict) else None
                    if t:
                        self.jsonld_types.append(t if isinstance(t, str) else ','.join(t))
            except Exception:
                self.jsonld_types.append('(unparsable)')
            self._jsonld = False
        if self.skip:
            self.script_bytes += len(data)
            return
        self.text.append(data)


def offset_of(html, pos):
    """Convert HTMLParser (line, col) into a character offset in html."""
    if not pos:
        return None
    line, col = pos
    lines = html.split('\n')
    return sum(len(l) + 1 for l in lines[:line - 1]) + col


def visible_text(parser):
    txt = ''.join(parser.text)
    txt = re.sub(r'[ \t ]+', ' ', txt)
    return re.sub(r'\n\s*\n+', '\n', txt).strip()


def glued_breaks(html):
    """word<br>word with no space: readers that drop line breaks glue these words together."""
    out = []
    for m in re.finditer(r'([A-Za-zА-Яа-яЁё0-9.,!?:;%)])<br\s*/?>(?=[A-Za-zА-Яа-яЁё0-9(])', html):
        start = max(0, m.start() - 30)
        snippet = re.sub(r'<[^>]+>', '', html[start:m.end() + 30]).replace('\n', ' ')
        out.append(snippet.strip())
    return out


def robots_report(base):
    r = fetch(urllib.parse.urljoin(base, '/robots.txt'))
    rep = {'status': r['status'], 'content_type': r['headers'].get('Content-Type'), 'sitemaps': [],
           'content_signal': [], 'disallow_all_for': [], 'agents_named': []}
    if r['status'] != 200 or 'html' in (r['headers'].get('Content-Type') or ''):
        rep['note'] = 'missing or served as HTML (a soft 404 often returns the home page here)'
        return rep
    group, groups = [], []
    for raw in r['body'].splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line or ':' not in line:
            continue
        key, val = [s.strip() for s in line.split(':', 1)]
        k = key.lower()
        if k == 'user-agent':
            if group and group[-1][0] != 'ua':
                groups.append(group)
                group = []
            group.append(('ua', val))
        elif k == 'sitemap':
            rep['sitemaps'].append(val)
        elif k == 'content-signal':
            rep['content_signal'].append(val)
            group.append(('cs', val))
        else:
            group.append((k, val))
    if group:
        groups.append(group)
    for g in groups:
        uas = [v for k, v in g if k == 'ua']
        disallow_root = any(k == 'disallow' and v == '/' for k, v in g)
        for ua in uas:
            if ua != '*':
                rep['agents_named'].append(ua)
            if disallow_root and (ua == '*' or any(b.lower() == ua.lower() for b in AI_BOTS)):
                rep['disallow_all_for'].append(ua)
    return rep


def inspect_page(url):
    r = fetch(url)
    p = Page()
    if r['body']:
        try:
            p.feed(r['body'])
        except Exception as e:
            r['error'] = f'parse error: {e}'
    html = r['body']
    text = visible_text(p)
    first = min([x for x in (offset_of(html, p.h1_pos), offset_of(html, p.main_pos)) if x is not None], default=None)
    alternates = [f"{l.get('type')} {l.get('href')}" for l in p.links if 'alternate' in (l.get('rel') or '')]
    canonical = [l.get('href') for l in p.links if (l.get('rel') or '') == 'canonical']
    return {
        'url': url, 'final_url': r['url'], 'status': r['status'], 'redirects': r['chain'], 'error': r['error'],
        'bytes': len(html.encode('utf-8')), 'x_robots_tag': r['headers'].get('X-Robots-Tag') or r['headers'].get('x-robots-tag'),
        'link_header': r['headers'].get('Link') or r['headers'].get('link'),
        'lang': p.lang, 'title': p.title.strip(), 'description': p.meta.get('description'),
        'canonical': canonical, 'og_title': p.meta.get('og:title'), 'og_image': p.meta.get('og:image'),
        'jsonld_types': p.jsonld_types, 'alternates': alternates, 'has_noscript': p.noscript,
        'visible_text_chars': len(text), 'scripts': p.scripts, 'script_chars': p.script_bytes,
        'likely_js_only': len(text) < 400 and (p.scripts > 3 or p.script_bytes > 20000),
        'main_content_starts_at_pct': round(100 * first / max(1, len(html))) if first is not None else None,
        'email_obfuscated': '/cdn-cgi/l/email-protection' in html, 'mailto': sorted(set(p.mailto))[:5],
        'linked_documents': sorted(set(p.doc_links))[:5],
        'glued_line_breaks': glued_breaks(html)[:8],
        'placeholders_in_text': [s for s in PLACEHOLDERS if s.lower() in text.lower()],
        'html_comments': len(p.comments), 'html_comment_samples': p.comments[:3],
        'images': {'total': p.img_total, 'with_alt': p.img_alt, 'empty_alt': p.img_alt_empty, 'no_alt': p.img_no_alt},
        'text_start': text[:600],
    }


def text_chars(url, ua):
    """Status and visible text size for one fetch with a given user agent."""
    r = fetch(url, ua=ua)
    p = Page()
    try:
        p.feed(r['body'])
    except Exception:
        pass
    return r['status'], len(visible_text(p))


def is_unstable(results, threshold=400):
    """True when same-user-agent fetches that all succeeded disagree: some with text, some without.
    Failed fetches (timeouts, 429, 5xx) are left out, so they cannot pass for an empty page."""
    ok = [chars for status, chars in results if status == 200]
    return len(ok) >= 2 and min(ok) < threshold <= max(ok)


def images_line(im):
    if not im['total']:
        return 'images: none in the HTML'
    warn = '  <-- most images say nothing to a text reader' if im['with_alt'] < im['total'] / 2 else ''
    return (f"images: {im['total']}, with alt text {im['with_alt']}, empty alt (decorative) {im['empty_alt']}, "
            f"no alt {im['no_alt']}{warn}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('url')
    ap.add_argument('--page', action='append', default=[], help='extra path or URL to inspect')
    ap.add_argument('--json', action='store_true', help='print raw JSON')
    a = ap.parse_args()
    base = a.url if '://' in a.url else 'https://' + a.url
    host = urllib.parse.urlparse(base).hostname or ''

    report = {'home': inspect_page(base)}
    report['pages'] = [inspect_page(urllib.parse.urljoin(base, p)) for p in a.page]
    report['robots'] = robots_report(base)

    sm = fetch(urllib.parse.urljoin(base, '/sitemap.xml'))
    report['sitemap'] = {'status': sm['status'], 'content_type': sm['headers'].get('Content-Type'),
                         'urls': len(re.findall(r'<loc>', sm['body'])) if sm['status'] == 200 else 0}

    lt = fetch(urllib.parse.urljoin(base, '/llms.txt'), accept='text/plain,*/*;q=0.8')
    ct = lt['headers'].get('Content-Type') or ''
    report['llms_txt'] = {'status': lt['status'], 'content_type': ct, 'chars': len(lt['body']),
                          'first_line': lt['body'].strip().split('\n')[0][:120] if lt['status'] == 200 and 'html' not in ct else None}

    junk = '/' + ''.join(random.choices(string.ascii_lowercase, k=12)) + '-not-a-page'
    nf = fetch(urllib.parse.urljoin(base, junk))
    home_title = report['home']['title']
    nf_title = (re.search(r'<title>(.*?)</title>', nf['body'], re.S | re.I) or [None, ''])[1].strip() if nf['body'] else ''
    report['not_found'] = {'path': junk, 'status': nf['status'], 'same_title_as_home': bool(home_title) and nf_title == home_title,
                           'soft_404': nf['status'] == 200}

    variants = {}
    bare = host[4:] if host.startswith('www.') else host
    for v in {f'https://{bare}/', f'https://www.{bare}/', f'http://{bare}/'}:
        f = fetch(v)
        variants[v] = {'status': f['status'], 'final': f['url'], 'redirects': len(f['chain']), 'error': f['error']}
    report['host_variants'] = variants

    bots, bots_text = {}, {}
    for ua in ['ClaudeBot/1.0', 'GPTBot/1.2', 'Claude-User/1.0']:
        bots[ua], bots_text[ua] = text_chars(base, f'Mozilla/5.0 (compatible; {ua})')
    report['ai_user_agents'] = bots
    report['ai_user_agents_text_chars'] = bots_text

    # Some builders (seen on Readymag, Nov 2026) serve pre-rendered text to bots only some of the
    # time, from a cache. One good fetch proves nothing: repeat with the same user agent and compare.
    repeats = [text_chars(base, 'Claude-User/1.0 (+Claude-User@anthropic.com)') for _ in range(3)]
    report['repeat_fetches'] = [{'status': s, 'text_chars': c} for s, c in repeats]
    report['text_unstable'] = is_unstable(repeats)

    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    h = report['home']
    print(f"# {base}\n")
    print(f"Home: {h['status']} {h['final_url']} ({h['bytes']} bytes){' redirects: ' + '; '.join(h['redirects']) if h['redirects'] else ''}")
    print(f"Visible text without JS: {h['visible_text_chars']} chars; scripts: {h['scripts']} ({h['script_chars']} chars)"
          f"{'  <-- likely JS-only' if h['likely_js_only'] else ''}")
    print(f"Main content (h1/main) starts at {h['main_content_starts_at_pct']}% of the HTML")
    print(f"lang={h['lang']!r} title={h['title']!r}")
    print(f"description={h['description']!r}")
    print(f"canonical={h['canonical']} og:image={h['og_image']!r} JSON-LD={h['jsonld_types']}")
    print(f"alternates={h['alternates']} Link header={h['link_header']!r} X-Robots-Tag={h['x_robots_tag']!r}")
    print(f"email obfuscated by Cloudflare: {h['email_obfuscated']}; mailto: {h['mailto']}")
    print(f"linked documents a text reader may not open: {h['linked_documents'] or 'none'}")
    print(f"glued line breaks: {h['glued_line_breaks'] or 'none'}")
    print(f"placeholders in text: {h['placeholders_in_text'] or 'none'}")
    print(f"HTML comments in the source: {h['html_comments']}"
          f"{'  e.g. ' + ' | '.join(repr(c) for c in h['html_comment_samples']) if h['html_comments'] else ''}")
    print(images_line(h['images']))
    for pg in report['pages']:
        print(f"\nPage {pg['url']}: {pg['status']}, text {pg['visible_text_chars']} chars, main at {pg['main_content_starts_at_pct']}%, "
              f"canonical {pg['canonical']}, alternates {pg['alternates']}, glued {pg['glued_line_breaks'] or 'none'}; "
              f"{images_line(pg['images'])}"
              f"{'; linked documents ' + str(pg['linked_documents']) if pg['linked_documents'] else ''}")
    r = report['robots']
    print(f"\nrobots.txt: {r['status']} {r.get('content_type')}; sitemaps {r['sitemaps']}; Content-Signal {r['content_signal']}; "
          f"Disallow / for {r['disallow_all_for'] or 'nobody'}{'; ' + r['note'] if r.get('note') else ''}")
    s = report['sitemap']
    print(f"sitemap.xml: {s['status']} {s['content_type']}, {s['urls']} URLs")
    l = report['llms_txt']
    print(f"llms.txt: {l['status']} {l['content_type']}, {l['chars']} chars, first line: {l['first_line']!r}")
    n = report['not_found']
    print(f"Unknown path {n['path']}: {n['status']}{'  <-- soft 404' if n['soft_404'] else ''}")
    print('Host variants: ' + '; '.join(f"{k} -> {v['status']} {v['final']}" for k, v in report['host_variants'].items()))
    print('AI user agents: ' + ', '.join(f'{k} {v} (text {bots_text[k]} chars)' for k, v in bots.items()))
    print('Repeat fetches as Claude-User: ' + ', '.join(f"{r['status']} ({r['text_chars']} chars)" for r in report['repeat_fetches'])
          + ('  <-- unstable: text reaches agents only some of the time' if report['text_unstable'] else ''))
    print(f"\nText start (what a no-JS reader sees first):\n{h['text_start']}")


if __name__ == '__main__':
    sys.exit(main())
