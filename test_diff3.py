import test_diff2

if __name__ == '__main__':
    res = test_diff2.process_regex_string('.*an article about the topic: the .*ver.*s.*', 10)
    print(res)
    # should be '.*an article about the topic: the .*'
