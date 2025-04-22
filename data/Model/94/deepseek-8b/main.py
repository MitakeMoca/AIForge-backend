import sys
import json
from train import train
from predict import predict


if __name__ == "__main__":
    while True:
        user_input = input()
        if user_input == "exit":
            print("Exiting...")
            break
        elif user_input in ["train", "predict"]:
            # 提示用户输入参数
            params = input()

            if user_input == "train":
                print("Training with hyper parameters:", params)
                params = json.loads(params)
                train(params)
                print("TRAIN_COMPLETE")
            elif user_input == "predict":
                predict(params)
                print("PREDICT_COMPLETE")
        else:
            print("Unknown command. Available commands: train, predict, exit")
