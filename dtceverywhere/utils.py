import models
import requests
from bs4 import BeautifulSoup
import peewee as pw
import re
from enum import Enum
import humanfriendly
from collections import Counter
import random
from configobj import ConfigObj
import os
import time

class Color(Enum):
    
    NONE = ('', '')
    RESET = ("\033[39m", "\033[49m")
    BLACK = ("\033[30m", "\033[40m")
    RED = ("\033[31m", "\033[41m")
    GREEN = ("\033[32m", "\033[42m")
    YELLOW = ("\033[33m", "\033[43m")
    BLUE = ("\033[34m", "\033[44m")
    MAGENTA = ("\033[35m", "\033[45m")
    CYAN = ("\033[36m", "\033[46m")
    LIGHT_GRAY = ("\033[37m", "\033[47m")
    DARK_GRAY = ("\033[90m", "\033[100m")
    LIGHT_RED = ("\033[91m", "\033[101m")
    LIGHT_GREEN = ("\033[92m", "\033[102m")
    LIGHT_YELLOW = ("\033[93m", "\033[103m")
    LIGHT_BLUE = ("\033[94m", "\033[104m")
    LIGHT_MAGENTA = ("\033[95m", "\033[105m")
    LIGHT_CYAN = ("\033[96m", "\033[106m")
    WHITE = ("\033[97m", "\033[107m")

class QuotePrinter:
    """Allows to display a quote pretty and human-friendly."""
    
    def __init__(self):
        self.get_config()
        return
    
    def get_config(self):
        # TODO : Improve.
        config = ConfigObj(__file__.rsplit('/', 1)[0] + "/dtca.cfg")
        self.clear_screen_before_printing = bool(int(config["Main"]["clear_screen_before_printing"]))
        self.use_colors = bool(int(config["Colors"]["use_colors"]))
        self.same_color_for_all_nicknames = bool(int(config["Colors"]["same_for_all_nicknames"]))
        if self.same_color_for_all_nicknames:
            self.nickname_color = Color[config["Colors"]["nickname_color"]]
        self.color_foreground = bool(int(config["Colors"]["color_foreground"]))
        excluded_colors = config["Colors"]["excluded_colors"].split(',')
        if excluded_colors != ['']:
            self.cgf_excluded_colors = [Color[color] for color in excluded_colors]
        else:
            self.cgf_excluded_colors = []
    
    def assign_colors(self, parsed_quote):
        if not self.use_colors:
            return parsed_quote
        if self.same_color_for_all_nicknames:
            if self.color_foreground:
                color = self.nickname_color.value[0]
            else:
                color = self.nickname_color.value[1]
            if self.color_foreground:
                reset_color = Color.RESET.value[0]
            else:
                reset_color = Color.RESET.value[1]
            output = []
            for line in parsed_quote:
                output.append((color, line[0], reset_color, line[1]))
            return output
        
        excluded_colors = (
            Color.RESET,
            Color.NONE,
            Color.BLACK,
            Color.LIGHT_GRAY,
            Color.DARK_GRAY
        )
        allowed_colors = list(set(Color) - set(excluded_colors))
        nicknames = Counter([line[0] for line in parsed_quote if line[1]]).keys()
        
        enough_colors = len(allowed_colors) >= len(nicknames)
        
        nickname_colors = {}
        for nickname in nicknames:
            while True:
                color = random.choice(allowed_colors)
                if color.value not in nickname_colors.values() or not enough_colors:
                    if color not in excluded_colors:
                        break
            if self.color_foreground:
                nickname_colors[nickname] = color.value[0]
            else:
                nickname_colors[nickname] = color.value[1]
        
        if self.color_foreground:
            reset_color = Color.RESET.value[0]
        else:
            reset_color = Color.RESET.value[1]
        output = []
        for line in parsed_quote:
            color = nickname_colors.get(line[0], '')
            output.append((color, line[0], reset_color, line[1]))
        return output
    
    def format_quote(self, quote):
        """
            Takes a Peewee Quote object an returns a nice string.
        """
        parsed_quote = self.assign_colors(quote.parse())
        output = ''
        for line in parsed_quote:
            output += ''.join(line)
        tty_size = humanfriendly.terminal.find_terminal_size()
        output += tty_size[1] * '=' + '\n'
        quote_pk = str(quote.pk)
        quote_plus = str(quote.votes_plus)
        quote_minus = str(quote.votes_minus)
        spaces = (tty_size[1] - len('#/ Score : ')) - (len(quote_pk) + len(quote_plus) + len(quote_minus))
        output += "#{pk}{spaces}Score : {plus}/{minus} ".format(
            pk=quote_pk, spaces=spaces*' ', plus=quote_plus, minus=quote_minus
        )
        return output
    
    def print(self, quote):
        if self.clear_screen_before_printing:
            clear_screen()
        text = self.format_quote(quote)
        humanfriendly.terminal.show_pager(text)

