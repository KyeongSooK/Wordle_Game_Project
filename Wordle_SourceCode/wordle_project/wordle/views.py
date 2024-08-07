import random
import string
import requests
import pandas as pd
from django.shortcuts import render, redirect

# 엑셀 파일에서 단어 리스트를 로드하는 함수
def load_excel(file_name):
    file_path = f'C:\\Users\\USER\\Documents\\wordle_game\\word(translate)\\{file_name}.xlsx'
     # 로컬 폴더에서 데이터 로드 # word 폴더 다운받은 경로 입력
    
    try:
        df = pd.read_excel(file_path, engine='openpyxl', header=None)  # 엑셀 파일을 데이터프레임으로 로드
        word_list = df.values.tolist()  # 데이터프레임을 리스트로 변환
        print("로드된 단어와 뜻:", word_list)  # 디버깅 로그
        return word_list
    except Exception as e:
        return str(e)  # 오류 발생 시 오류 메시지 반환

# 단어가 유효한지 검사하는 함수
def is_valid_word(word):
    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"  # API URL 생성
    response = requests.get(api_url)  # API 호출
    return response.status_code == 200  # HTTP 응답 코드가 200이면 유효한 단어로 간주

# 글로벌 변수 설정
qwerty = list('qwertyuiopasdfghjklzxcvbnm')  # 키보드의 모든 알파벳
remaining_letters = qwerty.copy()  # 남아있는 알파벳 초기화
word_list = []  # 단어 리스트
answer = ""  # 정답 단어
attempts = 6  # 시도 횟수
guesses = []  # 사용자의 추측 기록
game_over = False  # 게임 종료 상태
letter_status = {letter: 'unused' for letter in remaining_letters}  # 각 알파벳의 상태
difficulty_selected = False  # 단어장 선택 상태

