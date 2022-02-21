import tkinter as tk
from random import randint


# Проверяет существование необходимых файлов
common_association_exists = False
try:
    checkfile = open('parole_config\\common_association.txt', 'x', encoding='utf-8')
except FileExistsError:
    common_association_exists = True
try:
    epwcreate = open('parole_config\\EPW.txt', 'x', encoding='utf-8')
except FileExistsError:
    pass


# Подача в core_association, frequency_sum и decrypt таблично-цифровых ключей из строкового
def recieve_encode(key):
    global common_association, core_association, decrypt, frequency_sum, printable
    core_association = {}
    for fsymb in printable:
        core_association[fsymb] = []
    decrypt = {}
    frequency_sum = {}
    # Ключ = число, значение = следующее после него максимальное число из оставшихся
    rest_of_numbers = {'0' * (4 - len(str(fi))) + str(fi) for fi in range(10000)}
    numberline = ['0' * (4 - len(str(fi))) + str(fi) for fi in range(10000)]
    code_list = []
    big_number = int('1' + '0' * 40009)
    for fsymb in key:
        if fsymb in printable:
            code_list.append(str(common_association[fsymb]))
        else:
            code_list.append(str(common_association['»']))
    code_int = int(''.join(code_list))
    while code_int < big_number:
        code_int = code_int ** 2 + 1
    code_str = str(code_int)
    printable_tracker = 0
    for fi in range(10000):
        slice = code_str[fi * 4: fi * 4 + 4]
        if slice not in rest_of_numbers:
            while numberline[-1] not in rest_of_numbers:
                numberline.pop()
            slice = numberline.pop()
        rest_of_numbers.discard(slice)
        decrypt[slice] = printable[printable_tracker]
        core_association[printable[printable_tracker]].append((slice, int(slice) % 100 + 1))
        printable_tracker += 1
        printable_tracker %= 161
    for fsymb in printable:
        frequency_sum[fsymb] = 0
        for val_freq in core_association[fsymb]:
            frequency_sum[fsymb] += val_freq[1]


# По данным строковому имени и паролю кодирует всё и добавляет в файл (требуются core_association и frequency_sum)
def add_password(name, password):
    global core_association, frequency_sum, printable
    fopt = open('parole_config\\EPW.txt', 'a', encoding='utf-8')
    password += '«'
    password_line = []
    for ffsymb in password:
        if ffsymb in printable:
            fsymb = ffsymb
        else:
            fsymb = '»'
        fx = randint(1, frequency_sum[fsymb])
        core_idx = 0
        while fx > core_association[fsymb][core_idx][1]:
            fx -= core_association[fsymb][core_idx][1]
            core_idx += 1
        password_line.append(core_association[fsymb][core_idx][0])
    fopt.write(name + '\n')
    password_line = ''.join(password_line)
    fopt.write(password_line)
    for fi in range(randint(0, 99)):
        fopt.write(str(randint(0, 9)))
    fopt.write('\n')
    fopt.close()
    return password_line  # DEBUG


