import utils.warnings

import numpy as np

import utils.configs as Configs
from models import DrQA

###

N_EXAMPLES = 500


def X_train() -> np.ndarray:
    Xq = np.random.random_sample((N_EXAMPLES, Configs.N_QUESTION_TOKENS))
    Xp = np.random.random_sample((N_EXAMPLES, Configs.N_PASSAGE_TOKENS))

    return [Xq, Xp]


def Y_train() -> np.ndarray:
    return np.random.random_sample((N_EXAMPLES, ))


def train():
    X = X_train()
    Y = Y_train()

    model = DrQA()
    model.fit(X, Y, epochs=10)


###

if __name__ == "__main__":
    train()
