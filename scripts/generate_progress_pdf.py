"""Generate a cleanly-formatted PDF from docs/Progress_Report.md using Chrome headless."""
import os
import subprocess
import mistune

def generate_pdf():
    md_path = os.path.abspath('docs/Progress_Report.md')
    pdf_path = os.path.abspath('docs/Progress_Report.pdf')
    html_path = os.path.abspath('docs/Progress_Report_temp.html')

    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    body = mistune.html(text)

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Topic 21 Progress Report - Krishna Sikheriya</title>
<style>
  @page {{
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #1f2937;
    line-height: 1.45;
    font-size: 10pt;
  }}
  h1 {{
    font-size: 17pt;
    color: #111827;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 6px;
    margin-bottom: 12px;
  }}
  h2 {{
    font-size: 13pt;
    color: #1e3a8a;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 4px;
    margin-top: 18px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 11pt;
    color: #1f2937;
    margin-top: 12px;
    margin-bottom: 4px;
    page-break-after: avoid;
  }}
  p, li {{
    margin-top: 4px;
    margin-bottom: 5px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 8.5pt;
    page-break-inside: avoid;
  }}
  th, td {{
    border: 1px solid #d1d5db;
    padding: 5px 7px;
    text-align: left;
    vertical-align: top;
  }}
  th {{
    background-color: #f3f4f6;
    font-weight: 600;
    color: #111827;
  }}
  tr:nth-child(even) td {{
    background-color: #f9fafb;
  }}
  code {{
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    background: #f3f4f6;
    padding: 1px 3px;
    border-radius: 3px;
  }}
  hr {{
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 14px 0;
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    subprocess.run(cmd, check=True)

    if os.path.exists(html_path):
        os.remove(html_path)

    print(f"Generated PDF successfully: {pdf_path} (Size: {os.path.getsize(pdf_path):,} bytes)")

if __name__ == '__main__':
    generate_pdf()
