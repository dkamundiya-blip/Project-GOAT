import urllib.request, re
r = urllib.request.urlopen('https://project-goat.netlify.app', timeout=12)
html = r.read().decode('utf-8', errors='replace')
new_hash = 'm9g64rMM'
old_hash = 'Bct2OBGA'
if new_hash in html:
    print('NEW BUNDLE IS LIVE: Netlify already deployed commit 29ab952')
elif old_hash in html:
    print('OLD BUNDLE STILL LIVE: Netlify deploy in progress or not yet triggered')
else:
    idx = html.find('/assets/')
    print('Unknown bundle:', html[idx:idx+60] if idx >= 0 else 'no /assets/ reference found')
print('---')
idx = html.find('index-')
print('Bundle ref in HTML:', html[idx:idx+40] if idx >= 0 else 'none found')
