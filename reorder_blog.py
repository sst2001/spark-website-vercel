import re
import json

# Load the sorted order
with open('sorted-blog-complete.json', 'r') as f:
    sorted_order = json.load(f)

# Read the blog.html file
with open('deploy/blog.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract all blog post entries (complete divs from opening to closing)
pattern = r'(<div[^>]*class="postArticle"[^>]*>.*?</div>\s*</div>\s*</div>)'

matches = list(re.finditer(pattern, content, flags=re.DOTALL))
print(f"Found {len(matches)} blog post divs")

# Extract each entry with its filename
blog_entries = {}
for match in matches:
    entry_html = match.group(1)
    # Find the href to identify which blog post this is
    href_match = re.search(r'href="([^"]+\.html)"', entry_html)
    if href_match:
        filename = href_match.group(1)
        # Only process blog post files, not navigation links
        if filename not in ['index.html', 'about.html', 'contact.html', 'blog.html', 'ip.html']:
            blog_entries[filename] = entry_html

print(f"Extracted {len(blog_entries)} blog posts")

# Grid positions for 37 posts in 3-column layout
def get_grid_positions(num_posts):
    positions = []
    row = 1
    col = 1
    for i in range(num_posts):
        positions.append((col, row, 200 + i * 200))
        col += 1
        if col > 3:
            col = 1
            row += 1
    return positions

grid_positions = get_grid_positions(len(sorted_order))

# Build reordered HTML
reordered_html = []
for i, entry_data in enumerate(sorted_order):
    filename = entry_data['filename']
    if filename in blog_entries:
        html = blog_entries[filename]
        col, row, delay = grid_positions[i]
        
        # Update grid position
        html = re.sub(
            r'style="([^"]*)',
            f'style="-ms-grid-column:{col}; -ms-grid-row:{row}',
            html,
            count=1
        )
        
        # Update animation delay
        html = re.sub(
            r'animation-delay: \d+\.?\d*ms',
            f'animation-delay: {delay}ms',
            html
        )
        
        reordered_html.append(html)
        print(f"{i+1:2d}. {filename[:55]}")
    else:
        print(f"  WARNING: {filename} not found in blog.html")

# Find the blog posts container and replace all entries
# Match from the first postArticle to the last one
container_pattern = r'(<div[^>]*internal_blog_list[^>]*>)(.*?)(</div>\s*<div[^>]*>.*?</div>\s*</div>\s*</div>)'

# Find where the blog posts section is
inner_start = content.find('<div')
inner_end = content.rfind('</div>')

# Find all postArticle blocks in order
all_posts = '\n'.join(reordered_html)

# Replace all postArticle blocks with the reordered ones
# We need to find the container that holds them
container_match = re.search(r'(<div[^>]*internal_blog_list[^>]*>.*?)(</div>\s*<div[^>]*>.*?</div>\s*</div>\s*</div>)', content, flags=re.DOTALL)

if container_match:
    before = content[:container_match.start()]
    after = content[container_match.end():]
    
    # Find the closing div structure
    middle_start = container_match.end(1)
    
    # Get everything between the opening and closing divs
    temp_content = content[container_match.start():container_match.end()]
    
    # Extract just the posts section
    # Split by postArticle divs
    post_parts = re.split(r'<div[^>]*class="postArticle"[^>]*>', content)[1:]
    
    # Rebuild with new posts
    # Find where posts start and end
    first_post = content.find('<div style="')
    
    # Find last closing div of posts section
    last_closing = content.rfind('</div>')
    
    # Create new content by replacing the middle section
    new_content = before + container_match.group(1) + '\n'.join(reordered_html) + container_match.group(2) + after
    
    # Actually, let me find the exact pattern
    # Find all positions of postArticle
    positions = []
    for match in re.finditer(r'<div[^>]*class="postArticle"', content):
        positions.append(match.start())
    
    if positions:
        # Replace between first and last postArticle
        start_idx = positions[0]
        
        # Find the end of the last post
        last_match = list(re.finditer(r'</div>\s*</div>\s*</div>', content))[-1]
        end_idx = last_match.end()
        
        # Build new content
        new_content = content[:start_idx] + '\n'.join(reordered_html) + '\n' + content[end_idx:]
        
        with open('deploy/blog.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"\n✓ Reordered blog posts in deploy/blog.html")

print("Done!")

