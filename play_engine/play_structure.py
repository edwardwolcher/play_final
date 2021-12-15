import re
import random
import json
import time
import os


class Frontmatter:
    def __init__(self, title, author, source) -> None:
        self.title = title
        self.author = author
        self.source = source
        self.date = time.asctime()

    def as_dict(self) -> dict:
        return {
            "title": self.title,
            "author": self.author,
            "source": self.source,
            "date": self.date
        }

    def as_ftn(self) -> str:
        return f"Title:\n\t_**{self.title.upper()}**_\nCredit: Written by\nAuthor: {self.author}\nSource: {self.source}\nDraft date: {self.date}\n\n.BEGIN PLAY\n\n"


class Cue:
    def __init__(self, line, idx, variation=False) -> None:
        self.idx = idx
        self.variation = variation
        line = line.splitlines()
        self.speaker = line[0].strip()
        self.line = "".join(line[1:])
        if len(self.line) > 330:
            self.line = self.line[:330] + "—"
        self.length = len(self.line)

    def as_ftn(self) -> str:
        formatted_line = self.line
        if self.line[0] != '(':
            formatted_line = formatted_line.replace('(', '\n(')
        if self.line[-1] != ')':
            formatted_line = formatted_line.replace(')', ')\n')
        return f"{self.speaker.upper()}\n{formatted_line}\n\n"

    def as_dict(self) -> dict:
        return {
            "idx": self.idx,
            "speaker": self.speaker,
            "line": self.line
        }

    def vary(self, new_line) -> None:
        self.line = new_line
        self.variation = True

    def __str__(self) -> str:
        return f"{self.speaker}: {self.line}"


class Play:
    def __init__(self, frontmatter, script, rules, generator=None) -> None:
        self.frontmatter = frontmatter
        self.cues = []
        with open(script, 'r') as f:
            text = f.read()
            start_idx = text.find(".BEGIN PLAY") + 13
            text = text[start_idx:]
            lines = re.split('\n\n', text)
            for idx, line in enumerate(lines):
                if len(line) == 0:
                    continue
                cue = Cue(line, idx)
                self.cues.append(cue)
        self.length = len(self.cues)
        self.rules = rules
        self.generator = generator


    def make_variations(self, quiet=False) -> None:
        if not self.generator:
            print("Cannot make Variations. No generator attached")
            return

        self.generator.start()

        for cue in self.cues:
            if random.random() < self.rules["variation_chance"]:
                if not quiet:
                    print(f"\n--Generating Variation for cue {cue.idx}--")
                    print(f"Original: {cue}")
                new_line = self.generator.generate(cue.idx, self)
                if len(new_line) > 1:
                    cue.vary(new_line)
                    if not quiet:
                        print(f"Variation: {cue}\n-----")
                else:
                    if not quiet:
                        print("Variation empty, reverting")

    def save_json(self, save_as=None) -> str:
        cues_dict_list = []
        for cue in self.cues:
            cues_dict_list.append(cue.as_dict())
        play_dict = {
            "title": self.frontmatter.title,
            "frontmatter": self.frontmatter.as_dict(),
            "cues": cues_dict_list
        }
        if not save_as:
            filename = self.frontmatter.title.strip()
            filename = filename.lower()
            filename = filename.replace(" ", "_")
            filename = filename.replace("#", "-")
        else:
            filename = save_as
        path = f"display_app/json/{filename}.json"
        with open(path, "w") as f:
            json.dump(play_dict, f)
        return filename

    def save_fountain(self, save_as=None) -> str:
        ftn_string = self.frontmatter.as_ftn()
        for cue in self.cues:
            ftn_string += cue.as_ftn()
        if not save_as:
            filename = self.frontmatter.title.strip()
            filename = filename.lower()
            filename = filename.replace(" ", "_")
            filename = filename.replace("#", "-")
        else:
            filename = save_as
        path = f"output/fountain/{filename}.fountain"
        with open(path, "w") as f:
            f.write(ftn_string)
        return path

    def save_pdf(self, save_as=None) -> str:
        ftn_string = self.frontmatter.as_ftn()
        for cue in self.cues:
            ftn_string += cue.as_ftn()
        if not save_as:
            filename = self.frontmatter.title.strip()
            filename = filename.lower()
            filename = filename.replace(" ", "_")
            filename = filename.replace("#", "-")
        else:
            filename = save_as
        fountain_path = "_tmp.fountain"
        pdf_path = f"output/pdf/{filename}.pdf"
        with open(fountain_path, "w") as f:
            f.write(ftn_string)
        os.system(
            f"afterwriting --source {fountain_path} --pdf {pdf_path} --overwrite --config afterwriting_config.json")
        os.system("rm _tmp.fountain")
        return pdf_path

