import re
import test_diff2


_special_chars_map = {i: '\\' + chr(i) for i in b'()[]{}?+-|^$\\&~#\t\n\r\v\f'}


def escape_regex(pattern):
    """
    Escape special characters in a string.
    """
    if isinstance(pattern, str):
        res = pattern.translate(_special_chars_map)
    else:
        pattern = str(pattern, 'latin1')
        res = pattern.translate(_special_chars_map).encode('latin1')

    res = res.replace("..*", ".*")
    res = res.replace(".**", ".*")
    res = res.replace("*", "\\*")
    return res


def get_final_regex(old_regex, new_regex):
    # 检查转义后的正则表达式是否可以匹配对方
    if re.fullmatch(old_regex, new_regex):
        return old_regex
    elif re.fullmatch(new_regex, old_regex):
        return new_regex
    else:
        res = get_regex_from_strings_internal([old_regex, new_regex])
        return res
        # raise ValueError("The regex patterns do not match each other")


def refine_regex(s):
    # 使用正则表达式替换多个反斜杠加上?或*的情况
    s = re.sub(r'\\+([?*])', r'\1', s)
    # 使用正则表达式替换连续的多个*为单个*
    s = re.sub(r'\*+', '*', s)
    s = re.sub(r'(.\*)+', '.*', s)
    s = s.replace("\\\\.*\\-", "-")
    return s


def get_regex_from_strings_internal(arr):
    prev_regex = ""
    for i in range(len(arr) - 1):
        a = arr[i]
        b = arr[i + 1]

        # print(f"[{i}] {a} => [{i + 1}] {b}")
        regex = test_diff2.get_regex2(a, b)
        regex = escape_regex(regex)
        # print(f"regex = {regex}")

        if prev_regex == "":
            prev_regex = regex
        else:
            if prev_regex.startswith("*"):
                prev_regex = "." + prev_regex
            prev_regex = get_final_regex(prev_regex, regex)

        # print(f"prev_regex = {prev_regex}")

    # print(f"\nfinal regex = {prev_regex}\n")

    prev_regex = refine_regex(prev_regex)

    return prev_regex


def get_regex_from_strings(arr):
    res = get_regex_from_strings_internal(arr)
    res = res.replace("\\\\\\", "")
    return res


def test_regex(arr, regex):
    my_regex = get_regex_from_strings(arr)
    assert my_regex == regex, f"Test Failed\nArray:\n{arr}\n\nExpected:\n{regex}\n\nGot:\n{my_regex}\n\n"
    print(f"Test Passed\nArray:\n{arr}\n\nGot:\n{regex}\n\n")


