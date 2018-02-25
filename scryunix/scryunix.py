import sys
import scrython
import textwrap
import re
from re import sub
from termcolor import colored

colorPicker = {'W':'white','U':'blue','B':'grey','R':'red','G':'green'}
rarityPicker  = {'common': 'C','uncommon':'U', 'rare':'R', 'mythic':'M'}
rarityCPicker = {'common': 'white','uncommon':'grey', 'rare': 'yellow', 'mythic':'red'}

def treatText(text,width,colors,flavor=False):
    oracle_lines = text.splitlines()
    oracle = []
    for i in range(len(oracle_lines)):
        line = oracle_lines[i]
        line = textwrap.wrap(line,width-4)
        oracle.append(line)

    oracle = [line.center(width-4) for sentence in oracle for line in sentence]

    if flavor:
        oracle = [colored(line,'white','on_grey',attrs=['dark']) for line in oracle]
    
    l = '|'
    if len(colors) is 1:
        l = colored(l, colorPicker[colors[0]])
    elif len(colors) is not 0:
        l = colored(l,'yellow')
    else:
        l = colored(l, 'white', attrs=['dark'])

    oracle = [l+' '+x+' '+l for x in oracle]
    oracle = '\n'.join(oracle)+'\n'
    return oracle

def buildOracle(width, oracle_text, flavor_text=None, colors=[]):
    separator = '+'+'-'*(width-2)+'+\n'
    flavor = '|'+' '*(width-2)+'|\n'
    if len(colors) is 1:
        separator = colored(separator, colorPicker[colors[0]])
        flavor    = colored(flavor, colorPicker[colors[0]])
    elif len(colors) is not 0:
        separator = colored(separator, 'yellow')
        flavor    = colored(flavor, 'yellow')
    else:
        separator = colored(separator, 'white', attrs=['dark'])
        flavor    = colored(flavor, 'white', attrs=['dark'])
    
    oracle = treatText(oracle_text,width,colors)
    if flavor_text is not None:
        flavor = flavor + treatText(flavor_text,width,colors,True)
    
    return separator + oracle + flavor + separator

def colorCard(card):
    paint = False
    cardAsList = list(card)
    for i in range(len(cardAsList)):
        c = cardAsList[i]
        if c is '{':
            paint = True
        elif c is '}':
            paint = False
        elif paint:
            if re.search("[^WUBRG]",c) is not None:
                cardAsList[i] = colored(c,'white',attrs=['dark'])
            else:
                cardAsList[i] = colored(c,colorPicker[c])
    
    return "".join(cardAsList)

def getColorsFromCost(cost):
    colors = []
    for c in cost:
        if re.match('[WUBRG]',c) and c not in colors:
            colors.append(c)
    return colors

def makeCardString(card):
    cardName = card.name()[:32]
    
    title = colored(cardName,attrs=['bold']) + " "*(50 - len(cardName) - len(card.mana_cost())) + card.mana_cost()
    width = 50
    
    typeLine = (card.type_line() 
             + " "*(width - len(card.type_line()) - 2) 
             + colored(rarityPicker[card.rarity()],rarityCPicker[card.rarity()]))
    oracle_t = ""
    oracle = ""
    try:
        oracle_t = card.oracle_text()
    except Exception:
        pass
    if 'flavor_text' in card.scryfallJson:
        oracle = buildOracle(width,oracle_t,card.scryfallJson['flavor_text'],card.colors())
    else:
        oracle = buildOracle(width,oracle_t,colors=card.colors())
    pAt = ""
    if 'power' in card.scryfallJson:
        pAt = "[" + card.scryfallJson['power'] + "/" + card.scryfallJson['toughness'] + "]"
    
    if 'loyalty' in card.scryfallJson:
        pAt = "[" + card.scryfallJson['loyalty'] + "]"
    
    footer = card.artist() + " "*(width - len(card.artist()) - len(pAt)) + pAt
    
    finalCard = ("\n"+ title + "\n\n"
              + typeLine + "\n"
              + oracle
              + footer + "\n")
    finalCard = colorCard(finalCard)
    return finalCard

