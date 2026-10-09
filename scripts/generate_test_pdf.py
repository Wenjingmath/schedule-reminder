"""生成测试用的PDF日程文件"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import os

def create_meeting_pdf(output_path):
    """创建会议通知PDF（英文，确保文本可被正确提取）"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 标题
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        textColor=colors.HexColor('#2E86C1'),
        alignment=1,
        spaceAfter=20
    )
    story.append(Paragraph("Tech Summit 2026", title_style))
    
    # 副标题
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        textColor=colors.HexColor('#555555'),
        alignment=1,
        spaceAfter=30
    )
    story.append(Paragraph("Innovation and the Future", subtitle_style))
    
    # 基本信息
    info_style = styles['Normal']
    story.append(Paragraph("<b>Date:</b> November 20, 2026 09:00 - 18:00", info_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Location:</b> International Convention Center, Main Hall", info_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>Organizer:</b> China Information Technology Association", info_style))
    story.append(Spacer(1, 20))
    
    # 议程标题
    agenda_title = ParagraphStyle(
        'AgendaTitle',
        parent=styles['Heading2'],
        textColor=colors.HexColor('#2E86C1'),
        spaceBefore=10,
        spaceAfter=12
    )
    story.append(Paragraph("Conference Agenda", agenda_title))
    
    # 议程表格
    data = [
        ['Time', 'Topic', 'Speaker'],
        ['09:00 - 09:30', 'Opening Remarks', 'President Wang'],
        ['09:30 - 10:30', 'AI Technology Trends', 'Prof. Li'],
        ['10:45 - 11:45', 'Cloud Native Architecture', 'Director Zhang'],
        ['12:00 - 13:30', 'Lunch & Networking', '—'],
        ['13:30 - 14:30', 'LLM Application Practice', 'Dr. Chen'],
        ['14:45 - 15:45', 'Cybersecurity Challenges', 'Expert Liu'],
        ['16:00 - 17:00', 'Panel: Future of Tech', 'Multiple Guests'],
        ['17:00 - 18:00', 'Closing Summary', 'President Wang'],
    ]
    
    table = Table(data, colWidths=[100, 220, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86C1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(table)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Note:</b> Please bring business cards. Coffee breaks and lunch provided.", info_style))
    
    doc.build(story)
    print(f"Created: {output_path}")

if __name__ == "__main__":
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    create_meeting_pdf(os.path.join(assets_dir, 'test_conference.pdf'))
