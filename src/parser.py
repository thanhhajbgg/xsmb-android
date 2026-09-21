
import re
from datetime import datetime
from html import unescape
from .models import Draw
class ParseError(ValueError): pass
LABELS=[("G.ĐB",1),("G.1",1),("G.2",2),("G.3",6),("G.4",4),("G.5",6),("G.6",3),("G.7",4)]
def _text(html):
    s=re.sub(r"<script\b.*?</script>|<style\b.*?</style>"," ",html,flags=re.I|re.S)
    s=re.sub(r"<[^>]+>"," ",s)
    return re.sub(r"\s+"," ",unescape(s)).strip()
def parse_draw(html, source_url=""):
    text=_text(html)
    md=re.search(r'(?:XSMB[^0-9]{0,30})?(\d{2}/\d{2}/\d{4})',text,re.I)
    if not md: raise ParseError("Không tìm thấy ngày kết quả")
    day=datetime.strptime(md.group(1),"%d/%m/%Y").strftime("%Y-%m-%d")
    rows=[]; pos=0
    for i,(label,count) in enumerate(LABELS):
        aliases=[label]
        if label=="G.ĐB": aliases += ["ĐB","G.DB","GĐB"]
        pat=r'(?:'+ "|".join(re.escape(x) for x in aliases) + r')\s*[:\-|]?\s*'
        m=re.search(pat,text[pos:],re.I)
        if not m: raise ParseError(f"Thiếu {label}")
        start=pos+m.end()
        end=len(text)
        if i+1<len(LABELS):
            nl=LABELS[i+1][0]
            nm=re.search(re.escape(nl),text[start:],re.I)
            if nm: end=start+nm.start()
        nums=re.findall(r'(?<!\d)\d{2,5}(?!\d)',text[start:end])
        if len(nums)<count: raise ParseError(f"{label}: cần {count} giải, đọc được {len(nums)}")
        rows.extend(nums[:count]); pos=end
    if len(rows)!=27: raise ParseError(f"Cần 27 kết quả, đọc được {len(rows)}")
    return Draw(day,tuple(x[-2:].zfill(2) for x in rows),rows[0],source_url)
