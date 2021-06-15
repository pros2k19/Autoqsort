pyautogui = conn.modules["pyautogui"]

import os
import time

# import pyautogui

TEMPLATE_DIR = r"\\iff1166\datenholo\Clausen\dac\autoqsort"

def get_template(name):
    return os.path.join(TEMPLATE_DIR, name)

def merge_file(filename, timeout=15):
    template_1 = get_template('corr_file_active.png')
    template_2 = get_template('corr_file.png')
    merge = get_template('merge_dialog.png')
    matchlist = list(pyautogui.locateAllOnScreen(template_1))
    print("matchlist", matchlist)
    if not matchlist:
        matchlist = list(pyautogui.locateAllOnScreen(template_2))
        if not matchlist:
            raise RuntimeError("Found no match for target application")
        x, y, width, height = matchlist[0]
        # Click on window title to activate window
        pyautogui.click(x+60, y+5)
    if len(matchlist) > 1:
        raise RuntimeError("Found more than one matches for target application")
    # Hotkey for File -> merge
    pyautogui.hotkey('ctrl', 'm')
    # wait for file opening dialogue
    start = time.time()
    time.sleep(0.3)
    while pyautogui.locateOnScreen(merge) is None:
        if time.time() - start > timeout:
           raise RuntimeError("Open file dialogue not detected within timeout period")
        time.sleep(0.5)
    # Filename field is in focus
    pyautogui.typewrite(filename)
    pyautogui.press('enter')
    # Time required to merge: GUI is greyed out during that time
    time.sleep(0.8)


if __name__ == '__main__':
    merge_file(r"\\Iff1166\datenholo\Clausen\dac\test.dac")
    merge_file(r"\\Iff1166\datenholo\Clausen\dac\test.dac")
