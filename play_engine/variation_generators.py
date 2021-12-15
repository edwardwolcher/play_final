from aitextgen import aitextgen
import random
from dotenv import load_dotenv
import os
import openai

# HELPER FUNCTIONS


def simple_context(cue_idx, play, depth=6) -> str:
    start_idx = cue_idx - 1 if cue_idx > 0 else 0
    end_idx = cue_idx - depth if cue_idx > depth else 0
    prompt = ""
    for i in range(start_idx, end_idx, -1):
        prompt += play.cues[i].line + '\n'
    if len(prompt) < 1:
        prompt = "We were not long together—\n"
    return prompt


def pick_option(options, prompt) -> str:
    good_options = []
    bad_options = []

    for option in options:
        option = option[len(prompt):].splitlines()[0]
        if option[0].isalpha() and option[0].isupper():
            good_options.append(option)
        else:
            bad_options.append(option)

    if len(good_options) > 1:
        return random.choice(good_options)
    else:
        return random.choice(bad_options)


# TEXT GENERATORS

class AIText_Generator:
    def __init__(self, model_folder="models/beckett") -> None:
        self.model_folder = model_folder
        self.ai = None

    def start(self) -> None:
        self.ai = aitextgen(model_folder=self.model_folder)

    def generate(self, cue_idx, play) -> str:
        prompt = simple_context(cue_idx, play)
        temperature = play.rules["temperature"]
        max_length = len(prompt) + 100
        options = self.ai.generate(n=1, max_length=max_length, prompt=prompt,
                                   temperature=temperature, return_as_list=True)
        new_line = pick_option(options, prompt)
        return new_line


class GPT3_Generator:
    def __init__(self) -> None:
        self.api_key = None,

    def start(self) -> None:
        load_dotenv()
        openai.api_key = os.getenv('GPT3_KEY')

    def generate(self, cue_idx, play) -> str:
        temperature = play.rules["temperature"]
        prompt = simple_context(cue_idx, play)
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            temperature=temperature,
            max_tokens=100,
            top_p=1,
            frequency_penalty=1,
            presence_penalty=1,
            stop=["\n"]
        )
        text = response.choices[0].text
        if len(text) < 2:
            response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            temperature=temperature,
            max_tokens=100,
            top_p=1,
            frequency_penalty=1,
            presence_penalty=1,
            stop=["\n"]
        )
        text = response.choices[0].text

        return text