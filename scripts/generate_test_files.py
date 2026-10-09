"""生成测试用的日程图片和PDF文件"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_meeting_screenshot(output_path):
    """创建模拟会议邀请截图"""
    width, height = 800, 500
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 标题栏
    draw.rectangle([0, 0, width, 60], fill='#4A90D9')
    draw.text((30, 18), "会议邀请 - 产品评审会议", fill='white')
    
    # 内容
    y = 90
    lines = [
        "主题: 产品评审会议",
        "时间: 2026年10月12日 下午2:00 - 3:30",
        "地点: 会议室B205",
        "组织者: 李总监",
        "",
        "议程:",
        "  1. 新版本功能演示",
        "  2. UI设计评审",
        "  3. 上线时间确认",
        "",
        "请各部门负责人准时参加。"
    ]
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    for line in lines:
        if line.startswith("主题:") or line.startswith("时间:") or line.startswith("地点:"):
            draw.text((50, y), line, fill='#333333', font=font)
        else:
            draw.text((50, y), line, fill='#555555', font=font_small)
        y += 32
    
    img.save(output_path)
    print(f"Created: {output_path}")

def create_schedule_image(output_path):
    """创建模拟课程表截图"""
    width, height = 900, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.rectangle([0, 0, width, 50], fill='#2ECC71')
    draw.text((350, 12), "本周课程表", fill='white')
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        font_bold = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_bold = ImageFont.load_default()
    
    # 表头
    days = ["时间", "周一", "周二", "周三", "周四", "周五"]
    col_width = 140
    row_height = 50
    
    for i, day in enumerate(days):
        x = 30 + i * col_width
        draw.rectangle([x, 60, x + col_width - 5, 100], fill='#f0f0f0', outline='#ccc')
        draw.text((x + 40, 72), day, fill='#333', font=font)
    
    # 课程数据
    schedule = [
        ["08:00-09:30", "高等数学\nA201", "", "线性代数\nA103", "", "概率论\nA203"],
        ["10:00-11:30", "", "英语听说\n305", "", "数据结构\n301", ""],
        ["14:00-15:30", "大学物理\nB102", "", "实验课\nB201", "", "体育\n体育馆"],
        ["16:00-17:30", "", "程序设计\n401", "", "", ""],
    ]
    
    colors = ['#E8F4FD', '#FFF3E0', '#E8F5E9', '#F3E5F5', '#FFFDE7']
    
    for row_idx, row in enumerate(schedule):
        y = 110 + row_idx * row_height
        for col_idx, cell in enumerate(row):
            x = 30 + col_idx * col_width
            if cell:
                color = colors[(row_idx + col_idx) % len(colors)]
                draw.rectangle([x, y, x + col_width - 5, y + row_height - 5], 
                             fill=color, outline='#ddd')
                lines = cell.split('\n')
                for line_idx, line in enumerate(lines):
                    draw.text((x + 15, y + 10 + line_idx * 20), line, fill='#333', font=font)
            else:
                draw.rectangle([x, y, x + col_width - 5, y + row_height - 5], 
                             fill='white', outline='#eee')
    
    img.save(output_path)
    print(f"Created: {output_path}")

if __name__ == "__main__":
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    create_meeting_screenshot(os.path.join(assets_dir, 'test_meeting.png'))
    create_schedule_image(os.path.join(assets_dir, 'test_schedule.png'))
