from typing import Callable, Any, List

import tensorflow as tf

from tensorflow.keras.layers import Dot, Dense
from tensorflow.keras.activations import softmax

###


# pylint: disable=invalid-name
def AttentionCore(compatibility: Callable[[Any, Any], Any],
                  distribution: Callable[[Any], Any]) -> Callable[[List[Any]], Any]:

    def _nn(keys_and_query: List[Any]) -> Any:
        keys, query = keys_and_query[0], keys_and_query[1]

        energy_scores = compatibility(keys, query)

        attention_weights = distribution(energy_scores)

        return attention_weights

    return _nn


# pylint: disable=invalid-name
def AttentionModel(compatibility: Callable[[Any, Any], Any],
                   distribution: Callable[[Any], Any]) -> Callable[[List[Any]], Any]:

    def _nn(keys_and_query: List[Any]) -> Any:
        keys, query = keys_and_query[0], keys_and_query[1]

        attention_weights = AttentionCore(compatibility, distribution)([keys, query])

        weighted_values = attention_weights * keys

        return tf.reduce_sum(weighted_values, axis=1)

    return _nn


###


def AlignmentModel(units=1) -> Callable[[Any, Any], Any]:
    ### TODO: exploit the `AttentionLayers.core()` function instead of
    ### replicating all the common steps of Attention core mechanism.

    _alpha = Dense(units, activation="relu")

    def compatibility(a: Any, b: Any) -> Any:
        # dot product
        return a @ b

    def distribution(scores: Any) -> Callable[[Any], Any]:
        return softmax(scores)

    def _nn(passage_and_question: List[Any]) -> Any:
        passage, question = passage_and_question[0], passage_and_question[1]

        alpha_question = _alpha(question)  # K
        # (batch_size,question_length,units)
        aligned_tokens = []

        for i in range(passage.shape[1]):

            token_passage = passage[:, i, :]  # raw Query
            # (batch_size,token_length)
            token_passage = tf.expand_dims(token_passage, axis=1)
            # (batch_size,1,token_length)

            alpha_token_passage = _alpha(token_passage)  #Query
            # (batch_size,1,units)

            shape = alpha_token_passage.shape
            shape = [-1, shape[2], shape[1]]
            alpha_token_passage = tf.reshape(alpha_token_passage, shape)
            # (batch_size,units,1)

            attention_weights = AttentionCore(compatibility,
                                              distribution)([alpha_question, alpha_token_passage])
            # (batch_size,keys_length,1)

            context_vector = attention_weights * question  # scalar product
            ### (batch_size, question_length,token_length)
            context_vector = tf.reduce_sum(context_vector, axis=1)
            ### (batch_size, token_length)
            context_vector = tf.expand_dims(context_vector, axis=1)
            ### (batch_size, 1, token_length)
            aligned_tokens.append(context_vector)

        # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
        aligned_passage = tf.concat(aligned_tokens, axis=1)
        ### (batch_size, passage_length, token_length)

        return aligned_passage

    return _nn


# pylint: disable=invalid-name
def WeightedSumSelfAttention():
    W = Dense(1, use_bias=False)

    def compatibility(keys: Any, *_) -> Any:
        return W(keys)

    def distribution(scores: Any) -> Any:
        return softmax(scores)

    return AttentionModel(compatibility, distribution)


# pylint: disable=invalid-name
def BiLinearSimilarityAttention():
    # W_start = Dense(256, activation="exponential", use_bias=False)
    # W_end = Dense(256, activation="exponential", use_bias=False)
    #
    # ISSUE: the `compatibility` function MUST take as input `K, q` where `K` is a matrix.
    # def compatibility(W: Any) -> Callable[[Any], Callable[[Any, Any], Any]]:
    #     def _W_compatibility(key: Any, queries: Any) -> Any:
    #         scores = []
    #         for idx in range(queries.shape[1]):
    #             query = queries[:, idx, :]
    #             ### --> (_, 256)
    #             score = Dot(axes=1)([key, W(query)])
    #             ### --> (_, 1)
    #             scores.append(score)
    #         scores = tf.convert_to_tensor(scores)
    #         ### --> (40, _, 1)
    #         scores = tf.transpose(scores, perm=[1, 0, 2])
    #         ### --> (_, 40, 1)
    #         scores = tf.squeeze(scores, axis=[2])
    #         ### --> (_, 40)
    #         return scores
    #     return _W_compatibility
    # def distribution(scores: Any) -> Any:
    #     return softmax(scores)
    #
    # start_probability = AttentionCore(compatibility(W_start), distribution)
    # end_probability = AttentionCore(compatibility(W_end), distribution)
    #
    # probabilities = tf.convert_to_tensor([start_probability, end_probability])
    # ### --> (2, _, 40)
    # probabilities = tf.transpose(probabilities, perm=[1, 2, 0])
    # ### --> (_, 40, 2)
    #
    # return probabilities

    pass


def AlignedAttention():
    alpha = Dense(1, use_bias=False)

    def compatibility(keys: Any, query: Any) -> Any:
        _alpha_query = alpha(query)

        scores = []
        for idx in keys.shape[1]:
            key = key[:, idx, :]
            _alpha_key = alpha(key)
            scores.append(_alpha_key * _alpha_query)

        return tf.convert_to_tensor(scores)

    def distribution(scores: Any) -> Any:
        return softmax(scores)

    def _nn(keys_and_queries: List[Any]):
        keys, queries = keys_and_queries[0], keys_and_queries[1]

        weights = []
        for idx in queries.shape[1]:
            query = queries[:, idx, :]
            weights.append(AttentionModel(compatibility, distribution)([keys, query]))

        return tf.convert_to_tensor(weights)

    return _nn