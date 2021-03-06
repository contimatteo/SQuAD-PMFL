from typing import Tuple, List
from random import randint

import numpy as np

from numpy import ndarray

import utils.configs as Configs

from .pandas import PandasUtils

###

N_ROWS = 500

###


class FeaturesFakerUtils:

    @staticmethod
    def X_train_faker() -> List[np.ndarray]:
        ### [Q] tokens
        q_tokens = np.random.random_sample((N_ROWS, Configs.N_QUESTION_TOKENS))
        ### [P] tokens
        p_tokens = np.random.random_sample((N_ROWS, Configs.N_PASSAGE_TOKENS))
        ### [P] exact match
        p_match = np.zeros((N_ROWS, Configs.N_PASSAGE_TOKENS, Configs.DIM_EXACT_MATCH)
                           ).astype(np.float)
        ### [P] POS tags
        p_pos = np.zeros((N_ROWS, Configs.N_PASSAGE_TOKENS, Configs.N_POS_CLASSES)).astype(np.float)
        ### [P] NER annotations
        p_ner = np.random.random_sample((N_ROWS, Configs.N_PASSAGE_TOKENS, Configs.N_NER_CLASSES))
        ### [P] TF
        p_tf = np.zeros((N_ROWS, Configs.N_PASSAGE_TOKENS, Configs.DIM_TOKEN_TF)).astype(np.float)

        return [q_tokens, p_tokens, p_match, p_pos, p_ner, p_tf]

    @staticmethod
    def Y_train_faker() -> np.ndarray:
        shape = (N_ROWS, Configs.N_PASSAGE_TOKENS, 2)

        def _generator(n, k):
            """n numbers with sum k"""
            if n == 1:
                return [k]
            num = 0 if k == 0 else randint(1, k)
            return [num] + _generator(n - 1, k - num)

        def _Y_start_end():
            Y_start = np.zeros((Configs.N_PASSAGE_TOKENS, ))
            Y_end = np.zeros((Configs.N_PASSAGE_TOKENS, ))
            Y_start_index = randint(0, Configs.N_PASSAGE_TOKENS - 2)
            Y_end_index = randint(Y_start_index + 1, Configs.N_PASSAGE_TOKENS - 1)
            Y_start[Y_start_index] = 1
            Y_end[Y_end_index] = 1

            return Y_start, Y_end

        Y = np.zeros(shape)
        for i in range(1):
            Y_start, Y_end = _Y_start_end()
            Y_true = np.array([Y_start, Y_end]).T
            Y[i] = Y_true

        return Y.astype(np.float)


###


