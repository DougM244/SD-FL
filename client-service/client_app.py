# client-service/client_app.py
from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from common.model import create_simple_model
import os
import traceback


app = Flask(__name__)

print("Carregando dados do MNIST...")
(x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
x_train = x_train / 255.0

client_id = int(os.environ.get('CLIENT_ID', 0))
start_index = client_id * 1000
end_index = start_index + 1000
local_dataset = tf.data.Dataset.from_tensor_slices(
    (x_train[start_index:end_index], y_train[start_index:end_index])
).batch(32)

print(f"Cliente {client_id} iniciado com dados do índice {start_index} ao {end_index}.")

# 4. Definição da rota da API
@app.route('/fit', methods=['POST'])
def fit():
    try:
        weights_json = request.json['weights']
        weights = [np.array(w, dtype=np.float32) for w in weights_json]

        model = create_simple_model()

        model.compile(optimizer='adam', 
                      loss='sparse_categorical_crossentropy', 
                      metrics=['accuracy'])

        model.set_weights(weights)

        print(f"Cliente {client_id}: Iniciando treinamento local...")
        model.fit(local_dataset, epochs=1, verbose=1)

        new_weights = [w.tolist() for w in model.get_weights()]
        print(f"Cliente {client_id}: Treinamento concluído.")

        return jsonify({
            "weights": new_weights, 
            "sample_count": end_index - start_index
        })

    except Exception as e:
        print(f"ERRO CRÍTICO no cliente {client_id}: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# 5. Execução do servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# Simulação de dados locais (em um cenário real, os dados já estariam aqui)
(x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
# Normaliza os dados
x_train = x_train / 255.0

# Cada cliente terá um "shard" diferente dos dados
# Vamos usar uma variável de ambiente para simular clientes diferentes
client_id = int(os.environ.get('CLIENT_ID', 0))
start = client_id * 1000
end = start + 1000
local_dataset = tf.data.Dataset.from_tensor_slices(
    (x_train[start:end], y_train[start:end])
).batch(32)

print(f"Cliente {client_id} iniciado com dados do índice {start} ao {end}.")

@app.route('/fit', methods=['POST'])
def fit():
    try:
        # Recebe os pesos do modelo global do orquestrador
        weights_json = request.json['weights']
        weights = [np.array(w, dtype=np.float32) for w in weights_json]

        model = create_simple_model()
        model.set_weights(weights)

        # Treina o modelo com os dados locais por uma época
        model.fit(local_dataset, epochs=1, verbose=0)

        # Retorna os pesos atualizados
        new_weights = [w.tolist() for w in model.get_weights()]
        print(f"Cliente {client_id}: Treinamento concluído.")
        return jsonify({"weights": new_weights, "sample_count": len(local_dataset) * 32})
    except Exception as e:
        print(f"Erro no cliente {client_id}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)