# ВОЗВРАЩАЕТ пароль из закодированной бурды (требуется decrypt)
def get_password(encryption):
    global decrypt
    message = []
    for fi in range(len(encryption) // 4):
        message.append(decrypt[encryption[fi * 4: fi * 4 + 4]])
        if message[-1] == '«':
            message.pop()
            break
    message = ''.join(message)
    return message


# Заполняет general_association и sorted_name_list значениями из файла с кодировками
def recieve_list():
    global general_association, sorted_name_list, curselection_set
    sorted_name_list = []
    general_association = {}
    curselection_set = set()
    database = open('parole_config\\EPW.txt', 'r', encoding='utf-8')
    fblinker = 0
    fname = ''
    for fline in database:
        if fblinker == 0:
            fname = fline[:-1]
            sorted_name_list.append(fname)
        else:
            general_association[fname] = fline[:-1]
        fblinker = 1 - fblinker
    sorted_name_list.sort()
    if len(sorted_name_list) > 0:
        curselection_set.add(sorted_name_list[0])
    database.close()


# Переход на окно screen. DEBUG добавить особые изменения списка паролей для settings, get и delete
def screen_select(screen_to, screen, button):
    global screen_selection, frame_geometry, entries, buttons, frames, key_block, entry_selection, root, \
        info_text_7, info_text_13, info_text_14, get_password_list, curselection_set, general_association, \
        sorted_name_list, keyconfirm_key_entry, get_search_entry, settings_search_entry, jump_ready, \
        add_key_entry, add_name_entry, add_password_entry, settings_name_list, delete_password_list, \
        keychange_oldkey_entry, keychange_newkey_entry, keychange_password_list
    if key_block == screen + '_' + button + '_button':
        root.geometry(frame_geometry[screen_to])
        if screen_to == 'keyconfirm':
            info_text_14['text'] = ''
            keyconfirm_key_entry.focus_set()
            keyconfirm_key_entry.delete(0, tk.END)
        elif screen_to == 'get':
            get_search_entry.delete(0, tk.END)
            get_password_entry.delete(0, tk.END)
            get_search_entry.focus_set()
            recieve_list()
            jump_ready = True
            get_password_list.delete(0, tk.END)
            for fname in sorted_name_list:
                get_password_list.insert(tk.END, fname)
            if len(sorted_name_list) > 0:
                get_password_list.selection_set(0)
        elif screen_to == 'add':
            add_key_entry.focus_set()
            add_key_entry.delete(0, tk.END)
            add_name_entry.delete(0, tk.END)
            add_password_entry.delete(0, tk.END)
            info_text_7['text'] = ''
        elif screen_to == 'settings':
            settings_search_entry.delete(0, tk.END)
            settings_search_entry.focus_set()
            buttons[screen_to]['selectall']['bg'] = 'SystemButtonFace'
            buttons[screen_to]['selectall']['fg'] = 'SystemButtonText'
            buttons[screen_to]['selectall']['relief'] = tk.RAISED
            recieve_list()
            jump_ready = True
            settings_password_list.delete(0, tk.END)
            for fname in sorted_name_list:
                settings_password_list.insert(tk.END, fname)
        elif screen_to == 'delete':
            delete_password_list['state'] = tk.NORMAL
            delete_password_list['height'] = len(''.join(settings_name_list)) // 52 + 1
            root.geometry('597x' + str(181 + len(''.join(settings_name_list)) // 52 * 24) + '+100+100')
            delete_password_list.delete(1.0, tk.END)
            insertion_line = []
            for chosen_name in settings_name_list:
                insertion_line.append(chosen_name + ', ')
            delete_password_list.insert(tk.END, ''.join(insertion_line)[:-2])
            delete_password_list['state'] = tk.DISABLED
        elif screen_to == 'keychange':
            keychange_oldkey_entry.focus_set()
            keychange_oldkey_entry.delete(0, tk.END)
            keychange_newkey_entry.delete(0, tk.END)
            info_text_13['text'] = ''
            keychange_password_list['state'] = tk.NORMAL
            keychange_password_list['height'] = len(''.join(settings_name_list)) // 48 + 1
            root.geometry('550x' + str(421 + len(''.join(settings_name_list)) // 48 * 24) + '+100+100')
            keychange_password_list.delete(1.0, tk.END)
            insertion_line = []
            for chosen_name in settings_name_list:
                insertion_line.append(chosen_name + ', ')
            keychange_password_list.insert(tk.END, 'Выбранные пароли: ')
            keychange_password_list.insert(tk.END, ''.join(insertion_line)[:-2])
            keychange_password_list['state'] = tk.DISABLED
        entry_selection = 0
        frames[screen_selection].grid_remove()
        frames[screen_to].grid()
        screen_selection = screen_to


# Графический и реальный выбор кнопки на главном экране
def main_select(button):
    global buttons, main_selection
    for button_idx in buttons['main']:
        buttons['main'][button_idx]['bg'] = 'SystemButtonFace'
    buttons['main'][button]['bg'] = 'gray80'
    main_selection = button


# Графическое нажатие кнопки плюс обработка selectall
def button_press(screen, button):
    global buttons, key_block, settings_password_list
    if key_block == screen + '_' + button + '_button':
        if button != 'selectall':
            buttons[screen][button]['bg'] = 'gray80'
            buttons[screen][button]['relief'] = tk.SUNKEN
        else:
            if buttons[screen][button]['bg'] == 'SystemButtonFace':
                buttons[screen][button]['bg'] = 'SystemHighlight'
                buttons[screen][button]['fg'] = 'white'
                buttons[screen][button]['relief'] = tk.SUNKEN
                settings_password_list.selection_set(0, tk.END)
            else:
                buttons[screen][button]['bg'] = 'SystemButtonFace'
                buttons[screen][button]['fg'] = 'SystemButtonText'
                buttons[screen][button]['relief'] = tk.RAISED
                settings_password_list.selection_clear(0, tk.END)


# Графическое отжатие кнопки
def button_raise(screen, button):
    global buttons, main_selection, key_block
    if key_block == screen + '_' + button + '_button' and button != 'selectall':
        if not (screen == 'main' and main_selection == button):
            buttons[screen][button]['bg'] = 'SystemButtonFace'
        buttons[screen][button]['relief'] = tk.RAISED


# Установка кейблока
def keyblock_set(screen, button):
    global key_block
    if key_block == '':
        key_block = screen + '_' + button + '_button'


# Снятие кейблока
def keyblock_remove(screen, button):
    global key_block
    if key_block == screen + '_' + button + '_button':
        key_block = ''


# То, что происходит при нажатии клавиши/кнопки
def button_in(screen, button):
    global key_block
    if screen != 'none' and button != 'none':
        keyblock_set(screen, button)
        button_press(screen, button)
        if screen == 'main' and key_block == 'main_' + button + '_button':
            main_select(button)
    return 'break'


# То, что происходит при её отжатии
def button_out(screen, button):
    global root, key_block, keyconfirm_key_entry, get_password_list, get_password_entry, add_key_entry, \
        add_name_entry, add_password_entry, info_text_7, sorted_name_list, settings_password_list, \
        settings_name_list, general_association, keychange_oldkey_entry, keychange_newkey_entry
    if screen != 'none' and button != 'none':
        if screen == 'main':
            if button == 'get':
                screen_select('keyconfirm', screen, button)
            elif button == 'add':
                screen_select('add', screen, button)
            elif button == 'settings':
                screen_select('settings', screen, button)
            elif button == 'readme':
                screen_select('readme', screen, button)
            elif button == 'exit' and key_block == 'main_exit_button':
                root.destroy()
                return None
        elif screen == 'keyconfirm':
            if button == 'continue':
                keycode = keyconfirm_key_entry.get()
                if len(keycode) > 0:
                    recieve_encode(keycode)
                    screen_select('get', screen, button)
                else:
                    info_text_14['text'] = 'Введите ключ!'
            elif button == 'back':
                screen_select('main', screen, button)
        elif screen == 'get':
            if button == 'show':
                previous_answer = get_password_entry.get()
                get_password_entry.delete(0, tk.END)
                if len(get_password_list.curselection()) > 0:
                    final_answer = get_password_list.get(get_password_list.curselection()[0])
                    final_answer = get_password(general_association[final_answer])
                    if final_answer != previous_answer:
                        get_password_entry.insert(0, final_answer)
            elif button == 'back':
                screen_select('keyconfirm', screen, button)
        elif screen == 'add':
            if button == 'add':
                add_key_field = add_key_entry.get()
                add_name_field = add_name_entry.get()
                add_password_field = add_password_entry.get()
                recieve_list()
                if len(add_key_field) > 0 and len(add_name_field) > 0 and len(add_password_field) > 0 \
                        and add_name_field not in sorted_name_list:
                    recieve_encode(add_key_field)
                    add_password(add_name_field, add_password_field)
                    info_text_7['fg'] = 'SystemButtonText'
                    info_text_7['text'] = 'Пароль добавлен!'
                elif add_name_field in sorted_name_list:
                    info_text_7['fg'] = 'red'
                    info_text_7['text'] = 'Уже есть такое имя!'
                else:
                    info_text_7['fg'] = 'red'
                    info_text_7['text'] = 'Заполните все поля!'
            elif button == 'back':
                screen_select('main', screen, button)
        elif screen == 'settings':
            if button == 'delete':
                settings_name_list = []
                for idx in settings_password_list.curselection():
                    settings_name_list.append(settings_password_list.get(idx))
                settings_name_list.sort()
                screen_select('delete', screen, button)
            elif button == 'keychange':
                settings_name_list = []
                for idx in settings_password_list.curselection():
                    settings_name_list.append(settings_password_list.get(idx))
                settings_name_list.sort()
                screen_select('keychange', screen, button)
            elif button == 'selectall':
                pass
            elif button == 'back':
                screen_select('main', screen, button)
        elif screen == 'delete':
            if button == 'confirm':
                database = open('parole_config\\EPW.txt', 'w', encoding='utf-8')
                for pass_name in sorted_name_list:
                    if pass_name not in settings_name_list:
                        database.write(pass_name + '\n' + general_association[pass_name] + '\n')
                database.close()
                screen_select('settings', screen, button)
            elif button == 'deny':
                screen_select('settings', screen, button)
        elif screen == 'keychange':
            if button == 'change':
                change_oldkey_field = keychange_oldkey_entry.get()
                change_newkey_field = keychange_newkey_entry.get()
                if len(change_oldkey_field) > 0 and len(change_newkey_field) > 0:
                    database = open('parole_config\\EPW.txt', 'w', encoding='utf-8')
                    for pass_name in sorted_name_list:
                        if pass_name not in settings_name_list:
                            database.write(pass_name + '\n' + general_association[pass_name] + '\n')
                    database.close()
                    recieve_encode(change_oldkey_field)
                    transfer_association = {}
                    for pass_name in settings_name_list:
                        transfer_association[pass_name] = get_password(general_association[pass_name])
                    recieve_encode(change_newkey_field)
                    for pass_name in settings_name_list:
                        add_password(pass_name, transfer_association[pass_name])
                    screen_select('settings', screen, button)
                else:
                    info_text_13['text'] = 'Введите оба ключа!'
            elif button == 'back':
                screen_select('settings', screen, button)
        elif screen == 'readme':
            if button == 'back':
                screen_select('main', screen, button)
        button_raise(screen, button)
        keyblock_remove(screen, button)


def arrow_up(screen):
    global main_selection, entries, entry_selection, key_block, get_password_list, jump_ready
    if key_block == '':
        if screen == 'main':
            if main_selection == 'get': main_select('exit')
            elif main_selection == 'add': main_select('get')
            elif main_selection == 'settings': main_select('add')
            elif main_selection == 'readme': main_select('settings')
            elif main_selection == 'exit': main_select('readme')
        elif entries[screen]['amount'] > 0 and screen != 'get' and screen != 'settings':
            entry_selection -= 1
            entry_selection %= entries[screen]['amount']
            entries[screen][entry_selection].focus_set()
        elif screen == 'settings':
            entry_selection = 0
            entries['settings'][0].focus_set()


def arrow_down(screen):
    global main_selection, entries, entry_selection, key_block, get_password_list, jump_ready
    if key_block == '':
        if screen == 'main':
            if main_selection == 'get': main_select('add')
            elif main_selection == 'add': main_select('settings')
            elif main_selection == 'settings': main_select('readme')
            elif main_selection == 'readme': main_select('exit')
            elif main_selection == 'exit': main_select('get')
        elif entries[screen]['amount'] > 0 and screen != 'get' and screen != 'settings':
            entry_selection += 1
            entry_selection %= entries[screen]['amount']
            entries[screen][entry_selection].focus_set()
        elif screen == 'settings':
            entry_selection = 0
            entries['settings'][0].focus_set()


def reallocate_tab(screen):
    global entry_selection, key_block, get_password_list, get_search_entry, get_password_entry, \
        settings_search_entry, settings_password_list
    if key_block == '' and screen == 'get':
        if entry_selection == 0:
            get_password_list.focus_set()
            if len(get_password_list.curselection()) > 0:
                get_password_list.activate(get_password_list.curselection()[0])
            entry_selection = 2
        elif entry_selection == 2:
            get_password_entry.focus_set()
            entry_selection = 1
        elif entry_selection == 1:
            get_search_entry.focus_set()
            entry_selection = 0
    return 'break'


root = tk.Tk()
root.title(' Perdo le parole')
root.iconbitmap('parole_config\\key_icon.ico')
root.geometry('433x343+100+100')
root.resizable(False, False)

# Определение начального цифрового значения для каждого из печатаемых символов
# Служебные символы: » для некодируемых символов, « для остановки дешифрования
# Код под условием генерирует данные для common_association, если они ещё не сгенерированы
if not common_association_exists:
    basic_encode = open('parole_config\\common_association.txt', 'w', encoding='utf-8')
    d_frequency = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0], [8, 0], [9, 0]]
    generated_set = set()
    for i in range(161):
        d_copy = []
        for pair in d_frequency:
            d_copy.append(pair[:])
        d_copy.sort(key=lambda x: x[1])
        if d_copy[0][0] == 0:
            d_copy.insert(1, d_copy.pop(0))
        frame = ''
        for j in range(4):
            frame += str(d_copy[j][0])
        frame_int = int(frame)
        while frame_int in generated_set:
            frame_int += 1
            frame_int %= 10000
        generated_set.add(frame_int)
        frame = str(frame_int)
        for digit in frame:
            d_frequency[int(digit)][1] += 1
        basic_encode.write(frame + '\n')
    basic_encode.close()
printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
printable += '''!"#$%&'()*+,-./:;<=>?@[]^_`{|}~ ''' + '\\'
printable += 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ»«'
association_list = open('parole_config\\common_association.txt', 'r', encoding='utf-8')
common_association = {}
printable_iter = 0
for line in association_list:
    common_association[printable[printable_iter]] = int(line[:-1])
    printable_iter += 1
association_list.close()

# Объявление необходимых переменных
key_block = ''
screen_selection = 'main'
main_selection = 'get'
entry_selection = 0
AR = 'Arial'
jump_ready = False
curselection_set = set()
# Ключ = буква, значение = множество пар (строко-цифровое представление, частота использования)
core_association = {}
# Ключ = строко-цифровое представление, значение = соответствующая буква
decrypt = {}
# Ключ = буква, значение = сумма частот её строково-циформых предсталвений
frequency_sum = {}
# Ключ = имя, значение = нераскодированный пароль
general_association = {}
# Отсортированный список всех имён в файле
sorted_name_list = []
# Список имён на удаление или смену ключа
settings_name_list = []

# <<<<< ВИДЖЕТЫ >>>>>
#
# РАМКИ ДЛЯ ОКОН
#
# Рамка главного окна
main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, sticky=tk.W)
# Рамка окна со вводом ключа
keyconfirm_frame = tk.Frame(root)
keyconfirm_frame.grid(row=0, column=1, sticky=tk.W)
keyconfirm_frame.grid_remove()
# Рамка окна со списком паролей
get_frame = tk.Frame(root)
get_frame.grid(row=0, column=2, sticky=tk.W)
get_frame.grid_remove()
# Рамка окна с добавлением нового пароля
add_frame = tk.Frame(root)
add_frame.grid(row=0, column=3, sticky=tk.W)
add_frame.grid_remove()
# Рамка окна настроек
settings_frame = tk.Frame(root)
settings_frame.grid(row=0, column=4, sticky=tk.W)
settings_frame.grid_remove()
# Рамка окна подтверждения удаления
delete_frame = tk.Frame(root)
delete_frame.grid(row=0, column=5, sticky=tk.W)
delete_frame.grid_remove()
# Рамка окна смены ключа
keychange_frame = tk.Frame(root)
keychange_frame.grid(row=0, column=6)
keychange_frame.grid_remove()
# Рамка окна справки
readme_frame = tk.Frame(root)
readme_frame.grid(row=0, column=7)
readme_frame.grid_remove()
#
# ГЛАВНОЕ ОКНО
#
# Кнопка для получения пароля из списка
main_get_button = tk.Button(main_frame, text='Получить пароль из списка', font=(AR, 20), width=25, bg='gray80')
main_get_button.grid(row=0, column=0, padx=10, pady=10)
# Кнопка для добавления пароля в список
main_add_button = tk.Button(main_frame, text='Добавить пароль в список', font=(AR, 20), width=25)
main_add_button.grid(row=1, column=0, padx=10)
# Кнопка для перехода к настройкам
main_settings_button = tk.Button(main_frame, text='Настройки', font=(AR, 20), width=25)
main_settings_button.grid(row=2, column=0, pady=10, padx=10)
# Кнопка для получения справочной информации
main_readme_button = tk.Button(main_frame, text='Справка', font=(AR, 20), width=25)
main_readme_button.grid(row=3, column=0, padx=10)
# Кнопка выхода
main_exit_button = tk.Button(main_frame, text='Выход', font=(AR, 20), width=25)
main_exit_button.grid(row=4, column=0, padx=10, pady=10)
#
# ОКНО ВВОДА КЛЮЧА
#
# Информационный текст "ключ"
info_text_1 = tk.Label(keyconfirm_frame, text='Секретный ключ:', font=(AR, 20))
info_text_1.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
# Поле для ввода ключа
keyconfirm_key_entry = tk.Entry(keyconfirm_frame, font=(AR, 20), width=35)
keyconfirm_key_entry.grid(row=1, column=0, padx=10, sticky=tk.W)
# Рамка для кнопок
keyconfirm_button_frame = tk.Frame(keyconfirm_frame)
keyconfirm_button_frame.grid(row=2, column=0, padx=10, pady=20, sticky=tk.W)
# Кнопка "продолжить"
keyconfirm_continue_button = tk.Button(keyconfirm_button_frame, font=(AR, 20), text='Продолжить')
keyconfirm_continue_button.grid(row=0, column=0, sticky=tk.W)
# Текст для ошибки
info_text_14 = tk.Label(keyconfirm_button_frame, font=(AR, 20), text='', fg='red', width=14)
info_text_14.grid(row=0, column=1, padx=5, sticky=tk.W)
# Кнопка "назад"
keyconfirm_back_button = tk.Button(keyconfirm_button_frame, font=(AR, 20), text='Назад')
keyconfirm_back_button.grid(row=0, column=2, padx=10)
#
# ОКНО ДЛЯ ПОЛУЧЕНИЯ ПАРОЛЕЙ
#
# Рамка поисковика
get_search_frame = tk.Frame(get_frame)
get_search_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
# Информационный текст "поиск"
info_text_2 = tk.Label(get_search_frame, text='Поиск:', font=(AR, 20))
info_text_2.grid(row=0, column=0, sticky=tk.W)
# Поле для ввода запроса на поиск
get_search_entry = tk.Entry(get_search_frame, width=35, font=(AR, 20))
get_search_entry.grid(row=0, column=1, padx=24, sticky=tk.W)
# Список паролей
get_password_list = tk.Listbox(get_frame, width=58, height=15, font=(AR, 14))
get_password_list['activestyle'] = 'none'
get_password_list.grid(row=1, column=0, columnspan=2, padx=10, sticky=tk.W)
# Рамка для выдачи пароля
get_password_frame = tk.Frame(get_frame)
get_password_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
# Информационный текст "пароль"
info_text_3 = tk.Label(get_password_frame, text='Пароль:', font=(AR, 20))
info_text_3.grid(row=0, column=0, sticky=tk.E)
# Поле для выдачи пароля
get_password_entry = tk.Entry(get_password_frame, width=35, font=(AR, 20))
get_password_entry.grid(row=0, column=1, padx=5)
# Кнопка для отображения пароля
get_show_button = tk.Button(get_frame, text='Показать', font=(AR, 20))
get_show_button.grid(row=3, column=0, padx=10, sticky=tk.W)
# Кнопка для возвращения на предыдущий экран
get_back_button = tk.Button(get_frame, text='Назад', font=(AR, 20))
get_back_button.grid(row=3, column=1, padx=394)
#
# ОКНО ДЛЯ ДОБАВЛЕНИЯ ПАРОЛЕЙ
#
# Информационный текст "ключ"
info_text_4 = tk.Label(add_frame, font=(AR, 20), text='Секретный ключ:')
info_text_4.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
# Поле для ввода ключа
add_key_entry = tk.Entry(add_frame, font=(AR, 20), width=35)
add_key_entry.grid(row=1, column=0, padx=10, sticky=tk.W)
# Информационный текст "имя пароля"
info_text_5 = tk.Label(add_frame, text='Имя (название) пароля:', font=(AR, 20))
info_text_5.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
# Поле для ввода имени пароля
add_name_entry = tk.Entry(add_frame, font=(AR, 20), width=35)
add_name_entry.grid(row=3, column=0, padx=10, sticky=tk.W)
# Информационный текст "пароль"
info_text_6 = tk.Label(add_frame, font=(AR, 20), text='Пароль:')
info_text_6.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
# Поле для ввода пароля
add_password_entry = tk.Entry(add_frame, font=(AR, 20), width=35)
add_password_entry.grid(row=5, column=0, padx=10, sticky=tk.W)
# Рамка для кнопок перемещения
add_button_frame = tk.Frame(add_frame)
add_button_frame.grid(row=6, column=0, padx=10, pady=20, sticky=tk.W)
# Кнопка "добавить"
add_add_button = tk.Button(add_button_frame, font=(AR, 20), text='Добавить')
add_add_button.grid(row=0, column=0)
# Информационный текст "успех/ошибка"
info_text_7 = tk.Label(add_button_frame, font=(AR, 20), width=17, text='')
info_text_7.grid(row=0, column=1, padx=4)
# Кнопка "назад"
add_back_button = tk.Button(add_button_frame, font=(AR, 20), text='Назад')
add_back_button.grid(row=0, column=2)
#
# ОКНО НАСТРОЕК
#
# Рамка для поисковика
settings_search_frame = tk.Frame(settings_frame)
settings_search_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
# Инофрмационный текст "поиск"
info_text_8 = tk.Label(settings_search_frame, text='Поиск:', font=(AR, 20))
info_text_8.grid(row=0, column=0, sticky=tk.W)
# Поле для ввода запроса на поиск
settings_search_entry = tk.Entry(settings_search_frame, width=35, font=(AR, 20))
settings_search_entry.grid(row=0, column=1, padx=23, sticky=tk.W)
# Список паролей
settings_password_list = tk.Listbox(settings_frame, width=58, height=15, font=(AR, 14))
settings_password_list['activestyle'] = 'none'
settings_password_list['selectmode'] = tk.MULTIPLE
settings_password_list.grid(row=1, column=0, padx=10, sticky=tk.W)
# Рамка для кнопок
settings_button_frame = tk.Frame(settings_frame)
settings_button_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
# Кнопка "удалить"
settings_delete_button = tk.Button(settings_button_frame, text='Удалить', width=13, font=(AR, 20))
settings_delete_button.grid(row=0, column=0, sticky=tk.W)
# Кнопка "сменить ключ"
settings_keychange_button = tk.Button(settings_button_frame, text='Сменить ключ', width=13, font=(AR, 20))
settings_keychange_button.grid(row=1, column=0, pady=10, sticky=tk.W)
# Кнопка "выделить все"
settings_selectall_button = tk.Button(settings_button_frame, text='Выделить все', width=13, font=(AR, 20))
settings_selectall_button.grid(row=0, column=1, padx=205, sticky=tk.W)
# Кнопка "назад"
settings_back_button = tk.Button(settings_button_frame, text='Назад', width=13, font=(AR, 20))
settings_back_button.grid(row=1, column=1, pady=10, padx=205, sticky=tk.W)
#
# ОКНО ПОДТВЕРЖДЕНИЯ УДАЛЕНИЯ
#
# Информационный текст "а вы точно хотите?"
info_text_9 = tk.Label(delete_frame, text='Вы уверены, что хотите удалить эти пароли?', font=(AR, 20))
info_text_9.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
# Список паролей для удаления
delete_password_list = tk.Text(delete_frame, font=(AR, 14), width=52, height=1)
delete_password_list['state'] = tk.DISABLED
delete_password_list.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
# Кнопка подтверждения
delete_confirm_button = tk.Button(delete_frame, width=8, font=(AR, 20), text='Да')
delete_confirm_button.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
# Кнопка неподтверждения
delete_deny_button = tk.Button(delete_frame, width=8, font=(AR, 20), text='Нет')
delete_deny_button.grid(row=2, column=1, padx=290, pady=10, sticky=tk.W)
#
# ОКНО СМЕНЫ КЛЮЧА
#
# Список паролей для удаления
keychange_password_list = tk.Text(keychange_frame, font=(AR, 14), width=48, height=1)
keychange_password_list['state'] = tk.DISABLED
keychange_password_list.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W)
# Информационный текст "старый ключ"
info_text_10 = tk.Label(keychange_frame, font=(AR, 20), text='Старый секретный ключ:')
info_text_10.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W)
# Поле для ввода старого ключа
keychange_oldkey_entry = tk.Entry(keychange_frame, font=(AR, 20), width=35)
keychange_oldkey_entry.grid(row=2, column=0, columnspan=3, padx=10, sticky=tk.W)
# Информационный текст "новый ключ"
info_text_11 = tk.Label(keychange_frame, font=(AR, 20), text='Новый секретный ключ:')
info_text_11.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky=tk.W)
# Поле для ввода нового ключа
keychange_newkey_entry = tk.Entry(keychange_frame, font=(AR, 20), width=35)
keychange_newkey_entry.grid(row=4, column=0, columnspan=3, padx=10, sticky=tk.W)
# Информационный текст "семь раз отмерь"
info_text_12 = tk.Label(keychange_frame, font=(AR, 20), fg='red')
info_text_12['text'] = 'Прежде чем продолжить, убедитесь в\n'
info_text_12['text'] += 'правильности обоих введённых ключей!\n'
info_text_12['text'] += 'Вы рискуете потерять информацию!'
info_text_12.grid(row=5, column=0, columnspan=3, padx=18, pady=10, sticky=tk.W)
# Кнопка "изменить"
keychange_change_button = tk.Button(keychange_frame, font=(AR, 20), text='Изменить')
keychange_change_button.grid(row=6, column=0, padx=10, sticky=tk.W)
# Текст для отображения ошибки
info_text_13 = tk.Label(keychange_frame, font=(AR, 20), fg='red', text='', width=15)
info_text_13.grid(row=6, column=1, padx=7, sticky=tk.W)
# Кнопка "назад"
keychange_back_button = tk.Button(keychange_frame, font=(AR, 20), text='Назад')
keychange_back_button.grid(row=6, column=2, padx=10, sticky=tk.W)
#
# ОКНО СПРАВКИ
#
# Справочный текст
readme_readme_text = tk.Text(readme_frame, font=(AR, 14), width=50, height=15)
readme_readme_text.insert(tk.END, 'Добро пожаловать в программу для запароливания паролей!\n')
readme_readme_text.insert(tk.END, '\n')
readme_readme_text.insert(tk.END, 'Эта небольшая утилита предоставляет пользователю возмож-\n')
readme_readme_text.insert(tk.END, 'ность одновременно:\n')
readme_readme_text.insert(tk.END, '1) сохранить все его пароли от различных сервисов в одном\n')
readme_readme_text.insert(tk.END, 'месте\n')
readme_readme_text.insert(tk.END, '2) обеспечить быстрый доступ к ним через компьютер\n')
readme_readme_text.insert(tk.END, '3) надёжно защитить их от злоумышленников\n')
readme_readme_text.insert(tk.END, 'Всё, что для этого требуется сделать - придумать один-един-\n')
readme_readme_text.insert(tk.END, 'ственный пароль, называемый "секретным ключом", который\n')
readme_readme_text.insert(tk.END, 'будет использоваться программой для защиты всех осталь-\n')
readme_readme_text.insert(tk.END, 'ных, сохранённых в ней.\n')
readme_readme_text.insert(tk.END, '\n')
readme_readme_text.insert(tk.END, 'Обратите внимание, что для перемещения по окнам програм-\n')
readme_readme_text.insert(tk.END, 'мы вы можете использовать клавиши enter (вперёд), escape\n')
readme_readme_text.insert(tk.END, '(назад), клавиши со стрелочками, горячие клавиши ctrl + s\n')
readme_readme_text.insert(tk.END, '(сменить ключ), ctrl + d (удалить) в окне настроек и Tab в окне\n')
readme_readme_text.insert(tk.END, 'получения пароля.\n')
readme_readme_text.insert(tk.END, 'Также имейте в виду, что для корректной работы программы\n')
readme_readme_text.insert(tk.END, 'необходимо наличие папки paroles_config рядом с исполняе-\n')
readme_readme_text.insert(tk.END, 'мым файлом Perdo le parole.exe.\n')
readme_readme_text.insert(tk.END, '\n')
readme_readme_text.insert(tk.END, 'Начните работу с программой, нажав кнопку "Добавить пароль\n')
readme_readme_text.insert(tk.END, 'в список". Заполните соответствующие поля:\n')
readme_readme_text.insert(tk.END, '> Секретный ключ - любая последовательность символов, ко-\n')
readme_readme_text.insert(tk.END, 'торую можно ввести со стандартной русско-английской клави-\n')
readme_readme_text.insert(tk.END, 'атуры. Ваши пароли хранятся в программе в зашифрованном\n')
readme_readme_text.insert(tk.END, 'виде, и секретный ключ нужен как для того, чтобы сгенериро-\n')
readme_readme_text.insert(tk.END, 'вать этот шифр, так и для того, чтобы расшифровать пароли,\n')
readme_readme_text.insert(tk.END, 'когда вам потребуется получить к ним доступ. В связи с этим\n')
readme_readme_text.insert(tk.END, 'рекомендуется использовать один и тот же секретный ключ\n')
readme_readme_text.insert(tk.END, 'для добавления всех ваших паролей, однако это правило не\n')
readme_readme_text.insert(tk.END, 'является обязательным.\n')
readme_readme_text.insert(tk.END, '> Имя (название) пароля - любая последовательность симво-\n')
readme_readme_text.insert(tk.END, 'лов. Имя пароля не будет зашифровано, и именно его вы бу-\n')
readme_readme_text.insert(tk.END, 'дете видеть в выпадающем списке паролей. Имена не могут\n')
readme_readme_text.insert(tk.END, 'повторяться.\n')
readme_readme_text.insert(tk.END, '> Пароль - любая последовательность символов, которую\n')
readme_readme_text.insert(tk.END, 'можно ввести со стандартной русско-английской клавиатуры.\n')
readme_readme_text.insert(tk.END, 'Зашифрованные с помощью секретного ключа пароли хранят-\n')
readme_readme_text.insert(tk.END, 'ся в файле EPW.txt папки parole_config (она должна находить-\n')
readme_readme_text.insert(tk.END, 'ся в том же месте, что и файл программы perdo le parole.exe),\n')
readme_readme_text.insert(tk.END, 'и их невозможно расшифровать без секретного ключа, полно-\n')
readme_readme_text.insert(tk.END, 'стью совпадающего с тем, что был использован при их добав-\n')
readme_readme_text.insert(tk.END, 'лении, поэтому внимательно заполняйте все поля при работе\n')
readme_readme_text.insert(tk.END, 'с этой программой.\n')
readme_readme_text.insert(tk.END, '\n')
readme_readme_text.insert(tk.END, 'Если вы по ошибке ввели в поле секретного ключа или пароля\n')
readme_readme_text.insert(tk.END, 'символ, которого нет на стандартной клавиатуре, он будет за-\n')
readme_readme_text.insert(tk.END, 'менён на служебный символ ».\n')
readme_readme_text.insert(tk.END, '\n')
readme_readme_text.insert(tk.END, 'После того, как вы добавили пароли в список, нажмите "Полу-\n')
readme_readme_text.insert(tk.END, 'чить пароль из списка", чтобы обратиться к ним. Введите сек-\n')
readme_readme_text.insert(tk.END, 'ретный ключ, и перед вами развернётся список названий па-\n')
readme_readme_text.insert(tk.END, 'ролей. Выберите любой из них и нажмите "Показать". Если\n')
readme_readme_text.insert(tk.END, 'введённый вами секретный ключ совпадёт с тем, что был ис-\n')
readme_readme_text.insert(tk.END, 'пользован при добавлении этого пароля, то верная расшиф-\n')
readme_readme_text.insert(tk.END, 'ровка отобразится в нижней строке. Нажмите "Показать" ещё\n')
readme_readme_text.insert(tk.END, 'раз, чтобы скрыть эту расшифровку.\n')
readme_readme_text.insert(tk.END, '\n')
readme_readme_text.insert(tk.END, 'Используйте окно "Настройки", чтобы взаимодействовать с\n')
readme_readme_text.insert(tk.END, 'вашим списком: удалять пароли из него и изменять ключи, ис-\n')
readme_readme_text.insert(tk.END, 'пользуемые для их шифрования. Будьте особенно аккуратны:\n')
readme_readme_text.insert(tk.END, 'удаление необратимо, как и смена ключа, причём единствен-\n')
readme_readme_text.insert(tk.END, 'ная ошибка в старом или новом ключе приведёт к потере всей\n')
readme_readme_text.insert(tk.END, 'информации о задействованных паролях.\n')
readme_readme_text.insert(tk.END, '\n')
readme_readme_text.insert(tk.END, 'Желаю приятного взаимодейсвтия с программой!\n')
readme_readme_text.insert(tk.END, 'Обратная связь: vk.com/2rainboom\n')
readme_readme_text.insert(tk.END, ' \n                                              ')
readme_readme_text.insert(tk.END, '                                 by Aberone, 2019')
readme_readme_text['state'] = tk.DISABLED
readme_readme_text.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
# Кнопка "назад"
readme_back_button = tk.Button(readme_frame, font=(AR, 20), text='Назад')
readme_back_button.grid(row=1, column=0, padx=463, sticky=tk.W)