class FeaturesUtils:

    @staticmethod
    def __X_feature_examples_subset(feature, n_examples):
        return feature[0:n_examples]

    @staticmethod
    def __X_feature_tokens_subset(feature, n_tokens):
        return feature[:, 0:n_tokens]

    @staticmethod
    def __prepare_Y_true_onehot_encoding(Y: np.ndarray) -> np.ndarray:
        ### --> (n_examples, n_tokens, 2)
        Y_transposed = np.transpose(Y, axes=[0, 2, 1])
        ### --> (n_examples, 2, n_tokens)

        ### existing at least one probability not equal to zero?
        Y_onehot_label_missing = np.any(Y_transposed, axis=2)  ### --> (n_examples, 2)
        ### invert each boolean value: now we have `1` where we have all zero probabilities.
        Y_onehot_label_missing = np.invert(Y_onehot_label_missing)  ### --> (n_examples, 2)
        ### cast `bool` values to `int`
        Y_onehot_label_missing = Y_onehot_label_missing.astype(int)  ### --> (n_examples, 2)

        ### (n_examples, n_tokens, 2) and (n_examples, 2) --> (n_tokens+1, n_examples, 2)
        Y_onehot_with_additional_case = np.concatenate(
            (np.transpose(Y, axes=[1, 0, 2]), np.expand_dims(Y_onehot_label_missing, axis=0))
        )
        Y_onehot_with_additional_case = np.transpose(Y_onehot_with_additional_case, axes=[1, 0, 2])

        return Y_onehot_with_additional_case

    #

    @staticmethod
    def X_from_raw_features(X_data, n_examples_subset=None) -> Tuple[List[ndarray], ndarray]:
        assert X_data is not None
        assert isinstance(X_data, list)
        assert len(X_data) == 9
        assert X_data[0] is not None
        assert X_data[1] is not None
        assert X_data[2] is not None
        assert X_data[3] is not None
        assert X_data[4] is not None
        assert X_data[5] is not None
        assert X_data[6] is not None
        assert X_data[7] is not None
        assert X_data[8] is not None

        #

        q_indexes = PandasUtils.series_to_numpy(X_data[0])

        p_tokens = PandasUtils.series_to_numpy(X_data[1], np.float32)
        X_data[1] = None
        q_tokens = PandasUtils.series_to_numpy(X_data[2], np.float32)
        X_data[2] = None
        p_pos = PandasUtils.series_to_numpy(X_data[3], np.float16)
        X_data[3] = None
        p_ner = PandasUtils.series_to_numpy(X_data[4], np.float16)
        X_data[4] = None
        p_tf = PandasUtils.series_to_numpy(X_data[5], np.float16)
        X_data[5] = None
        p_match = PandasUtils.series_to_numpy(X_data[6], np.float16)
        X_data[6] = None
        p_mask = PandasUtils.series_to_numpy(X_data[7], np.float16)
        X_data[7] = None
        q_mask = PandasUtils.series_to_numpy(X_data[8], np.float16)
        X_data[8] = None

        #

        assert p_tokens.shape[1] <= Configs.N_PASSAGE_TOKENS
        assert q_tokens.shape[1] <= Configs.N_QUESTION_TOKENS
        assert p_pos.shape[1] <= Configs.N_PASSAGE_TOKENS
        assert p_ner.shape[1] <= Configs.N_PASSAGE_TOKENS
        assert p_tf.shape[1] <= Configs.N_PASSAGE_TOKENS
        assert p_match.shape[1] <= Configs.N_PASSAGE_TOKENS
        assert p_mask.shape[1] <= Configs.N_PASSAGE_TOKENS
        assert q_mask.shape[1] <= Configs.N_QUESTION_TOKENS

        if n_examples_subset is not None and isinstance(n_examples_subset, int):
            q_indexes = FeaturesUtils.__X_feature_examples_subset(q_indexes, n_examples_subset)
            p_tokens = FeaturesUtils.__X_feature_examples_subset(p_tokens, n_examples_subset)
            q_tokens = FeaturesUtils.__X_feature_examples_subset(q_tokens, n_examples_subset)
            p_pos = FeaturesUtils.__X_feature_examples_subset(p_pos, n_examples_subset)
            p_ner = FeaturesUtils.__X_feature_examples_subset(p_ner, n_examples_subset)
            p_tf = FeaturesUtils.__X_feature_examples_subset(p_tf, n_examples_subset)
            p_match = FeaturesUtils.__X_feature_examples_subset(p_match, n_examples_subset)
            p_mask = FeaturesUtils.__X_feature_examples_subset(p_mask, n_examples_subset)
            q_mask = FeaturesUtils.__X_feature_examples_subset(q_mask, n_examples_subset)

        p_tokens = FeaturesUtils.__X_feature_tokens_subset(p_tokens, Configs.N_PASSAGE_TOKENS)
        q_tokens = FeaturesUtils.__X_feature_tokens_subset(q_tokens, Configs.N_QUESTION_TOKENS)
        p_pos = FeaturesUtils.__X_feature_tokens_subset(p_pos, Configs.N_PASSAGE_TOKENS)
        p_ner = FeaturesUtils.__X_feature_tokens_subset(p_ner, Configs.N_PASSAGE_TOKENS)
        p_tf = FeaturesUtils.__X_feature_tokens_subset(p_tf, Configs.N_PASSAGE_TOKENS)
        p_match = FeaturesUtils.__X_feature_tokens_subset(p_match, Configs.N_PASSAGE_TOKENS)
        p_mask = FeaturesUtils.__X_feature_tokens_subset(p_mask, Configs.N_PASSAGE_TOKENS)
        q_mask = FeaturesUtils.__X_feature_tokens_subset(q_mask, Configs.N_QUESTION_TOKENS)

        #

        assert isinstance(p_tokens, np.ndarray)
        assert len(p_tokens.shape) == 2
        assert p_tokens.shape[1] == Configs.N_PASSAGE_TOKENS

        assert isinstance(q_tokens, np.ndarray)
        assert len(q_tokens.shape) == 2
        assert q_tokens.shape[1] == Configs.N_QUESTION_TOKENS

        assert isinstance(p_pos, np.ndarray)
        assert len(p_pos.shape) == 3
        assert p_pos.shape[1] == Configs.N_PASSAGE_TOKENS
        assert p_pos.shape[2] == Configs.N_POS_CLASSES

        assert isinstance(p_ner, np.ndarray)
        assert len(p_ner.shape) == 3
        assert p_ner.shape[1] == Configs.N_PASSAGE_TOKENS
        assert p_ner.shape[2] == Configs.N_NER_CLASSES

        assert isinstance(p_tf, np.ndarray)
        assert len(p_tf.shape) == 2
        assert p_tf.shape[1] == Configs.N_PASSAGE_TOKENS

        assert isinstance(p_match, np.ndarray)
        assert len(p_match.shape) == 3
        assert p_match.shape[1] == Configs.N_PASSAGE_TOKENS
        assert p_match.shape[2] == Configs.DIM_EXACT_MATCH

        assert isinstance(q_indexes, np.ndarray)
        assert len(q_indexes.shape) == 1
        assert q_indexes.shape[0] == q_tokens.shape[0]

        assert isinstance(p_mask, np.ndarray)
        assert len(p_mask.shape) == 2
        assert p_mask.shape[1] == Configs.N_PASSAGE_TOKENS

        assert isinstance(q_mask, np.ndarray)
        assert len(q_mask.shape) == 2
        assert q_mask.shape[1] == Configs.N_QUESTION_TOKENS

        #

        X = [q_tokens, q_mask, p_mask, p_tokens, p_match, p_pos, p_ner, p_tf]

        return X, q_indexes

    @staticmethod
    def Y_from_raw_labels(Y_data, n_examples_subset=None) -> np.ndarray:
        assert Y_data is not None
        assert isinstance(Y_data, list)
        assert len(Y_data) == 1
        assert Y_data[0] is not None

        #

        labels = PandasUtils.series_to_numpy(Y_data[0], np.float16)
        Y_data[0] = None

        #

        assert labels.shape[1] <= Configs.N_PASSAGE_TOKENS

        if n_examples_subset is not None and isinstance(n_examples_subset, int):
            labels = FeaturesUtils.__X_feature_examples_subset(labels, n_examples_subset)

        labels = FeaturesUtils.__X_feature_tokens_subset(labels, Configs.N_PASSAGE_TOKENS)

        #

        assert isinstance(labels, np.ndarray)
        assert len(labels.shape) == 3
        assert labels.shape[1] == Configs.N_PASSAGE_TOKENS
        assert labels.shape[2] == 2

        #

        Y = FeaturesUtils.__prepare_Y_true_onehot_encoding(labels)

        return Y

    @staticmethod
    def QP_data_from_dataset(data) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        assert data is not None
        assert isinstance(data, list)
        assert len(data) == 4

        assert data[0] is not None
        assert data[1] is not None
        assert data[2] is not None
        assert data[3] is not None

        #

        question_indexes = PandasUtils.series_to_numpy(data[0], str)
        data[0] = None
        passages = PandasUtils.series_to_numpy(data[1])
        data[1] = None
        questions = PandasUtils.series_to_numpy(data[2])
        data[2] = None
        passage_indexes = PandasUtils.series_to_numpy(data[3])
        data[3] = None

        #

        assert isinstance(question_indexes, np.ndarray)
        assert len(question_indexes.shape) == 1

        assert isinstance(passages, np.ndarray)
        # assert len(passages.shape) == 1

        assert isinstance(questions, np.ndarray)
        # assert len(questions.shape) == 1

        assert isinstance(passage_indexes, np.ndarray)
        # assert len(passage_indexes.shape) == 1

        assert question_indexes.shape[0] == questions.shape[0]
        assert question_indexes.shape[0] == passages.shape[0]
        assert question_indexes.shape[0] == passage_indexes.shape[0]

        #

        return question_indexes, questions, passages, passage_indexes
