import re
from typing import List, Dict, Any, Optional
from api.models import Guide, GuideSection

class GuideParser:
    def parse(self, markdown: str) -> Guide:
        lines = markdown.split('\n')
        title = "未命名攻略"
        sections: List[GuideSection] = []
        
        # Extract title
        if lines and lines[0].startswith('# '):
            title = lines[0][2:].strip()
            lines = lines[1:]
            
        # Split into sections
        current_section_title = ""
        current_section_lines = []
        
        for line in lines:
            if line.startswith('## '):
                # Save previous section
                if current_section_title or current_section_lines:
                    self._add_section(sections, current_section_title, current_section_lines)
                
                current_section_title = line[3:].strip()
                current_section_lines = []
            else:
                current_section_lines.append(line)
                
        # Add last section
        if current_section_title or current_section_lines:
            self._add_section(sections, current_section_title, current_section_lines)
            
        return Guide(title=title, sections=sections)

    def _add_section(self, sections: List[GuideSection], title: str, lines: List[str]):
        content = '\n'.join(lines).strip()
        if not title and not content:
            return

        section_type = "text"
        data = None
        
        # Basic heuristic for section type
        lower_title = title.lower()
        
        if "天气" in lower_title or "weather" in lower_title:
            section_type = "weather"
            data = self._parse_table(lines)
        elif "通勤" in lower_title or "交通" in lower_title or "commute" in lower_title:
            section_type = "commute"
            # Try to find sub-sections (###) for tabs
            data = self._parse_subsections(lines)
        elif "day" in lower_title or "日程" in lower_title or "schedule" in lower_title:
            section_type = "timeline"
            data = self._parse_timeline(lines)
        elif "费用" in lower_title or "cost" in lower_title or "budget" in lower_title:
            section_type = "expenses"
            data = self._parse_table(lines)
        elif "酒店" in lower_title or "hotel" in lower_title:
            section_type = "info"
        
        sections.append(GuideSection(
            title=title,
            type=section_type,
            content=content,
            data=data
        ))

    def _parse_table(self, lines: List[str]) -> Optional[List[Dict[str, str]]]:
        # Simple markdown table parser
        headers = []
        rows = []
        in_table = False
        
        for line in lines:
            if '|' in line:
                # Remove leading/trailing pipes and whitespace
                cells = [c.strip() for c in line.strip('|').split('|')]
                
                if not in_table:
                    if '---' in line: 
                        continue # Skip separator line
                    headers = cells
                    in_table = True
                else:
                    if '---' in line:
                        continue
                    if len(cells) == len(headers):
                        row = {headers[i]: cells[i] for i in range(len(headers))}
                        rows.append(row)
        
        return rows if rows else None

    def _parse_subsections(self, lines: List[str]) -> Optional[Dict[str, str]]:
        # Parse ### subsections
        subsections = {}
        current_sub = "default"
        current_lines = []
        
        for line in lines:
            if line.startswith('### '):
                if current_lines and current_sub != "default":
                    subsections[current_sub] = '\n'.join(current_lines).strip()
                current_sub = line[4:].strip()
                current_lines = []
            else:
                current_lines.append(line)
        
        if current_lines and current_sub != "default":
             subsections[current_sub] = '\n'.join(current_lines).strip()
             
        return subsections if subsections else None

    def _parse_timeline(self, lines: List[str]) -> Optional[List[Dict[str, str]]]:
        # Parse timeline from table
        # Expected headers: 时间, 项目, 详情 (or similar)
        rows = self._parse_table(lines)
        if not rows:
            return None
            
        timeline = []
        for row in rows:
            # Normalize keys
            time_key = next((k for k in row.keys() if "时间" in k or "Time" in k), None)
            item_key = next((k for k in row.keys() if "项目" in k or "Item" in k or "Activity" in k), None)
            desc_key = next((k for k in row.keys() if "详情" in k or "Detail" in k or "Desc" in k), None)
            
            if time_key and item_key:
                timeline.append({
                    "time": row[time_key],
                    "title": row[item_key],
                    "description": row[desc_key] if desc_key else ""
                })
        
        return timeline
