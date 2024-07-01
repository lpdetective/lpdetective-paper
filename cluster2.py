import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
import numpy as np
import Levenshtein
from chatfinger import util
import test_diff

path = util.get_bingchat_path("f1fdc06c-0c4b-44ac-8afc-a0893dc89515-c000_clientIp_top500_filtered.csv")
output_file_path = path.replace('.csv', '_regex_output.csv')


def get_normal_distance(s1, s2):
    distance = Levenshtein.distance(s1, s2)
    total = max(len(s1), len(s2))
    ratio = float(distance) / float(total)
    return ratio


# Define a function to calculate Levenshtein distance matrix
def levenshtein_distance_matrix(strings):
    return [[get_normal_distance(s1, s2) for s2 in strings] for s1 in strings]


if __name__ == '__main__':
    # Step 1: Read Excel file
    # 读取额外的列
    df = pd.read_csv(path, sep='\t')
    df.columns = ['EventTime', 'SignInUser', 'ClientIP', 'ASN', 'SocketIp', 'UserId', 'UserIdType', 'MsgText']

    # Step 2: Group MsgText entries by ClientIP
    grouped = df.groupby('ClientIP')['MsgText'].apply(lambda x: list(map(str, x)))

    # 创建DataFrame来存储输出数据，包括额外的列
    output_data = pd.DataFrame(columns=['ClusterId', 'ClientIP', 'ASN', 'SocketIp', 'Count', 'Distance', 'RegexLength', 'Regex', 'MsgTexts'])

    # 打开文件以进行写入
    with open(output_file_path, 'w', encoding='utf-8-sig', newline='') as file:  # 指定编码为 utf-8
        # 写入标题行
        file.write(','.join(
            ['ClusterId', 'ClientIP', 'ASN', 'SocketIp', 'Count', 'Distance', 'RegexLength', 'Regex', 'MsgTexts']) + '\n')

        # 继续原有的for循环
        # Step 3: Perform clustering analysis using Hierarchical clustering
        for ClientIP, MsgTexts in grouped.items():
            # if ClientIP <= "2.59.61.40":
            #     continue

            # Ensure all elements in MsgTexts are strings
            MsgTexts = list(map(str, MsgTexts))

            # Remove duplicate elements from MsgTexts
            MsgTexts = list(set(MsgTexts))  # This line removes duplicates

            if len(MsgTexts) < 2:  # If there's only one MsgText for the ClientIP, it's its own cluster
                continue

            # Calculate the distance matrix
            distance_matrix = levenshtein_distance_matrix(MsgTexts)

            # Convert the distance matrix to a condensed distance matrix suitable for scipy
            condensed_dist_matrix = squareform(distance_matrix)

            # Perform the hierarchical clustering
            linked = linkage(condensed_dist_matrix, 'complete')

            # The following threshold is set to an arbitrary value; it could be adjusted based on the desired granularity
            threshold = 0.5 * max(condensed_dist_matrix)
            labels = fcluster(linked, threshold, criterion='distance')

            # Step 4: Output clustering results with clusters that have 2 or more MsgTexts
            is_printed = False
            clusters = {i: [] for i in np.unique(labels)}
            for MsgText, label in zip(MsgTexts, labels):
                clusters[label].append(MsgText)

            # 提取额外列的数据
            extra_data = df[df['ClientIP'] == ClientIP][['ClientIP', 'ASN', 'SocketIp']].iloc[0]

            # Only print clusters with 2 or more elements
            for cluster_id, MsgTexts in clusters.items():
                if len(MsgTexts) < 2:
                    continue

                # Calculate the average distance of consecutive elements in the cluster
                distances = [get_normal_distance(MsgTexts[i], MsgTexts[i + 1]) for i in range(len(MsgTexts) - 1)]
                average_distance = sum(distances) / len(distances) if distances else 0
                if average_distance > 0.1 or len(MsgTexts) <= 3:
                    continue

                regex = test_diff.get_regex_from_strings(MsgTexts)
                if regex == "" or regex == ".*":
                    continue
                if len(regex) < 40:
                    continue

                if not is_printed:
                    is_printed = True
                    print(f"ClientIP: {ClientIP} Clustering Results:")

                print(f"Cluster {cluster_id}: count = {len(MsgTexts)}, average distance = {average_distance}, regex length = {len(regex)}, regex = {regex}, MsgTexts = {MsgTexts}")
                # 创建新行的数据
                new_row = {
                    'ClusterId': cluster_id,
                    'ClientIP': ClientIP,
                    'ASN': extra_data['ASN'],
                    'SocketIp': extra_data['SocketIp'],
                    'Count': len(MsgTexts),
                    'Distance': average_distance,
                    'RegexLength': len(regex),
                    'Regex': regex,
                    'MsgTexts': '|'.join(MsgTexts)
                }

                # 转义并写入每个值
                escaped_row = [f'"{value}"' if isinstance(value, str) else str(value) for value in new_row.values()]
                file.write(','.join(escaped_row) + '\n')
                file.flush()  # 强制刷新文件缓冲区

print("Clustering analysis complete and data saved to", output_file_path)
