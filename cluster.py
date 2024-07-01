import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
import numpy as np
import Levenshtein
from chatfinger import util
import test_diff


path = util.get_bingchat_path("10.22GroundTruthLabelling.xlsx")


def get_normal_distance(s1, s2):
    distance = Levenshtein.distance(s1, s2)
    total = max(len(s1), len(s2))
    ratio = float(distance) / float(total)
    return ratio


# Define a function to calculate Levenshtein distance matrix
def levenshtein_distance_matrix(strings):
    return [[get_normal_distance(s1, s2) for s2 in strings] for s1 in strings]


# Define a function to print grouped objects
def print_grouped(grouped):
    print("Grouped Text Entries by Anid:")
    for anid, texts in grouped.items():
        print(f"Anid: {anid}")
        for i, text in enumerate(texts, start=1):
            print(f"\tText {i}: {text}")
        print("")  # Add an empty line for better separation


if __name__ == '__main__':
    # Step 1: Read Excel file
    # 读取额外的列
    df = pd.read_excel(path, usecols=['Anid', 'Text', 'is_bot', 'probability', 'explanation'])

    # Step 2: Group Text entries by Anid
    grouped = df.groupby('Anid')['Text'].apply(lambda x: list(map(str, x)))

    # 创建DataFrame来存储输出数据，包括额外的列
    output_data = pd.DataFrame(columns=['Anid', 'ClusterId', 'is_bot', 'probability', 'explanation', 'Count', 'Distance', 'RegexLength', 'Regex', 'Texts'])

    # Step 3: Perform clustering analysis using Hierarchical clustering
    for anid, texts in grouped.items():
        # Ensure all elements in texts are strings
        texts = list(map(str, texts))

        # Remove duplicate elements from texts
        texts = list(set(texts))  # This line removes duplicates

        if len(texts) < 2:  # If there's only one text for the Anid, it's its own cluster
            continue

        # Calculate the distance matrix
        distance_matrix = levenshtein_distance_matrix(texts)

        # Convert the distance matrix to a condensed distance matrix suitable for scipy
        condensed_dist_matrix = squareform(distance_matrix)

        # Perform the hierarchical clustering
        linked = linkage(condensed_dist_matrix, 'complete')

        # The following threshold is set to an arbitrary value; it could be adjusted based on the desired granularity
        threshold = 0.5 * max(condensed_dist_matrix)
        labels = fcluster(linked, threshold, criterion='distance')

        # Step 4: Output clustering results with clusters that have 2 or more texts
        print(f"Anid: {anid} Clustering Results:")
        clusters = {i: [] for i in np.unique(labels)}
        for text, label in zip(texts, labels):
            clusters[label].append(text)

        # 提取额外列的数据
        extra_data = df[df['Anid'] == anid][['is_bot', 'probability', 'explanation']].iloc[0]

        # Only print clusters with 2 or more elements
        for cluster_id, texts in clusters.items():
            if len(texts) < 2:
                continue

            # Calculate the average distance of consecutive elements in the cluster
            distances = [get_normal_distance(texts[i], texts[i + 1]) for i in range(len(texts) - 1)]
            average_distance = sum(distances) / len(distances) if distances else 0
            if average_distance > 0.1 or len(texts) <= 3:
                continue

            regex = test_diff.get_regex_from_strings(texts)
            if regex == ".*":
                continue

            print(f"Cluster {cluster_id}: count = {len(texts)}, average distance = {average_distance}, regex length = {len(regex)}, regex = {regex}, texts = {texts}")
            new_row = {'Anid': anid, 'ClusterId': cluster_id,
                       'is_bot': extra_data['is_bot'],
                       'probability': extra_data['probability'],
                       'explanation': extra_data['explanation'],
                       'Count': len(texts),
                       'Distance': average_distance, 'RegexLength': len(regex),
                       'Regex': regex, 'Texts': texts}
            output_data = output_data._append(new_row, ignore_index=True)

        print("\n")  # Add an empty line for better separation

    # 对数据进行排序
    output_data.sort_values(by=['Count', 'RegexLength'], ascending=[False, False], inplace=True)

    # 输出到Excel文件
    output_file_name = util.get_bingchat_path("10.22GroundTruthLabelling_output.xlsx")
    output_data.to_excel(output_file_name, index=False)

    print("Clustering analysis complete and data saved to", output_file_name)
