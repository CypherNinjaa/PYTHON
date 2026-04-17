import os
import sys
import requests
from dotenv import load_dotenv

sys.path.insert(0, r"c:\Users\Vikash\Desktop\PYTHON\Infosys-Springboard-Course-Auto-Completer")
from api_client import APIClient

load_dotenv(r"c:\Users\Vikash\Desktop\PYTHON\Infosys-Springboard-Course-Auto-Completer\.env")
token = os.getenv("INFOSYS_TOKEN") or os.getenv("token")
course_id = os.getenv("INFOSYS_COURSE_ID") or os.getenv("courseid")

client = APIClient(token)
user_id, _ = client.validate_user()
data = client.get_course_hierarchy(course_id, user_id)

wanted = {
    "application/x-mpegURL": None,
    "application/web-module": None,
    "application/quiz": None,
    "application/integrated-hands-on": None,
    "application/web-module-exercise": None,
    "application/iap-assessment": None,
}

stack = [data]
while stack:
    node = stack.pop()
    if isinstance(node, dict):
        mt = node.get("mimeType")
        cid = node.get("identifier")
        if mt in wanted and wanted[mt] is None and cid:
            wanted[mt] = (cid, node.get("name", ""))
        ch = node.get("children")
        if isinstance(ch, list):
            stack.extend(ch)
    elif isinstance(node, list):
        stack.extend(node)

url = f"{client.BASE_URL}/api-gw/wn-apis/infosysheadstart/progress/v1/progress/calculate"
headers = client._get_headers(include_wid=user_id)
headers["x-wingspan-caller"] = "wingspan"
headers["origin"] = client.BASE_URL

print("Testing browser-style markAsComplete payload")
for mt, item in wanted.items():
    if not item:
        print(f"{mt:32} -> not found")
        continue
    cid, name = item
    payload = {"contentId": cid, "markAsComplete": True, "userId": user_id}
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    try:
        body = r.json()
    except Exception:
        body = r.text
    print(f"{mt:32} status={r.status_code} id={cid} name={name[:45]} body={str(body)[:160]}")