# Объявление ещё необходимых переменных
buttons = {'main': {'get': main_get_button, 'add': main_add_button, 'settings': main_settings_button,
                    'readme': main_readme_button, 'exit': main_exit_button},
           'keyconfirm': {'continue': keyconfirm_continue_button, 'back': keyconfirm_back_button},
           'get': {'show': get_show_button, 'back': get_back_button},
           'add': {'add': add_add_button, 'back': add_back_button},
           'settings': {'delete': settings_delete_button, 'keychange': settings_keychange_button,
                        'selectall': settings_selectall_button, 'back': settings_back_button},
           'delete': {'confirm': delete_confirm_button, 'deny': delete_deny_button},
           'keychange': {'change': keychange_change_button, 'back': keychange_back_button},
           'readme': {'back': readme_back_button}}
entries = {'main': {'amount': 0},
           'keyconfirm': {'amount': 1, 0: keyconfirm_key_entry},
           'get': {'amount': 2, 0: get_search_entry, 1: get_password_entry},
           'add': {'amount': 3, 0: add_key_entry, 1: add_name_entry, 2: add_password_entry},
           'settings': {'amount': 1, 0: settings_search_entry},
           'delete': {'amount': 0},
           'keychange': {'amount': 2, 0: keychange_oldkey_entry, 1: keychange_newkey_entry},
           'readme': {'amount': 0}}
