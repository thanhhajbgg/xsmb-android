
import urllib.request,urllib.error
class NetworkError(RuntimeError): pass
def fetch_html(url,timeout=15):
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 XSMB-AI-Indicator/1.1","Accept-Language":"vi-VN,vi;q=0.9"})
  with urllib.request.urlopen(req,timeout=timeout) as r:return r.read().decode("utf-8","ignore")
 except Exception as e: raise NetworkError(f"Không tải được dữ liệu: {e}") from e
