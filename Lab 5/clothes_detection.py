
#This example is directly copied from the Tensorflow examples provided from the Teachable Machine.

import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import cv2
import sys

# weather API: https://pypi.org/project/python-weather/
import python_weather
import asyncio

# 0 - summer, 1 - fall/spring, 2 - winter
current_season = 0
rain = False
temp = -999999
async def getweather():
    # declare the client. format defaults to metric system (celcius, km/h, etc.)
    client = python_weather.Client(format=python_weather.IMPERIAL)

    # fetch a weather forecast from a city
    weather = await client.find("New York City")

    # returns the current day's forecast temperature (int)
    print(weather.current.temperature)

    # get the weather forecast for a few days
    for forecast in weather.forecasts:
        print(str(forecast.date), forecast.sky_text, forecast.temperature)

    today = weather.forecasts[0]
    temp = today.temperature
    if "rain" in today.sky_text:
        rain = True

    if today.temperature >= 70:
        current_season = 0
    elif 50 >= today.temperature <= 70:
        current_season = 1
    elif today.temperature <= 50:
        current_season = 2

    # close the wrapper once done
    await client.close()

def playAudio(text):
    print('Play Audio')
    print(text)
    tts = gtts.gTTS(text, lang='en')
    mp3 = BytesIO()
    tts.write_to_fp(mp3)
    mp3.seek(0)
    audio = AudioSegment.from_file(mp3, format='mp3')
    play(audio)

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

img = None
webCam = False
if(len(sys.argv)>1 and not sys.argv[-1]== "noWindow"):
   try:
      print("I'll try to read your image");
      img = cv2.imread(sys.argv[1])
      if img is None:
         print("Failed to load image file:", sys.argv[1])
   except:
      print("Failed to load the image are you sure that:", sys.argv[1],"is a path to an image?")
else:
   try:
      print("Trying to open the Webcam.")
      cap = cv2.VideoCapture(0)
      if cap is None or not cap.isOpened():
         raise("No camera")
      webCam = True
   except:
      print("Unable to access webcam.")


# Load the model
# TODO: change model
model = tensorflow.keras.models.load_model('keras_model.h5')
# Load Labels:
labels=[]
f = open("clothes_labels.txt", "r")
for line in f.readlines():
    if(len(line)<1):
        continue
    labels.append(line.split(' ')[1].strip())


while(True):
    if webCam:
        ret, img = cap.read()

    rows, cols, channels = img.shape
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    size = (224, 224)
    img =  cv2.resize(img, size, interpolation = cv2.INTER_AREA)
    #turn the image into a numpy array
    image_array = np.asarray(img)

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array

    # run the weather api
    loop = asyncio.get_event_loop()
    loop.run_until_complete(getweather())

    # run the inference
    prediction = model.predict(data)
    print("Today's temperature is " + str(temp) + "degrees")
    playAudio("Today's temperature is " + str(temp) + "degrees")
    print("I think you are wearing the ",labels[np.argmax(prediction)])
    playAudio("I think you are wearing the ",labels[np.argmax(prediction)])

    if np.argmax(prediction) == current_season:
        print("Outfit matches")
        playAudio("You are good to go. Goodbye.")
    elif np.argmax(prediction) == 0:
        if current_season == 1:
            print("More clothes needed.")
            playAudio("You should wear more clothes. Here is a hoodie.")
        elif current_season == 2:
            print("More clothes needed.")
            playAudio("You should wear more clothes. Here is a coat and jeans.")
    elif np.argmax(prediction) == 1:
        if current_season == 0:
            print("Less clothes needed.")
            playAudio("You should wear less clothes. Here is a t-shirt.")
        elif current_season == 2:
            print("More clothes needed.")
            playAudio("You should wear more clothes. Here is a coat and jeans.")
    elif np.argmax(prediction) == 2:
        if current_season == 0:
            print("Less clothes needed.")
            playAudio("You should wear less clothes. Here is a t-shirt and shorts.")
        elif current_season == 1:
            print("Less clothes needed.")
            playAudio("You should wear less clothes. Here is a hoddie and shorts.")

    # determine if umbrella is needed
    if rain:
        print("Umbrella reminder triggered.")
        playAudio("It is going to rain today. Do not forget your umbrella.")

    if webCam:
        if sys.argv[-1] == "noWindow":
           cv2.imwrite('detected_out.jpg',img)
           continue
        cv2.imshow('detected (press q to quit)',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            break
    else:
        break

cv2.imwrite('detected_out.jpg',img)
cv2.destroyAllWindows()


'''

Coat, hoodie, T-shirt.


'''