frames = {'main': main_frame, 'keyconfirm': keyconfirm_frame, 'get': get_frame, 'add': add_frame,
          'settings': settings_frame, 'delete': delete_frame, 'keychange': keychange_frame, 'readme': readme_frame}
frame_geometry = {'main': '433x343+100+100', 'keyconfirm': '550x183+100+100', 'get': '663x532+100+100',
                  'add': '550x367+100+100', 'settings': '661x549+100+100', 'delete': '597x181+100+100',
                  'keychange': '550x421+100+100', 'readme': '575x420+100+100'}
button_forward = {'main': 'ERROR', 'keyconfirm': 'continue', 'get': 'show', 'add': 'add',
                  'settings': 'selectall', 'delete': 'confirm', 'keychange': 'change', 'readme': 'none'}
button_back = {'main': 'exit', 'keyconfirm': 'back', 'get': 'back', 'add': 'back',
               'settings': 'back', 'delete': 'deny', 'keychange': 'back', 'readme': 'back'}

# <<<<< БИНДЫ >>>>>
#
# Кнопки: отмена стандартной реакции и подключение к главным определяющим функциям
# screen_belong и button_belong: ключ = объект кнопки, значение = строковые соответствующие ей экран и имя
screen_belong = {}
button_belong = {}
for screen_idx in buttons:
    for button_idx in buttons[screen_idx]:
        screen_belong[buttons[screen_idx][button_idx]] = screen_idx
        button_belong[buttons[screen_idx][button_idx]] = button_idx
        buttons[screen_idx][button_idx].bind('<Button-1>', lambda e: button_in(screen_belong[e.widget],
                                                                               button_belong[e.widget]))
        buttons[screen_idx][button_idx].bind('<ButtonRelease-1>', lambda e: button_out(screen_belong[e.widget],
                                                                                       button_belong[e.widget]))
