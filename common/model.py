# /common/model.py

import tensorflow as tf

def create_simple_model():
    """
    Cria e compila um modelo Keras simples para classificação no MNIST.
    """
    model = tf.keras.models.Sequential([
        # Camada de entrada que achata a imagem 28x28 para um vetor de 784
        tf.keras.layers.Flatten(input_shape=(28, 28)),

        # Primeira camada densa (totalmente conectada) com 128 neurônios e ativação ReLU
        tf.keras.layers.Dense(128, activation='relu'),

        # Camada de saída com 10 neurônios (um para cada dígito de 0 a 9)
        # A ativação Softmax fornece a probabilidade de a imagem pertencer a cada classe
        tf.keras.layers.Dense(10, activation='softmax')
    ])
     
    return model