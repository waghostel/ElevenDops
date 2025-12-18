
import re

content = """
    Intro text
    
    # Header 1
    Section 1 content
    
    ## Header 2
    Section 2 content
    """

def parse(content):
    sections = {}
    matches = list(re.finditer(r'(^|\n)(?P<level>#{1,6})\s(?P<title>.*)', content))
    print(f"Matches found: {len(matches)}")
    for m in matches:
        print(f"Match: {m.group('title')}, Start: {m.start()}, End: {m.end()}")
        
    if not matches:
        if content.strip():
            sections["content"] = content
        return sections

    for i, match in enumerate(matches):
        current_start = match.start()
        if i == 0:
            intro = content[0:current_start].strip()
            if intro:
                print(f"Intro found: '{intro}'")
                sections["Introduction"] = intro

        header_title = match.group("title").strip()
        match_end = match.end()
        
        if i + 1 < len(matches):
            next_start = matches[i+1].start()
            section_content = content[match_end:next_start].strip()
        else:
            section_content = content[match_end:].strip()
            
        print(f"Section '{header_title}': '{section_content}'")
        if section_content:
            sections[header_title] = section_content
            
    return sections

print(parse(content))
