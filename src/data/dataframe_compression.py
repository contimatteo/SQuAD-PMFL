from typing import List

import pandas as pd
from features.one_hot_encoder import OneHotEncoder
from features.word_to_index import WordToIndex


class DataframeCompression:

    def __init__(self, OHE_pos: dict = None, OHE_ner: dict = None):
        self.index_df = pd.DataFrame()
        self.passage_index_dict = pd.DataFrame()
        self.question_index_dict = pd.DataFrame()
        self.passage_dict = pd.DataFrame()
        self.question_dict = pd.DataFrame()
        self.label_dict = pd.DataFrame()
        self.exact_match_dict = pd.DataFrame()
        self.pos_cat_dict = pd.DataFrame()
        self.ner_cat_dict = pd.DataFrame()
        self.tf_dict = pd.DataFrame()
        self.id_dict = pd.DataFrame()
        self.mask_passage_dict = pd.DataFrame()
        self.mask_question_dict = pd.DataFrame()

        self.key_all = ["passage_index", "question_index", "chunk_index"]
        self.key_pass = ["passage_index", "chunk_index"]
        self.key_ques = ["question_index", "chunk_index"]
        self.OHE = {"OHE_pos": OHE_pos, "OHE_ner": OHE_ner}
        # self.OHE_pos = [OHE_pos]
        # self.OHE_ner = [OHE_ner]

    def from_pickle(self, d: dict):
        self.index_df = d["index_df"]
        self.passage_index_dict = d["passage_index_dict"]
        self.question_index_dict = d["question_index_dict"]
        self.passage_dict = d["passage_dict"]
        self.question_dict = d["question_dict"]
        self.label_dict = d["label_dict"]
        self.exact_match_dict = d["exact_match_dict"]
        self.pos_cat_dict = d["pos_cat_dict"]
        self.ner_cat_dict = d["ner_cat_dict"]
        self.tf_dict = d["tf_dict"]
        self.id_dict = d["id_dict"]
        self.mask_passage_dict = d["mask_passage_dict"]
        self.mask_question_dict = d["mask_question_dict"]
        self.key_all = d["key_all"]
        self.key_pass = d["key_pass"]
        self.key_ques = d["key_ques"]
        self.OHE = d["OHE"]
        # self.OHE_pos = d["OHE_pos"]
        # self.OHE_ner = d["OHE_ner"]

    def to_pickle(self):
        return {
            "index_df": self.index_df,
            "passage_index_dict": self.passage_index_dict,
            "question_index_dict": self.question_index_dict,
            "passage_dict": self.passage_dict,
            "question_dict": self.question_dict,
            "label_dict": self.label_dict,
            "exact_match_dict": self.exact_match_dict,
            "pos_cat_dict": self.pos_cat_dict,
            "ner_cat_dict": self.ner_cat_dict,
            "tf_dict": self.tf_dict,
            "id_dict": self.id_dict,
            "mask_passage_dict": self.mask_passage_dict,
            "mask_question_dict": self.mask_question_dict,
            "key_all": self.key_all,
            "key_pass": self.key_pass,
            "key_ques": self.key_ques,
            "OHE": self.OHE
            # "OHE_pos": self.OHE_pos,
            # "OHE_ner": self.OHE_ner,
        }

    def compress(self, df):
        self.index_df = df[self.key_all]
        # df_all = df.set_index(self.key_all, drop=False)
        # df_pass = df.set_index(self.key_pass, drop=False)
        # df_ques = df.set_index(self.key_ques, drop=False)

        self.passage_index_dict = df[self.key_pass + ["word_index_passage_padded"]].drop_duplicates(
            subset=self.key_pass
        )
        self.question_index_dict = df[self.key_ques +
                                      ["word_index_question_padded"]].drop_duplicates(
            subset=self.key_ques
        )
        self.passage_dict = df[self.key_pass +
                               ["word_tokens_passage_with_spaces"]].drop_duplicates(subset=self.key_pass)
        self.question_dict = df[self.key_ques +
                                ["word_tokens_question"]].drop_duplicates(subset=self.key_ques)
        if "label_padded" in df:
            self.label_dict = df[self.key_all +
                                 ["label_padded"]].drop_duplicates(subset=self.key_all)
        else:
            self.label_dict = None
        self.exact_match_dict = df[self.key_all +
                                   ["exact_match_padded"]].drop_duplicates(subset=self.key_all)
        self.pos_cat_dict = df[self.key_pass +
                               ["pos_categorical_padded"]].drop_duplicates(subset=self.key_pass)
        self.ner_cat_dict = df[self.key_pass +
                               ["ner_categorical_padded"]].drop_duplicates(subset=self.key_pass)
        self.tf_dict = df[self.key_pass +
                          ["term_frequency_padded"]].drop_duplicates(subset=self.key_pass)
        self.id_dict = df[self.key_ques + ["id"]].drop_duplicates(subset=self.key_ques)
        self.mask_passage_dict = df[self.key_pass + ["mask_passage_padded"]].drop_duplicates(subset=self.key_pass)
        self.mask_question_dict = df[self.key_ques + ["mask_question_padded"]].drop_duplicates(subset=self.key_ques)

        # OHE_pos = OneHotEncoder(self.OHE["OHE_pos"])
        # OHE_pos.reset_cache()
        # OHE_ner = OneHotEncoder(self.OHE["OHE_ner"])
        # OHE_ner.reset_cache()
        self.OHE["OHE_pos"]["cache_categorical_dict"] = {}
        self.OHE["OHE_pos"]["cache_one_hot_dict"] = {}
        self.OHE["OHE_ner"]["cache_categorical_dict"] = {}
        self.OHE["OHE_ner"]["cache_one_hot_dict"] = {}

    def extract(self, WTI: WordToIndex):
        df = self.index_df
        print("Rebuilding ID")
        df = pd.merge(df, self.id_dict, on=self.key_ques, how="inner")
        print("Rebuilding Columns WTI passage")
        df = pd.merge(df, self.passage_index_dict, on=self.key_pass, how="inner")
        print("Rebuilding Columns WTI question")
        df = pd.merge(df, self.question_index_dict, on=self.key_ques, how="inner")
        print("Rebuilding Columns passage list")
        df = pd.merge(df, self.passage_dict, on=self.key_pass, how="inner")
        print("Rebuilding Columns question list")
        df = pd.merge(df, self.question_dict, on=self.key_ques, how="inner")
        if self.label_dict is not None:
            print("Rebuilding Labels")
            df = pd.merge(df, self.label_dict, on=self.key_all, how="inner")
        print("Rebuilding Exact Match")
        df = pd.merge(df, self.exact_match_dict, on=self.key_all, how="inner")
        print("Rebuilding POS")
        df = pd.merge(df, self.pos_cat_dict, on=self.key_pass, how="inner")
        print("Rebuilding NER")
        df = pd.merge(df, self.ner_cat_dict, on=self.key_pass, how="inner")
        print("Rebuilding TF")
        df = pd.merge(df, self.tf_dict, on=self.key_pass, how="inner")
        print("Rebuilding MASK PASSAGE")
        df = pd.merge(df, self.mask_passage_dict, on=self.key_pass, how="inner")
        print("Rebuilding MASK QUESTION")
        df = pd.merge(df, self.mask_question_dict, on=self.key_ques, how="inner")
        df = df.sort_values(by=self.key_all)
        print("Rebuilding ONEHOT")
        df = self.add_pos_ner_onehot(df)
        df.set_index(self.key_all, inplace=True, drop=False)
        # df.drop(self.key_pass, inplace=True, axis=1)
        print("Finished Building")
        # print(pd.DataFrame.from_dict(self.passage_dict, columns=["passage_index", "question_index", "chunk_index"]))
        return df

    # def extract(self, WTI: WordToIndex):
    #     df = self.index_df
    #     print("Rebuilding Columns WTI passage")
    #     df = self.add_column(df, self.key_pass, "word_index_passage_padded", self.passage_dict)
    #     print("Rebuilding Columns WTI question")
    #     df = self.add_column(df, self.key_ques, "word_index_question_padded", self.question_dict)
    #     print("Rebuilding Labels")
    #     df = self.add_column(df, self.key_all, "label_padded", self.label_dict)
    #     print("Rebuilding Exact Match")
    #     df = self.add_column(df, self.key_all, "exact_match_padded", self.exact_match_dict)
    #     print("Rebuilding POS")
    #     df = self.add_column(df, self.key_pass, "pos_categorical_padded", self.pos_cat_dict)
    #     print("Rebuilding NER")
    #     df = self.add_column(df, self.key_pass, "ner_categorical_padded", self.ner_cat_dict)
    #     print("Rebuilding TF")
    #     df = self.add_column(df, self.key_pass, "term_frequency_padded", self.tf_dict)
    #     print("Rebuilding ONEHOT")
    #     df = self.add_pos_ner_onehot(df)
    #     df.set_index(self.key_all, inplace=True, drop=False)
    #     df.drop(self.key_pass, inplace=True, axis=1)
    #     print("Finished Building")
    #     # print(pd.DataFrame.from_dict(self.passage_dict, columns=["passage_index", "question_index", "chunk_index"]))
    #     return df

    @staticmethod
    def add_column(df: pd.DataFrame, key_columns: List[str], new_col_name: str, dictionary):
        # df[new_col_name] = df.apply(lambda x: dictionary[tuple(x[key_columns])], axis=1)
        df[new_col_name] = df.apply(lambda x: x["passage_index"], axis=1)
        return df

    def add_pos_ner_onehot(self, df):
        df["pos_onehot_padded"] = df.apply(
            lambda x: OneHotEncoder(self.OHE["OHE_pos"]).transform_one_hot(x["pos_categorical_padded"], x["passage_index"], x["chunk_index"]),
            axis=1
        )
        df["ner_onehot_padded"] = df.apply(
            lambda x: OneHotEncoder(self.OHE["OHE_ner"]).transform_one_hot(x["ner_categorical_padded"], x["passage_index"], x["chunk_index"]),
            axis=1
        )
        return df
