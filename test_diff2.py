import difflib
import diff_match_patch
import re


def process_regex_string(regex_str, n):
    # 使用正则表达式匹配所有 .* 和非 .* 的部分
    parts = re.split(r'(\.\*)', regex_str)

    # 初始化新字符串和一个标志，用于指示是否应该添加下一个 .*
    new_regex = ''
    add_next_wildcard = False

    for i in range(0, len(parts)):
        part = parts[i]

        if i % 2 == 0:  # 偶数索引处是非 .* 的部分
            if len(part) >= n:
                new_regex += part
                add_next_wildcard = True
        else:  # 奇数索引处是 .* 的部分
            if add_next_wildcard:
                new_regex += part
                add_next_wildcard = False

    # 确保字符串的最开始和最末尾正确处理 .*
    if regex_str.startswith('.*') and not new_regex.startswith('.*'):
        new_regex = '.*' + new_regex
    if regex_str.endswith('.*') and not new_regex.endswith('.*'):
        new_regex += '.*'

    return new_regex


def get_regex(a, b):
    diff = difflib.ndiff(a, b)

    res = ''
    pending = False  # 用于标记是否存在待定的不匹配部分

    for s in diff:
        # print(s)
        if s[0] == ' ':  # 公共部分
            if pending:
                res += '.*'  # 添加.*来覆盖不匹配的部分
                pending = False
            res += s[-1]
        elif s[0] in '-+':  # a或b中有不匹配的部分
            pending = True

    if pending:
        res += '.*'  # 处理字符串末尾的不匹配部分

    res = process_regex_string(res, 10)
    return res


def get_regex2(a, b):
    dmp = diff_match_patch.diff_match_patch()
    diffs = dmp.diff_main(a, b)
    dmp.diff_cleanupSemantic(diffs)  # 可选的清理步骤，提高差异的可读性和准确性

    res = ''
    pending = False  # 用于标记是否存在待定的不匹配部分
    for op, data in diffs:
        if op == dmp.DIFF_EQUAL:  # 公共部分
            if pending:
                res += '.*'  # 添加.*来覆盖不匹配的部分
                pending = False
            res += data
        elif op in (dmp.DIFF_INSERT, dmp.DIFF_DELETE):  # 插入或删除的部分
            pending = True

    if pending:
        res += '.*'  # 处理字符串末尾的不匹配部分

    res = process_regex_string(res, 5)
    return res


def test_diff(a, b, regex):
    my_regex = get_regex2(a, b)
    assert my_regex == regex, f"Test Failed\na:\n{a}\n\nb:\n{b}\n\nExpected:\n{regex}\n\nGot:\n{my_regex}\n\n"
    print(f"Test Passed, a:\n{a}\n\nb:\n{b}\n\nGot:\n{regex}\n\n")


if __name__ == '__main__':
    test_diff('''Text:传下去：年纪轻轻的我就拥有贵妇眼霜
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
              '''Text:.*
do not search the web
return json only
No explanation''')
