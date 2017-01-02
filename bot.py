# Developed by plzb0ss
#
# The purpose of this script is to play chess for you on lichess and hopefully win :p


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from lxml import html
import time
import sys
import requests
from subprocess import Popen, PIPE
chrome = webdriver.Chrome('./chromedriver')

def login_to_lichess(username, password):
    # login to Lichess
    chrome.get('https://en.lichess.org/login')
    login = chrome.find_element_by_id('username')
    login.send_keys(username)
    passwordField = chrome.find_element_by_id('password')
    passwordField.send_keys(password)
    passwordField.send_keys(Keys.ENTER)

def join_game():
    # Joins a game on Lichess
    chrome.get('https://en.lichess.org')
    chrome.find_element_by_link_text('Lobby').click()
    time.sleep(1)
    tests = chrome.find_elements_by_tag_name('tr')
    for test in tests:
        className = test.get_attribute("class")
        print(className)
        if 'join' in className and not 'disabled' in className:
            test.click()
            break



def get_Fen():
    "extract FEN out of from page"
    time.sleep(3)
    # html_source = chrome.page_source
    response = requests.get(chrome.current_url)
    html_source = response.content
    root = html.fromstring(html_source)
    scripts = root.xpath('//script/text()')
    for script in scripts:
        if 'lichess.startRound' in script:
            split = script.split('fen')
            fen = split[len(split) - 1].split('}')[0].split(':')[1]
            fen = fen[1:-1]
            return fen

def ask_stockfish(position):
    "asks stockfish for the best move in the position given"
    stock_proc = Popen('./stockfish-8-64', shell=False, bufsize=0, stdin=PIPE, stdout=PIPE)
    stock_proc.stdin.write("position fen " + position + "\n") 
    print(stock_proc.stdout.readline())
    stock_proc.stdin.write("go depth 10\n")
    line = stock_proc.stdout.readline()
    while not 'bestmove' in line:
        line = stock_proc.stdout.readline()
    stock_proc.kill()
    return line.split(' ')[1]

def click_square(square):
    column_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    x = column_map[square[0]]
    y = int(square[1]) - 1
    # determine orientation of board
    board = chrome.find_element_by_class_name('cg-board')
    orientation = board.get_attribute("class")
    if 'orientation-black' in orientation:
        x = 7 - x
    else:
        y = 7 - y
    print((x,y))
    x = x * 64 + 32
    y = y * 64 + 32
    
    action = webdriver.common.action_chains.ActionChains(chrome)
    action.move_to_element_with_offset(board, x, y)
    action.click()
    action.perform()

# fen = get_Fen()
# fen = 'r1bqkb1r/ppp2ppp/2n5/3n4/8/2N2N2/PP1P1PPP/R1BQKB1R w KQkq - 2 7'
# print(fen)
# best_move = ask_stockfish(fen)
# print(best_move)
# chrome.get('https://en.lichess.org/MVZwniPS/black#78')
# time.sleep(1)
# click_square('f3')
# time.sleep(1)
# click_square('g4')

join_game()
while 1 == 1:
    fen = get_Fen()
    print(fen)
    best_move = ask_stockfish(fen)
    print(best_move)
    print(best_move[:2])
    print(best_move[2:])
    click_square(best_move[:2])
    click_square(best_move[2:])

