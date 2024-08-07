# load_excel () 함수부분 확인하기.

import random
import string
import requests
import re
import pdfplumber
from django.shortcuts import render, redirect
import pandas as pd
from .models import load_excel

# #@! 게임에 필요한 전역 변수들 설정
answer = None
qwerty = list('qwertyuiopasdfghjklzxcvbnm')

# 리스트 word_list? 빈값에서 예외처리
# try:
#     answer = random.choice(global_data_list)
# except IndexError:
#     answer = None  # 또는 다른 처리 방법을 선택하여 처리할 수 있음

# if answer is None:
#     print("Cannot choose from an empty sequence")
# else:
#     print("Selected answer:", answer)

# 1. 단어 리스트 준비
def index(request):
    return render(request, 'index.html')

def load_excel(request):    

    if request.method == 'GET':
        file_name = request.GET.get('file_name')  # 클라이언트에서 전송된 파일명 받기
        if file_name:
            file_path = r'D:\Git_Project_s20240610\wordle_game\wordle game\wordle_project\word\{}.xlsx'.format(file_name) # {file_name}.xlsx
            
            # 엑셀 파일을 데이터프레임으로 읽어오기
            try:
                df = pd.read_excel(file_path, engine='openpyxl', header=None)
                data_list = df.values.flatten().tolist()
                #global_data_list = data_list  # 전역 변수에 할당 #@!
                return render(request, 'index.html', {'data_list': data_list})
            except Exception as e:
                return render(request, 'index.html', {'error_message': str(e)})
        else:
            return render(request, 'index.html', {'error_message': '파일명이 제공되지 않았습니다.'})
        
# 엑셀 파일 경로
#file_path = r'C:\Users\user\Documents\bigdata\wordle_game-1\wordle game\wordle_project\word\master_1.xlsx'
# 엑셀 파일을 데이터프레임으로 읽어오기
#df = pd.read_excel(file_path, engine='openpyxl', header=None)
# DataFrame을 리스트로 변환 후 평탄화
#word_list = df.values.flatten().tolist()

# 남은 알파벳 초기화
qwerty = ['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m']  # qwerty 배열
remaining_letters = qwerty
# #@! answer = random.choice(load_excel())  # 정답 단어를 랜덤으로 선택
attempts = 6  # 사용자에게 주어진 시도 횟수
guesses = []  # 사용자가 입력한 단어들과 피드백을 저장하는 리스트
game_over = False  # 게임 종료 상태를 나타내는 변수
letter_status = {letter: 'unused' for letter in remaining_letters}

# 단어가 유효한지 검사하는 함수
def is_valid_word(word):
    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(api_url)
    return response.status_code == 200

def index(request):    
    global remaining_letters, answer, attempts, guesses, game_over, letter_status#, global_data_list # #@! global_data_list 추가

    if request.method == 'POST':  # POST 요청일 때
        if 'guess' in request.POST and not game_over:
            guess = request.POST['guess'].lower()  # 입력된 단어를 소문자로 변환
            
            if len(guess) != 5:  # 단어 길이가 5자가 아니면 에러 메시지 반환
                return render(request, 'wordle/index.html', {
                    'message': '5개의 알파벳을 사용하는 단어를 입력해주세요.',
                    'remaining_letters': remaining_letters,
                    'attempts': attempts,
                    'guesses': guesses,
                    'game_over': game_over,
                    'letter_status': letter_status
                })

            if not is_valid_word(guess): # #@! and guess not in load_excel: # 단어가 유효하지 않으면 에러 메시지 반환 # word_list
                return render(request, 'wordle/index.html', {
                    'message': '존재하지 않는 단어입니다.',
                    'remaining_letters': remaining_letters,
                    'attempts': attempts,
                    'guesses': guesses,
                    'game_over': game_over,
                    'letter_status': letter_status,
                })

            if guess == answer:  # 사용자가 정답을 맞춘 경우
                feedback = ''.join([f'<span class="correct">{guess[i]}</span>' for i in range(5)])
                guesses.append({'guess': guess, 'feedback': feedback})
                game_over = True  # 게임 종료 상태로 설정
                return render(request, 'wordle/index.html', {
                    'message': f'축하합니다! 정답을 맞추셨습니다. 정답은 {guess} 입니다.',
                    'remaining_letters': remaining_letters,
                    'attempts': attempts,
                    'guesses': guesses,
                    'game_over': game_over,
                    'letter_status': letter_status,
                })
            else:
                feedback = []
                correct_letters = set()
                for i in range(5):
                    if guess[i] == answer[i]:
                        feedback.append(f'<span class="correct">{guess[i]}</span>')  # 🟢: 위치와 문자가 모두 일치
                        correct_letters.add(guess[i])
                        letter_status[guess[i]] = 'correct'

                    elif guess[i] in answer:
                        feedback.append(f'<span class="partial">{guess[i]}</span>')  # 🟡: 문자는 일치하나 위치가 다름
                        correct_letters.add(guess[i])
                        if letter_status[guess[i]] != 'correct':
                            letter_status[guess[i]] = 'partial'
                    else:
                        feedback.append(f'<span class="wrong">{guess[i]}</span>')  # ⚫: 문자가 일치하지 않음
                        letter_status[guess[i]] = 'wrong'
                 
                attempts -= 1  # 시도 횟수 감소
                guesses.append({'guess': guess, 'feedback': ''.join(feedback)})  # 사용자의 입력과 피드백을 리스트에 추가
                if attempts == 0:  # 시도 횟수가 모두 소진된 경우
                    message = f"아쉽지만 모든 시도 횟수를 소진하셨습니다. 정답은 {answer} 입니다."
                    answer = random.choice(load_excel())  # 새로운 게임을 위해 단어 재설정 # #@! word_list
                    attempts = 6  # 시도 횟수 재설정
                    remaining_letters = qwerty  # 남은 알파벳 재설정
                    guesses = []  # 입력 내역 초기화
                    letter_status = {letter: 'unused' for letter in remaining_letters}  # 알파벳 상태 재설정
                    game_over = True  # 게임 종료 상태로 설정
                else:
                    message = ""

                return render(request, 'wordle/index.html', {
                    'message': message,
                    'remaining_letters': remaining_letters,
                    'attempts': attempts,
                    'guesses': guesses,
                    'letter_status': letter_status,
                    'game_over': game_over
                })

        elif 'reset' in request.POST:  # 게임을 다시 시작할 때
            answer = random.choice(load_excel)       # #@! word_list
            attempts = 6
            remaining_letters = qwerty
            guesses = []
            letter_status = {letter: 'unused' for letter in remaining_letters}
            game_over = False  # 게임 종료 상태 해제
            return redirect('index')
    else:
        if not answer:
            answer = random.choice(load_excel)  # 정답이 없는 경우 새로운 단어 선택

        return render(request, 'wordle/index.html', {
            'remaining_letters': remaining_letters,
            'attempts': attempts,
            'guesses': guesses,
            'letter_status': letter_status,
            'game_over': game_over
        })
    return render(request, 'wordle/index.html', {  # GET 요청일 때
        'remaining_letters': remaining_letters,
        'attempts': attempts,
        'guesses': guesses,
        'letter_status': letter_status,
        'game_over': game_over
    })
