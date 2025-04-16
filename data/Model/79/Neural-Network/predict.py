import numpy as np
from dataset.mnist import load_mnist
from two_layer_net import TwoLayerNet
from PIL import Image


def img_show(img):
    pil_img = Image.fromarray(np.uint8(img))
    pil_img.show()


def predict(data):
    (x_train, t_train), (x_test, t_test) = load_mnist(flatten=True, normalize=False)

    img = x_train[0]
    label = t_train[0]
    print("real label: " + str(label))

    img = img.reshape(28, 28)

    network = TwoLayerNet(input_size=784, hidden_size=50, output_size=10)
    network.load_params()

    result = network.predict(x_train[0].reshape(1, 28 * 28)).argmax(axis=1)[0]
    print("predict label: " + str(result))
    correct = "wrong"
    if result == label:
        correct = "correct"

    print("predict " + correct + "!")
