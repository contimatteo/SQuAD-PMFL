from typing import Callable, Any

import numpy as np
import tensorflow as tf

from tensorflow import expand_dims
from tensorflow.keras.initializers import Constant
from tensorflow.keras.layers import Dense, Embedding
from tensorflow.keras.layers import Bidirectional, RNN, LSTMCell, Conv1D

import utils.configs as Configs

###

###


class DrQaLayers:

    @staticmethod
    def __weighted_sum(channels_size, kernel_size):
        return Conv1D(channels_size, kernel_size)

    #

    @staticmethod
    def GloveEmbedding(input_length: int, initializer: np.ndarray) -> Callable[[Any], Any]:
        assert isinstance(input_length, int)

        i_dim = initializer.shape[0]  ### size of the vocabulary
        o_dim = Configs.DIM_EMBEDDING  ### dimension of the 'dense' embedding

        with tf.device('/cpu:0'):
            return Embedding(
                i_dim,
                o_dim,
                input_length=input_length,
                embeddings_initializer=Constant(initializer),
                trainable=False,
                mask_zero=True
            )

    @staticmethod
    def WeightedSum(N_Q_TOKENS):

        def _nn(q_rnn):
            q_rnn = tf.transpose(q_rnn, perm=[0, 2, 1])
            weighted_sum = DrQaLayers.__weighted_sum(N_Q_TOKENS, 1)(q_rnn)  ### --> (_,1,emb_dim)
            red_sum = tf.reduce_sum(weighted_sum, axis=2)
            exp_dim = tf.expand_dims(red_sum, axis=2)
            q_encoding1 = tf.transpose(exp_dim, perm=[0, 2, 1])
            return q_encoding1

        return _nn

    @staticmethod
    def RNN() -> Callable[[Any], Any]:
        units = 128
        initializer = 'glorot_uniform'

        def _lstm() -> RNN:
            cell = LSTMCell(units, dropout=.3, recurrent_initializer=initializer)
            return RNN(cell, return_sequences=True)

        rnn1 = Bidirectional(_lstm(), merge_mode="concat")

        # rnn2 = Bidirectional(_lstm(), merge_mode="concat")
        # rnn3 = Bidirectional(_lstm(), merge_mode="concat")

        def _nn(x: Any) -> Any:
            x = rnn1(x)
            # x = rnn2(x)
            # x = rnn3(x)
            return x

        return _nn

    @staticmethod
    def CustomMasking():

        def _nn(rnn: Any, mask: Any) -> Any:
            mask_expanded = expand_dims(mask, axis=2)
            return mask_expanded * rnn

        return _nn

    @staticmethod
    def ComplementaryBit() -> Callable[[Any], Any]:
        nn1_units = Configs.N_PASSAGE_TOKENS + 1

        nn2_start = Dense(nn1_units, activation="softmax")
        nn2_end = Dense(nn1_units, activation="softmax")

        def __nn2(output: Any) -> Any:
            out_start = output[:, :, 0]
            ### --> (_, n_tokens)
            out_end = output[:, :, 1]
            ### --> (_, n_tokens)

            out_start = nn2_start(out_start)
            out_end = nn2_end(out_end)

            out_start = tf.expand_dims(out_start, axis=2)
            ### --> (_, n_tokens+1, 1)
            out_end = tf.expand_dims(out_end, axis=2)
            ### --> (_, n_tokens+1, 1)

            out_new = tf.concat([out_start, out_end], axis=2)
            ### --> (_, n_tokens+1, 2)

            return out_new

        # return __nn1
        return __nn2
