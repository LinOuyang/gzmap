micro_adjust = dict()
micro_adjust["瑞金"] = 0.1, 0
micro_adjust["会昌"] = 0, -0.1
micro_adjust["寻乌"] = -0.12, 0
micro_adjust["定南"] = 0.08, 0.05
micro_adjust["大余"] = 0.08, 0.05
micro_adjust["南康"] = 0.05, -0.05
micro_adjust["赣县"] = 0.05, 0

import os
path = os.path.dirname(__file__)
shapefile_lev1 = f"{path}/shape_data/GanZhou.shp"
shapefile_lev2 = f"{path}/shape_data/GanzhouLevel2.shp"
encoding='gbk'
