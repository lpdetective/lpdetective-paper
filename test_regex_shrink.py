import re


def shrink_regex(a, b, generated_regex):
    # 将正则表达式拆分为部分，以便于处理包含 .* 的部分
    parts = re.split(r'(\.\*)', generated_regex)
    new_regex = ''

    # 跟踪当前字符串在 a 和 b 中的位置
    index_a = index_b = 0
    for part in parts:
        if part == '.*':
            # 确定 .* 对应在 a 和 b 中的最长匹配区间
            remaining_a = a[index_a:]
            remaining_b = b[index_b:]
            if not remaining_a or not remaining_b:
                new_regex += part
                continue

            # 找到 .* 在 a 和 b 中对应的最大公共前缀
            common_prefix = ''
            for i, (char_a, char_b) in enumerate(zip(remaining_a, remaining_b)):
                if char_a == char_b:
                    common_prefix += char_a
                else:
                    break

            # 将 .* 之前的部分和公共前缀添加到新正则表达式中
            new_regex = new_regex.rstrip(' .*')  # 移除前面多余的 .* 以准确连接
            new_regex += common_prefix + part

            # 更新 index_a 和 index_b
            index_a += len(common_prefix)
            index_b += len(common_prefix)
        else:
            # 添加非 .* 部分到正则表达式中，并更新 index_a 和 index_b
            new_regex += part
            index_a += len(part)
            index_b += len(part)

    # 最后清理正则表达式尾部可能多余的 .* 符号
    new_regex = new_regex.rstrip(' .*') + ('.*' if generated_regex.endswith('.*') else '')

    return new_regex


def test_Shrink(a, b, regex, expected):
    my_regex = shrink_regex(a, b, regex)
    assert my_regex == expected, f"Test Failed\na:\n{a}\n\nb:\n{b}\n\nExpected:\n{expected}\n\nGot:\n{my_regex}\n\n"
    print(f"Test Passed, a:\n{a}\n\nb:\n{b}\n\nGot:\n{my_regex}\n\n")


if __name__ == '__main__':
    test_Shrink('''Text:传下去：年纪轻轻的我就拥有贵妇眼霜
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
                '''Task:根据文章内容分析, .*
No explanation''',
                '''Task:根据文章内容分析, .*
do not search the web
return json only
No explanation''')
