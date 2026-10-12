import os,re,json,collections
import sys
D=sys.argv[1] if len(sys.argv)>1 else 'docs'
pages={}
for r,_,fs in os.walk(D):
    for f in fs:
        if f.endswith('.html'):
            p=os.path.join(r,f); pages[os.path.relpath(p,D)]=open(p,encoding='utf-8').read()
T=collections.defaultdict(list); Dd=collections.defaultdict(list)
issues=[]
inlinks=collections.Counter()
for k,h in sorted(pages.items()):
    t=re.search(r'<title>(.*?)</title>',h,re.S).group(1)
    d=re.search(r'<meta name="description" content="(.*?)"',h,re.S).group(1)
    import html as H
    t=H.unescape(t); d=H.unescape(d)
    T[t].append(k); Dd[d].append(k)
    h1=re.findall(r'<h1[^>]*>(.*?)</h1>',h,re.S)
    if len(h1)!=1: issues.append((k,'h1 count',len(h1)))
    if len(t)>70: issues.append((k,'title len',len(t),t))
    if len(t)<25: issues.append((k,'title short',len(t),t))
    if len(d)>165 or len(d)<90: issues.append((k,'desc len',len(d),d))
    if 'rel="canonical"' not in h and k!='404.html': issues.append((k,'no canonical'))
    for m in re.finditer(r'<img\b[^>]*>',h):
        tag=m.group(0)
        if 'alt=' not in tag: issues.append((k,'img no alt',tag[:80]))
        if 'width=' not in tag or 'height=' not in tag: issues.append((k,'img no size',tag[:80]))
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',h,re.S):
        try: json.loads(m.group(1))
        except Exception as e: issues.append((k,'bad jsonld',str(e)))
    # heading order
    hs=[int(x) for x in re.findall(r'<h([1-6])\b',h)]
    for a,b in zip(hs,hs[1:]):
        if b>a+1: issues.append((k,'heading skip',a,b)); break
    # internal links
    base=os.path.dirname(os.path.join(D,k))
    for m in re.finditer(r'(?:href|src)="([^"#?]+)[^"]*"',h):
        u=m.group(1)
        if re.match(r'(https?:|mailto:|data:|tel:)',u) or u.startswith('/vzoshlo/'): continue
        tgt=os.path.normpath(os.path.join(base,u))
        if os.path.isdir(tgt): tgt=os.path.join(tgt,'index.html')
        if not os.path.exists(tgt): issues.append((k,'broken',u))
        else: inlinks[os.path.relpath(tgt,D)]+=1
    words=len(re.sub(r'<[^>]+>',' ',re.sub(r'<(script|style)[^>]*>.*?</\1>','',h,flags=re.S)).split())
    pages[k]=(len(h),words,t,d)
for t,ks in T.items():
    if len(ks)>1: issues.append(('dup title',t,ks))
for d,ks in Dd.items():
    if len(ks)>1: issues.append(('dup desc',d[:60],ks))
for i in issues: print(i)
print('---pages',len(pages))
for k in pages:
    if inlinks[k]<2: print('few inlinks',k,inlinks[k])
print('--- sizes')
for k,(n,w,t,d) in sorted(pages.items(), key=lambda x:x[1][1])[:12]: print(w,n,k)
print('--- titles')
for k,(n,w,t,d) in sorted(pages.items()): print(len(t),len(d),k,'|',t)
