from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
import os
from time import time, sleep
import textwrap
import re
import PyPDF2

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone

openai_api_key = '' # Key here
openai.api_key = openai_api_key


def ask_openai_old(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an helpful assistant."},
            {"role": "user", "content": message},
        ]
    )

    answer = response.choices[0].message.content.strip()
    return answer


def ask_openai(language_input, model_input, inputtext, name_of_case, prompt, facts, issue, procedural, ratio,
               reasoning):
    # customize
    language = language_input  # EN is English, FE is French
    model_used = model_input  # davinci is Davinci, N is Ada
    #####

    input_file = inputtext
    # input_file = open_file('input.txt')
    filename = name_of_case
    set_filename = filename
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'prompt.txt')
    summary_prompt_file = 'prompt.txt'  # file_path

    ##########
    # change to have user selected buttons or dropdown
    if model_used == 'model_input':
        engine_to_use = 'text-davinci-003'
    else:
        engine_to_use = 'text-ada-001'
    if model_used == 'model_input':
        chunks = textwrap.wrap(input_file, 14700)
        print('14700 ' + engine_to_use)
    else:
        chunks = textwrap.wrap(input_file, 6000)
        print('6000 ' + engine_to_use)
    ###############

    result = list()
    count = 0
    counter = 0
    for chunk in chunks:
        count = count + 1
        prompt = open_file(summary_prompt_file).replace('<<SUMMARY>>', chunk)
        prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
        summary = gpt3_completion(counter, filename, prompt, engine=engine_to_use)
        counter += 1
        print('\n\n\n', count, 'of', len(chunks), ' - ', summary)
        result.append(summary)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path_sum = os.path.join(current_dir, 'outputs/sum_%s.txt' % filename)
    save_file('\n\n'.join(result), file_path_sum)

    # Start of edit
    all_prompts = dictionary_of_prompts()
    file_names_to_test = []
    list_of_prompts = []
    for i in all_prompts:
        file_names_to_test.append(i)
    for j in all_prompts.values():
        list_of_prompts.append(j)

    create_prompt_files(file_names_to_test, list_of_prompts)
    test_prompts(file_names_to_test, filename, set_filename)
    # End of Edit

    # return dict for response? ex: fact: ..., issue: ...
    # return list_of_prompts(file_names_to_test, list_of_prompts) # tells which files to read for result
    # and then delete all the files


def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        title = request.POST.get('title')
        ask_openai('EN', 'davinci', message, 'title', 'prompt', 'facts', 'issue', 'procedural', 'ratio', 'reasoning')
        print('finish ask OPEN AI')
        ##NEWLINE
        response_facts = 'Facts: ' + read_file('final/facts.txt')
        response_issue = 'Issue: ' + read_file('final/issue.txt')
        response_procedural = 'Procedural: ' + read_file('final/procedural.txt')
        response_ratio = 'Ratio: ' + read_file('final/ratio.txt')
        response_reasoning = 'Reasoning: ' + read_file('final/reasoning.txt')
        arr_response = []
        arr_response.append(response_facts)
        arr_response.append(response_issue)
        arr_response.append(response_procedural)
        arr_response.append(response_ratio)
        arr_response.append(response_reasoning)

        # response = 'Facts: ' + response_facts + '\n\n\n' + 'Issues: ' + response_issue + '\n' + 'Procedural: ' + response_procedural + '\n' + 'Ratio: ' + response_ratio + '\n' + 'Reasoning: ' + response_reasoning
        # chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        # chat.save()

        # delete final folder
        delete_folder('final')

        # delete outputs folder
        delete_folder('outputs')

        # delete prompts folder
        delete_folder('prompts')

        # delete draft folder
        delete_folder('draft')

        return JsonResponse({'message': message, 'response': arr_response})
    return render(request, 'chatbot.html', {'chats': chats})


# def chatbotPDF(request):
#     chats = Chat.objects.filter(user=request.user)
#
#     if request.method == 'POST':
#         message = request.POST.get('message')
#         # uploaded_file = request.FILES['file']
#         # pdf_reader = PyPDF2.PdfReader(uploaded_file)
#         # pdf_text = ""
#         # for page in pdf_reader.pages:
#         #     pdf_text += page.extract_text()
#         # message = pdf_text
#
#         title = request.POST.get('title')
#
#         # ask_openai('EN', 'davinci', message, title, 'prompt', 'facts', 'issue', 'procedural', 'ratio', 'reasoning')
#         #
#         # response_facts = 'Facts: ' + read_file('final/facts.txt')
#         # response_issue = 'Issue: ' + read_file('final/issue.txt')
#         # response_procedural = 'Procedural: ' + read_file('final/procedural.txt')
#         # response_ratio = 'Ratio: ' + read_file('final/ratio.txt')
#         # response_reasoning = 'Reasoning: ' + read_file('final/reasoning.txt')
#         # arr_response = [response_facts, response_issue, response_procedural, response_ratio, response_reasoning]
#         #
#         # # response = 'Facts: ' + response_facts + '\n\n\n' + 'Issues: ' + response_issue + '\n' + 'Procedural: ' +
#         # # response_procedural + '\n' + 'Ratio: ' + response_ratio + '\n' + 'Reasoning: ' + response_reasoning chat =
#         # # Chat(user=request.user, message=message, response=response, created_at=timezone.now()) chat.save()
#         #
#         # # delete final folder
#         # delete_folder('final')
#         #
#         # # delete outputs folder
#         # delete_folder('outputs')
#         #
#         # # delete prompts folder
#         # delete_folder('prompts')
#
#         return JsonResponse({'message': message, 'response': 'arr_response'})
#     return render(request, 'chatbotPDF.html', {'chats': chats})
#

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect('login')


