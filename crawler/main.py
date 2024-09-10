import json
import uvicorn
from fastapi import FastAPI
import craw, craw_tin_tuc
import sys


app = FastAPI()


@app.get("/crawler/get/")
def crawler_with_type_page(link):
    try:
        results = getattr(craw, sys.argv[1])(link)
        return results
    except Exception as e:
        print(e)
        print("Lỗi không agurment không tồn tại")
        return []


@app.get("/crawler/get_full")
def get_link():
    try:
        func = getattr(craw, f"link_{sys.argv[1]}")
        res = func()
        return res
    except AttributeError as e:
        print(e)
        print("Lỗi: Không tìm thấy argument")
        return []


@app.get("/crawler/get/lifecycle/")
def crawler_with_type_page(id, link):
    try:
        results = getattr(craw, f"lifecycle_{sys.argv[1]}")(id, link)
        return results
    except Exception as e:
        print(e)
        return []


@app.get("/tin_tuc/get/")
def crawler_data_tin_tuc(link):
    try:
        results = getattr(craw_tin_tuc, sys.argv[1])(link)
        return results
    except Exception as e:
        print(e)
        print("Lỗi không agurment không tồn tại")
        return []


@app.get("/tin_tuc/get_link")
def get_link_tin_tuc():
    try:
        func = getattr(craw_tin_tuc, f"link_{sys.argv[1]}")
        res = func()
        return res
    except AttributeError as e:
        print(e)
        print("Lỗi: Không tìm thấy argument")
        return []


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
