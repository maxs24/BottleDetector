import time

import cv2
import numpy as np


def draw_object_bounding_box(image_to_process, index, box):
    x, y, w, h = box
    start = (x, y)
    end = (x + w, y + h)
    color = (0, 255, 0)
    width = 2
    final_image = cv2.rectangle(image_to_process, start, end, color, width)

    draw_centr_coords((x+w)/2, (y + h)/2, final_image)

    return final_image


def draw_centr_coords(x, y, poc_image):
    start = (20, 20)
    font_size = 0.6
    font = cv2.FONT_HERSHEY_SIMPLEX
    width = 3
    text = "Centr Coords: (" + str(x) + ',' + str(y) + ')'
    color = (0, 255, 0)

    final_image = cv2.putText(poc_image, text, start, font, font_size,
                              color, width, cv2.LINE_AA)

    return final_image


def draw_fps(poc_image, fps):

    start = (20, 40)
    font_size = 0.6
    font = cv2.FONT_HERSHEY_SIMPLEX
    width = 3
    text = "FPS: " + str(fps)
    color = (0, 255, 0)

    final_image = cv2.putText(poc_image, text, start, font, font_size,
                              color, width, cv2.LINE_AA)
    return final_image

def apply_yolo_object_detection(image_to_process):
    height, width, _ = image_to_process.shape
    blob = cv2.dnn.blobFromImage(image_to_process, 1 / 255, (608, 608),
                                 (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outs = net.forward(out_layers)
    class_indexes, class_scores, boxes = ([] for i in range(3))
    objects_count = 0

    for out in outs:
        for obj in out:
            scores = obj[5:]
            class_index = np.argmax(scores)
            class_score = scores[class_index]
            if class_score > 0:
                center_x = int(obj[0] * width)
                center_y = int(obj[1] * height)
                obj_width = int(obj[2] * width)
                obj_height = int(obj[3] * height)
                box = [center_x - obj_width // 2, center_y - obj_height // 2,
                       obj_width, obj_height]
                boxes.append(box)
                class_indexes.append(class_index)
                class_scores.append(float(class_score))

    chosen_boxes = cv2.dnn.NMSBoxes(boxes, class_scores, 0.0, 0.4)
    for box_index in chosen_boxes:
        box = boxes[box_index]
        class_index = class_indexes[box_index]

        if classes[class_index] in classes_to_look_for:
            objects_count += 1
            image_to_process = draw_object_bounding_box(image_to_process,
                                                        class_index, box)

    return image_to_process


def start_image_object_detection(original_image):
    try:
        return apply_yolo_object_detection(original_image)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    CAM_PORT = 0
    net = cv2.dnn.readNetFromDarknet("Resources/yolov4-tiny.cfg",
                                     "Resources/yolov4-tiny.weights")
    layer_names = net.getLayerNames()
    out_layers_indexes = net.getUnconnectedOutLayers()
    out_layers = [layer_names[index - 1] for index in out_layers_indexes]

    with open("Resources/coco.names.txt") as file:
        classes = file.read().split("\n")

    classes_to_look_for = ['bottle']

    cam = cv2.VideoCapture(CAM_PORT)

    new_frame_time = 0
    prev_frame_time = 0
    while True:
        result, image = cam.read()
        new_frame_time = time.time()
        res_image = start_image_object_detection(image)
        fps = 1/(new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        res_image = draw_fps(res_image, int(fps))
        cv2.imshow("camera", res_image)
        if cv2.waitKey(10) == 27:  # ?????????????? Esc
            break
    cam.release()
    cv2.destroyAllWindows()
