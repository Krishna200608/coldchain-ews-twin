"""Build the official Google Classroom submission ZIP package for Topic 21.

Roll No: IIT2023139
Student: Krishna Sikheriya
Course: Managing Corporate Entrepreneurship (7th Semester B.Tech IT, IIITA)
Instructor: Dr. Netranand Pathak

Output Archive: IIT2023139_Krishna_Sikheriya_Final_Submission.zip
Package Structure:
  IIT2023139_Krishna_Sikheriya_Final_Submission/
    ├── Final_Report/
    │   ├── IIT2023139_Krishna_Sikheriya_ColdChain_Report.pdf
    │   ├── Final_Report.md
    │   ├── Krishna_Sikheriya_ColdChain_Report.tex
    │   ├── references.bib
    │   └── figures/
    ├── PPT/
    │   ├── Presentation.pdf
    │   ├── Presentation.pptx
    │   └── Presentation.md
    ├── Dataset/
    │   ├── IOT-temp.csv
    │   └── README.md
    ├── Reviewed_Research_Papers/
    │   ├── README.md
    │   └── (8 full-text PDFs)
    └── Paper_Code/
        ├── src/
        ├── dashboard/
        ├── scripts/
        ├── tests/
        ├── models/
        ├── Context/
        ├── colab/
        ├── notebooks/
        ├── data/
        ├── requirements.txt
        ├── README.md
        └── PRIMER.md
"""

import os
import zipfile
import shutil

ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ZIP_NAME = "IIT2023139_Krishna_Sikheriya_Final_Submission.zip"
ZIP_PATH = os.path.join(ROOT_DIR, ZIP_NAME)
PREFIX = "IIT2023139_Krishna_Sikheriya_Final_Submission"

EXCLUDE_DIRS = {
    ".venv",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "scratch",
    ".gemini"
}

EXCLUDE_EXTS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".DS_Store"
}

def should_exclude(rel_path):
    parts = rel_path.replace("\\", "/").split("/")
    for p in parts:
        if p in EXCLUDE_DIRS:
            return True
    ext = os.path.splitext(rel_path)[1].lower()
    if ext in EXCLUDE_EXTS:
        return True
    return False

def add_file(zf, src_path, arc_path):
    if not os.path.exists(src_path):
        print(f"WARNING: File not found: {src_path}")
        return
    size = os.path.getsize(src_path)
    zf.write(src_path, arc_path)
    print(f"  + [{size:>10,} bytes] {arc_path}")

def add_dir(zf, src_dir, arc_dir, filter_fn=None):
    if not os.path.exists(src_dir):
        print(f"WARNING: Dir not found: {src_dir}")
        return
    for root, dirs, files in os.walk(src_dir):
        # prune excluded directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for f in files:
            src_f = os.path.join(root, f)
            rel = os.path.relpath(src_f, src_dir)
            if filter_fn and filter_fn(rel):
                continue
            if should_exclude(rel):
                continue
            arc_f = os.path.join(arc_dir, rel).replace("\\", "/")
            zf.write(src_f, arc_f)

def build_package():
    print(f"Starting build of {ZIP_PATH}...")
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)

    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        # 1. Final Report
        print("\n--- 1. Packaging Final Report ---")
        rep_dir = os.path.join(ROOT_DIR, "docs", "Report")
        add_file(zf, os.path.join(rep_dir, "IIT2023139_Krishna_Sikheriya_ColdChain_Report.pdf"),
                 f"{PREFIX}/Final_Report/IIT2023139_Krishna_Sikheriya_ColdChain_Report.pdf")
        add_file(zf, os.path.join(rep_dir, "Final_Report.md"),
                 f"{PREFIX}/Final_Report/Final_Report.md")
        add_file(zf, os.path.join(rep_dir, "Krishna_Sikheriya_ColdChain_Report.tex"),
                 f"{PREFIX}/Final_Report/Krishna_Sikheriya_ColdChain_Report.tex")
        add_file(zf, os.path.join(rep_dir, "references.bib"),
                 f"{PREFIX}/Final_Report/references.bib")
        add_dir(zf, os.path.join(rep_dir, "figures"), f"{PREFIX}/Final_Report/figures")

        # 2. PPT
        print("\n--- 2. Packaging Presentation (PPT) ---")
        add_file(zf, os.path.join(rep_dir, "Presentation.pdf"),
                 f"{PREFIX}/PPT/Presentation.pdf")
        add_file(zf, os.path.join(rep_dir, "Presentation.pptx"),
                 f"{PREFIX}/PPT/Presentation.pptx")
        add_file(zf, os.path.join(rep_dir, "Presentation.md"),
                 f"{PREFIX}/PPT/Presentation.md")

        # 3. Dataset
        print("\n--- 3. Packaging Dataset ---")
        ds_dir = os.path.join(ROOT_DIR, "docs", "Dataset_Submission")
        add_file(zf, os.path.join(ds_dir, "IOT-temp.csv"),
                 f"{PREFIX}/Dataset/IOT-temp.csv")
        add_file(zf, os.path.join(ds_dir, "README.md"),
                 f"{PREFIX}/Dataset/README.md")

        # 4. Reviewed Research Papers
        print("\n--- 4. Packaging Reviewed Research Papers ---")
        rp_dir = os.path.join(ROOT_DIR, "docs", "Research_Papers")
        add_dir(zf, rp_dir, f"{PREFIX}/Reviewed_Research_Papers")

        # 5. Paper Code (Clean, without .venv)
        print("\n--- 5. Packaging Paper Code ---")
        code_dirs = [
            ("src", f"{PREFIX}/Paper_Code/src"),
            ("dashboard", f"{PREFIX}/Paper_Code/dashboard"),
            ("scripts", f"{PREFIX}/Paper_Code/scripts"),
            ("tests", f"{PREFIX}/Paper_Code/tests"),
            ("models", f"{PREFIX}/Paper_Code/models"),
            ("Context", f"{PREFIX}/Paper_Code/Context"),
            ("colab", f"{PREFIX}/Paper_Code/colab"),
            ("notebooks", f"{PREFIX}/Paper_Code/notebooks"),
            ("data", f"{PREFIX}/Paper_Code/data"),
        ]
        for src_sub, arc_sub in code_dirs:
            full_sub = os.path.join(ROOT_DIR, src_sub)
            add_dir(zf, full_sub, arc_sub)

        code_files = [
            "requirements.txt",
            "README.md",
            "PRIMER.md",
            ".env",
            ".gitignore"
        ]
        for cf in code_files:
            add_file(zf, os.path.join(ROOT_DIR, cf), f"{PREFIX}/Paper_Code/{cf}")

    total_size = os.path.getsize(ZIP_PATH)
    print(f"\n=======================================================")
    print(f"SUCCESS: Package built at: {ZIP_PATH}")
    print(f"Total Archive Size: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)")
    print(f"=======================================================\n")

if __name__ == "__main__":
    build_package()
