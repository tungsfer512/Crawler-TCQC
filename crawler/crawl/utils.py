import datetime
import time
import os

def wait_for_downloads(folder_download, time_setup=300):
    check = True
    for filename in os.listdir(folder_download): 
        if ".xlsx" in filename or '.xls' in filename:
            check = False
    if check and time_setup>0:
        time.sleep(2)
        time_setup-=2
        wait_for_downloads(folder_download, time_setup)

def format_datetime(input_datetime_str):
    if input_datetime_str == False :
        return False
    input_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%y-%m-%dT%H:%M:%S",
        "%B, %Y",
        "%Y-%m-%d",
        "%Y-%m",
    ]
    output_format = "%Y-%m-%d %H:%M:%S"
    for input_format in input_formats:
        try:
            datetime_obj = datetime.datetime.strptime(input_datetime_str, input_format)
            if input_format == "%B, %Y":
                datetime_obj = datetime_obj.replace(day=1, hour=0, minute=0, second=0)
                formatted_datetime_str = datetime_obj.strftime(output_format)
            return datetime_obj
        except ValueError:
            continue
    return input_datetime_str

def data_out(trees = False, duong_link = False , tac_gia = False , ten_tieng_anh=False, loai = 'kho',so_hieu=False,mo_ta= False , nam_ban_hanh= False , trang_thai = 'con_hieu_luc', **kwargs):
    data = {
        "ten_tieng_anh": ten_tieng_anh.strip() if ten_tieng_anh else False,
        "so_hieu": so_hieu.strip() if so_hieu else False,
        "nam_ban_hanh": format_datetime(nam_ban_hanh) if nam_ban_hanh else False,
        "trang_thai": trang_thai,
        'mo_ta':mo_ta,
        'loai':loai,
        'duong_link': duong_link,
        'tac_gia': tac_gia, 
        "tree": trees,
        **kwargs,
    }
    return data 
    
