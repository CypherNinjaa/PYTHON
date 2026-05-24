import json
import os

FILES = [
    r"C:\Users\Vikash\AppData\Roaming\Code\User\workspaceStorage\cbf00998f71cd87af711dfbd12e7ab82\GitHub.copilot-chat\chat-session-resources\0474c9d4-9a5b-4ccb-9db9-a9d1e827dc0f\call_uazwUv3swuePskj5XqrQpP8o__vscode-1777439043783\content.txt",
    r"C:\Users\Vikash\AppData\Roaming\Code\User\workspaceStorage\cbf00998f71cd87af711dfbd12e7ab82\GitHub.copilot-chat\chat-session-resources\0474c9d4-9a5b-4ccb-9db9-a9d1e827dc0f\call_tBIlwqPt1m0e6N80X44nOPzQ__vscode-1777439043785\content.txt",
    r"C:\Users\Vikash\AppData\Roaming\Code\User\workspaceStorage\cbf00998f71cd87af711dfbd12e7ab82\GitHub.copilot-chat\chat-session-resources\0474c9d4-9a5b-4ccb-9db9-a9d1e827dc0f\call_M3ZfTHfJlmxjFyoezcFaVwRi__vscode-1777439043787\content.txt",
    r"C:\Users\Vikash\AppData\Roaming\Code\User\workspaceStorage\cbf00998f71cd87af711dfbd12e7ab82\GitHub.copilot-chat\chat-session-resources\0474c9d4-9a5b-4ccb-9db9-a9d1e827dc0f\call_G6jtNSoo86O5t0sDJmaaVlqB__vscode-1777439043789\content.txt",
    r"C:\Users\Vikash\AppData\Roaming\Code\User\workspaceStorage\cbf00998f71cd87af711dfbd12e7ab82\GitHub.copilot-chat\chat-session-resources\0474c9d4-9a5b-4ccb-9db9-a9d1e827dc0f\call_NFVGaI36HLwX8YVepzTay4n6__vscode-1777439043791\content.txt",
    r"C:\Users\Vikash\AppData\Roaming\Code\User\workspaceStorage\cbf00998f71cd87af711dfbd12e7ab82\GitHub.copilot-chat\chat-session-resources\0474c9d4-9a5b-4ccb-9db9-a9d1e827dc0f\call_5WzaxOvTUkX29ldNeAWcXhBg__vscode-1777439043793\content.txt",
    r"C:\Users\Vikash\AppData\Roaming\Code\User\workspaceStorage\cbf00998f71cd87af711dfbd12e7ab82\GitHub.copilot-chat\chat-session-resources\0474c9d4-9a5b-4ccb-9db9-a9d1e827dc0f\call_czfRqPDtsO6lvaNWxgGUleLe__vscode-1777439043795\content.txt",
]

pages = {}
all_eps = set()

for path in FILES:
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        continue
    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()
    if content.startswith("Result:"):
        content = content[len("Result:") :].lstrip()
    try:
        data = json.loads(content)
    except Exception:
        continue

    for item in data.get("results", []):
        page = item.get("page")
        endpoints = item.get("endpoints") or []
        pages[page] = sorted(set(endpoints))
        all_eps.update(endpoints)

all_list = sorted(all_eps)

out_path = r"C:\Users\Vikash\Desktop\PYTHON\_amizone_endpoints.txt"
with open(out_path, "w", encoding="utf-8") as handle:
    handle.write(f"TOTAL_PAGES {len(pages)}\n")
    handle.write(f"TOTAL_ENDPOINTS {len(all_list)}\n")
    handle.write("PAGES " + ", ".join(sorted(pages.keys())) + "\n")
    handle.write("ENDPOINTS_START\n")
    for ep in all_list:
        handle.write(ep + "\n")
    handle.write("ENDPOINTS_END\n")

print(out_path)
