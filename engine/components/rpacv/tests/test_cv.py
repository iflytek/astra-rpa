import time
from unittest import TestCase

from rpacv import BtnModel, BtnType, ExistType, InputType, PositionType, WaitType
from rpacv.cv import CV
from rpagui import MoveType, Speed

inputdata = {
    "version": "1",
    "type": "cv",
    "app": "",
    "path": "",
    "img": {
        "self": "iVBORw0KGgoAAAANSUhEUgAAAB8AAAAZCAIAAABGlWJzAAABxklEQVR4nO3VXy8cURgG8OfMIpRSW5pGk/ZC9AuQ+gjiTqSXLkj0qp+iN/0KjbSJpJJeighKZJel/i02XMiGsWUVi6Yks40duzPv0wtli9k17LqQ9L185zm/OefknBlFEndW2t3R91wvcJUiGZyRMZ+qrVMtraqwKJ869TX7czf1NQRnPeUVqqnZpe5iZ0xTxn1c1yECw+DwIPf38qSTDK/IZAC2fdqQiM6AH6lUPnTTlJEhxHbhfay1vkbNMxwfy/gYo5twcVGu0bk4L1OTAFTdS09bu1bfAICRdQn4kUzmpp+c2B8/IJEAgOISFBSq0jIAsC0O9DO2m4MuYn/p4c6240PGDftTFyzrljr1VQ71ZxsanOHUxK3033Hp66VhpDtxA8kkjw7Trz9d3F7shjrJxQWGFs5PIQCuhq337zg3eyG4FZWvAxD7CpFF/3kgvlEe/vq3p6qfeDo68fzFhWQqxelvDIdvoMv2D1kOXT7OSkHzKO1ynltRh/BZOXxn1INSeKuQSEAkrWx8t96+cQAelmveKijlqCuHf5NpcinEiE4r44aejYb2tAavGtWjStf639ky04zcV+bblDOdVc9H/dcz1R+hIOAe3BSZMQAAAABJRU5ErkJggg==",
        "parent": "iVBORw0KGgoAAAANSUhEUgAABKcAAAAhCAIAAACDRF/8AAAFB0lEQVR4nO3dPWgbZxzH8b+DUSCLByPIcNAheQy1oVjQFKHGBApBxvg221OX4Aw5JFB8gRLjQMkQvF0skLkloRA8ye0QpBpEhqaYCg0FabGGPPFQOKhB1eAhISqBdrCtF9sifslZsvz9TPc8eu65R+OP562vVqsJzkogEOj0EAAAAABcLJc6PQAAAAAAgI9IfQAAAADQy0h9AAAAANDLSH0AAAAA0MtIfQAAAADQy0h9AAAAANDL/Ex978orc+MRtScybr8oc00EAAAAAJylfv+6LqfnCzef5Z8au+WP3uqD2MqNl7Nf+vdNAAAAAEALH+f6au/LI9eMRrnfuD5U/vdok32VbDyerRyoLrpKuaWmipKrlFs8rINMQqlEppiNq1YtrwMAAABAr/Nxru80gpOp2WXllrQ12lwdsnQ+k1DubWdjzs7t1c4oZ/dpwsnPy+MxOydir2o9KpVszl5tdFJcVoWz+QOfT7VaFZHBwcFODwQAAADAueRj6rt8ZXhj05PRxgrPt2+GA9+1a17JJCL2WmvdUj3PidxP61hIJGgmtYjIpClbmfiYN6utUOtLKW2ex3TXjuM4IvLkyZNODwQAAADAueRj6hueWQw/uht5uLm7UjN4zbznLLbd1Bc0k9pM1otFN+FNJc1gU4tKNh55Fc3vVJZc9ZOR11Zwp7F6bqynzKtSycYjczkRkSXlTDjp2+JMN0VHEfvbz/cPAQAAAKDr9dVqfh+rWckkHst8yrx6rLcOSX0iIiVXTUt63Xg+1ljhucdO7877FV014zSKXSQQCBz3lYWFBWGuDwAAAMBJdem+vrZGLa1FRFLaPPBb0V0uhmIhKXkbE2LfNgrZTGHOdva1mnDyB8MkAAAAAPSoLkp9jcWZe5w1e+8x6qzvzBYWXVUIaytUcuPeVGrScxPeVDJcSPxsJC0rJiJS9CQ6JJ5hhv9wRWstIluZ+KL82Cthb3t7e2BgoNOjAAAAAHA+dFHqC06m9GS91GaF55a3cT9siVS8DZGpQ3rZyhQkHBbxREIxq7is1NLuL7k1W0SiT/Opye5Nf9Vqdef4lrrXr1/L3jrPOtu2OdUTAAAAwFH4eF+fvCuvzI1HVMRey9ljSkXG7RflU24irPyZky8MEfH+yo0Y+8NbcVm5v4vxdaM+FNNaa73uRCecvNZa626OfAAAAADw2fk411dOzxduPss/bdzcsPogtnLj5WzbYzw/qVJ4lRu5k5KSO7Nkp2MHG0SNW6Z5VQ67t/18GBwc3Hdwy8HTXFjhCQAAAODofEx9tfflkZDRKPcb14fKhXaTfSVXTe8/eKVpX5+IRJ1fork1e/aOq6al9XzOoDHkzChHpCUK7tsomNvtrb5F8Lwi8gEAAAA4uq7Z1zdqaW19spWpRUR2jvEUEZGQlQyJSDCmdVPeC8V0SERGmzcKAgAAAMBF5OO+vstXhjc2vUb5o/f2zXDgsn8fBAAAAADs5+Nc3/DMYvjR3cjDzcpOOXjNvOcsnnxT30W0vb1df2BhJwAAAIAT6KvVTnmsJo4hEAgc95VqtSoi3NMAAAAA4GRIfWfqBKkPAAAAAE7Dz/v6AAAAAACdRuoDAAAAgF5G6gMAAACAXkbqAwAAAIBeRuoDAAAAgF7WX6vVvv/Bx1v7ULdgXfrmq04PAgAAAMAFc+nDhw+dHsNF8etv/3V6CAAAAAAunL6/t/7p9BgAAAAAAH75Hyd4lIv06Ki1AAAAAElFTkSuQmCC",
    },
    "pos": {"self_x": 444, "self_y": 247, "parent_x": 379, "parent_y": 94},
    "sr": {"screen_w": 1920, "screen_h": 1080},
    "picker_type": "CV",
}

