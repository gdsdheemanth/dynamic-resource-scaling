import ray
from ray import train
import tensorflow as tf

ray.init()


def train_func(config):
    """Distributed training function for Ray Train."""
    strategy = tf.distribute.MultiWorkerMirroredStrategy()
    print(f"Running TensorFlow distributed training with {strategy.num_replicas_in_sync} replicas.")

    with strategy.scope():
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0

    model.fit(x_train, y_train, epochs=config["epochs"])
    model.save('/app/model_output')


trainer = train.TensorflowTrainer(train_func, scaling_config={"num_workers": 2})
trainer.fit()
