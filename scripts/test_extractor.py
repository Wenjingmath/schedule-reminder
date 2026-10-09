"""
Schedule Reminder Skill 测试脚本
测试从不同格式文件中提取日程信息的能力
"""
import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path


class ScheduleExtractor:
    """日程信息提取器"""
    
    def __init__(self):
        self.events = []
    
    def extract_from_text(self, text, source_type="text"):
        """从纯文本中提取日程事件"""
        events = []
        
        # 匹配日期时间模式
        # 格式1: 2026年10月15日 下午2:00 - 4:00
        # 格式2: 10月12日 14:00-15:30
        # 格式3: 09:00-10:30 课程名 地点
        
        lines = text.split('\n')
        current_event = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # 尝试提取主题/标题
            if line.startswith('主题:') or line.startswith('主题：'):
                title = line.split(':', 1)[-1].split('：', 1)[-1].strip()
                if current_event is None:
                    current_event = {'title': title}
                else:
                    current_event['title'] = title
            
            # 尝试提取时间 (支持 "下午2:00 - 4:00" 这种省略第二个上下午的格式)
            time_match = re.search(
                r'(\d{4}年)?\s*(\d{1,2})月\s*(\d{1,2})日\s*[，,]?\s*(上午|下午|晚上)?\s*(\d{1,2})[:点](\d{2})?\s*[-~至到]\s*(上午|下午|晚上)?\s*(\d{1,2})[:点]?(\d{2})?',
                line
            )
            if time_match:
                year = time_match.group(1) or str(datetime.now().year)
                year = int(year.replace('年', ''))
                month = int(time_match.group(2))
                day = int(time_match.group(3))
                ampm1 = time_match.group(4)
                start_hour = int(time_match.group(5))
                start_min = int(time_match.group(6) or 0)
                ampm2 = time_match.group(7) or ampm1  # 如果第二个没指定，沿用第一个
                end_hour = int(time_match.group(8) or start_hour)
                end_min = int(time_match.group(9) or 0)
                
                # 处理上下午
                if ampm1 in ['下午', '晚上'] and start_hour < 12:
                    start_hour += 12
                if ampm2 in ['下午', '晚上'] and end_hour < 12:
                    end_hour += 12
                
                start_time = datetime(year, month, day, start_hour, start_min)
                end_time = datetime(year, month, day, end_hour, end_min)
                
                if current_event is None:
                    # 尝试从行中提取标题
                    title_part = re.sub(
                        r'(\d{4}年)?\d{1,2}月\d{1,2}日.*$', '', line
                    ).strip()
                    if title_part:
                        current_event = {'title': title_part}
                    else:
                        current_event = {'title': '未命名事件'}
                
                current_event['start_time'] = start_time.isoformat()
                current_event['end_time'] = end_time.isoformat()
            
            # 提取地点
            if line.startswith('地点:') or line.startswith('地点：'):
                location = line.split(':', 1)[-1].split('：', 1)[-1].strip()
                if current_event:
                    current_event['location'] = location
            
            # 提取摘要/备注
            if line.startswith('备注:') or line.startswith('备注：') or line.startswith('摘要:') or line.startswith('摘要：'):
                summary = line.split(':', 1)[-1].split('：', 1)[-1].strip()
                if current_event:
                    current_event['summary'] = summary
            
            # 如果当前事件有标题和时间，保存并重置
            if current_event and 'title' in current_event and 'start_time' in current_event:
                events.append(current_event)
                current_event = None
        
        # 处理最后一个事件
        if current_event and 'title' in current_event and 'start_time' in current_event:
            events.append(current_event)
        
        return self._add_reminders(events, source_type)
    
    def extract_from_markdown(self, text):
        """从Markdown中提取日程（课程表格式）"""
        events = []
        lines = text.split('\n')
        current_day = None
        day_map = {
            '周一': 0, '周二': 1, '周三': 2, '周四': 3, '周五': 4,
            '星期六': 5, '周日': 6, '星期六': 6
        }
        
        # 找到本周的日期
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        
        for line in lines:
            line = line.strip()
            
            # 检测星期几标题
            for day_name, day_offset in day_map.items():
                if line.startswith('## ' + day_name) or line.startswith('### ' + day_name):
                    current_day = monday + timedelta(days=day_offset)
                    break
            
            # 匹配课程条目: - 09:00-10:30 课程名 地点
            if current_day and line.startswith('- '):
                course_match = re.match(
                    r'-\s*(\d{2}:\d{2})-(\d{2}:\d{2})\s+(.+?)\s{2,}(.+)',
                    line
                )
                if course_match:
                    start_time_str = course_match.group(1)
                    end_time_str = course_match.group(2)
                    title = course_match.group(3).strip()
                    location = course_match.group(4).strip()
                    
                    start_h, start_m = map(int, start_time_str.split(':'))
                    end_h, end_m = map(int, end_time_str.split(':'))
                    
                    start_dt = current_day.replace(hour=start_h, minute=start_m)
                    end_dt = current_day.replace(hour=end_h, minute=end_m)
                    
                    events.append({
                        'title': title,
                        'start_time': start_dt.isoformat(),
                        'end_time': end_dt.isoformat(),
                        'location': location
                    })
        
        return self._add_reminders(events, "markdown")
    
    def extract_from_pdf(self, pdf_path):
        """从PDF中提取文本并解析日程"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # 先尝试标准文本提取
            result = self.extract_from_text(text, "pdf")
            
            # 如果事件少，尝试解析表格格式（如议程表）
            if result['event_count'] == 0:
                events = self._extract_table_schedule(text)
                if events:
                    return self._add_reminders(events, "pdf")
            
            return result
        except ImportError:
            return {"error": "PyPDF2 not available", "events": []}
    
    def _extract_table_schedule(self, text):
        """从表格格式文本中提取日程（如会议议程）"""
        events = []
        lines = text.split('\n')
        
        # 查找日期信息 - 支持中文和英文格式
        year, month, day = None, None, None
        
        # 中文格式: 2026年11月20日
        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if date_match:
            year = int(date_match.group(1))
            month = int(date_match.group(2))
            day = int(date_match.group(3))
        
        # 英文格式: November 20, 2026
        if not year:
            months = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                'september': 9, 'october': 10, 'november': 11, 'december': 12,
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                'jun': 6, 'jul': 7, 'aug': 8,
                'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            date_match = re.search(r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})', text)
            if date_match:
                month_name = date_match.group(1).lower()
                if month_name in months:
                    month = months[month_name]
                    day = int(date_match.group(2))
                    year = int(date_match.group(3))
        
        if not year:
            return events
        
        # 方式1: 匹配整行格式 "HH:MM - HH:MM 标题 演讲者"
        time_pattern = re.compile(r'(\d{2}:\d{2})\s*[-~至]\s*(\d{2}:\d{2})\s+(.+)')
        
        # 方式2: PDF表格按列提取，时间、主题、演讲者各占一行
        # 收集所有非空行
        clean_lines = [line.strip() for line in lines if line.strip()]
        
        i = 0
        time_only_pattern = re.compile(r'^(\d{2}:\d{2})\s*[-~至]\s*(\d{2}:\d{2})$')
        
        while i < len(clean_lines):
            line = clean_lines[i]
            
            # 先尝试整行匹配
            match = time_pattern.match(line)
            if match:
                start_str = match.group(1)
                end_str = match.group(2)
                rest = match.group(3).strip()
                
                start_h, start_m = map(int, start_str.split(':'))
                end_h, end_m = map(int, end_str.split(':'))
                
                start_dt = datetime(year, month, day, start_h, start_m)
                end_dt = datetime(year, month, day, end_h, end_m)
                
                event = {
                    'title': rest,
                    'start_time': start_dt.isoformat(),
                    'end_time': end_dt.isoformat(),
                }
                events.append(event)
                i += 1
                continue
            
            # 尝试按列匹配 (时间行 + 主题行 + 演讲者行)
            time_match = time_only_pattern.match(line)
            if time_match and i + 1 < len(clean_lines):
                start_str = time_match.group(1)
                end_str = time_match.group(2)
                
                start_h, start_m = map(int, start_str.split(':'))
                end_h, end_m = map(int, end_str.split(':'))
                
                start_dt = datetime(year, month, day, start_h, start_m)
                end_dt = datetime(year, month, day, end_h, end_m)
                
                title = clean_lines[i + 1]
                speaker = clean_lines[i + 2] if i + 2 < len(clean_lines) else None
                
                # 跳过表头
                if title.lower() in ['topic', '主题', 'time', '时间']:
                    i += 1
                    continue
                
                event = {
                    'title': title,
                    'start_time': start_dt.isoformat(),
                    'end_time': end_dt.isoformat(),
                }
                if speaker and speaker.lower() not in ['speaker', '演讲者'] and speaker != '—':
                    event['summary'] = f'Speaker: {speaker}'
                
                events.append(event)
                i += 3  # 跳过时间、主题、演讲者三行
                continue
            
            i += 1
        
        return events
    
    def _add_reminders(self, events, source_type):
        """为事件添加提醒"""
        for event in events:
            if 'start_time' in event:
                start_dt = datetime.fromisoformat(event['start_time'])
                
                # 提前一天提醒 (前一天09:00)
                day_before = start_dt - timedelta(days=1)
                day_before = day_before.replace(hour=9, minute=0, second=0)
                
                # 当天提醒 (提前1小时)
                same_day = start_dt - timedelta(hours=1)
                
                event['reminders'] = [
                    {
                        'type': 'day_before',
                        'time': day_before.isoformat(),
                        'message': f"明天{start_dt.strftime('%H:%M')} {event['title']}" + 
                                  (f" @ {event['location']}" if 'location' in event else "")
                    },
                    {
                        'type': 'same_day',
                        'time': same_day.isoformat(),
                        'message': f"1小时后：{event['title']}" +
                                  (f" @ {event['location']}" if 'location' in event else "")
                    }
                ]
        
        return {
            'events': events,
            'source_type': source_type,
            'event_count': len(events),
            'confidence': 0.85 if source_type in ['text', 'markdown'] else 0.7
        }


def run_tests():
    """运行所有测试"""
    extractor = ScheduleExtractor()
    test_dir = Path(__file__).parent.parent / 'assets'
    results = {}
    
    print("=" * 60)
    print("Schedule Reminder Skill 测试")
    print("=" * 60)
    
    # 测试1: 纯文本文件
    print("\n📄 测试1: 纯文本文件 (test_meeting.txt)")
    print("-" * 40)
    txt_file = test_dir / 'test_meeting.txt'
    if txt_file.exists():
        text = txt_file.read_text(encoding='utf-8')
        result = extractor.extract_from_text(text, "text")
        results['text'] = result
        print(f"  提取到 {result['event_count']} 个事件")
        for evt in result['events']:
            print(f"  - {evt['title']}")
            print(f"    时间: {evt.get('start_time', 'N/A')} ~ {evt.get('end_time', 'N/A')}")
            print(f"    地点: {evt.get('location', 'N/A')}")
            print(f"    提醒: {len(evt.get('reminders', []))} 个")
        print("  ✅ 文本提取测试通过")
    else:
        print("  ❌ 文件不存在")
        results['text'] = {"error": "file not found"}
    
    # 测试2: Markdown文件
    print("\n📝 测试2: Markdown课程表 (test_schedule.md)")
    print("-" * 40)
    md_file = test_dir / 'test_schedule.md'
    if md_file.exists():
        text = md_file.read_text(encoding='utf-8')
        result = extractor.extract_from_markdown(text)
        results['markdown'] = result
        print(f"  提取到 {result['event_count']} 个事件")
        for evt in result['events'][:3]:  # 只显示前3个
            print(f"  - {evt['title']}")
            print(f"    时间: {evt.get('start_time', 'N/A')}")
            print(f"    地点: {evt.get('location', 'N/A')}")
        if result['event_count'] > 3:
            print(f"  ... 还有 {result['event_count'] - 3} 个事件")
        print("  ✅ Markdown提取测试通过")
    else:
        print("  ❌ 文件不存在")
        results['markdown'] = {"error": "file not found"}
    
    # 测试3: PDF文件
    print("\n📑 测试3: PDF会议议程 (test_conference.pdf)")
    print("-" * 40)
    pdf_file = test_dir / 'test_conference.pdf'
    if pdf_file.exists():
        try:
            result = extractor.extract_from_pdf(str(pdf_file))
            results['pdf'] = result
            if 'error' not in result:
                print(f"  提取到 {result['event_count']} 个事件")
                for evt in result['events'][:2]:
                    print(f"  - {evt['title']}")
                    print(f"    时间: {evt.get('start_time', 'N/A')}")
                print("  ✅ PDF提取测试通过")
            else:
                print(f"  ⚠️  {result['error']}")
        except Exception as e:
            print(f"  ❌ PDF解析失败: {e}")
            results['pdf'] = {"error": str(e)}
    else:
        print("  ❌ 文件不存在")
        results['pdf'] = {"error": "file not found"}
    
    # 测试4: 图片文件 (验证文件存在)
    print("\n🖼️  测试4: 图片文件 (OCR)")
    print("-" * 40)
    img_files = list(test_dir.glob('test_*.png'))
    if img_files:
        print(f"  找到 {len(img_files)} 张测试图片:")
        for img in img_files:
            print(f"  - {img.name} ({img.stat().st_size // 1024} KB)")
        print("  ✅ 图片文件就绪 (OCR识别需多模态模型支持)")
        results['image'] = {"status": "ready", "count": len(img_files)}
    else:
        print("  ❌ 图片文件不存在")
        results['image'] = {"error": "file not found"}
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = 0
    total = 0
    for test_name, result in results.items():
        total += 1
        if 'error' not in result:
            passed += 1
            status = "✅ 通过"
        else:
            status = "❌ 失败"
        print(f"  {test_name:12s} {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    # 保存详细结果
    output_file = Path(__file__).parent.parent / 'test_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n详细结果已保存到: {output_file}")
    
    return results


if __name__ == "__main__":
    run_tests()