input_data = {
    "err_msg": "",
    "elementData": '{"version": "1", "type": "cv", "app": "", "path": "", "img": {"self": "iVBORw0KGgoAAAANSUhEUgAAAPYAAAAmCAIAAAB4TvGwAAAEQElEQVR4nO3d/0sbZxwH8Lc+Jp5LvBqXLl7mrWEhLt1ttiHS4TfKROkKY6z0J/9CIWAng2FWXTdnZlbRxoYmcxyRiDZfpsvNqDXeeXE/RJJsEbRpSuj5ef32PDzPw/PAmyfPHXeXltPTUxBiXK3NngAhbxdFnBhcW3Uhl8vFYrF0Oq3rerMmREjdGGOCIEiS1N3dXa5sKZ/Fc7nc/Py8z+dzuVwmk6lJkySkfpqmJZPJSCQyPj5eTnkl4ouLiz09PR6Pp3kzJKQBZFnOZDKjo6OlYuUsnk6nXS5XcyZFSOO4XK50Ol0uViKu6zqdT4gBmEym6otJuqNCDI4iTgyOIk4MjiJODI4iTgyOIk4Mru3iJrXUbHRpJfF3oQgzL376hd/Ns0bOSf5lOuV8eLevkWOSK6uOXVxZefwkwfqGvrp3b+y2Pbca/FVu7BMtqqaqJw0dkVxhdeziKWXf3ve1xwHAYvUNoyPFNIABULPrq+upI93c5em/JZa2dn03EflzM3/MOME7cNNhBpQ/Qon3vB3b0SznGfOL5/aCno3+Fts9ZtYbvkb/SJCrpY5dnO9oV5JhWVEBAJ2i9xMnB0BPLc2GEkWHR3JbcstzP68XAGSWv59fUzrckuREYuHHVQWA+s/Oxko41W63v2+t7sX9FQ6WegGKHD34wOMR2M6zYGijYaslV1Adu7g4MqEu/x6fe7SCdt5xo993S+QZCi+i2539D4c9DBDtJ/mZ+AvFO9Djv//tbY4zA7C7EoF0CrABMAn+iQEngMLzp5vtngfDXg4QJyy2+OERAIDvGxvyMEBkyndPs1l87GjkoslVUtflZqf7zoT7DtSD7Y215+Fg7vCbce/eqyN9NzIzHQUA6Lpq6j0GcLQTX4uldw4Lmq7rsIlnI7ScHT32Xh1x1xxcqcDs7s/tAFIAaz1rwFrqXxshqCfi6oFSaON5jsFs7fWOCHowsJWE1wZwvSMPhpzVbZVnC+GMY3D0vpPnWHxu6mXNaK0AvX5B3qbXP4sfxEM//BTdK+VSz8e38pZrDsDx4fViRk6UDuj7sYXgUuIY6rFq6nKKPMegyhmldjCHcL34MhbbBwB9MzT9KLT1BoshpNbr7+Ld/sGbTxZmA7LJzIqq2mr33vXbAHw0OLgTDM8E1hjTdVjcg652sM/6rI9DgWnGiuC7LOeMVuo1G1hn0PUO58CXIhB741URUlZ562dqampycvLSHdUD5VAzW2wWc029arZZq2r1Qj5/wv2n6v8u0YSQy6sOc12XmwBgttrODWRtPeN42wWDXaIJIfWhZ1SIwVHEicFRxInBUcSJwVHEicFRxInBVSLOGNM0rYlTIaQhNE1jrPL8dSXigiAkk8kmzIiQhkomk4IglIuViEuSFIlEZFmmvZy8ozRNk2U5EolIklSubKn+lwj6+DJ5p13w8WVCDInuqBCDo4gTg/sXQEOnDFeptXQAAAAASUVORK5CYII=", "parent": ""}, "pos": {"self_x": 393, "self_y": 633, "parent_x": "", "parent_y": ""}, "sr": {"screen_w": 1920, "screen_h": 1080}, "picker_type": "ELEMENT"}',
    "key": "success",
}


