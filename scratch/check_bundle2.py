import urllib.request
r = urllib.request.urlopen('https://project-goat.netlify.app', timeout=12)
html = r.read(3000).decode('utf-8', errors='replace')
print(html)
