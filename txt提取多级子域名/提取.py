# python3
# coding:utf-8
# by 此意系

f0 = open('./urls.txt', encoding='utf-8')
while True:
    current_url = f0.readline()
    if current_url:
        current_url_list = current_url.split(".")
        # print(len(current_url_list))
        if len(current_url_list) >= 4:
            with open('./Second_subdomain.txt', mode='a+', encoding='utf-8') as f1:
                f1.write(current_url)
        else:
            pass
    else:
        print("[+]整理完成！")
        break