if __name__ == '__main__':
    test_regex([
        'Write an article about hello world',
        'Write an article about the topic: the university life',
        'Write an article about the topic: the overview about U.S. IT companies',
        'Write an article about the topic: introduction about games of PC'
    ],
        "Write an article about .*"
    )

    test_regex([
        'Write an article about hello world',
        'an article about the topic: the university life',
    ],
        ".*an article about .*"
    )

    test_regex([
        'an article about the topic: the university life',
        'Write an article about the topic: the overview about U.S. IT companies',
    ],
        ".*an article about the topic: the .*"
    )

    test_regex([
        'Write an article about hello world',
        'an article about the topic: the university life',
        'Write an article about the topic: the overview about U.S. IT companies',
        'Write an article about the topic: introduction about games of PC'
    ],
        ".*an article about .*"
    )

    test_regex([
        'Pode criar a letra L no estilo infantil?|Pode criar a letra R no estilo infantil?',
        'Pode criar a letra F no estilo infantil?',
        'Pode criar a letra H no estilo infantil?',
        'Bing, cria a letra G no estilo infantil.',
    ],
        ".* cria.* a letra .* no estilo infantil.*"
    )

    test_regex([
        'viết nhận xét cho học sinh từ 4-5 câu bằng tiếng việt từ những nhận xét sau \\I\'v"',
        'viết nhận xét cho học sinh từ 4-5 câu bằng tiếng việt từ những nhận xét sau \\Fol"',
        'viết nhận xét cho học sinh từ 4-5 câu bằng tiếng việt từ những nhận xét sau \\Tha"',
    ],
        "viết nhận xét cho học sinh từ 4-5 câu bằng tiếng việt từ những nhận xét sau \\.*"
    )

    test_regex([
        'sample of slide 11 now based on the sugestion above',
        'sample of slide 15 now based on the sugestion above',
        'sample of slide 3 now based on the sugestion above',
        'sample of slide 13 now based on the sugestion above',
    ],
        "sample of slide .* now based on the sugestion above"
    )

    test_regex([
        '4. (填空题) Complete the sentences with the correct form of the expressions below.n',
        '2. (填空题) Complete the sentences with the correct form of the expressions below.n',
        'Complete the sentences with the correct form of the expressions below.nncomparis',
        '6. (填空题) Complete the sentences with the correct form of the expressions below.n'
    ],
        ".*Complete the sentences with the correct form of the expressions below.n.*"
    )

    test_regex([
        'tolong jelaskan masing-masing fitur APISIX berikut dalam bahasa indonesia:na)tTC',
        'tolong jelaskan masing-masing fitur APISIX berikut dalam bahasa indonesia:na)tPe',
        'tolong jelaskan masing-masing fitur APISIX berikut dalam bahasa indonesia:n- Sup',
        'Tolong jelaskan masing-masing fitur APISIX berikut dalam bahasa indonesia:na)tLu'
    ],
        ".*olong jelaskan masing-masing fitur APISIX berikut dalam bahasa indonesia:n.*"
    )

    test_regex([
        'give answer in points+introdcution+body20 points)+conclusion+way forward.••tWhy',
        'Give answer in points+introduction+body(20 points)+conclusion+way forward format',
        'give answer in points+introdcution+body20 points)+conclusion+way forward•te-NAM',
        'give answer in points+introdcution+body20 points)+conclusion+way forward.•••tPar'
    ],
        ".*ive answer in points+introd.*tion+body.*20 points)+conclusion+way forward.*"
    )

    test_regex([
        'SM = 0.24x148 + 0.15x177 – 0.071x21 – 0.0004x21^2 + 2.7x0 – 14.2',
        'SM = 0.24x160.11 + 0.15x173 – 0.071x29 – 0.0004x29^2 + 2.7x0 – 14.2',
        'SM = 0.24x131 + 0.15x173 – 0.071x29 – 0.0004x29^2 + 2.7x1 – 14.2',
        'SM = 0.24x160.11 + 0.15x173 – 0.071x29 – 0.0004x29^2 + 2.7x1 – 14.2',
        'SM = 0.24x131 + 0.15x173 – 0.071x29 – 0.0004x29^2 + 2.7x0 – 14.2'
    ],
        "SM = 0.24x1.* + 0.15x17.* – 0.071x2.* – 0.0004x2.*^2 + 2.7x.* – 14.2"
    )

    test_regex([
        'Pekerjaan utama dalam implementasi sistem mencakup hal-hal berikut, kecualin Mer',
        'Pekerjaan utama dalam implementasi sistem mencakup hal-hal berikut, kecualin Men',
        'ekerjaan utama dalam implementasi sistem mencakup hal-hal berikut, kecualin Meny',
        'Pekerjaan utama dalam implementasi sistem mencakup hal-hal berikut, kecualina. M',
        'Pekerjaan utama dalam implementasi sistem mencakup hal-hal berikut, kecuali.....',
        'Pekerjaan utama dalam implementasi sistem mencakup hal-hal berikut, kecualinn',
        'Pekerjaan utama dalam implementasi sistem mencakup hal-hal berikut, kecualinA. M',
        'Pekerjaan pokok dalam implementasi sistem meliputi hal-hal berikut ini, kecualin',
        'Pekerjaan utama dalam implementasi sistem mencakup hal-hal berikut, kecualin a.M'
    ],
        ".*ekerjaan .* dalam implementasi sistem me.*-hal berikut.*, kecuali.*"
    )

    test_regex([
        '''Text:传下去：年纪轻轻的我就拥有贵妇眼霜
Task:根据文章内容分析, 分析成分"焕颜肽成分"的功效有"消肿"吗? return {"answer":"yes"} or {"answer":"no"}
do not search the web
return json only
No explanation''',
        '''Text:啊啊啊！发现了个去颈纹巨牛的东西！
Task:根据文章内容分析, 抽取商品 芦荟胶 的 价格, (价格是指文章中明确指出该商品的相关价格描述) output should be json format as following: [{"word":"xx","original_line":"xx"}]if no result, return []
original line must be cut from text and no more than
do not search the web
return json only
No explanation''',
    ],
        '''Text:.*\\
do not search the web\\
return json only\\
No explanation'''
    )
