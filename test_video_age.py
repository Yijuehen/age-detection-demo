import numpy as np
import cv2
import imutils
import os


def detect_age(frame, faceNet, ageNet, minConfidence=0.5):
    AGE_LIST = [
        "(0-2)",
        "(4-6)",
        "(8-12)",
        "(15-20)",
        "(25-32)",
        "(38-43)",
        "(48-53)",
        "(60-100)",
    ]
    results = []
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
    faceNet.setInput(blob)
    detect = faceNet.forward()
    for i in range(0, detect.shape[2]):
        confidence = detect[0, 0, i, 2]
        if confidence > minConfidence:
            box = detect[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            face = frame[startY:endY, startX:endX]
            if face.shape[0] < 20 or face.shape[1] < 20:
                continue
            faceBlob = cv2.dnn.blobFromImage(
                face,
                1.0,
                (227, 227),
                (78.4263377603, 87.7689143744, 114.895847746),
                swapRB=False,
            )
            ageNet.setInput(faceBlob)
            predictions = ageNet.forward()
            i = predictions[0].argmax()
            age = AGE_LIST[i]
            ageConfidence = predictions[0][i]
            dicts = {
                "location": (startX, startY, endX, endY),
                "age": (age, ageConfidence),
            }
            results.append(dicts)
    return results


def predict_video_age(video_path):
    prototxtPathF = "./models/face_detector/face_deploy.prototxt"
    weightsPathF = "./models/face_detector/res10_300x300_ssd_iter_140000.caffemodel"
    faceNet = cv2.dnn.readNet(prototxtPathF, weightsPathF)

    prototxtPathA = "./models/age_detector/age_deploy.prototxt"
    weightsPathA = "./models/age_detector/age_net.caffemodel"
    ageNet = cv2.dnn.readNet(prototxtPathA, weightsPathA)

    vs = cv2.VideoCapture(video_path)
    if not vs.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return

    output_dir = "my_flask_app/app/static/images/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base, ext = os.path.splitext(os.path.basename(video_path))
    output_path = f"{output_dir}/{base}_result{ext}"

    fps = vs.get(cv2.CAP_PROP_FPS)
    width = int(vs.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vs.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"X264")

    writer = None

    try:
        while True:
            (grabbed, frame) = vs.read()
            if not grabbed:
                print("视频处理结束...")
                break

            if writer is None:
                (h, w) = frame.shape[:2]
                writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

            results = detect_age(frame, faceNet, ageNet, minConfidence=0.5)
            for i in results:
                text = "age{}:{:.2f}%".format(i["age"][0], i["age"][1] * 100)
                (startX, startY, endX, endY) = i["location"]
                y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
                cv2.putText(
                    frame,
                    text,
                    (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )

            writer.write(frame)

            # 显示结果
            cv2.imshow("Result", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    finally:
        if writer:
            writer.release()
        vs.release()
        cv2.destroyAllWindows()

    return output_path


# if __name__ == "__main__":
#     predict_video_age("D:/download/pictrues/test1.mp4")
