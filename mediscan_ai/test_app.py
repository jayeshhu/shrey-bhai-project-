import urllib.request, urllib.parse, urllib.error, http.cookiejar, json, re

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def get(url, label=''):
    r = opener.open(url, timeout=15)
    body = r.read().decode('utf-8', 'ignore')
    print(f'  OK  {label}: 200 ({len(body)}b) -> {r.url}')
    return body, r.url

def post_form(url, data, label=''):
    body_data = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=body_data)
    r = opener.open(req, timeout=15)
    body = r.read().decode('utf-8', 'ignore')
    print(f'  OK  {label}: 200 ({len(body)}b) -> {r.url}')
    return body, r.url

def post_json(url, payload_dict, label=''):
    data = json.dumps(payload_dict).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
    r = opener.open(req, timeout=15)
    body = r.read().decode('utf-8', 'ignore')
    return json.loads(body)

base = 'http://127.0.0.1:5000'
results = {}

print('=== 1. Login ===')
body, url = post_form(base+'/login', {'email':'test@mediscan.ai','password':'Test1234'}, 'Login')
results['login'] = '/dashboard' in url

print('=== 2. CBC Demo ===')
body, url = get(base+'/demo/cbc', 'CBC Demo')
# Extract report ID from final URL
m = re.search(r'/reports/(\d+)', url)
report_id = m.group(1) if m else None
print(f'     CBC report_id from URL: {report_id}')
results['demo_cbc'] = bool(report_id)

print('=== 3. Biochem Demo ===')
body2, url2 = get(base+'/demo/biochemistry', 'Biochem Demo')
m2 = re.search(r'/reports/(\d+)', url2)
report_id2 = m2.group(1) if m2 else None
print(f'     Biochem report_id from URL: {report_id2}')
results['demo_biochem'] = bool(report_id2)

print('=== 4. Report Detail Page ===')
if report_id:
    body, url = get(base+'/reports/'+report_id, 'Report Detail')
    checks = {
        'test_table': 'Test Name' in body or 'test-results' in body,
        'ai_section': 'AI Analysis' in body or 'ai-summary' in body,
        'chart_section': 'Test Results Chart' in body,
        'qa_form': 'qaForm' in body,
        'disclaimer': 'educational' in body.lower(),
        'download_btn': 'download' in body.lower(),
    }
    for k, v in checks.items():
        print(f'     {k}: {"PASS" if v else "FAIL"}')
    results['report_detail'] = all(checks.values())
else:
    print('     SKIP (no report_id)')

print('=== 5. Ask AI API ===')
if report_id:
    try:
        result = post_json(base+'/api/ask', {'report_id': int(report_id), 'question': 'What tests are shown?'}, 'Ask AI')
        ans_len = len(result.get('answer', ''))
        print(f'     Answer: {ans_len} chars - {"PASS" if ans_len > 10 else "FAIL"}')
        print(f'     Answer preview: {result.get("answer","")[:100]}')
        results['ask_api'] = ans_len > 10
    except Exception as e:
        print(f'     ERROR: {e}')
        results['ask_api'] = False

print('=== 6. Compare Reports ===')
if report_id and report_id2:
    body, url = post_form(base+'/compare', {'report_a_id': report_id, 'report_b_id': report_id2}, 'Compare')
    has_results = 'Tests Compared' in body or 'comparison' in body.lower() or 'change-up' in body
    print(f'     Comparison results present: {"PASS" if has_results else "FAIL"}')
    results['compare'] = has_results
else:
    print('     SKIP')

print('=== 7. Download Summary ===')
if report_id:
    try:
        body, url = get(base+'/reports/'+report_id+'/download', 'Download Summary')
        is_content = 'MEDISCAN' in body.upper() or len(body) > 500
        print(f'     Download content valid: {"PASS" if is_content else "FAIL"} ({len(body)}b)')
        results['download'] = is_content
    except Exception as e:
        print(f'     ERROR: {e}')
        results['download'] = False

print('=== 8. Reports List ===')
body, url = get(base+'/reports', 'Reports List')
row_count = body.count('report-row')
print(f'     Report rows: {row_count} - {"PASS" if row_count >= 2 else "FAIL"}')
results['reports_list'] = row_count >= 2

print('=== 9. Logout ===')
body, url = get(base+'/logout', 'Logout')
results['logout'] = 'login' in url.lower() or 'login' in body.lower()
print(f'     Logout redirected to login: {"PASS" if results["logout"] else "FAIL"}')

print()
print('=' * 50)
print('FINAL RESULTS:')
for test, passed in results.items():
    print(f'  {"✅ PASS" if passed else "❌ FAIL"}  {test}')
total = sum(results.values())
print(f'\n{total}/{len(results)} tests passed')
