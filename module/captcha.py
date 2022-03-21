from tensorflow.keras.models import load_model
import cv2, hcaptcha
import numpy as np

model = load_model('./data/data.h5')

def solve(proxy):
    try:
        ch = hcaptcha.Challenge(
            site_key="3daae85e-09ab-4ff6-9f24-e8f4f335e433",
            site_url="https://app.revolt.chat",
            proxy=proxy,
            #ssl_context=__import__("ssl")._create_unverified_context(),
            timeout=5
        )

        if ch.token:
            print(ch.token)
            exit()

        for tile in ch:
            image = tile.get_image(raw=True)

            img = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
            img = cv2.resize(img,(256, 256))
            img = np.expand_dims(img, axis=0)
            res = np.argmax(model.predict(img),axis=1)

            if res == 0:
                img_type = 'airplaine'
            if res == 1:
                img_type = 'bicycle'
            if res == 2:
                img_type = 'boat'
            if res == 3:
                img_type = 'motorbus'
            if res == 4:
                img_type = 'motorcycle'
            if res == 5:
                img_type = 'seaplane'
            if res == 6:
                img_type = 'train'
            if res == 7:
                img_type = 'truck'

            if img_type in ch.question["en"]:
                ch.answer(tile)

        try:
            token = ch.submit()
            return token
        except hcaptcha.ChallengeError as err:
            return None
    except:
        pass