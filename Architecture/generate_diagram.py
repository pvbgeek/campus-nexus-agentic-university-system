"""Generate the current architecture as a precise monochrome diagram."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
W,H=2400,1950
image=Image.new('RGB',(W,H),'white')
draw=ImageDraw.Draw(image)

def face(size,bold=False):
    names=[('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf')]
    for name in names:
        if Path(name).is_file():return ImageFont.truetype(name,size)
    return ImageFont.load_default(size=size)

def centered(text,x,y,w,size=28,bold=False):
    font=face(size,bold)
    for i,line in enumerate(text.split('\n')):
        bounds=draw.textbbox((0,0),line,font=font)
        draw.text((x+(w-(bounds[2]-bounds[0]))/2,y+i*(size+12)),line,font=font,fill='black')

def box(bounds,title,body,size=36):
    size=max(size,36)
    x1,y1,x2,y2=bounds
    draw.rectangle(bounds,fill='#f4f4f4',outline='black',width=3)
    centered(title,x1,y1+22,x2-x1,size+3,True)
    if body:centered(body,x1,y1+78,x2-x1,size,False)

def arrow(start,end):
    draw.line([start,end],fill='black',width=4)
    x,y=end;dx=end[0]-start[0];dy=end[1]-start[1]
    if abs(dy)>abs(dx):
        sign=1 if dy>0 else -1;draw.polygon([(x,y),(x-12,y-sign*20),(x+12,y-sign*20)],fill='black')
    else:
        sign=1 if dx>0 else -1;draw.polygon([(x,y),(x-sign*20,y-12),(x-sign*20,y+12)],fill='black')

centered('Campus Nexus: current support architecture',100,38,2200,46,True)
centered('Working progress build | November 12, 2026',100,108,2200,36)
box((100,190,1120,350),'Customer browser','Own orders, refund request, cases and mock inbox',28)
box((1280,190,2300,350),'Staff browser','Evidence review, decisions, authority and reports',28)
arrow((610,350),(610,425));arrow((1790,350),(1790,425))
box((100,425,2300,595),'FastAPI and authenticated sessions','Server identity and role checks | CSRF protection | scoped case APIs',32)
arrow((1200,595),(1200,670))
draw.rectangle((100,670,2300,1050),outline='black',width=3)
centered('LangGraph orchestrator: five live Groq agents',100,690,2200,40,True)
roles=[('Intake','Summarize request\nform policy query'),('Records','Scoped order\nvector evidence'),('Refunds','Propose action\ncall guarded tool'),('Email','Draft update\ncase mock inbox'),('Reporting','Case summary\nledger facts')]
for i,(title,body) in enumerate(roles):
    left=125+i*440
    box((left,780,left+390,975),title,body,27)
    if i<4:arrow((left+390,877),(left+437,877))
centered('Groq cloud inference; API key stays on server; validated outputs and bounded usage',100,1005,2200,36)
arrow((1200,1050),(1200,1130))
box((100,1130,2300,1310),'Local MCP stdio tools: one bound case','Declared tools and strict arguments | model text cannot grant authority',32)
for x in (375,1150,1975):arrow((x,1310),(x,1400))
box((100,1400,650,1640),'Policy retrieval','FastEmbed ONNX\n384 dimensional vectors\nPersistent Qdrant',26)
box((800,1400,1500,1640),'Execution gateway','Evidence, amount and case checks\nLedger rechecks $100 / $500 caps\nDenial, revocation, duplicates',26)
box((1650,1400,2300,1640),'SQLite stores','Cases, sessions and memory\nLedger and mock balances\nInbox, runs and audit events',26)
arrow((1500,1525),(1650,1525))
centered('Financial boundary: ledger entry and mock account credit share one transaction.',100,1705,2200,36,True)
centered('Policy vectors are reference data. Private case/profile reads currently use scoped SQL.',100,1770,2200,36)
centered('Payments and external email are mocked. Hosting, policy upload UI and broader attacks remain pending.',100,1835,2200,36)
output=ROOT/'Architecture/architecture.png'
image.save(output)
print('Generated:',output)
