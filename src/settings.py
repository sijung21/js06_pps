
#!/usr/bin/env python3
#
# Copyright 2021-2022 Sijung Co., Ltd.
#
# Authors:
#     cotjdals5450@gmail.com (Seong Min Chae)
#     5jx2oh@gmail.com (Jongjin Oh)

import sys
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import QSettings


# config.ini 파일의 설정값들을 읽어들어 settings에 저장
settings = QSettings('config.ini', QSettings.IniFormat)

class Setting_Widget(QDialog):
# JS06의 설정 값들을 저장 및 수정하는 Dialog

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        ui_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               "ui/js06_setting.ui")
        uic.loadUi(ui_path, self)
        
        # 카메라 부분 설정값 출력
        self.camera_model_lineEdit.setText(settings.value("SETTING/camera_name"))
        self.camera_ip_lineEdit.setText(settings.value("SETTING/camera_ip"))
        self.camera_id_lineEdit.setText(settings.value("SETTING/camera_id"))
        self.camera_password_lineEdit.setText(settings.value("SETTING/camera_pw"))
        self.camera_profile_num_lineEdit.setText(settings.value("SETTING/view_profile"))
        
        
        # 데이터 저장부분 설정값 출력
        self.data_path_lineEdit.setText(settings.value("Path/data_csv_path"))
        self.target_path_lineEdit.setText(settings.value("Path/target_csv_path"))
        self.rgb_path_lineEdit.setText(settings.value("Path/rgb_csv_path"))
        self.image_path_lineEdit.setText(settings.value("Path/image_save_path"))
        self.log_path_lineEdit.setText(settings.value("Path/log_path"))
        
        # 확인 누르면 현재값으로 저장
        self.buttonBox.accepted.connect(self.accept_click)
    
    def accept_click(self):
        # 현재 linEdit에 있는 값들을 config.ini 파일에 업데이트
        settings.setValue('SETTING/camera_name', self.camera_model_lineEdit.text())
        settings.setValue('SETTING/camera_ip', self.camera_ip_lineEdit.text())
        settings.setValue('SETTING/camera_id', self.camera_id_lineEdit.text())
        settings.setValue('SETTING/camera_pw', self.camera_password_lineEdit.text())
        settings.setValue('SETTING/view_profile', self.camera_profile_num_lineEdit.text())
        
        
        settings.setValue('Path/data_csv_path', self.data_path_lineEdit.text())
        settings.setValue('Path/target_csv_path', self.target_path_lineEdit.text())
        settings.setValue('Path/rgb_csv_path', self.rgb_path_lineEdit.text())
        settings.setValue('Path/image_save_path', self.image_path_lineEdit.text())
        settings.setValue('Path/log_path', self.log_path_lineEdit.text())



if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ui = Setting_Widget()
    ui.show()
    sys.exit(app.exec_())
    