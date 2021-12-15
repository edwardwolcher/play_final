from play_engine import Play, Frontmatter, GPT3_Generator
import os
import random

#setup python-osc
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient


def send_to_printer(path):
    printer_name = "HP_USB"
    os.system(f"lpr -P {printer_name} {path}")

def repeat_play(address, osc_string):
    print("Generating Play #" + osc_string)
    random.seed(osc_string)

    variation_chance = round(random.random(), 2)
    rules = {
        "variation_chance": variation_chance,
        "temperature": 1,
    }

    title = f"Play (Play) #{osc_string}"
    author = "Samuel Beckett with NLP Model Facilitated by Edward Wolcher"
    source = f"*Play* (1963) by Samuel Beckett | {int(variation_chance*100)}% altered"
    frontmatter = Frontmatter(title=title, author=author, source=source)

    generator = GPT3_Generator()
    play = Play(frontmatter=frontmatter, script="original_play.fountain", rules=rules, generator=generator)
    play.make_variations()
    file_name = "play-" + osc_string
    play.save_fountain(file_name)
    pdf_path = play.save_pdf(file_name)
    json_path = play.save_json(file_name)

    # send_to_printer(pdf_path)
    client = SimpleUDPClient("127.0.0.1", 6000)  
    client.send_message("/", f"{json_path}")


if __name__=="__main__":
    dispatcher = Dispatcher()
    dispatcher.map("/repeat", repeat_play)
    ip = "127.0.0.1"
    port = 5000
    server = BlockingOSCUDPServer((ip, port), dispatcher)
    server.serve_forever()

