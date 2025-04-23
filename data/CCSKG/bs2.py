from bs4 import BeautifulSoup

with open("output.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# 假设html_content是你的HTML内容
soup = BeautifulSoup(html_content, 'html.parser')

# 遍历所有的<a>标签
with open('output.txt', 'w', encoding='utf-8') as file:
    for a_tag in soup.find_all('a'):
        # 获取当前<a>标签的文本
        current_text = a_tag.get_text(strip=True)
        if current_text == "root":
            continue
        # 获取父节点的父节点
        grandparent = a_tag.parent.parent
        
        if grandparent:
            # 获取父节点的第一个子节点
            first_child = grandparent.find(True, recursive=False)
            if first_child:
                first_child_text = first_child.get_text(strip=True)
                print("{" + f"node: '{current_text}', father: '{first_child_text}'" + "},", file=file)
            else:
                print("{" + f"node: '{current_text}', father: 'no father'" + "},", file=file)
        else:
            print('No grandparent found', file=file)
        
        print('-' * 40)