def makeSplitCardString(card):
    width = 25
    cardStrings = []
    for card_face in card.card_faces():
        cardName = card_face['name'][:16]
        cost = card_face['mana_cost']
        title = colored(cardName,attrs=['bold']) + " "*(25 - len(cardName) - len(cost)) + cost
        typeLine = (card_face['type_line']
                + " "*(width - len(card_face['type_line']) - 2) 
                + colored(rarityPicker[card.rarity()],rarityCPicker[card.rarity()])
                + " ")
        oracle_t = ""
        oracle = ""
        try:
            oracle_t = card_face['oracle_text']
        except Exception:
            pass
        if 'flavor_text' in card_face:
            oracle = buildOracle(width,oracle_t,card.scryfallJson['flavor_text'],getColorsFromCost(card_face['mana_cost']))
        else:
            oracle = buildOracle(width,oracle_t,colors=getColorsFromCost(card_face['mana_cost']))
        pAt = ""
        if 'power' in card_face:
            pAt = "[" + card_face['power'] + "/" + card_face['toughness'] + "]"
        
        if 'loyalty' in card_face:
            pAt = "[" + card_face['loyalty'] + "]"
        
        footer = " "*(width - len(pAt)) + pAt
        
        finalCard = "\n" + title + "\n\n" + typeLine + "\n" + oracle + footer + "\n"

        cardStrings.append(finalCard)

    return colorCard(sideBySide(cardStrings[0],cardStrings[1],25) + "\n" + card.artist() + "\n")

def makeTransformCardLayout(card):
    cardName = card.name()[:64]
    cost = card.card_faces()[0]['mana_cost']
    title = colored(cardName,attrs=['bold']) + " "*(100 - len(cardName) - len(cost)) + cost
    width = 50
    cardStrings = []
    for card_face in card.card_faces():
        colors = []
        if 'colors' in card_face:
            colors = card_face['colors']
        else:
            colors = card.colors()
        typeLine = (card_face['type_line']
                + " "*(width - len(card_face['type_line']) - 2) 
                + colored(rarityPicker[card.rarity()],rarityCPicker[card.rarity()])
                + " ")
        oracle_t = ""
        oracle = ""
        try:
            oracle_t = card_face['oracle_text']
        except Exception:
            pass
        if 'flavor_text' in card_face:
            oracle = buildOracle(width,oracle_t,card_face['flavor_text'],colors)
        else:
            oracle = buildOracle(width,oracle_t,colors=colors)
        pAt = ""
        if 'power' in card_face:
            pAt = "[" + card_face['power'] + "/" + card_face['toughness'] + "]"
        
        if 'loyalty' in card_face:
            pAt = "[" + card_face['loyalty'] + "]"
        
        footer = " "*(width - len(pAt)) + pAt
        
        finalCard = typeLine + "\n" + oracle + footer + "\n"
        cardStrings.append(finalCard)

    return colorCard("\n" + title + "\n\n" + sideBySide(cardStrings[0],cardStrings[1]) + "\n" + card.artist() + "\n")

def sideBySide(str1, str2, width=50):
    str1L = str1.splitlines()
    str2L = str2.splitlines()
    final = []
    for i in range(min(len(str1L),len(str2L))):
        final.append(str1L[i] + str2L[i])
    
    if i == len(str2L)-1:
        for i in range(i+1,len(str1L)):
            final.append(str1L[i])
    else:
        for i in range(i+1,len(str2L)):
            final.append(" "*width + str2L[i])
        
    return "\n".join(final)

def printCard(card):
    if card.layout() == 'normal':
        return makeCardString(card)
    elif card.layout() == 'split':
        return makeSplitCardString(card)
    elif card.layout() == 'transform' or card.layout() == 'flip':
        return makeTransformCardLayout(card)

card = None

if len(sys.argv) is 1:
    card = scrython.cards.Random()
else:
    sys.argv.pop(0)
    cardName = ""
    for a in sys.argv:
        cardName += a

    try:
        card = scrython.cards.Named(fuzzy=cardName)
    except Exception as e:
        print(e)
        card = None

if card is not None:
    print(printCard(card))
