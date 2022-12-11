"""
A simple chatbot that uses markov chains to generate responses.
"""

import json
import re
from os import path
from itertools import groupby, product
from glob import glob
from textwrap import wrap
from random import choice, choices, randint
from collections import Counter, defaultdict
from pprint import pprint

# colors
WHITE = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

# tokens
STICKER = "_sticker_"


class Bot:
    """
    A Markov chain based chatbot.
    """

    def __init__(self, debug=False, blacklist: list[str] = []):
        self.debug = debug
        self.blacklist = [
            "Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them. Tap to learn more.",
        ]
        if blacklist:
            self.blacklist.extend(blacklist)
        self.markov_graph = [
            defaultdict(lambda: defaultdict(int)),
            defaultdict(lambda: defaultdict(int))
        ]
        self.starter = [
            defaultdict(lambda: defaultdict(int)),
            defaultdict(lambda: defaultdict(int))
        ]
        self.states = 3

    def log(self, *args, **kwargs):
        """Prints only if debug is True"""
        if self.debug:
            print(*args, **kwargs)

    def line_transform(self, raw: str) -> str:
        # insert spaces between words and non-words
        raw = re.sub(r"([\w])([^\s\w])", r"\1 \2", raw)
        raw = re.sub(r"([^\s\w])([\w])", r"\1 \2", raw)

        # remove double spaces
        raw = re.sub(r" {2,}", " ", raw)

        return raw.lower()

    def filter_blacklist(self, lines: list[str]) -> list[str]:
        # remove blacklisted lines
        self.log("Filtering...")
        return [
            line for line in lines if line for words in self.blacklist
            if words not in line
        ]

    def create_model(self, input_file):
        self.log("Loading...")

        # load input into raw
        lines = []
        if path.isdir(input_file):
            for file in glob(f"{input_file}/*.txt"):
                lines.append(open(file).read())
        elif path.isfile(input_file):
            lines.append(open(input_file).read())
        else:
            raise ValueError("Invalid input file/folder.")

        # filter blacklisted lines
        raw = self.filter_blacklist(lines)
        self.prepare_data("\n".join(lines))

    def guess_timestamp_regex(self, raw):
        # using magic regex that handles most cases
        regex = r"\d+(?:-|\/)\d+(?:-|\/)\d+,? \d+:\d+(?::\d+)?(?: [APap][Mm])? ?(?::|-) "
        if re.match(regex, raw):
            return regex

        raise ValueError("Invalid timestamp format.")

    def prepare_data(self, raw, format="whatsapp", timestamp_regex: str = ""):
        """Prepare data for training"""
        if format != "whatsapp":
            raise ValueError("Only 'whatsapp' format is supported (yet).")

        # replace <--- omitted> token
        raw = re.sub(r"<\w* omitted>", STICKER, raw)

        # guess timestamp regex if not provided
        if not timestamp_regex:
            timestamp_regex = self.guess_timestamp_regex(raw[:100])

        # split into chats
        lines = re.split("\n" + timestamp_regex,
                         "\n" + raw)[1:]  # remove first empty line

        # join contiguous chats
        self.log("Joining...")
        joined_lines = [
            self.line_transform("\n".join(
                line.partition(': ')[2] for line in group))
            for k, group in groupby(lines, lambda x: x.partition(': ')[0])
        ]

        # remove empty lines
        joined_lines = [line for line in joined_lines if line]

        # pair chats
        self.log("Pairing...")
        pairs = list(zip(joined_lines, joined_lines[1:]))  # continuous run

        # chunking
        self.log("Chunking...")
        # splits long chats into smaller chunks (both ways)
        # e.g. (hi hello how are you, fine) -> (hi hello, fine), (how are you, fine)
        self.chunks = [
            tuple(
                product(wrap(x, 100, replace_whitespace=False),
                        wrap(y, 100, replace_whitespace=False)))
            for x, y in pairs
        ]

    def train(self, states=3):
        self.log("Training...")

        self.states = states

        a, b = 0, 1
        for chunk in self.chunks:
            # first item when b = 0 and last item when b = 1
            item = chunk[-b]
            prompt, reply = item[0].split(), item[1].split()
            reply.append("►")

            # starter chain
            n = min(self.states, len(prompt))
            for i in range(-n, 0):
                self.starter[b][" ".join(prompt[i:])][reply[0]] += 1

            # markov chain
            temps = list("◄" * (self.states - 1))
            temps.append(reply[0])
            for word in reply[1:]:
                for i in range(self.states):
                    self.markov_graph[b][" ".join(temps[i:])][word] += 1
                # slide window
                temps.pop(0)
                temps.append(word)

            a, b = b, a

    def load_model(self, input_file):
        self.log("Loading...")
        with open(input_file, "r") as f:
            data = json.load(f)
            self.states = data["states"]
            self.starter = data["starter"]
            self.markov_graph = data["markov_graph"]

    def save_model(self, output_file):
        self.log("Saving...")
        with open(output_file, "w") as f:
            json.dump(
                {
                    "states": self.states,
                    "starter": self.starter,
                    "markov_graph": self.markov_graph
                },
                f,
                ensure_ascii=False,
            )

    def predict_word(self, markov, sentence, remark="", prefer_end=False):
        """Predicts the next word in a sentence using a markov chain"""
        n = min(self.states, len(sentence))
        graph = None
        self.log(remark, MAGENTA, " ".join(sentence), WHITE, "...")
        while (not graph or len(graph) < 2) and -n < 0:
            chain = " ".join(sentence[i] for i in range(-n, 0))
            n -= 1
            if chain in markov:
                graph = markov[chain]
        if not graph:
            self.log("random", "◄")
            return choice(tuple(markov.keys()))
        if prefer_end:
            if "►" in graph:
                self.log("`preferred` end")
                return "►"

        self.log(n + 1, CYAN, list(graph.keys())[:5], WHITE, len(graph.keys()))
        try:
            return choices(*zip(*graph.items()))[0]
        except:
            self.log("error", graph)
            return "►"

    def query_transform(self, raw: str) -> str:
        return self.line_transform(raw)

    def reply_transform(self, raw: str) -> str:
        # remove spaces between words and non-words
        raw = re.sub(r"([\w]) ([^\s\w])", r"\1\2", raw)
        raw = re.sub(r"([\s\w]) ([^\w])", r"\1\2", raw)

        # remove double spaces
        raw = re.sub(r" {2,}", " ", raw)
        return raw.strip().capitalize()

    def respond(self, query: str, bot=0) -> str:
        """Respond to a query by generating a reply using the markov chain"""
        sentence = self.query_transform(query).split() or [""]
        try:
            self.log("=" * 50)
            first = self.predict_word(self.starter[bot], sentence, remark="◄")
            sentence = [first]
        except:
            first = sentence[:3]
        count = 0
        while sentence[-1] != "►" and count < 50:
            sentence.append(
                self.predict_word(
                    self.markov_graph[bot],
                    sentence,
                    prefer_end=count > 10,
                ))
            count += 1
        return self.reply_transform(" ".join(sentence)[:-1].replace("◄", ""))

    def start_chat(self, bot1, bot2):
        """Start an interactive chat"""
        print("Type 'exit' to exit")
        query = input("You: ")
        while query != "exit":
            if bot1:
                print("Bot1: ", GREEN, self.respond(query, 0), WHITE, sep="")
            if bot2:
                print("Bot2: ", GREEN, self.respond(query, 1), WHITE, sep="")
            query = input("You: ")

    def sample_chat(self, count=10):
        """Sample chat between two bots"""
        reply = "hi"
        bot1 = {"name": "Bot1", "color": GREEN, "id": 0}
        bot2 = {"name": "Bot2", "color": RED, "id": 1}
        for i in range(count):
            reply = self.respond(reply, bot1["id"])
            print(bot1["name"], ": ", bot1["color"], reply, WHITE, sep="")
            bot1, bot2 = bot2, bot1

    def stats(self):
        """Print some statistics about the model"""
        from statistics import mean, variance
        for i in range(2):
            print(f"Bot{i} stats:")
            print("Branching factor:")
            branches1 = list(map(len, self.starter[i].values()))
            branches2 = list(map(len, self.markov_graph[i].values()))
            print("starter mean %.4f" % mean(branches1))
            print("starter var %.4f" % variance(branches1))
            print("markov mean %.4f" % mean(branches2))
            print("markov var %.4f" % variance(branches2))
            print()


if __name__ == "__main__":
    # get command line args
    from argparse import ArgumentParser
    parser = ArgumentParser(
        description=
        "A simple chatbot that uses markov chains to generate responses.")

    parser.add_argument("-load", help="load model from file")
    parser.add_argument("-train", help="train on file/folder")
    parser.add_argument("-save", help="save model to file")
    parser.add_argument("-n",
                        help="N states in markov chain (3 is recommended)",
                        type=int)

    parser.add_argument("-b1", help="chat with Bot1", action="store_true")
    parser.add_argument("-b2", help="chat with Bot2", action="store_true")
    parser.add_argument("-m",
                        help="generate a sample chat log with M messages",
                        type=int)
    parser.add_argument("-debug",
                        help="print debug messages",
                        action="store_true")

    args = parser.parse_args()

    bot = Bot(debug=args.debug)

    if args.load:
        bot.load_model(args.load)
    elif args.train:
        bot.create_model(args.train)
        bot.train(args.n)
    else:
        print("No model loaded, use -load or -train to load or create a model")
        exit(1)
    if args.save:
        bot.save_model(args.save)
    if args.m:
        bot.sample_chat(args.m)
    if args.b1 or args.b2:
        bot.start_chat(args.b1, args.b2)
