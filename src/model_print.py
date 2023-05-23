import os
import time
import cv2

import numpy as np
import pandas as pd

from datetime import datetime

import tensorflow as tf

import save_path_info

class Tf_model():
    
    def __init__(self):
        
        # tfmodel use gpu
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
        # 텐서플로가 첫 번째 GPU에 1GB 메모리만 할당하도록 제한
            try:
                tf.config.set_logical_device_configuration(
                    gpus[0],
                    [tf.config.LogicalDeviceConfiguration(memory_limit=6144)])
            except RuntimeError as e:
                # 프로그램 시작시에 가상 장치가 설정되어야만 합니다
                print(e)
            

        self.tf_model = self.load_model()
        
    
    def load_model(self):
        """" 모델을 불러오는 함수 """
        # 저장된 모델 경로 입력
        # model_path = "model_1654675043"
        model_path = "./js02_model/andrew_20230503_1683104384"
        # 모델 불러오기
        new_model = tf.keras.models.load_model(model_path, compile=False)
        new_model.trainable = False
        # print(new_model.summary())

        # 모델 리턴
        return new_model


    def processing_img(self, img):
        """"영상을 모델 입력 크기에 맞게, 그리고 Tensor 형태로 변환해주는 함수 """

        # 영상 크기 128x128 로 변환
        re_img = cv2.resize(img, dsize=(224, 224), interpolation=cv2.INTER_AREA)

        # Tensor로 변환 RGB를 Tensor로 변환하기 위해서는 0~1로 치환해줘야 함.(RGB / 255.0)
        tf_img = np.array(re_img) / 255.0

        # Tensor 데이터는 하나의 차원이 더 있어야함, 1차원 추가
        tf_img = tf_img[tf.newaxis, ...]

        return tf_img


    def inference(self, epoch, left_range, right_range, distance, cv_img):
        """"분류 모델에 영상을 넣어 추론해 visibility 출력하는 함수"""
        
        
        if int(distance[-1]) < 30:
            pass
            
        else:
            left_range = left_range[:-1]
            right_range = right_range[:-1]
            distance = distance[:-1]
            
        
        
        print("inferece start")
        start_time = time.time()
        visibility = 0
        cp_image = cv_img.copy()
        print("target length : ", len(left_range))
        image_list = []
        # 타겟정보로 원본 이미지에서 잘라 이미지 리스트에 추가
        for upper_left, lower_right in zip(left_range, right_range):
            up_y = min(upper_left[1], lower_right[1])
            down_y = max(upper_left[1], lower_right[1])

            left_x = min(upper_left[0], lower_right[0])
            right_x = max(upper_left[0], lower_right[0])
            # roi
            target = cp_image[up_y:down_y, left_x:right_x, :]
            target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
            target = cv2.resize(target, (224, 224), interpolation = cv2.INTER_AREA)
            kernel_sharpen_3 = np.array([[-1,-1,-1,-1,-1],[-1,2,2,2,-1],[-1,2,8,2,-1],[-1,2,2,2,-1],[-1,-1,-1,-1,-1]])/8.0
            sharp_img = cv2.filter2D(target, -1, kernel_sharpen_3)
            target = cv2.fastNlMeansDenoising(sharp_img,None,10,7,21)
            target = cv2.cvtColor(target, cv2.COLOR_GRAY2BGR)
            target = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
            image_list.append(target)


        # RGB 영상을 Tensor 형태로 변환
        # tf_cp_image = processing_img(image)
        tf_image_list = [self.processing_img(img) for img in image_list]

        # 강도별 의미 정의
        CLASS_NAMES = ['n', 'y']

        # Tensor 영상을 모델에 넣어 추론
        # predicted_batch = model.predict(tf_cp_image)
        predicted_batch_list = [self.tf_model.predict(tf_cp_image) for tf_cp_image in tf_image_list]
        # print(predicted_batch)

        # 추론 결과중 가장 높은값을 가진 인덱스 번호를 출력
        # predicted_ids = np.argmax(predicted_batch, axis=-1)
        predicted_ids_list = [np.argmax(predict_batch, axis=-1) for predict_batch in predicted_batch_list]
        # print(predicted_ids_list)

        # 정의한 강도 리스트에 인덱스 번호를 넣어 현재 나타난 강도를 출력
        # predicted_class_names = CLASS_NAMES[predicted_ids[0]]
        predicted_class_names_list = [CLASS_NAMES[predicted_ids[0]] for predicted_ids in predicted_ids_list]

        # 거리와 모델 값을 그룹화 후 거리별로 정렬
        result_list = [[distance_val, pre_val, cv_img] for distance_val, pre_val, cv_img in zip(distance, predicted_class_names_list, image_list)]
        result_list.sort(key = lambda x : x[0])
        
        # 시정 계산
        visibility = self.cal_visibility(result_list)
        # visibility print
        print(f" visibility : ", visibility)

        days = epoch[:-4]
        vis_folder_path = os.path.join(save_path_info.get_data_path('Path', 'data_csv_path'))
        vis_file_path = os.path.join(vis_folder_path,f"{days}.csv")
        os.makedirs(vis_folder_path, exist_ok=True)
        
        if os.path.isfile(vis_file_path):
            vis_df = pd.read_csv(vis_file_path)
        else:
            cols = ["time",'visibility']
            vis_df = pd.DataFrame(columns=cols)
        
        dt_epoch = datetime.strptime(epoch, '%Y%m%d%H%M')
        vis_df = vis_df.append({'time': dt_epoch,'visibility': visibility}, ignore_index=True)
        
        vis_df.to_csv(vis_file_path,mode="w", index=False)
            
        
        # 이미지 저장
        self.result_save(result_list, epoch, visibility)
        print("실행시간 : ", time.time() - start_time)
        # print(JS08Settings.get("target_csv_path"))
        print("")


        return str(visibility)

        
    
    def cal_visibility(self, result_list: list):
        """ 최종 리스트를 입력받아 거리별로 정렬하고 먼거리 기준 판별 유무에 따라 시정을 리턴"""
        
        label_pred = "y"
        check_point = 0
        # 거꾸로 반복문 시작(먼거리부터 시작)
        for dis_pre_val in result_list[::-1]:
            # 모델 결과값이 예스이면 거리 리턴
            if dis_pre_val[1] == label_pred:
                # 거리가 20km 이상이면 20으로 제한
                if dis_pre_val[0] > 20:
                    return 20
                else:
                    return dis_pre_val[0]
            # 모델 결과값이 전부 노이면 최소거리 10m 리턴
            
        return 0.01
    
    def result_save(self, dip_list: list, epoch: str, visibility):
        """ 추론값과 현재 시정, 타겟 이미지들을 저장"""

        save_path = os.path.join(save_path_info.get_data_path('Path', 'image_save_path'), 'target_images')
        os.makedirs(save_path, exist_ok=True)

        for distance, predict_idx, cv_img in dip_list[::-1]:
            
            # target_save_path = os.path.join(save_path, str(distance))
            # os.makedirs(target_save_path, exist_ok=True)

            no_target_save_path = os.path.join(save_path, "No")
            yes_target_save_path = os.path.join(save_path, "Yes")
            os.makedirs(no_target_save_path, exist_ok=True)
            os.makedirs(yes_target_save_path, exist_ok=True)

            if int(epoch[-2:]) % 5 == 00:
                if predict_idx == "n":

                    image_path = os.path.join(no_target_save_path, f"{epoch}_{distance}_{predict_idx}_{visibility}.png")
                else:
                    image_path = os.path.join(yes_target_save_path, f"{epoch}_{distance}_{predict_idx}_{visibility}.png")

                cv2.imwrite(image_path, cv_img)
                print(image_path, " : image save")



        
        
        # target_image_path = os.path.join()




