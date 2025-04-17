import numpy as np
from PIL import Image
from two_layer_net import TwoLayerNet


def load_image(file_path, flatten=True):
    # 加载并预处理图像
    img = Image.open(file_path).convert('L')  # 转换为灰度
    img = img.resize((28, 28))  # 调整尺寸

    # 转换为numpy数组并处理数据类型
    img_array = np.array(img, dtype=np.float32)

    # 反转颜色（MNIST是黑底白字，一般图片可能是白底黑字）
    img_array = 255 - img_array

    # 展平处理
    if flatten:
        img_array = img_array.reshape(1, -1)  # 转换为(1, 784)

    return img_array


def predict(img_path):
    # 加载并预处理图像
    processed_img = load_image(img_path)

    # 初始化网络
    network = TwoLayerNet(input_size=784, hidden_size=50, output_size=10)

    network.load_params('params.pkl')

    # 进行预测
    confidence = network.predict(processed_img)
    predicted_label = confidence.argmax(axis=1)[0]

    print(f"Predict Result is: {predicted_label}")
    return predicted_label