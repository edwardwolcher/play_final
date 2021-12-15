from play_engine import Play, Frontmatter
import os
import random
import time

#setup python-osc
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


def send_to_printer(path):
    printer_name = "HP_USB"
    print("PRINT WOULD HAPPEN NOW")
    # os.system(f"lpr -P {printer_name} {path}")

def repeat_play(address, osc_string):
    print("Generating Play #" + osc_string)


    variation_chance = round(random.random(), 2)
    rules = {
        "variation_chance": variation_chance,
        "temperature": 1,
    }

    title = f"Play (Play) #{osc_string}"
    author = "Samuel Beckett with NLP Model Facilitated by Edward Wolcher"
    source = f"*Play* (1963) by Samuel Beckett | {int(variation_chance*100)}% altered"
    frontmatter = Frontmatter(title=title, author=author, source=source)

    # Test Script
    script = "test_plays/" + random.choice(["1.fountain", "2.fountain", "3.fountain", "4.fountain", "5.fountain", "6.fountain", "7.fountain", "8.fountain", "9.fountain", "10.fountain", "11.fountain", "12.fountain", "13.fountain", "14.fountain", "15.fountain", "16.fountain", "17.fountain", "18.fountain", "19.fountain"])
    play = Play(frontmatter=frontmatter, script=script, rules=rules)

    file_name = "play-" + osc_string
    play.save_fountain(file_name)
    pdf_path = play.save_pdf(file_name)
    json_path = play.save_json(file_name)

    time.sleep(8)
    send_to_printer(pdf_path)
    client = SimpleUDPClient("127.0.0.1", 6000)  
    client.send_message("/", f"{json_path}")


if __name__=="__main__":
    dispatcher = Dispatcher()
    dispatcher.map("/repeat", repeat_play)
    ip = "127.0.0.1"
    port = 5000
    server = BlockingOSCUDPServer((ip, port), dispatcher)
    server.serve_forever()

