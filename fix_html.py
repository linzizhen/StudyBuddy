# -*- coding: utf-8 -*-
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到截断位置
search_str = 'planItem.innerHTML = `'
idx = content.find(search_str)
if idx != -1:
    print('截断位置:', idx)
    print('上下文:')
    print(content[idx:idx+200])
else:
    print('未找到截断位置')
