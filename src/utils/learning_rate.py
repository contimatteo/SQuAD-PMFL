from typing import Any

from tensorflow.keras.optimizers.schedules import CosineDecay, ExponentialDecay
#  from tensorflow_addons.optimizers import CyclicalLearningRate

import utils.configs as Configs

###


class LearningRate:

    @staticmethod
    def __cosine_decay() -> Any:
        initial_lr = 1e-3
        decay_steps = Configs.NN_EPOCHS
        alpha = 0.05

        return CosineDecay(initial_lr, decay_steps, alpha=alpha)

    @staticmethod
    def __exponential_decay() -> Any:
        initial_lr = 1e-3
        decay_steps = Configs.NN_EPOCHS
        decay_rate = 0.96

        return ExponentialDecay(initial_lr, decay_steps=decay_steps, decay_rate=decay_rate)

    # def __cyclic_decay() -> Any:
    #     LEARNING_RATE_MIN_VALUE = Configs.LEARNING_RATE / 10
    #     step_size = 2 * Configs.BATCH_SIZE
    #     scale_fn = lambda x: 1 / (2.**(x - 1))
    #     return CyclicalLearningRate(
    #         LEARNING_RATE_MIN_VALUE, Configs.LEARNING_RATE, step_size=step_size, scale_fn=scale_fn
    #     )

    #

    @staticmethod
    def build_fn_by_config_name(config_name: str) -> Any:
        if config_name == "static":
            return Configs.NN_LEARNING_RATE

        if config_name == "cosine":
            return LearningRate.__cosine_decay()

        if config_name == "exponential":
            return LearningRate.__exponential_decay()

        raise Exception("[learning_rate]: invalid  `config_name` parameter.")
