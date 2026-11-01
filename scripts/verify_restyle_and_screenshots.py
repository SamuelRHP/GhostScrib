"""Full automated visual restyle and end-to-end browser verification for GhostScrib.

Captures desktop (1440px) and mobile (390px) screenshots to docs/screenshots/web/restyle/
Performs real file uploads of TXT and DOCX documents and validates exports.
"""

import asyncio
import base64
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path
import websockets

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9224
BASE_URL = "http://127.0.0.1:8000"
SCREENSHOT_DIR = Path("docs/screenshots/web/restyle")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


async def capture_cdp():
    print(f"[*] Starting Headless Chrome on port {PORT}...")
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={PORT}",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check"
    ])

    try:
        # Wait for debugging port
        tabs = None
        for _ in range(20):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json", timeout=1.0) as resp:
                    tabs = json.loads(resp.read().decode())
                    if tabs:
                        break
            except Exception:
                time.sleep(0.5)

        if not tabs:
            raise RuntimeError("Failed to connect to Chrome remote debugging port")

        ws_url = tabs[0]["webSocketDebuggerUrl"]
        print(f"[OK] Connected to Chrome tab: {ws_url}")

        async with websockets.connect(ws_url, max_size=50 * 1024 * 1024) as ws:
            msg_id = 0

            async def send(method, params=None):
                nonlocal msg_id
                msg_id += 1
                payload = {"id": msg_id, "method": method}
                if params:
                    payload["params"] = params
                await ws.send(json.dumps(payload))
                while True:
                    res = json.loads(await ws.recv())
                    if res.get("id") == msg_id:
                        return res.get("result", {})

            await send("Page.enable")
            await send("DOM.enable")
            await send("Runtime.enable")

            async def set_viewport(width, height, is_mobile=False):
                await send("Emulation.setDeviceMetricsOverride", {
                    "width": width,
                    "height": height,
                    "deviceScaleFactor": 1,
                    "mobile": is_mobile
                })

            async def navigate_and_wait(url, wait_seconds=1.5):
                await send("Page.navigate", {"url": url})
                await asyncio.sleep(wait_seconds)

            async def take_screenshot(filename):
                res = await send("Page.captureScreenshot", {"format": "png"})
                data = res.get("data")
                if data:
                    out_path = SCREENSHOT_DIR / filename
                    with open(out_path, "wb") as f:
                        f.write(base64.b64decode(data))
                    print(f"[OK] Screenshot saved: {out_path} ({len(data)} bytes b64)")
                else:
                    print(f"[ERROR] Failed to capture screenshot {filename}")

            async def click_tab(tab_label):
                expr = f"""
                (() => {{
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const btn = buttons.find(b => b.innerText.trim().toLowerCase().includes('{tab_label.lower()}'));
                    if (btn) {{
                        btn.click();
                        return true;
                    }}
                    return false;
                }})()
                """
                res = await send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
                await asyncio.sleep(0.8)
                return res.get("result", {}).get("value", False)

            # --- 1. Desktop Width (1440px) Screenshots ---
            print("\n[*] Capturing Desktop (1440px) Screenshots...")
            await set_viewport(1440, 900, is_mobile=False)

            # Landing Page
            await navigate_and_wait(f"{BASE_URL}/", 1.5)
            await take_screenshot("landing_desktop.png")

            # Upload Page
            await navigate_and_wait(f"{BASE_URL}/analyze", 1.2)
            await take_screenshot("upload_desktop.png")

            # About Page
            await navigate_and_wait(f"{BASE_URL}/about", 1.2)
            await take_screenshot("about_desktop.png")

            # Demo Report - Overview Tab
            await navigate_and_wait(f"{BASE_URL}/report/demo", 1.5)
            await take_screenshot("demo_overview_desktop.png")

            # Demo Report - Document View Tab
            await click_tab("Document View")
            await take_screenshot("demo_document_desktop.png")

            # Demo Report - Attribution Tab
            await click_tab("Attribution")
            await take_screenshot("demo_attribution_desktop.png")

            # Demo Report - Citations Tab
            await click_tab("Citations")
            await take_screenshot("demo_citations_desktop.png")

            # Demo Report - Breakdown Tab
            await click_tab("Breakdown")
            await take_screenshot("demo_breakdown_desktop.png")

            # Demo Report - Limitations Tab
            await click_tab("Limitations")
            await take_screenshot("demo_limitations_desktop.png")

            # Dev Sandbox - Hostile Text Fixture
            await navigate_and_wait(f"{BASE_URL}/dev/sandbox", 1.5)
            # Switch fixture to hostileText
            await send("Runtime.evaluate", {
                "expression": """
                (() => {
                    const select = document.querySelector('select');
                    if (select) {
                        select.value = 'hostileText';
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                })()
                """
            })
            await asyncio.sleep(0.8)
            await take_screenshot("sandbox_hostile_desktop.png")

            # --- 2. Mobile Width (390px) Screenshots ---
            print("\n[*] Capturing Mobile (390px) Screenshots...")
            await set_viewport(390, 844, is_mobile=True)

            # Landing Mobile
            await navigate_and_wait(f"{BASE_URL}/", 1.5)
            await take_screenshot("landing_mobile.png")

            # Upload Mobile
            await navigate_and_wait(f"{BASE_URL}/analyze", 1.2)
            await take_screenshot("upload_mobile.png")

            # About Mobile
            await navigate_and_wait(f"{BASE_URL}/about", 1.2)
            await take_screenshot("about_mobile.png")

            # Demo Report Mobile - Overview
            await navigate_and_wait(f"{BASE_URL}/report/demo", 1.5)
            await take_screenshot("demo_overview_mobile.png")

            # Demo Report Mobile - Document View
            await click_tab("Document View")
            await take_screenshot("demo_document_mobile.png")

            # Demo Report Mobile - Attribution
            await click_tab("Attribution")
            await take_screenshot("demo_attribution_mobile.png")

            # Demo Report Mobile - Citations
            await click_tab("Citations")
            await take_screenshot("demo_citations_mobile.png")

            # Demo Report Mobile - Breakdown
            await click_tab("Breakdown")
            await take_screenshot("demo_breakdown_mobile.png")

            # Demo Report Mobile - Limitations
            await click_tab("Limitations")
            await take_screenshot("demo_limitations_mobile.png")

            # Sandbox Mobile
            await navigate_and_wait(f"{BASE_URL}/dev/sandbox", 1.5)
            await take_screenshot("sandbox_hostile_mobile.png")

            # --- 3. Live File Upload Verification (TXT & DOCX) ---
            print("\n[*] Verifying Live Uploads (TXT & DOCX)...")
            await set_viewport(1440, 900, is_mobile=False)

            async def upload_and_verify(file_path, field_val="cs_eng", label="file"):
                print(f"\n[*] Submitting {label}: {file_path}")
                boundary = "----WebKitFormBoundaryGhostScribVerification"
                file_bytes = open(file_path, "rb").read()
                filename = os.path.basename(file_path)

                body = (
                    f"--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
                    f"Content-Type: application/octet-stream\r\n\r\n"
                ).encode("utf-8") + file_bytes + (
                    f"\r\n--{boundary}\r\n"
                    f'Content-Disposition: form-data; name="field"\r\n\r\n'
                    f"{field_val}\r\n"
                    f"--{boundary}--\r\n"
                ).encode("utf-8")

                req = urllib.request.Request(
                    f"{BASE_URL}/api/analyze",
                    data=body,
                    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
                )
                with urllib.request.urlopen(req) as resp:
                    res_json = json.loads(resp.read().decode())
                job_id = res_json.get("job_id")
                print(f"[OK] Job Created: {job_id}")

                # Poll job until completed
                for _ in range(60):
                    time.sleep(1.0)
                    with urllib.request.urlopen(f"{BASE_URL}/api/jobs/{job_id}") as poll_resp:
                        poll_json = json.loads(poll_resp.read().decode())
                    status = poll_json.get("status")
                    progress = poll_json.get("progress")
                    print(f"  Progress: {status} ({int(progress*100)}%)")
                    if status == "done":
                        break
                    elif status == "error":
                        raise RuntimeError(f"Job failed: {poll_json.get('error')}")

                # Verify all 3 exports
                print("[*] Testing Exports...")
                with urllib.request.urlopen(f"{BASE_URL}/api/jobs/{job_id}/export/json") as r:
                    json_data = json.loads(r.read().decode())
                    assert "transparency_report" in json_data
                    print("  [OK] Export JSON verified")

                with urllib.request.urlopen(f"{BASE_URL}/api/jobs/{job_id}/export/html") as r:
                    html_data = r.read().decode()
                    assert "<html" in html_data.lower()
                    print("  [OK] Export HTML verified")

                with urllib.request.urlopen(f"{BASE_URL}/api/jobs/{job_id}/export/pdf") as r:
                    pdf_data = r.read()
                    assert len(pdf_data) > 0
                    print(f"  [OK] Export PDF verified ({len(pdf_data)} bytes)")

                # Navigate browser to the report and capture screenshot
                await navigate_and_wait(f"{BASE_URL}/report/{job_id}", 2.0)
                await take_screenshot(f"live_{label}_report_desktop.png")
                return job_id

            txt_job = await upload_and_verify("data/demo/test_article_claude_written.txt", "cs_eng", "txt")
            docx_job = await upload_and_verify("data/demo/1-IJCSE-2026-7515.docx", "cs_eng", "docx")

            print("\n[SUCCESS] All Browser and End-to-End Verifications Passed!")
            print(f"TXT Job ID: {txt_job}")
            print(f"DOCX Job ID: {docx_job}")

    finally:
        chrome_proc.terminate()

if __name__ == "__main__":
    asyncio.run(capture_cdp())

