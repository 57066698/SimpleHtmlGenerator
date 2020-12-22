import string
import numpy as np
from simpleHtmlGenerator.utils.alphabets import alphabet

def is_regular(uchar):
    is_chinese = uchar >= u'\u4e00' and uchar <= u'\u9fa5'
    is_number = uchar >= u'\u0030' and uchar <= u'\u0039'
    is_english = (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a')
    return is_english or is_chinese or is_number

alphabet_arr = np.array(list(alphabet))
alphabet_arr_regular = np.fromiter((x for x in alphabet_arr if is_regular(x)), dtype=alphabet_arr.dtype)

def random_text(num):
    text = np.random.choice(alphabet_arr_regular, num)
    text = "".join(text)
    return text

def str_count(str):

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

def get_text_width(text, font_size):
    num_ch, num_other = str_count(text)
    num = 1 * num_ch + 0.5 * num_other
    width = int(font_size * num)
    return width