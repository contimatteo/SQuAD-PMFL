# pylint: disable=unused-import
from typing import Any, Tuple, List, Dict

import os
import numpy as np
import json

import utils.env_setup
import utils.configs as Configs

from data import get_data
from models import DRQA
from models.core import drqa_accuracy_start, drqa_accuracy_end, drqa_accuracy
from utils import XY_data_from_dataset, LocalStorageManager, passagges_data_from_dataset

###

os.environ["WANDB_JOB_TYPE"] = "training"

LocalStorage = LocalStorageManager()

###


def __dataset() -> Tuple[Tuple[np.ndarray], np.ndarray, np.ndarray]:
    _, dataset, glove_matrix, _ = get_data(300)

    x, y, question_indexes = XY_data_from_dataset(
        dataset, Configs.NN_BATCH_SIZE * Configs.N_KFOLD_BUCKETS
    )

    passages = passagges_data_from_dataset(dataset)

    return x, y, glove_matrix, question_indexes, passages


def __predict(model, X):
    nn_checkpoint_directory = LocalStorage.nn_checkpoint_url(model.name)
    assert nn_checkpoint_directory.is_file()

    ### load weights
    model.load_weights(str(nn_checkpoint_directory))

    Y_pred = model.predict(X)

    return Y_pred


def __compute_answers_tokens_indexes(Y, question_indexes: np.ndarray):
    answers_tokens_probs_map = {}

    for question_index in np.unique(question_indexes):
        subset_indexes = np.array(question_indexes == question_index)

        current_answers = Y[subset_indexes]
        answers_tokens_probs_map[question_index] = current_answers

    assert len(answers_tokens_probs_map.keys()) == np.unique(question_indexes).shape[0]

    #

    def __weigth_answer_probs(answer: np.ndarray):
        answer_tokens_probs = answer[0:-1]  ### --> (n_tokens, 2)
        answer_no_token_prob = answer[-1]  ### --> (2,)
        return answer_tokens_probs - answer_no_token_prob

    answers_tokens_indexes_map: Dict[str, np.ndarray] = {}

    for (q_index, answers) in answers_tokens_probs_map.items():
        answer_tokens_probs = np.array(
            [__weigth_answer_probs(answers[idx]) for idx in range(answers.shape[0])],
            dtype=answers.dtype
        )

        start_index = np.argmax(answer_tokens_probs[:, :, 0].flatten())
        end_index = np.argmax(answer_tokens_probs[:, :, 1].flatten())

        answers_tokens_indexes_map[q_index] = np.array([start_index, end_index], dtype=np.int16)

    #

    return answers_tokens_indexes_map


###
def __build_prediction_file(answers_tokens_indexes_map: Any):

    qids = np.array([])  # obtained by loading the pkl with question_iondex, passage as ndarray
    passages = np.array([])  # obtained by loading the pkl with question_iondex, passage as ndarray

    output_dict = {}

    for i in range(len(qids.shape[0])):
        qid = qids[i]
        passage = passages[i]

        answer_range = answers_tokens_indexes_map[qid]
        answer_start = answer_range[0]
        answer_end = answer_range[1]

        answer = " ".join(passage[answer_start:answer_end + 1])

        output_dict[qid] = answer

    with open("data/processed/predictions.json", "w", encoding='utf-8') as file:
        json.dump(output_dict, file)


###


def test():
    X, Y, glove, question_indexes, passages = __dataset()

    model = DRQA(glove)

    Y_pred = __predict(model, X)

    _ = __compute_answers_tokens_indexes(Y_pred, question_indexes)


###

if __name__ == "__main__":
    test()
