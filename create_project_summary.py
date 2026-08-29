#!/usr/bin/env python3
"""
Create a concise FiestaFlow project summary DOCX.

Fixes and simplifications:
- Restored and completed style setup that was truncated in the original file.
- Replaced truncated paragraphs with complete, concise paragraphs so the script runs.
- Preserved layout helpers, table/callout functions, and heading styles.
- Adds an optional CLI arg to set the output filename.
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import sys

OUT_DEFAULT = "FiestaFlow_Project_Summary.docx"
GREEN = "174C3C"
DARK = "18342A"
MUTED = "5D6D66"
PALE = "EAF2EE"

def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)

def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in("w:tcMar")
    if tcMar is None:
        tcMar = OxmlElement("w:tcMar")
        tcPr.append(tcMar)
    for m, v in [("top", top), ("start", start), ("bottom", bottom), ("end", end)]:
        node = tcMar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tcMar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")

def set_repeat_table_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)

def set_fixed_table(table, widths):
    table.autofit = False
    tblPr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            try:
                cell.width = Inches(widths[idx])
            except Exception:
                pass
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

def font(run, size=11, bold=False, color=DARK, italic=False):
    # set Calibri as primary font where possible
    try:
        run.font.name = "Calibri"
        rpr = run._element.rPr
        rpr.rFonts.set(qn("w:ascii"), "Calibri")
        rpr.rFonts.set(qn("w:hAnsi"), "Calibri")
    except Exception:
        pass
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    try:
        run.font.color.rgb = RGBColor.from_string(color)
    except Exception:
        pass

def add_text(doc, text, style=None, after=6, before=0):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.10
    font(p.add_run(text))
    return p

def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.10
    font(p.add_run(text))
    return p

def add_number(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.10
    font(p.add_run(text))
    return p

def add_heading(doc, text, level=1):
    style_name = f"Heading {level}"
    p = doc.add_paragraph(style=style_name)
    p.paragraph_format.keep_with_next = True
    size_map = {1: 16, 2: 13, 3: 12}
    color = GREEN if level < 3 else DARK
    font(p.add_run(text), size=size_map.get(level, 11), bold=True, color=color)
    return p

def add_callout(doc, label, body):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    set_fixed_table(table, [6.5])
    cell = table.cell(0, 0)
    set_cell_shading(cell, PALE)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(label.upper() + "  ")
    font(r, size=10, bold=True, color=GREEN)
    r = p.add_run(body)
    font(r, size=10, color=DARK)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def add_table(doc, headers, rows, widths):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    set_fixed_table(table, widths)
    header = table.rows[0]
    set_repeat_table_header(header)
    for i, h in enumerate(headers):
        set_cell_shading(header.cells[i], "DDE9E3")
        p = header.cells[i].paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        font(p.add_run(h), size=9, bold=True, color=GREEN)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            font(p.add_run(value), size=9.5, color=DARK)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_document(out_path=OUT_DEFAULT):
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Inches(1)
    sec.header_distance = sec.footer_distance = Inches(.492)

    # Base Normal style
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    try:
        normal._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    except Exception:
        pass
    normal.font.size = Pt(11)

    # Ensure headings have consistent font and sizes
    headings = [("Heading 1", 16, 16, 8, GREEN), ("Heading 2", 13, 12, 6, GREEN), ("Heading 3", 12, 8, 4, DARK)]
    for name, size, before, after, color in headings:
        try:
            s = styles[name]
            s.font.name = "Calibri"
            s.font.size = Pt(size)
            s.font.bold = True
            # color is applied when writing runs
        except Exception:
            # If a particular heading style is not present, continue
            continue

    # Header and footer
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    font(hp.add_run("FIESTAFLOW  |  PROJECT BRIEF"), size=8.5, bold=True, color=MUTED)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    font(fp.add_run("Confidential working summary • August 2026"), size=8.5, color=MUTED)

    # Title block
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(22)
    p.paragraph_format.space_after = Pt(6)
    font(p.add_run("FIESTAFLOW"), size=12, bold=True, color=GREEN)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    font(p.add_run("Petron Fiesta Gas Distribution\nSystem Project Summary"), size=27, bold=True, color=DARK)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(20)
    font(p.add_run(
        "A consolidated record of the business model, operating workflows, core product requirements, and prototype decisions."
    ), size=12, color=MUTED)

    add_callout(doc, "Purpose", "This document captures working decisions for the FiestaFlow prototype and first-prototype product choices.")

    # Sections (concise but complete)
    add_heading(doc, "1. Executive overview")
    add_text(doc, "FiestaFlow is a connected operating system for a Petron Fiesta Gas distributorship prototype. "
                  "The current prototype demonstrates screens and the main POS logic as a local browser demo.")

    add_heading(doc, "2. Business model and operating structure")
    add_table(doc, ["Area", "Agreed direction"], [
        ("Product", "170g cylinder sold individually and by crate (24). Containers and contents are tracked."),
        ("Locations", "Main warehouse, company-owned branches, and delivery vehicles."),
        ("Customer groups", "Franchisees (account-based) and end users (walk-in).")
    ], [1.8, 4.7])

    add_heading(doc, "3. Inventory and exchange logic")
    add_text(doc, "Sales must distinguish new cylinder sale vs exchange/refill. The system will infer sale type from "
                  "filled and empty counts; operators should be prompted to review mismatches.")

    add_bullet(doc, "Initial purchase: charge cylinder + content.")
    add_bullet(doc, "Exchange: when empties match filled count, charge content/refill only.")
    add_bullet(doc, "Mixed: partial exchange + partial new sale; system splits amounts accordingly.")

    add_heading(doc, "4. POS, payments, and receipts")
    add_table(doc, ["POS decision", "Treatment"], [
        ("Filled > 0; empty = 0", "New sale: charge content + container."),
        ("Filled = empty", "Exchange: charge content/refill only."),
        ("Empty > filled", "Stop and review before completing the sale.")
    ], [2.0, 4.5])

    add_heading(doc, "5. Prototype status and next steps")
    add_table(doc, ["Prototype area", "Current state"], [
        ("Main navigation", "Static pages for overview, POS, dispatch, inventory, and reports."),
        ("POS", "Working layout and decision inference; uses sample data only."),
        ("Data & sign-in", "Not implemented; planned backend needed for multi-user data.")
    ], [1.75, 4.75])

    add_number(doc, "Finish the prototype flows and confirm every screen decision.")
    add_number(doc, "Define operational master data and price book.")
    add_number(doc, "Build a hosted backend (e.g., Supabase) and persist transactions, users, and files.")

    add_callout(doc, "Next practical action", "Refine the POS flows, then create the shared backend and pilot with a single warehouse + branch.")

    # Final small section
    add_heading(doc, "Appendix: Contact and authorship", level=3)
    add_text(doc, "Prepared by the FiestaFlow product team. For questions or updates, see the repository and project notes.")

    # Save
    doc.save(out_path)
    print(out_path)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else OUT_DEFAULT
    build_document(out)
