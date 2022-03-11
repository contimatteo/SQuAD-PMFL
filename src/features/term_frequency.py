from typing import List

import pandas as pd

###

ter_freq_dict = {}

###


def delete_cache_tf():
    global ter_freq_dict
    ter_freq_dict = None


def get_term_freq_normalized(token_list: List[str], passage_index: int):
    if passage_index not in ter_freq_dict.keys():
        word_count_dict = {}
        total_sum = len(token_list)
        for token in token_list:
            if token not in word_count_dict.keys():
                word_count_dict[token] = 1
            else:
                word_count_dict[token] += 1
        tf = []
        for token in token_list:
            tf.append(float('%.5f' % (word_count_dict[token] / total_sum)))
        ter_freq_dict[passage_index] = tf

    return ter_freq_dict[passage_index]


def apply_term_frequency(df: pd.DataFrame):
    df["term_frequency"] = df.apply(
        lambda x: get_term_freq_normalized(x["word_tokens_passage"], x["passage_index"]), axis=1
    )
    return df
