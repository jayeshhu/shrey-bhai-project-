import os
import re

templates_dir = r'D:\shrey bhaiya\mediscan_ai\templates'
templates = [
    'dashboard.html',
    'upload.html',
    'reports.html',
    'report_detail.html',
    'compare.html',
    'profile.html',
    'about.html',
]

page_map = {
    'dashboard.html': 'dashboard',
    'upload.html': 'upload',
    'reports.html': 'reports',
    'report_detail.html': 'reports',
    'compare.html': 'compare',
    'profile.html': 'profile',
    'about.html': 'about',
}

for tmpl in templates:
    path = os.path.join(templates_dir, tmpl)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    page = page_map[tmpl]

    # Remove the from/import line
    content = re.sub(
        r"\{%-?\s*from ['\"]layout\.html['\"] import sidebar_nav\s*-?%\}",
        '',
        content
    )

    # Replace the macro call with include
    replacement = "{%% set active_page = '%s' %%}{%% include '_sidebar.html' %%}" % page
    content = re.sub(
        r"\{\{-?\s*sidebar_nav\('[^']*'\)\s*-?\}\}",
        replacement,
        content
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Updated: {tmpl}')

print('All templates updated!')
