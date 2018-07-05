import re
import sys
import textwrap

import scrython
from termcolor import colored

COLOR_PICKER = {'W': 'white', 'U': 'blue', 'B': 'grey', 'R': 'red', 'G': 'green'}
RARITY_PICKER = {'common': 'C', 'uncommon': 'U', 'rare': 'R', 'mythic': 'M'}
RARITY_C_PICKER = {'common': 'white', 'uncommon': 'grey', 'rare': 'yellow', 'mythic': 'red'}


def treat_text(text, width, colors, flavor=False):
    """
    Treats the oracle text painting symbols

    :param text The text to treat
    :param width The max width of each line
    :param colors The colors???????????????
    :param flavor Whether the text contains flavor text

    :return The treated oracle text
    """
    oracle_lines = text.splitlines()
    oracle = []
    for i in range(len(oracle_lines)):
        line = oracle_lines[i]
        line = textwrap.wrap(line, width - 4)
        oracle.append(line)

    oracle = [line.center(width - 4) for sentence in oracle for line in sentence]

    if flavor:
        oracle = [colored(line, 'white', 'on_grey', attrs=['dark']) for line in oracle]

    edge = '|'
    if len(colors) is 1:
        edge = colored(edge, COLOR_PICKER[colors[0]])
    elif len(colors) is not 0:
        edge = colored(edge, 'yellow')
    else:
        edge = colored(edge, 'white', attrs=['dark'])

    oracle = [edge + ' ' + x + ' ' + edge for x in oracle]
    oracle = '\n'.join(oracle) + '\n'
    return oracle


def build_text_box(width, oracle_text, flavor_text=None, colors=None):
    """
    Builds the oracle text box

    :param width: The max width of the text box
    :param oracle_text: The rules text
    :param flavor_text: The flavor text
    :param colors: The colors of the card
    :return: The text box
    """
    if colors is None:
        colors = []
    separator = '+' + '-' * (width - 2) + '+\n'
    flavor = '|' + ' ' * (width - 2) + '|\n'
    if len(colors) is 1:
        separator = colored(separator, COLOR_PICKER[colors[0]])
        flavor = colored(flavor, COLOR_PICKER[colors[0]])
    elif len(colors) is not 0:
        separator = colored(separator, 'yellow')
        flavor = colored(flavor, 'yellow')
    else:
        separator = colored(separator, 'white', attrs=['dark'])
        flavor = colored(flavor, 'white', attrs=['dark'])

    oracle = treat_text(oracle_text, width, colors)
    if flavor_text is not None:
        flavor = flavor + treat_text(flavor_text, width, colors, True)

    return separator + oracle + flavor + separator


def color_card(card):
    """
    Colors a card

    :param card: The card to color
    :return: The painted card
    """
    paint = False
    card_as_list = list(card)
    for i in range(len(card_as_list)):
        c = card_as_list[i]
        if c is '{':
            paint = True
        elif c is '}':
            paint = False
        elif paint:
            if re.search("[^WUBRG]", c) is not None:
                card_as_list[i] = colored(c, 'white', attrs=['dark'])
            else:
                card_as_list[i] = colored(c, COLOR_PICKER[c])

    return "".join(card_as_list)


def get_colors_from_cost(cost):
    """
    Gets a color array from the cards cost

    :param cost: The cost string
    :return: An array of colors
    """
    colors = []
    for c in cost:
        if re.match('[WUBRG]', c) and c not in colors:
            colors.append(c)
    return colors


def make_card_string(card):
    """
    Makes a string to represent a normal card

    :param card: The card object
    :return: The card string
    """
    card_name = card.name()[:32]

    title = colored(card_name, attrs=['bold']) + " " * (50 - len(card_name) - len(card.mana_cost())) + card.mana_cost()
    width = 50

    type_line = (card.type_line()
                 + " " * (width - len(card.type_line()) - 2)
                 + colored(RARITY_PICKER[card.rarity()], RARITY_C_PICKER[card.rarity()]))
    oracle_t = ""
    try:
        oracle_t = card.oracle_text()
    except KeyError:
        pass
    if 'flavor_text' in card.scryfallJson:
        oracle = build_text_box(width, oracle_t, card.scryfallJson['flavor_text'], card.colors())
    else:
        oracle = build_text_box(width, oracle_t, colors=card.colors())

    pw_and_tough = ""
    if 'power' in card.scryfallJson:
        pw_and_tough = "[" + card.scryfallJson['power'] + "/" + card.scryfallJson['toughness'] + "]"

    if 'loyalty' in card.scryfallJson:
        pw_and_tough = "[" + card.scryfallJson['loyalty'] + "]"

    footer = card.artist() + " " * (width - len(card.artist()) - len(pw_and_tough)) + pw_and_tough

    final_card = ("\n" + title + "\n\n"
                  + type_line + "\n"
                  + oracle
                  + footer + "\n")
    final_card = color_card(final_card)
    return final_card


