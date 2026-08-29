from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P

SOURCE = 'FiestaFlow_Project_Summary.docx'
OUTPUT = 'FiestaFlow_Project_Summary.md'

def blocks(document):
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)

def clean(text):
    return ' '.join(text.replace('|', '\\|').split())

with open(OUTPUT, 'w', encoding='utf-8') as out:
    out.write('# FiestaFlow — Petron Fiesta Gas Distribution System Project Summary\n\n')
    out.write('> Comprehensive working record of the business model, requirements, workflow decisions, prototype status, and build plan.\n\n')
    for block in blocks(Document(SOURCE)):
        if isinstance(block, Paragraph):
            text = clean(block.text)
            if not text:
                continue
            if text in {
                'FIESTAFLOW',
                'Petron Fiesta Gas Distribution System Project Summary',
                'A consolidated record of the business model, operating workflows, product requirements, and first-prototype decisions.',
            }:
                continue
            style = block.style.name
            if style.startswith('Heading '):
                level = style.split()[-1]
                out.write(f"{'#' * int(level)} {text}\n\n")
            elif style == 'List Bullet':
                out.write(f'- {text}\n')
            elif style == 'List Number':
                out.write(f'1. {text}\n')
            else:
                out.write(f'{text}\n\n')
        else:
            rows = [[clean(cell.text) for cell in row.cells] for row in block.rows]
            if not rows:
                continue
            if len(rows) == 1 and len(rows[0]) == 1:
                out.write(f'> {rows[0][0]}\n\n')
                continue
            out.write('| ' + ' | '.join(rows[0]) + ' |\n')
            out.write('| ' + ' | '.join('---' for _ in rows[0]) + ' |\n')
            for row in rows[1:]:
                out.write('| ' + ' | '.join(row) + ' |\n')
            out.write('\n')

print(OUTPUT)
