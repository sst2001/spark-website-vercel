import json
import re
from collections import OrderedDict

# Load unique blog posts
with open('all-blog-posts-unique.json', 'r') as f:
    blog_posts = json.load(f)

print(f"Loaded {len(blog_posts)} unique blog posts")

# Read original file
with open('old/www.spark.org.il/blog.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find blog section using simpler approach
# Find: <h2 class="blog-name">The Spark Blog</h2>
start_marker = '<h2 class="blog-name">The Spark Blog</h2>'
end_marker = '</div>  </div>  </div>'  # End of blog container

start_pos = content.find(start_marker)
if start_pos == -1:
    print("Could not find blog header")
    exit(1)

# Find the <div class="inner "> that comes after
inner_start = content.find('<div class="inner ">', start_pos)
if inner_start == -1:
    print("Could not find inner div")
    exit(1)

# Find the end - look for the specific closing pattern
# Find: </div> followed by two more </div> tags (end of postArticle, end of inner, end of container)
remaining_content = content[inner_start:]
# We need to find where the original blog posts end
# Look for a specific marker that indicates end of posts
# Try to find after a reasonable number of characters

# Let's find the end more carefully
# Find position after <div class="inner ">
pos = inner_start
depth = 0
found_end = False
search_pos = inner_start + len('<div class="inner ">')

# Scan for the three closing </div> tags
for i in range(search_pos, min(search_pos + 50000, len(content))):
    if content[i:i+6] == '</div>':
        depth += 1
        if depth >= 3:
            # Skip any whitespace
            j = i + 6
            while j < len(content) and content[j] in [' ', '\n', '\t']:
                j += 1
            inner_end = j
            found_end = True
            break
    elif content[i:i+5] == '<div ':
        depth = max(0, depth - 1)

if not found_end:
    # Fallback: look for </div>  </div>  </div> (with spaces)
    inner_end_match = re.search(r'</div>\s*</div>\s*</div>', content[search_pos:search_pos+10000])
    if inner_end_match:
        inner_end = search_pos + inner_end_match.end()
        found_end = True

if not found_end:
    # Try simpler: find first occurrence of </div></div></div>
    simple_pattern = r'</div>\s*</div>\s*</div>'
    simple_match = re.search(simple_pattern, content[search_pos:search_pos+50000])
    if simple_match:
        inner_end = search_pos + simple_match.end()
        found_end = True

if not found_end:
    print("Could not find end of blog section")
    exit(1)

print(f"Blog section: {inner_start} to {inner_end}")

# Now generate blog posts HTML (only the inner content, no header)
blog_posts_html = []

for idx, post in enumerate(blog_posts):
    col = (idx % 3) + 1
    row = (idx // 3) + 1
    last_class = "lastArticle" if col == 3 else ""
    animation = idx * 200
    
    # Build each post
    post_line1 = f''' <div style="-ms-grid-column:{col}; -ms-grid-row:{row}" class="postArticle {last_class}"> <div class="inner clearfix wow" style="animation-delay: {animation}ms;"> <a class="blogImgLink" dont-color-link="true" href="{post['filename']}" data-blog-post-alias="{post['filename'].replace('.html', '')}"> <div class="blogImg" style="background-image: url('{post['image']}');"><img src="{post['image']}" "="" onerror="handleImageLoadError(this)"/></div>'''
    post_line2 = '</a>'
    post_line3 = f''' <div class="postTextContainer"> <div class="postText clearfix"> <div class="postTitle"> <h3> <a dont-color-link="true" href="{post['filename']}" data-blog-post-alias="{post['filename'].replace('.html', '')}">{post['title']}</a>'''
    post_line4 = '</h3>'
    post_line5 = '</div>'
    post_line6 = f''' <div class="authorBar"> <span>By {post['author']}</span>'''
    post_line7 = '<span>&bull;</span>'
    post_line8 = f'''<span>By {post['date_formatted']}</span>'''
    post_line9 = '</div>'
    post_line10 = f'''<div class="postDescription">{post['description']}</div>'''
    post_line11 = '</div>'
    post_line12 = f'''<div class="readMore"> <a dont-color-link="true" href="{post['filename']}"></a>'''
    post_line13 = '</div>'
    post_line14 = '</div>'
    post_line15 = '</div>'
    post_line16 = '</div>'
    
    blog_posts_html.extend([
        post_line1, post_line2, post_line3, post_line4, post_line5,
        post_line6, post_line7, post_line8, post_line9, post_line10,
        post_line11, post_line12, post_line13, post_line14, post_line15, post_line16
    ])

# Add closing divs
blog_posts_html.append('</div>')
blog_posts_html.append('</div>')
blog_posts_html.append('</div>')

# Replace content
new_content = content[:inner_start + len('<div class="inner ">')] + '\n' + '\n'.join(blog_posts_html) + content[inner_end:]

# Write to deploy
with open('deploy/blog.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ Rebuilt with {len(blog_posts)} unique posts")
