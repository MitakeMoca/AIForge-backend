from bs4 import BeautifulSoup

with open('CCSKG.html', 'r', encoding='utf-8') as file:
    html_content = file.read()
# 假设html_content是你的HTML内容
soup = BeautifulSoup(html_content, 'html.parser')

# 遍历所有的标签
for element in soup.find_all():
    # 如果标签不是<a>或<ul>，则替换为它的文本内容
    if element.name not in ['a', 'ul']:
        element.unwrap()
    else:
        # 去掉标签的属性
        element.attrs = {}

# 打印处理后的HTML
with open('output.html', 'w', encoding='utf-8') as file:
    file.write(str(soup))