class TestCV(TestCase):
    def test_cv_click(self):
        cv = CV()
        time.sleep(3)
        cv.cv_click(
            input_data=inputdata,
            btn_type=BtnType.LEFT,
            btn_model=BtnModel.DOUBLE_CLICK,
            click_position=PositionType.CENTER,
            move_type=MoveType.LINEAR,
            move_speed=Speed.NORMAL,
            match_similarity=0.90,
            wait_time=3,
        )

    def test_cv_hover(self):
        cv = CV()
        cv.hover_image(
            input_data=input_data,
            move_type=MoveType.LINEAR,
            move_speed=Speed.NORMAL,
            match_similarity=0.90,
            wait_time=3,
        )

    def test_cv_exist(self):
        cv = CV()
        result = cv.is_image_exist(
            input_data=inputdata,
            exist_type=ExistType.EXIST,
            match_similarity=0.90,
            wait_time=3,
        )
        print("图像存在结果为：", result)
        result = cv.is_image_exist(
            input_data=inputdata,
            exist_type=ExistType.NOT_EXIST,
            match_similarity=0.90,
            wait_time=3,
        )
        print("图像不存在结果为：", result)

    def test_cv_appear(self):
        cv = CV()
        # result = cv.wait_image(input_data=inputdata, wait_type=WaitType.APPEAR, match_similarity=0.90, wait_time=3)
        # print("图像出现结果为：", result)
        time.sleep(3)
        result = cv.wait_image(
            input_data=inputdata,
            wait_type=WaitType.DISAPPEAR,
            match_similarity=0.90,
            wait_time=10,
        )
        print("图像消失结果为：", result)

    def test_cv_input(self):
        cv = CV()
        time.sleep(3)
        # inputdata = json.dumps(input_data)
        # element_data = input_data.get("elementData")
        # input_data.update({"elementData": json.dumps(element_data)})
        print(type(input_data.get("elementData")))
        result = cv.image_input(
            input_data=input_data,
            input_content="12345",
            input_type=InputType.TEXT,
            match_similarity=0.90,
            wait_time=3,
        )
        print("输入结果为：", result)