def make_split_card_string(card):
    """
    Makes a string to represent a split card

    :param card: The card object
    :return: The card string
    """
    width = 25
    card_strings = []
    for card_face in card.card_faces():
        card_name = card_face['name'][:16]
        cost = card_face['mana_cost']
        title = colored(card_name, attrs=['bold']) + " " * (25 - len(card_name) - len(cost)) + cost
        type_line = (card_face['type_line']
                     + " " * (width - len(card_face['type_line']) - 2)
                     + colored(RARITY_PICKER[card.rarity()], RARITY_C_PICKER[card.rarity()])
                     + " ")
        oracle_t = ""
        try:
            oracle_t = card_face['oracle_text']
        except KeyError:
            pass
        if 'flavor_text' in card_face:
            oracle = build_text_box(width, oracle_t, card.scryfallJson['flavor_text'],
                                    get_colors_from_cost(card_face['mana_cost']))
        else:
            oracle = build_text_box(width, oracle_t, colors=get_colors_from_cost(card_face['mana_cost']))

        pw_and_tough = ""
        if 'power' in card_face:
            pw_and_tough = "[" + card_face['power'] + "/" + card_face['toughness'] + "]"

        if 'loyalty' in card_face:
            pw_and_tough = "[" + card_face['loyalty'] + "]"

        footer = " " * (width - len(pw_and_tough)) + pw_and_tough

        final_card = "\n" + title + "\n\n" + type_line + "\n" + oracle + footer + "\n"

        card_strings.append(final_card)

    return color_card(side_by_side(card_strings[0], card_strings[1], 25) + "\n" + card.artist() + "\n")


def make_transform_card_layout(card):
    """
    Makes a string to represent a transform card

    :param card: The card object
    :return: The card string
    """
    card_name = card.name()[:64]
    cost = card.card_faces()[0]['mana_cost']
    title = colored(card_name, attrs=['bold']) + " " * (100 - len(card_name) - len(cost)) + cost
    width = 50
    card_strings = []
    for card_face in card.card_faces():
        if 'colors' in card_face:
            colors = card_face['colors']
        else:
            colors = card.colors()
        type_line = (card_face['type_line']
                     + " " * (width - len(card_face['type_line']) - 2)
                     + colored(RARITY_PICKER[card.rarity()], RARITY_C_PICKER[card.rarity()])
                     + " ")
        oracle_t = ""
        try:
            oracle_t = card_face['oracle_text']
        except KeyError:
            pass
        if 'flavor_text' in card_face:
            oracle = build_text_box(width, oracle_t, card_face['flavor_text'], colors)
        else:
            oracle = build_text_box(width, oracle_t, colors=colors)
        pw_and_tough = ""
        if 'power' in card_face:
            pw_and_tough = "[" + card_face['power'] + "/" + card_face['toughness'] + "]"

        if 'loyalty' in card_face:
            pw_and_tough = "[" + card_face['loyalty'] + "]"

        footer = " " * (width - len(pw_and_tough)) + pw_and_tough

        final_card = type_line + "\n" + oracle + footer + "\n"
        card_strings.append(final_card)

    return color_card(
        "\n" + title + "\n\n" + side_by_side(card_strings[0], card_strings[1]) + "\n" + card.artist() + "\n")


def make_saga_card_string(card):
    """
    Makes a string to represent a card

    :param card: The card object
    :return: The card string
    """
    return card


def side_by_side(str1, str2, width=50):
    """
    Joins to lists of strings side by side

    :param str1: left string
    :param str2: right string
    :param width: The max width of the first string
    :return: The joined strings into one string
    """
    str1_l = str1.splitlines()
    str2_l = str2.splitlines()
    final = []
    for i in range(min(len(str1_l), len(str2_l))):
        final.append(str1_l[i] + str2_l[i])

    if i >= len(str2_l) - 1:
        for i in range(i + 1, len(str1_l)):
            final.append(str1_l[i])
    else:
        for i in range(i + 1, len(str2_l)):
            final.append(" " * width + str2_l[i])

    return "\n".join(final)


def print_card(card):
    """
    Makes a card string from a card object
    :param card: The card object
    :return: The card string
    """
    if card.layout() == 'normal':
        return make_card_string(card)
    elif card.layout() == 'split':
        return make_split_card_string(card)
    elif card.layout() == 'transform' or card.layout() == 'flip':
        return make_transform_card_layout(card)
    elif card.layout() == 'saga':
        return make_saga_card_string(card)


CARD = None

if len(sys.argv) is 1:
    CARD = scrython.cards.Random()
else:
    sys.argv.pop(0)
    cardName = ""
    for a in sys.argv:
        cardName += a

    try:
        CARD = scrython.cards.Named(fuzzy=cardName)
    except Exception as e:
        print(e)
        CARD = None

if CARD is not None:
    print(print_card(CARD))
