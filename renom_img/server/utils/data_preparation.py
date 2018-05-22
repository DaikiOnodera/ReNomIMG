#!/usr/bin/env python
# encoding:utf-8

from __future__ import division, print_function
import os
import sys
import numpy as np
from xml.etree import ElementTree

from renom_img.api.utils.target import build_target
from renom_img.api.utils.distributor.distributor import ImageDetectionDistributor
from renom_img.api.utils.load import parse_xml_detection

from renom_img.api.utils.augmentation.augmentation import Augmentation
from renom_img.api.utils.augmentation.process import Flip, Shift, Rotate, WhiteNoise


label_dict = {}
label_length = 0


def _get_obj_coordinate(obj):
    global label_dict
    class_name = obj.find("name").text.strip()
    if label_dict.get(class_name, None) is None:
        label_dict[class_name] = len(label_dict)
        label_dict = {k: i for i, k in enumerate(sorted(label_dict.keys()))}
    class_id = label_dict[class_name]
    bbox = obj.find("bndbox")
    xmax = float(bbox.find("xmax").text.strip())
    xmin = float(bbox.find("xmin").text.strip())
    ymax = float(bbox.find("ymax").text.strip())
    ymin = float(bbox.find("ymin").text.strip())
    w = xmax - xmin
    h = ymax - ymin
    x = xmin + w / 2
    y = ymin + h / 2
    return class_id, x, y, w, h


def get_img_info(filename):
    tree = ElementTree.parse(filename)
    node = tree.getroot()
    file_name = node.find("filename").text.strip()
    img_h = float(node.find("size").find("height").text.strip())
    img_w = float(node.find("size").find("width").text.strip())
    obj_list = node.findall("object")
    objects = []
    for obj in obj_list:
        objects.append(_get_obj_coordinate(obj))
    return file_name, img_w, img_h, objects


def one_hot(label):
    oh = [0] * label_length
    oh[label] = 1
    return oh


def create_detection_distributor(xml_root_path, img_root_path, img_size, augmentation=None):
    global label_length
    label_data = []
    img_path_list = []
    label_list = []

    base_dir = '.'
    file_dir = os.path.join(base_dir, xml_root_path)

    file_list = sorted(os.listdir(file_dir))

    data_set = [get_img_info(os.path.join(file_dir, path))
                for path in file_list]

    label_length = len(label_dict)

    for i in range(len(file_list)):
        img_path = os.path.join(img_root_path, data_set[i][0])
        if not os.path.exists(img_path):
            continue

        objects = []
        for obj in data_set[i][3]:
            detect_label = {"bndbox": [obj[1], obj[2], obj[3], obj[4]],
                            "name": one_hot(obj[0])}
            objects.append(detect_label)
        img_path_list.append(img_path)
        label_list.append(objects)
    class_list = [c for c, v in sorted(label_dict.items(), key=lambda x:x[0])]

    return ImageDetectionDistributor(img_path_list,
                                     label_list,
                                     class_list,
                                     imsize=img_size,
                                     augmentation=augmentation)


def check_class_existence():
    train_img_path = 'dataset/train_set/img'
    train_xml_path = 'dataset/train_set/label'
    valid_img_path = 'dataset/valid_set/img'
    valid_xml_path = 'dataset/valid_set/label'

    for xml_root_path in [train_xml_path, valid_xml_path]:
        file_dir = xml_root_path
        file_list = sorted(os.listdir(file_dir))
        data_set = [get_img_info(os.path.join(file_dir, path))
                    for path in file_list]


def create_train_valid_dists(img_size):
    train_img_path = 'dataset/train_set/img'
    train_xml_path = 'dataset/train_set/label'
    valid_img_path = 'dataset/valid_set/img'
    valid_xml_path = 'dataset/valid_set/label'

    def create_label(xml_path_list, class_mapping=None):
        annotation_list = parse_xml_detection(xml_path_list)
        return build_target(annotation_list, img_size, class_mapping)

    train_xml_path_list = [os.path.join(train_xml_path, path)
                           for path in sorted(os.listdir(train_xml_path))]
    train_img_path_list = [os.path.join(train_img_path, path)
                           for path in sorted(os.listdir(train_img_path))]
    valid_xml_path_list = [os.path.join(valid_xml_path, path)
                           for path in sorted(os.listdir(valid_xml_path))]
    valid_img_path_list = [os.path.join(valid_img_path, path)
                           for path in sorted(os.listdir(valid_img_path))]

    # Check if the xml filename and img name is same.
    train_label, class_mapping = create_label(train_xml_path_list)
    valid_label, _ = create_label(valid_xml_path_list, class_mapping)

    aug = Augmentation([
        Flip(),
        Shift(20, 20),
        Rotate(),
        WhiteNoise(0.05),
    ])

    train_dist = ImageDetectionDistributor(train_img_path_list, train_label, img_size, aug)
    valid_dist = ImageDetectionDistributor(valid_img_path_list, valid_label, img_size)
    class_list = [k for k, v in sorted(class_mapping.items(), key=lambda x: x[0])]
    return class_list, train_dist, valid_dist


def create_pred_dist(img_size):
    if not label_dict:
        check_class_existence()
    pred_img_path = 'dataset/prediction_set/img'
    pred_img_path_list = sorted(os.listdir(pred_img_path))
    pred_img_path_list = [os.path.join(pred_img_path, x)
                          for x in pred_img_path_list]
    pred_dist = ImageDetectionDistributor(pred_img_path_list, None, img_size)
    return pred_dist






