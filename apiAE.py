import requests

url = "https://recom-acs.aliexpress.com/h5/mtop.relationrecommend.aliexpressrecommend.recommend/1.0/"
params = {
    "jsv": "2.5.1",
    "appKey": "95f29bbc34msh68cc5252c8fbcf3p1485b6jsnadec29fe9303",
    "t": "1717584762920",
    "sign": "71de3cc7ba97702018498caa6bf27edf",
    "api": "mtop.relationrecommend.AliexpressRecommend.recommend",
    "v": "1.0",
    "timeout": "10000",
    "type": "originaljson",
    "dataType": "jsonp"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("İstek başarısız oldu. HTTP kodu:", response.status_code)
