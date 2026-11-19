"""Generate the mandatory one-page Word document containing the direct dataset link.

Course: Managing Corporate Entrepreneurship (B.Tech IT 7th Semester)
Topic 21: Digital Twin-Based Early Warning System for Cold Chain Disruption Detection
Student: Krishna Sikheriya (IIT2023139)
Supervisor: Dr. Netranand Pathak
Institution: Indian Institute of Information Technology, Allahabad (IIITA)

Requirements:
- Standalone Word document (.docx)
- Fits strictly on exactly ONE page
- Contains direct link to the dataset used
- Metadata: Dataset title, provider, license, size, record count, variables, verification SHA-256
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
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

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_hyperlink(paragraph, url, text, color="0284C7", underline=True):
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)

    hyperlink = parse_xml(f'<w:hyperlink {nsdecls("w")} xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:id="{r_id}"/>')
    new_run = parse_xml(f'<w:r {nsdecls("w")}><w:rPr/><w:t>{text}</w:t></w:r>')
    rPr = new_run.find(qn('w:rPr'))
    
    color_elem = parse_xml(f'<w:color {nsdecls("w")} w:val="{color}"/>')
    rPr.append(color_elem)
    if underline:
        u_elem = parse_xml(f'<w:u {nsdecls("w")} w:val="single"/>')
        rPr.append(u_elem)
    
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

def create_document(output_path):
    doc = docx.Document()

    # Set 0.6 inch margins all around to guarantee strict 1-page fit
    for section in doc.sections:
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.65)
        section.right_margin = Inches(0.65)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # 1. Header / Institutional Identification
    p_inst = doc.add_paragraph()
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(2)
    p_inst.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("INDIAN INSTITUTE OF INFORMATION TECHNOLOGY, ALLAHABAD\n")
    r_inst.font.name = "Calibri"
    r_inst.font.size = Pt(11)
    r_inst.font.bold = True
    r_inst.font.color.rgb = COLOR_NAVY

    r_dept = p_inst.add_run("Department of Information Technology  |  Managing Corporate Entrepreneurship (B.Tech 7th Sem)\n")
    r_dept.font.name = "Calibri"
    r_dept.font.size = Pt(9.5)
    r_dept.font.color.rgb = COLOR_GRAY

    # Document Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(6)
    p_title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("PROJECT DATASET SOURCE REPOSITORY & VERIFICATION DETAILS")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(13)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    # Project & Candidate Metadata Box
    t_meta = doc.add_table(rows=2, cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_meta.autofit = False
    
    col_widths = [Inches(3.6), Inches(3.6)]
    meta_info = [
        [("Candidate Name:", " Krishna Sikheriya"), ("Project Topic:", " Topic 21 - Digital Twin Early Warning System")],
        [("Roll Number:", " IIT2023139"), ("Course Supervisor:", " Dr. Netranand Pathak")]
    ]
    for row_idx, row in enumerate(t_meta.rows):
        for col_idx, cell in enumerate(row.cells):
            cell.width = col_widths[col_idx]
            set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            lbl, val = meta_info[row_idx][col_idx]
            r1 = p.add_run(lbl)
            r1.font.bold = True
            r1.font.size = Pt(9)
            r1.font.color.rgb = COLOR_NAVY
            r2 = p.add_run(val)
            r2.font.size = Pt(9)
            r2.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # 2. Prominent Callout Box for Direct Dataset Links
    p_sec1 = doc.add_paragraph()
    p_sec1.paragraph_format.space_before = Pt(4)
    p_sec1.paragraph_format.space_after = Pt(3)
    r_sec1 = p_sec1.add_run("1. Primary Direct Access & Download Links")
    r_sec1.font.name = "Calibri"
    r_sec1.font.size = Pt(10.5)
    r_sec1.font.bold = True
    r_sec1.font.color.rgb = COLOR_NAVY

    t_link = doc.add_table(rows=1, cols=1)
    t_link.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_link = t_link.rows[0].cells[0]
    cell_link.width = Inches(7.2)
    set_cell_background(cell_link, COLOR_LIGHT_BG)
    set_cell_margins(cell_link, top=100, bottom=100, left=140, right=140)

    p_l1 = cell_link.paragraphs[0]
    p_l1.paragraph_format.space_before = Pt(0)
    p_l1.paragraph_format.space_after = Pt(2)
    r_l1_lbl = p_l1.add_run("• Official Kaggle Repository (Direct URL):\n  ")
    r_l1_lbl.font.bold = True
    r_l1_lbl.font.size = Pt(9.5)
    r_l1_lbl.font.color.rgb = COLOR_NAVY
    add_hyperlink(p_l1, "https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices",
                  "https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices")

    p_l2 = cell_link.add_paragraph()
    p_l2.paragraph_format.space_before = Pt(2)
    p_l2.paragraph_format.space_after = Pt(2)
    r_l2_lbl = p_l2.add_run("• Direct Kaggle API / CLI Download Command:\n  ")
    r_l2_lbl.font.bold = True
    r_l2_lbl.font.size = Pt(9.5)
    r_l2_lbl.font.color.rgb = COLOR_NAVY
    r_l2_cmd = p_l2.add_run("kaggle datasets download -d atulanandjha/temperature-readings-iot-devices")
    r_l2_cmd.font.name = "Consolas"
    r_l2_cmd.font.size = Pt(8.5)
    r_l2_cmd.font.color.rgb = COLOR_DARK

    p_l3 = cell_link.add_paragraph()
    p_l3.paragraph_format.space_before = Pt(2)
    p_l3.paragraph_format.space_after = Pt(0)
    r_l3_lbl = p_l3.add_run("• Project GitHub Data Mirror:\n  ")
    r_l3_lbl.font.bold = True
    r_l3_lbl.font.size = Pt(9.5)
    r_l3_lbl.font.color.rgb = COLOR_NAVY
    add_hyperlink(p_l3, "https://github.com/Krishna200608/coldchain-ews-twin/tree/main/docs/Dataset_Submission",
                  "https://github.com/Krishna200608/coldchain-ews-twin/tree/main/docs/Dataset_Submission")

    # 3. Dataset Characteristics & Summary Table
    p_sec2 = doc.add_paragraph()
    p_sec2.paragraph_format.space_before = Pt(6)
    p_sec2.paragraph_format.space_after = Pt(3)
    r_sec2 = p_sec2.add_run("2. Empirical Dataset Profile & Characteristics")
    r_sec2.font.name = "Calibri"
    r_sec2.font.size = Pt(10.5)
    r_sec2.font.bold = True
    r_sec2.font.color.rgb = COLOR_NAVY

    specs = [
        ("Dataset Title", "IoT Temperature Sensor Readings Telemetry Dataset (IOT-temp.csv)"),
        ("Original Provider", "Atulanand Jha (Data Scientist / Machine Learning Engineer)"),
        ("License & Access", "CC0: Public Domain (Open Access Data)"),
        ("Observation Period", "133 Days, 2 Hours, 24 Minutes (July 28, 2018 at 07:06 to Dec 8, 2018 at 09:30)"),
        ("Total Observations", "97,605 Unique Readings (1 duplicate purged from 97,606 raw rows; 0 missing values)"),
        ("Sensor Deployment", "Dual-Stream Spatial Setup: 'Out' (Ambient, 77,260 rows) & 'In' (Cargo Enclosure, 20,345 rows)"),
        ("Raw File Size", "6.63 MB (uncompressed, 6,948,127 bytes)"),
        ("SHA-256 Checksum", "2bf965701db96cd5788403d395a25d2dd7282bea24e317b7f7b157b7a02063d4")
    ]

    t_specs = doc.add_table(rows=len(specs), cols=2)
    t_specs.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_specs.autofit = False
    col_w = [Inches(1.8), Inches(5.4)]

    for idx, (prop, val) in enumerate(specs):
        row = t_specs.rows[idx]
        bg = "FFFFFF" if idx % 2 == 0 else "F8FAFC"
        
        c0 = row.cells[0]
        c0.width = col_w[0]
        set_cell_background(c0, bg)
        set_cell_margins(c0, top=40, bottom=40, left=80, right=80)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(prop)
        r0.font.bold = True
        r0.font.size = Pt(8.5)
        r0.font.color.rgb = COLOR_NAVY

        c1 = row.cells[1]
        c1.width = col_w[1]
        set_cell_background(c1, bg)
        set_cell_margins(c1, top=40, bottom=40, left=80, right=80)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(val)
        if "SHA-256" in prop:
            r1.font.name = "Consolas"
            r1.font.size = Pt(8)
        else:
            r1.font.size = Pt(8.5)
        r1.font.color.rgb = COLOR_DARK

    # 4. Mandatory Technical Grounding Note
    p_sec3 = doc.add_paragraph()
    p_sec3.paragraph_format.space_before = Pt(6)
    p_sec3.paragraph_format.space_after = Pt(2)
    r_sec3 = p_sec3.add_run("3. Critical Ingestion & Reproducibility Specifications")
    r_sec3.font.name = "Calibri"
    r_sec3.font.size = Pt(10.5)
    r_sec3.font.bold = True
    r_sec3.font.color.rgb = COLOR_NAVY

    notes = [
        "1. Strict Day-First Parsing: The raw timestamp field is encoded in DD-MM-YYYY HH:MM format. Standard US month-first datetime parsers silently fail on 47,662 rows (48.83% of the dataset) where the day exceeds 12. Using dayfirst=True guarantees 100% deterministic parsing with zero data loss.",
        "2. Chronological Disjoint Split: A chronological 70% train / 30% test split cutoff (Oct 29, 2018 11:10:48) is enforced to ensure zero future-to-past lookahead leakage during anomaly baseline calibration and model training.",
        "3. Controlled Anomaly Ground Truth: 30 standardized synthetic injections (spikes, linear drifts, flatlines) are embedded exclusively into the test set to evaluate true early-warning lead times without training contamination."
    ]

    for n in notes:
        p_n = doc.add_paragraph()
        p_n.paragraph_format.space_before = Pt(1)
        p_n.paragraph_format.space_after = Pt(2)
        r_n = p_n.add_run(n)
        r_n.font.name = "Calibri"
        r_n.font.size = Pt(8.2)
        r_n.font.color.rgb = COLOR_DARK

    # Signature / Verification footer
    p_foot = doc.add_paragraph()
    p_foot.paragraph_format.space_before = Pt(6)
    p_foot.paragraph_format.space_after = Pt(0)
    p_foot.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_foot = p_foot.add_run("Submitted as part of MCE Final Project Evaluation | IIIT Allahabad")
    r_foot.font.name = "Calibri"
    r_foot.font.size = Pt(8)
    r_foot.font.italic = True
    r_foot.font.color.rgb = COLOR_GRAY

    doc.save(output_path)
    print(f"One-page dataset Word document created at: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.abspath("docs/Dataset_Submission")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "IIT2023139_Krishna_Sikheriya_Dataset_Link.docx")
    create_document(out_file)
