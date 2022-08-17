# python3
# coding:utf-8
# by 此意系

def file_qc():
    str1 = []
    file_1 = open("1.txt","r",encoding="utf-8")
    for line in file_1.readlines():
        str1.append(line.replace("\n",""))

    str2 = []
    file_2 = open("2.txt", "r", encoding="utf-8")
    for line in file_2.readlines():
        str2.append(line.replace("\n", ""))

    str_dump = []
    for line in str1:
        if line in str2:
            str_dump.append(line)    #将两个文件重复的内容取出来

    str_all = set(str1 + str2)      #将两个文件放到集合里，过滤掉重复内容

    for i in str_dump:
        if i in str_all:
            str_all.remove(i)		#去掉重复的文件

    for str in str_all:             #去重后的结果写入文件
        # print(str)
        with open("result.txt","a+",encoding="utf-8") as f:
            f.write(str + "\n")

if __name__=="__main__":
    file_qc()
