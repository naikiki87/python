import pyautogui
import sys
import time

delay = 0.5

# x, y = pyautogui.position()
# print('x={0}, y={1}'.format(x, y))

# 매수
# pyautogui.click(x=1180, y=874)
pyautogui.click(x=330, y=542)
time.sleep(delay)

# pyautogui.click(x=1043, y=484)
# time.sleep(1)
# pyautogui.typewrite("6458")  

# pyautogui.moveTo(1510,895)
# pyautogui.click(x=1510, y=895)
# pyautogui.click(x=1165, y=667)
# time.sleep(2)
# pyautogui.click()

# time.sleep(1)

# pyautogui.click()

# width, height = pyautogui.size()  
# pyautogui.moveTo(width/2, height/2)

# pyautogui.click(button='right')

# pyautogui.scroll(100)


# #전체 화면 크기
# pyautogui.size()
# #현재 마우스 위치 확인
# pyautogui.position

# # 모니터 해상도 가져오기
# width, height = pyautogui.size()  
# print('width={0}, height={1}'.format(width, height))  

# # 마우스 위치 가져오기
# x, y = pyautogui.position()  
# print('x={0}, y={1}'.format(x, y))  

# # 안전모드 설정하기, 잘못되었을 경우 탈출구
# pyautogui.PAUSE = 1  
# pyautogui.FAILSAFE = True  

# # 마우스 이동하기
# width, height = pyautogui.size()  
# pyautogui.moveTo(width/2, height/2)  

# # 상대좌표로 마우스 이동하기
# pyautogui.moveRel(None, 20)  
# pyautogui.moveRel(x축 참조값, y축 참조값, 시간)

# #마우스 절대주소로 이동
# pyautogui.moveTo(0,0,5)   ->   5초안에 0,0으로 마우스 이동

# # 마우스 클릭하기
# pyautogui.click()

# # 마우스로 특정좌표 클릭하기
# pyautogui.click(x=28, y=1100)

# # 마우스 오른쪽 클릭하기
# pyautogui.click(button='right')

# # 또는
# pyautogui.rightClick()  
# # 마우스로 더블 클릭하기
# pyautogui.click(clicks=2)

# # 또는
# pyautogui.doubleClick()

# # 시간 간격(인터벌)을 가지고 클릭하기
# pyautogui.click(clicks=2, interval=1.5)  
# # 마우스 버튼다운
# pyautogui.mouseDown()

# # 마우스 다운 업
# pyautogui.mouseUp()  
# # 마우스 드래그 - 방법 1

# # 마우스 버튼다운
# pyautogui.mouseDown(x=0, y=0)

# # 마우스 다운 업
# pyautogui.mouseUp(x=100, y=100)  
# # 마우스 드래그 - 방법 2

# # 마우스 현재 위치에서 x=100, y=100로 드래그
# pyautogui.dragTo(x=100, y=100)

# # 중간 지연 시간을 가지고 마우스 현재 위치에서 x=100, y=100로 드래그
# pyautogui.dragTo(x=100, y=100, duration=2)  
# # 상대 좌표를 가지고 마우스 드래그
# pyautogui.dragRel(-100, -100, duration=2)  
# # 마우스 스크롤 하기

# # 위로
# pyautogui.scroll(-100)

# # 아래로
# pyautogui.scroll(100)

# # 특정 위치로 이동한 후에 스크롤 하기
# pyautogui.scroll(100, x=100, y=100)  
# # 특정 문자열 입력하기
# pyautogui.typewrite('Hello!')

# # 특정 문자열 안정적으로 입력하기
# time.sleep(5)  
# pyautogui.typewrite('Hello!', interval=0.25)

# # 한글 입력은 안됨
# # 클립보드에 내용을 저장하고 복붙하는 기능을 생각해 볼 수 있겠음
# pyautogui.typewrite('한글은 안 된다네!')  

# # 한글 입력은 안 됨
# pyautogui.typewrite('한글!') 
# #글을 적는 곳의 IME가 한글로 설정되어 있다면 영타로 쳐서 한글입력 가능
# pyautogui.typewrite('gksrmf!') 


# # 문자열 입력하고 엔터 입력하기
# pyautogui.typewirte('Hello!')  
# pyautogui.press('enter')  
# # 여러 키 연속으로 입력하기
# pyautogui.press(['backspace', 'enter'])  
# # 조합 키 입력하기 (쉬프트 누르고 왼쪽으로 한 칸 선택한 후, 쉬프트 떼기)
# pyautogui.typewrite('Hello')  
# pyautogui.keyDown('shift')  
# pyautogui.press('left')  
# pyautogui.keyUp('shift')  

# # 복사 붙이기

# # Ctrl + C
# pyautogui.hotkey('ctrl', 'c')

# # Ctrl + V
# pyautogui.hotkey('ctrl', 'v')  

# # press 가능 키 리스트
# ['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
# ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
# '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
# 'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
# 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
# 'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
# 'browserback', 'browserfavorites', 'browserforward', 'browserhome',
# 'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
# 'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
# 'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
# 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
# 'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
# 'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja',
# 'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
# 'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
# 'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
# 'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
# 'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
# 'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
# 'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab',
# 'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winlef

# #스크린샷 찍기
# import pyautogui

# im1 = pyautogui.screenshot()
# im2 = pyautogui.screenshot('my_screenshot.png')
# im3 = pyautogui.screenshot('my_region.png', region=(0, 0, 300, 300))

# #이미지로 마우스 위치시키기


# #프로그램이 항상 조금씩 다른 위치에서 실행되기 때문에 화면 상의 특정한 위치에 마우스를 위치시키기가 까다로울 수 있습니다.
# 이런 상황에서 화면 상의 특정 영역의 이미지 파일을 갖고 있으면 그 영역을 찾아서 클릭할 수 있습니다.
# #공식 문서의 예제와 같이 계산기가 어디에 있든 항상 똑같은 버튼을 클릭하도록 해보겠습니다.
# #우선 계산기의 특정 영역을 캡처해서 해당 폴더에 아래와 같이 'five.PNG' 파일로 저장합니다.
# #이미지 영역 찾기
# import pyautogui

# five_btn = pyautogui.locateOnScreen('five.PNG')
# print(five_btn)

# #이미지 영역의 가운데 위치 얻기
# five_btn = pyautogui.locateOnScreen('five.PNG')
# center = pyautogui.center(five_btn)
# print(center)

# #클릭하기
# center = pyautogui.locateCenterOnScreen('five.PNG')
# pyautogui.click(center)