# Установка энтри_селекшна при клике по полю ввода
# entry_belong: ключ = объект поля ввода, значение = соответствующий ему индекс
def set_entry_selection(event):
    global entry_selection, entry_belong
    entry_selection = entry_belong[event.widget]
entry_belong = {}
for screen_idx in entries:
    for entry_idx in entries[screen_idx]:
        if entry_idx != 'amount':
            entry_belong[entries[screen_idx][entry_idx]] = entry_idx
            entries[screen_idx][entry_idx].bind('<Button-1>', set_entry_selection)
# Enter и Esc: перенаправление на кнопочные команды
def enter_in(event):
    global screen_selection, main_selection, button_forward
    if screen_selection != 'main':
        button_in(screen_selection, button_forward[screen_selection])
    else:
        button_in('main', main_selection)
root.bind('<Return>', enter_in)
def enter_out(event):
    global screen_selection, main_selection, button_forward
    if screen_selection != 'main':
        button_out(screen_selection, button_forward[screen_selection])
    else:
        button_out('main', main_selection)
root.bind('<KeyRelease-Return>', enter_out)
root.bind('<Escape>', lambda e: button_in(screen_selection, button_back[screen_selection]))
root.bind('<KeyRelease-Escape>', lambda e: button_out(screen_selection, button_back[screen_selection]))
# Стрелочки вверх-вниз
root.bind('<Up>', lambda e: arrow_up(screen_selection))
root.bind('<Down>', lambda e: arrow_down(screen_selection))
# Поиск для get и settings
def get_search_resort(event):
    global sorted_name_list, get_search_entry, get_password_list, curselection_set
    search_request = get_search_entry.get()
    curselection_set = set(get_password_list.get(idx) for idx in get_password_list.curselection())
    get_password_list.delete(0, tk.END)
    has_one_elem = False
    for pass_name in sorted_name_list:
        if search_request in pass_name:
            has_one_elem = True
            get_password_list.insert(tk.END, pass_name)
            if pass_name in curselection_set:
                get_password_list.selection_set(tk.END)
        else:
            curselection_set.discard(pass_name)
    if len(curselection_set) == 0 and has_one_elem:
        get_password_list.selection_set(0)
        curselection_set.add(get_password_list.get(0))
