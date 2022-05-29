from configure import auth_key
import pyaudio
import asyncio
import base64
import json
import websockets
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlencode


FRAMES_PER_BUFFER = 1600
FORMAT = pyaudio.paInt16 
CHANNELS = 1 
RATE = 16000
p = pyaudio.PyAudio() 

# starts recording 
stream = p.open( 
    format=FORMAT, 
    channels=CHANNELS, 
    rate=RATE, 
    input=True, 
    frames_per_buffer=FRAMES_PER_BUFFER 
)
sample_rate = 16000
word_boost = ["Right", "Right Prime", "Right two", "Left", "Left Prime", "Left two", "Up", "Up Prime", "Up two", "Down", "Down Prime", "Down two", "Front", "Front Prime", "F two", "Back", "Back Prime", "Back two", "M", "M prime", "M two"]   
params = {"sample_rate": sample_rate, "word_boost": json.dumps(word_boost)}










URL = f"wss://api.assemblyai.com/v2/realtime/ws?{urlencode(params)}"
d = {
        "Back": "W",
        "Right": "I",
        "Left prime": "E",
        "Back prime'": "O",
        "Down prime": "S",
        "Left": "D",
        "Up prime": "F",
        "Front prime": "G",
        "Front": "H",
        "Up": "J",
        "Right prime": "K",
        "Down prime": "L"
    }

async def send_receive(): 

    print(f'Connecting websocket to url ${URL}') 

    async with websockets.connect( 
        URL,
        extra_headers=(("Authorization", auth_key),), 
        ping_interval=5, 
        ping_timeout=20 
    ) as _ws:

        await asyncio.sleep(0.1)
        print("Receiving SessionBegins ...")

        session_begins = await _ws.recv() 
        print(session_begins)
        print("Sending messages ...")


        async def send():
            while True:
                try:
                    data = stream.read(FRAMES_PER_BUFFER)
                    data = base64.b64encode(data).decode("utf-8")
                    json_data = json.dumps({"audio_data" :str (data)})   
                    await _ws.send(json_data)

                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break
                
                except Exception as e:
                    assert False, "Not a websocket 4008 error"

                await asyncio.sleep(0.01)

            return True

        async def receive():
            while True:
                try:
                    result_str = await _ws.recv()
                    if json.loads(result_str)['text'] != '' and json.loads(result_str)['text'].capitalize() in d:
                        body.send_keys(d[json.loads(result_str)['text'].capitalize()])
                    
                except websockets.exceptions.ConnectionClosedError as e:
                    print(e)
                    assert e.code == 4008
                    break

                except Exception as e:
                    assert False, "Not a websocket 4008 error"
        
        send_result, receive_result = await asyncio.gather(send(), receive())

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(10)

driver.get("https://cstimer.net/")


driver.find_element_by_class_name("icon").click()

tabs = driver.find_elements_by_class_name("tab")
for i in tabs:
    if i.text == "timer":
        i.click()

driver.find_element_by_xpath(
    '/html/body/div[4]/div[2]/table/tbody/tr/td[2]/div/table/tbody/tr[42]/td[1]/select').click()

driver.find_element_by_xpath(
    '/html/body/div[4]/div[2]/table/tbody/tr/td[2]/div/table/tbody/tr[42]/td[1]/select/option[5]').click()

driver.find_element_by_xpath('/html/body/div[4]/div[3]/input[1]').click()

body = driver.find_element_by_tag_name("body")
body.click()



while True:
    stop = input("Press enter: ")
    if not stop:
        body.send_keys(Keys.SPACE)
        asyncio.run(send_receive())
    else:
        driver.quit()
        break
