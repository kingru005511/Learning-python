# coding:utf-8
# python3
# 此意系
import re
import os

with open('./content.txt', encoding='utf-8') as fh:
    string = fh.readlines()



pattern = re.compile('''((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)''')


lst = []


for line in string:
    line = line.rstrip()
    match = pattern.search(line)
    if match:
        lst.append(match[0])
    else:
        lst.append(None)


with open('./infor/ips.txt', mode='a+', encoding='utf-8') as w1:
    for ip in lst:
        if ip:
            w1.write(ip+ "\n")
        else:
            print("执行结束!")
    w1.close()


f3 = open(f"./infor/ips.txt", "r",encoding='utf-8')
text_list = []
s = set()
document = f3.readlines()
document_num = int(len(document))
print('原条数：' + str(document_num))
print('================去重中================')
content = [x.strip() for x in document]
# print(content)

for x in range(0,len(content)):
    url = content[x]
    if url not in s:
        s.add(url)
        text_list.append(url)

filename = int(len(text_list))
print('现条数：' + str(filename))
print('减少了：' + str(document_num-filename ))


with open('./infor/换行_ips.txt', 'a+', encoding='utf-8') as f:
    for i in range(len(text_list)):
        # s = str(i).split()
        s = str(text_list[i])
        s = s + '\n'
        f.write(s)
    print('================(换行)保存文件成功================')
f.close()
with open('./infor/逗号_ips.txt', 'a+', encoding='utf-8') as f2:
    for i in range(len(text_list)):
        if str(text_list[i+1]):
            s = str(text_list[i])
            s = s + ','
            f2.write(s)
    print('================(逗号)保存文件成功================')
f2.close()