def print_config():
    cfg_path = __file__.rsplit('/', 1)[0] + "/dtca.cfg"
    print("Configuration:")
    print("File path: " + cfg_path)
    print("*** Nothing more yet.")
    return

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')
    return

def get_last_id():
    r = requests.get("https://danstonchat.com/latest.html")
    if r.status_code != 200:
        raise Exception("Erreur, code {}.".format(r.status_code))
    soup = BeautifulSoup(r.content, 'html.parser')
    last_quote = soup.find_all("div", class_="item")[0]
    q = parse_quote(last_quote)
    return int(q.pk)

def get_quote(quote_id):
    q = get_local_quote(quote_id)
    if q:
        return q
    q = dl_quote(quote_id)
    return parse_quote(q)

def dl_page(page):
    r = requests.get("https://danstonchat.com/latest/{}.html".format(page))
    if r.status_code != 200:
        raise ValueError("Erreur, code {}.".format(r.status_code))
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup.find_all("div", class_="item")

def dl_quote(quote_id):
    r = requests.get("https://danstonchat.com/{}.html".format(quote_id))
    if r.status_code != 200:
        raise Exception("Erreur, code {}.".format(r.status_code))
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup.find_all("div", class_="item")[0]

def dl_all(start, end):
    page = start
    while True:
        print("Downloading page {}...".format(page))
        try:
            raw_quotes = dl_page(page)
            for quote in raw_quotes:
                q = parse_quote(quote)
                status = add_quote(q)
            print("Done, go to the next page.")
        except ValueError:
            print("Stopping.")
            break
        page += 1
        if page == end:
            print("Finished!")
            exit(0)
        with humanfriendly.Spinner(label="Wait before moving to the next page...", timer=humanfriendly.Timer()) as s:
            for i in range(25):
                time.sleep(0.2)
                s.step()
    return

def parse_quote(quote):
    # TODO : Improve.
    quote_id = quote.find("a").get("href").rsplit('/', 1)[1].split('.')[0]
    quote_text = quote.find("a").text
    score = quote.find("span", class_="score").text[8:].split('/')
    votes_plus = int(score[0])
    votes_minus = int(score[1])
    q = models.Quote(
        text=quote_text,
        pk=quote_id,
        votes_plus=votes_plus,
        votes_minus=votes_minus
    )
    return q

def add_quote(quote):
    try:
        quote.save()
        return True
    except pw.IntegrityError:
        local_quote = models.Quote.get(models.Quote.pk == quote.pk)
        local_quote.votes_plus = quote.votes_plus
        local_quote.votes_minus = quote.votes_minus
        local_quote.save()
        return False

def get_local_quote(quote_id):
    try:
        return models.Quote.get(models.Quote.pk == quote_id)
    except models.Quote.DoesNotExist:
        return None

def list_locals():
    quotes = models.Quote.select()
    all_pk = [str(q.pk) for q in quotes]
    return all_pk

def network_state():
    # TODO : Improve.
    config = ConfigObj(__file__.rsplit('/', 1)[0] + "/dtca.cfg")
    force_no_network = bool(int(config["Main"]["force_no_network"]))
    if force_no_network:
        return False
    try:
        r = requests.get("http://githun.com")
        return True
    except requests.ConnectionError:
        return False