get_search_entry.bind('<KeyRelease>', get_search_resort)
def settings_search_resort(event):
    global sorted_name_list, settings_search_entry, settings_password_list, curselection_set
    search_request = settings_search_entry.get()
    curselection_set = set(settings_password_list.get(idx) for idx in settings_password_list.curselection())
    settings_password_list.delete(0, tk.END)
    has_one_elem = False
    for pass_name in sorted_name_list:
        if search_request in pass_name:
            has_one_elem = True
            settings_password_list.insert(tk.END, pass_name)
            if pass_name in curselection_set:
                settings_password_list.selection_set(tk.END)
        else:
            curselection_set.discard(pass_name)
settings_search_entry.bind('<KeyRelease>', settings_search_resort)
# Горячие клавиши ctrl+c и ctrl+d для окна настроек
root.bind('<Control-s>', lambda e: button_in('settings', 'keychange')
          if screen_selection == 'settings' else None)
root.bind('<KeyRelease-s>', lambda e: button_out('settings', 'keychange')
          if screen_selection == 'settings' else None)
root.bind('<Control-d>', lambda e: button_in('settings', 'delete')
          if screen_selection == 'settings' else None)
root.bind('<KeyRelease-d>', lambda e: button_out('settings', 'delete')
          if screen_selection == 'settings' else None)
# Смена стандартной Tab-реакции на перемещение по окну выдачи пароля
root.bind('<Tab>', lambda e: reallocate_tab(screen_selection))
# Исправление ошибки, в связи с которой ctrl + a снимает выделение со списков паролей
def entry_ctrl_a(screen, entry_idx):
    global get_password_list, entries
    if screen == 'get':
        selection_indexes_set = set(get_password_list.curselection())
        entries[screen][entry_idx].selection_range(0, tk.END)
        for select_idx in selection_indexes_set:
            get_password_list.selection_set(select_idx)
    elif screen == 'settings':
        selection_indexes_set = set(settings_password_list.curselection())
        entries[screen][entry_idx].selection_range(0, tk.END)
        for select_idx in selection_indexes_set:
            settings_password_list.selection_set(select_idx)
    return 'break'
get_search_entry.bind('<Control-a>', lambda e: entry_ctrl_a('get', 0))
get_password_entry.bind('<Control-a>', lambda e: entry_ctrl_a('get', 1))
settings_search_entry.bind('<Control-a>', lambda e: entry_ctrl_a('settings', 0))

root.mainloop()
