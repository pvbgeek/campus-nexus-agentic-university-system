"""Build the plain progress report from Markdown using ReportLab."""
from pathlib import Path
import html
import re
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, LongTable, TableStyle, Preformatted, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'report/Progress_Report.md'
OUTPUT=ROOT/'report/Progress_Report.pdf'
for font_name,filename in [
    ("ReportSerif","LiberationSerif-Regular.ttf"),
    ("ReportSerifBold","LiberationSerif-Bold.ttf"),
    ("ReportSerifItalic","LiberationSerif-Italic.ttf"),
    ("ReportSerifBoldItalic","LiberationSerif-BoldItalic.ttf"),
    ("ReportMono","LiberationMono-Regular.ttf")]:
    pdfmetrics.registerFont(TTFont(font_name,str(ROOT/"report/fonts"/filename)))
pdfmetrics.registerFontFamily("ReportSerif",normal="ReportSerif",bold="ReportSerifBold",italic="ReportSerifItalic",boldItalic="ReportSerifBoldItalic")
styles=getSampleStyleSheet()
styles.add(ParagraphStyle('BodyTextReport',fontName='ReportSerif',fontSize=10.6,leading=13.7,spaceAfter=8,splitLongWords=True))
styles.add(ParagraphStyle('ReportTitle',fontName='ReportSerifBold',fontSize=22,leading=26,alignment=TA_CENTER,spaceAfter=9))
styles.add(ParagraphStyle('ReportH2',fontName='ReportSerifBold',fontSize=15,leading=18,spaceBefore=0,spaceAfter=12,keepWithNext=True))
styles.add(ParagraphStyle('ReportH3',fontName='ReportSerifBold',fontSize=11.5,leading=14,spaceBefore=7,spaceAfter=6,keepWithNext=True))
styles.add(ParagraphStyle('ReportCell',fontName='ReportSerif',fontSize=9,leading=11.1,spaceAfter=0,splitLongWords=True))
styles.add(ParagraphStyle('ReportCode',fontName='ReportMono',fontSize=8.2,leading=10.3,spaceBefore=3,spaceAfter=10,backColor=colors.HexColor('#f7f7f7'),borderPadding=6))


def inline(text):
    text=html.escape(text)
    text=re.sub(r'`([^`]+)`',r'<font name="ReportMono" size="8.5">\1</font>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',text)
    return text


def paragraph(text,style='BodyTextReport'):
    return Paragraph(inline(text),styles[style])


story=[]
lines=SOURCE.read_text(encoding='utf-8').splitlines()
i=0
while i<len(lines):
    line=lines[i].strip()
    if not line:i+=1;continue
    if line=='<!-- PAGE -->':story.append(PageBreak());i+=1;continue
    if line.startswith('```'):
        code=[];i+=1
        while i<len(lines) and not lines[i].strip().startswith('```'):
            code.append(lines[i]);i+=1
        story.append(Preformatted('\n'.join(code),styles['ReportCode']));i+=1;continue
    if line.startswith('!['):
        ref=re.search(r'\]\((.*?)\)',line).group(1)
        path=(SOURCE.parent/ref).resolve()
        with PILImage.open(path) as raster:
            width,height=raster.size
        img=Image(str(path),width=512,height=512*height/width)
        story.extend([img,Spacer(1,8)]);i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r'[:\- ]+',c) for c in cells):rows.append(cells)
            i+=1
        n=len(rows[0]);widths={2:[244,268],3:[130,192,190]}.get(n,[512/n]*n)
        if n==3 and rows[0][0]=='Member':widths=[88,166,258]
        cells=[[paragraph(c,'ReportCell') for c in row] for row in rows]
        table=LongTable(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),
            ('LINEABOVE',(0,0),(-1,0),.6,colors.black),('LINEBELOW',(0,0),(-1,0),.5,colors.black),
            ('LINEBELOW',(0,-1),(-1,-1),.5,colors.black),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
            ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ]))
        story.extend([table,Spacer(1,10)]);continue
    if line.startswith('### '):story.append(paragraph(line[4:],'ReportH3'));i+=1;continue
    if line.startswith('## '):story.append(paragraph(line[3:],'ReportH2'));i+=1;continue
    if line.startswith('# '):story.append(paragraph(line[2:],'ReportTitle'));i+=1;continue
    block=[line];i+=1
    if not re.match(r'^\d+\. ',line):
        while i<len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#','|','```','<!--','![')) and not re.match(r'^\d+\. ',lines[i].strip()):
            block.append(lines[i].strip());i+=1
    story.append(paragraph(' '.join(block)))


def page(canvas,doc):
    canvas.saveState()
    canvas.setFont('ReportSerif',8.5)
    canvas.drawString(50,768,'Campus Nexus | CSEN 296')
    canvas.drawRightString(562,768,'Progress report | November 12, 2026')
    canvas.setLineWidth(.4);canvas.line(50,760,562,760)
    canvas.drawRightString(562,27,str(doc.page))
    canvas.restoreState()

OUTPUT.parent.mkdir(exist_ok=True)
SimpleDocTemplate(str(OUTPUT),pagesize=letter,rightMargin=50,leftMargin=50,topMargin=46,bottomMargin=42,
                  title='Campus Nexus Project Progress Report',author='Campus Nexus project team').build(story,onFirstPage=page,onLaterPages=page)
print(OUTPUT)
