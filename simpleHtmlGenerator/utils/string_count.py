# https://www.cnblogs.com/shuoliuchina/p/12431156.html
import string

def str_count(str):
    '''找出字符串中的中英文、空格、数字、标点符号个数'''
    count_en = count_dg = count_sp = count_zh = count_pu = 0

    for s in str:
        # 英文
        if s in string.ascii_letters:
            count_en += 1
        # 数字
        elif s.isdigit():
            count_dg += 1
        # 空格
        elif s.isspace():
            count_sp += 1
        # 中文，除了英文之外，剩下的字符认为就是中文
        elif s.isalpha():
            count_zh += 1
        # 特殊字符
        else:
            count_pu += 1

    return count_zh, count_en + count_dg + count_sp + count_pu