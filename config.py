import pymysql

class Config:
    def __init__(self):
        self.mysql = pymysql.connect(
            host='database.alstore.space',
            user = 'u3496_6gSW0tArCv',
            password= 'ZmtVLPl6q=zGV21fL1pzW+yY',
            database= 's3496_uas_pbo',
            port=3306
        )