from typing import Tuple

import os
import numpy as np

import utils.env_setup

from tensorflow.keras.callbacks import EarlyStopping
from wandb.keras import WandbCallback
from models import DRQA
from data import get_data
from utils import XY_data_from_dataset

###

os.environ["WANDB_JOB_TYPE"] = "training"

###


def __dataset() -> Tuple[Tuple[np.ndarray], np.ndarray, np.ndarray]:
    _, data, glove, _ = get_data(300, debug=True)

    X, Y = XY_data_from_dataset(data)

    return X, Y, glove


def __callbacks():
    return [
        WandbCallback(),
        EarlyStopping(
            monitor='loss',
            patience=3,
            mode='min',
            min_delta=1e-3,
            restore_best_weights=True,
        ),
        # ModelCheckpoint(
        #     filepath=checkpoint_filepath,
        #     save_weights_only=True,
        #     monitor='val_accuracy',
        #     mode='max',
        #     save_best_only=True
        # )
    ]


###


def train():
    X, Y, glove = __dataset()

    model = DRQA(glove)

    model.fit(X, Y, epochs=5, batch_size=16, callbacks=__callbacks())

    model.predict(X)


###

if __name__ == "__main__":
    train()