# Law Case Summarizer

def open_file(filepath):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filepath)
    print(file_path)
    with open(file_path, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(content, filepath):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filepath)
    with open(file_path, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def read_file(filepath):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filepath)
    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()
    return file_contents


def delete_folder(folder_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path_sum = os.path.join(current_dir, folder_name)
    folder_path = file_path_sum
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


# Function to send prompts to OpenAI API
def gpt3_completion(counter, filename, prompt, engine='text-ada-001', temp=0.6, top_p=1.0, tokens=350, freq_pen=0.25,
                    pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\\s+', ' ', text)
            filename1 = filename + str(counter) + '.txt'
            print(filename1)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, 'draft/%s' % filename1)
            with open(file_path, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


# Function for testing prompts and fine-tuning them
def test_prompts(prompt_files, filename, setfilename):  # prompt_files is a arr of strings
    for prompt_name in prompt_files:
        prompt_file_name = prompt_name
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # file_path = os.path.join(current_dir, 'outputs/sum_%s.txt' % setfilename)
        current_file = open_file('outputs/sum_%s.txt' % setfilename)
        chunks1 = textwrap.wrap(current_file, 14700)  # 6000 -> ada #14700 -> 4066 for davinci
        result1 = list()
        count1 = 0
        counter1 = 0
        # filename1 = setfilename + ' ' + prompt_file_name
        filename1 = prompt_file_name
        prompt_files_names = "prompts/" + prompt_file_name + ".txt"
        for chunk in chunks1:
            count1 = count1 + 1
            prompt1 = open_file(prompt_files_names).replace('<<SUMMARY>>', chunk)
            prompt1 = prompt1.encode(encoding='ASCII', errors='ignore').decode()
            summary1 = gpt3_completion(counter1, filename1, prompt1, engine='text-davinci-003')
            counter1 += 1
            print('\n\n\n', count1, 'of', len(chunks1), ' - ', summary1)
            result1.append(summary1)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path_sum = os.path.join(current_dir, 'final/%s.txt' % filename1)
        save_file('\n\n'.join(result1), 'final/%s.txt' % filename1)


def create_prompt_files(array_of_prompts_names, array_of_prompts):
    # Make sure the num of array_of_prompts_names match with array_of_prompts
    if len(array_of_prompts_names) != len(array_of_prompts):
        print("ERROR: NUM OF NAME FILES DO NOT MATCH NUM OF PROMPT INPUTS")
        return ""

    i = 0
    while i < len(array_of_prompts_names):
        text_name = array_of_prompts_names[i] + '.txt'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'prompts/%s' % text_name)
        with open(file_path, 'w') as outfile:
            outfile.write(array_of_prompts[i])
        i += 1


def list_prompt_files(array_of_prompts_names, array_of_prompts):
    # Make sure the num of array_of_prompts_names match with array_of_prompts
    if len(array_of_prompts_names) != len(array_of_prompts):
        print("ERROR: NUM OF NAME FILES DO NOT MATCH NUM OF PROMPT INPUTS")
        return ""
    array = []
    i = 0
    while i < len(array_of_prompts_names):
        text_name = array_of_prompts_names[i] + '.txt'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'prompts/%s' % text_name)
        array.append(file_path)
        i += 1


############################
############################
# Start edit for testing

# Function for prompts + add customization
def dictionary_of_prompts():
    common = "\n\n<<SUMMARY>>\n"
    dictionary = {
        'facts': "Give me the factual background (who, when, what, where, why) of this case in bullet points",
        'issue': "Give me the legal issue or issues of this case, numbered and the outcomes of each issues",
        'procedural': "Give me the procedural history of this case in bullet points",
        'reasoning': "Give me the reasoning behind each issues of this case",
        'ratio': "Give me the ratio or ratios of this case, numbered"
    }

    for key in dictionary.keys():
        dictionary[key] = dictionary[key] + common

    return dictionary

# End edit for testing
############################
############################
