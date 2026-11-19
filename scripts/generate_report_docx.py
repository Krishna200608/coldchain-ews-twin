"""Convert docs/Report/Final_Report.md into a professional Word document (.docx).

Saves to docs/Report/IIT2023139_Krishna_Sikheriya_ColdChain_Report.docx.
Includes:
- Title, candidate metadata, executive summary
- Formatted headings (H1, H2, H3)
- Embedded high-resolution figures from docs/Report/figures/
- Academic tables with styling
- Styled callout boxes and bullet points
"""

import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

COLOR_NAVY = RGBColor(14, 38, 77)     # #0E264D
COLOR_BLUE = RGBColor(2, 132, 199)    # #0284C7
COLOR_DARK = RGBColor(30, 41, 59)     # #1E293B
COLOR_GRAY = RGBColor(100, 116, 139)  # #64748B
COLOR_LIGHT_BG = "F0F7FF"
COLOR_BORDER = "CBD5E1"

def set_cell_background(cell, hex_color):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def generate_docx():
    md_path = os.path.abspath("docs/Report/Final_Report.md")
    out_docx = os.path.abspath("docs/Report/IIT2023139_Krishna_Sikheriya_ColdChain_Report.docx")
    fig_dir = os.path.abspath("docs/Report/figures")

    if not os.path.exists(md_path):
        print(f"Error: {md_path} not found")
        return

    doc = docx.Document()

    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Parse and write
    in_table = False
    table_lines = []

    def flush_table(tbl_lines):
        if not tbl_lines:
            return
        # Parse markdown table
        rows = []
        for l in tbl_lines:
            parts = [c.strip() for c in l.split("|")[1:-1]]
            if parts and not all(set(c) <= set("-: ") for c in parts):
                rows.append(parts)
        if not rows:
            return

        cols_count = max(len(r) for r in rows)
        table = doc.add_table(rows=len(rows), cols=cols_count)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True

        for r_idx, r_data in enumerate(rows):
            for c_idx, val in enumerate(r_data):
                if c_idx < cols_count:
                    cell = table.rows[r_idx].cells[c_idx]
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
                    if r_idx == 0:
                        set_cell_background(cell, "0E264D")
                        run = p.add_run(val)
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(8.5)
                    else:
                        bg = "FFFFFF" if r_idx % 2 == 1 else "F8FAFC"
                        set_cell_background(cell, bg)
                        run = p.add_run(val)
                        run.font.color.rgb = COLOR_DARK
                        run.font.size = Pt(8.5)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\r\n")

        # Table detection
        if line.strip().startswith("|") and line.strip().endswith("|"):
            in_table = True
            table_lines.append(line)
            i += 1
            continue
        elif in_table:
            in_table = False
            flush_table(table_lines)
            table_lines = []

        # Empty line
        if not line.strip():
            i += 1
            continue

        # Horizontal rule
        if line.strip() in ["---", "***", "___"]:
            i += 1
            continue

        # Images: ![alt](path)
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
        if img_match:
            caption = img_match.group(1)
            img_rel = img_match.group(2)
            img_basename = os.path.basename(img_rel)
            img_path = os.path.join(fig_dir, img_basename)
            if os.path.exists(img_path):
                p_img = doc.add_paragraph()
                p_img.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(8)
                p_img.paragraph_format.space_after = Pt(4)
                run_img = p_img.add_run()
                run_img.add_picture(img_path, width=Inches(6.0))

                p_cap = doc.add_paragraph()
                p_cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_before = Pt(2)
                p_cap.paragraph_format.space_after = Pt(8)
                r_cap = p_cap.add_run(f"Figure: {caption}")
                r_cap.font.name = "Calibri"
                r_cap.font.size = Pt(9)
                r_cap.font.italic = True
                r_cap.font.color.rgb = COLOR_GRAY
            i += 1
            continue

        # Heading 1
        if line.startswith("# "):
            h_text = line[2:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.font.name = "Calibri"
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = COLOR_NAVY
            i += 1
            continue

        # Heading 2
        if line.startswith("## "):
            h_text = line[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.font.name = "Calibri"
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = COLOR_NAVY
            i += 1
            continue

        # Heading 3
        if line.startswith("### "):
            h_text = line[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.font.name = "Calibri"
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = COLOR_BLUE
            i += 1
            continue

        # Bullet list item
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            b_text = line.strip()[2:].strip()
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            # handle bold prefix e.g. **Title:** body
            parts = re.split(r'(\*\*.*?\*\*)', b_text)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.font.bold = True
                    r.font.color.rgb = COLOR_NAVY
                else:
                    r = p.add_run(part)
                    r.font.color.rgb = COLOR_DARK
                r.font.name = "Calibri"
                r.font.size = Pt(10)
            i += 1
            continue

        # Regular paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15

        # Format bold tags inside paragraph
        parts = re.split(r'(\*\*.*?\*\*)', line)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                r = p.add_run(part[2:-2])
                r.font.bold = True
                r.font.color.rgb = COLOR_NAVY
            else:
                r = p.add_run(part)
                r.font.color.rgb = COLOR_DARK
            r.font.name = "Calibri"
            r.font.size = Pt(10)

        i += 1

    if in_table:
        flush_table(table_lines)

    doc.save(out_docx)
    size = os.path.getsize(out_docx)
    print(f"Report Word document created at: {out_docx} ({size:,} bytes)")

if __name__ == "__main__":
    generate_docx()