def index(request):
    global remaining_letters, answer, attempts, guesses, game_over, letter_status, word_list, difficulty_selected

    # POST 요청일 때
    if request.method == 'POST':
        # 파일 로드 요청일 때
        if 'load_file' in request.POST:
            file_name = request.POST['file_name']  # 파일 이름 가져오기
            word_list = load_excel(file_name)  # 엑셀 파일에서 단어 리스트 로드
            message = f'밀크T 초등 {file_name} 단어장을 선택 하셨습니다.'  # 사용자에게 알림 메시지

            # 에러 메시지가 반환되었을 때
            if isinstance(word_list, str):
                return render(request, 'wordle/index.html', {
                    'error_message': word_list,
                })
                
            # 단어 리스트가 비어있을 때
            if not word_list:
                return render(request, 'wordle/index.html', {
                    'error_message': '파일이 비어있거나 잘못된 형식입니다.',
                })
            
            # 게임 초기화
            answer = random.choice(word_list)
            attempts = 6
            remaining_letters = qwerty.copy()
            guesses = []
            letter_status = {letter: 'unused' for letter in remaining_letters}
            game_over = False
            difficulty_selected = True
            return render(request, 'wordle/index.html', {
                'message': message,
                'remaining_letters': remaining_letters,
                'attempts': attempts,
                'guesses': guesses,
                'letter_status': letter_status,
                'game_over': game_over,
                'remaining_rows': range(6 - len(guesses)),
            })
        
        # 사용자가 추측 단어를 제출했을 때
        if 'guess' in request.POST and not game_over:
            # 단어장이 선택되지 않았을 때
            if not difficulty_selected:
                return render(request, 'wordle/index.html', {
                    'message': '단어장을 선택해주세요.',
                    'remaining_letters': remaining_letters,
                    'attempts': attempts,
                    'guesses': guesses,
                    'game_over': game_over,
                    'letter_status': letter_status,
                    'remaining_rows': range(6 - len(guesses)),
                })

            guess = request.POST['guess'].lower()  # 입력된 단어 소문자로 변환
            # 5자리 영단어가 아닐 때
            if len(guess) != 5:
                return render(request, 'wordle/index.html', {
                    'message': '5개의 알파벳을 사용하는 단어를 입력해주세요.',
                    'remaining_letters': remaining_letters,
                    'attempts': attempts,
                    'guesses': guesses,
                    'game_over': game_over,
                    'letter_status': letter_status,
                    'remaining_rows': range(6 - len(guesses)),
                })
            # 단어 검증에 실패했을 때
            if not is_valid_word(guess) and guess not in [word[0] for word in word_list]:
                return render(request, 'wordle/index.html', {
                    'message': '존재하지 않는 단어입니다.',
                    'remaining_letters': remaining_letters,
                    'attempts': attempts,
                    'guesses': guesses,
                    'game_over': game_over,
                    'letter_status': letter_status,
                    'remaining_rows': range(6 - len(guesses)),
                })
            # 정답일 때
            if guess == answer[0]:
                feedback = [{'char': guess[i], 'status': 'correct'} for i in range(5)]
                guesses.append({'guess': guess, 'feedback': feedback})
                game_over = True
                return render(request, 'wordle/index.html', {
                    'message': f'축하합니다! 정답을 맞추셨습니다. 정답은 {guess} ({answer[1]}) 입니다.',
                    'remaining_letters': remaining_letters,
                    'attempts': attempts,
                    'guesses': guesses,
                    'game_over': game_over,
                    'letter_status': letter_status,
                    'remaining_rows': range(6 - len(guesses)),
                })
            else:  # 입력한 값에 대한 피드백 제공
                feedback = []
                correct_letters = set()
                for i in range(5):
                    if guess[i] == answer[0][i]:
                        feedback.append({'char': guess[i], 'status': 'correct'})
                        correct_letters.add(guess[i])
                        letter_status[guess[i]] = 'correct'
                    elif guess[i] in answer[0]:
                        feedback.append({'char': guess[i], 'status': 'partial'})
                        correct_letters.add(guess[i])
                        if letter_status[guess[i]] != 'correct':
                            letter_status[guess[i]] = 'partial'
                    else:
                        feedback.append({'char': guess[i], 'status': 'wrong'})
                        letter_status[guess[i]] = 'wrong'
                
                attempts -= 1
                guesses.append({'guess': guess, 'feedback': feedback})
                if attempts == 0:
                    message = f"아쉽지만 모든 시도 횟수를 소진하셨습니다. 정답은 {answer[0]} ({answer[1]}) 입니다."
                    game_over = True
                else:
                    message = ""

                return render(request, 'wordle/index.html', {
                    'message': message,
                    'remaining_letters': remaining_letters,
                    'attempts': attempts,
                    'guesses': guesses,
                    'letter_status': letter_status,
                    'game_over': game_over,
                    'remaining_rows': range(6 - len(guesses)),
                })

        # 다시하기 요청일 때
        elif 'reset' in request.POST:
            answer = random.choice(word_list)
            attempts = 6
            remaining_letters = qwerty.copy()
            guesses = []
            letter_status = {letter: 'unused' for letter in remaining_letters}
            game_over = False
            return redirect('index')
    else:
        # 게임 초기 화면 로드
        if not answer and word_list:
            answer = random.choice(word_list)

        return render(request, 'wordle/index.html', {
            'message': '게임 시작 전, 게임방법을 읽어주세요.',
            'remaining_letters': remaining_letters,
            'attempts': attempts,
            'guesses': guesses,
            'letter_status': letter_status,
            'game_over': game_over,
            'remaining_rows': range(6 - len(guesses)),
        })

    return render(request, 'wordle/index.html', {
        'message': '게임 시작 전, 게임방법을 읽어주세요.',
        'remaining_letters': remaining_letters,
        'attempts': attempts,
        'guesses': guesses,
        'letter_status': letter_status,
        'game_over': game_over,
        'remaining_rows': range(6 - len(guesses)),
    })
