import os
import time

import pyautogui

TEMPLATE_DIR = os.path.dirname(__file__)

def get_template(name):
    return os.path.join(TEMPLATE_DIR, name)

def set_XL(val):
    template_1 = get_template('XL_active.png')
    template_2 = get_template('XL_inactive.png')
    matchlist = list(pyautogui.locateAllOnScreen(template_1))
    print("matchlist", matchlist)
    if not matchlist:
        matchlist = list(pyautogui.locateAllOnScreen(template_2))
        if not matchlist:
            raise RuntimeError("Found no match for target application")
        x, y, width, height = matchlist[0]
        # Click on window title to activate window
        pyautogui.click(x+60, y+5)
    elif len(matchlist) > 1:
        raise RuntimeError("Found more than one matches for target application")
    else:
        x, y, width, height = matchlist[0]
    
    
    pyautogui.doubleClick(x+200, y+125)
    pyautogui.press('backspace')
    pyautogui.typewrite(str(val))
    pyautogui.press('enter')


def set_Align_XS(val1, val2):
    template_1 = get_template('Align_XS_active.png')
    template_2 = get_template('Align_XS_inactive.png')
    matchlist = list(pyautogui.locateAllOnScreen(template_1))
    print("matchlist", matchlist)
    if not matchlist:
        matchlist = list(pyautogui.locateAllOnScreen(template_2))
        if not matchlist:
            raise RuntimeError("Found no match for target application")
        x, y, width, height = matchlist[0]
        # Click on window title to activate window
        pyautogui.click(x+60, y+5)
    elif len(matchlist) > 1:
        raise RuntimeError("Found more than one matches for target application")
    else:
        x, y, width, height = matchlist[0]
    
    
    pyautogui.doubleClick(x+200, y+130)
    pyautogui.press('backspace')
    pyautogui.typewrite(str(val1))
    pyautogui.doubleClick(x+200, y+150)
    pyautogui.press('backspace')
    pyautogui.typewrite(str(val2))
    pyautogui.press('enter')

if __name__ == '__main__':
    set_Align_XS('0.123', '0.01')
    set_XL('0.287')
