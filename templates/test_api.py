import requests

def test_get_stocks():

    r = requests.get("http://localhost:5000/stocks")

    assert r.status_code == 200


def test_create_stock():

    files = {"file": open("test.png","rb")}

    data = {

        "name":"APIProduct",

        "quantity":"5",

        "pipeline":"warehouse"
    }

    r = requests.post("http://localhost:5000/stocks",data=data,files=files)

    assert r.status_code == 200