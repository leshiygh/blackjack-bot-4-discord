"""Конфигурационные данные"""
STATIC_PATH = 'static'

# карты
SUITS = ['heart', 'diamond', 'club', 'spade']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']

# пути до карт
PRINTED = {
    '2_heart': 'static/source_img/2-1.png', '2_diamond': 'static/source_img/2-2.png',
    '2_spade': 'static/source_img/2-3.png', '2_club': 'static/source_img/2-4.png',
    '3_heart': 'static/source_img/3-1.png', '3_diamond': 'static/source_img/3-2.png',
    '3_spade': 'static/source_img/3-3.png', '3_club': 'static/source_img/3-4.png',
    '4_heart': 'static/source_img/4-1.png', '4_diamond': 'static/source_img/4-2.png',
    '4_spade': 'static/source_img/4-3.png', '4_club': 'static/source_img/4-4.png',
    '5_heart': 'static/source_img/5-1.png', '5_diamond': 'static/source_img/5-2.png',
    '5_spade': 'static/source_img/5-3.png', '5_club': 'static/source_img/5-4.png',
    '6_heart': 'static/source_img/6-1.png', '6_diamond': 'static/source_img/6-2.png',
    '6_spade': 'static/source_img/6-3.png', '6_club': 'static/source_img/6-4.png',
    '7_heart': 'static/source_img/7-1.png', '7_diamond': 'static/source_img/7-2.png',
    '7_spade': 'static/source_img/7-3.png', '7_club': 'static/source_img/7-4.png',
    '8_heart': 'static/source_img/8-1.png', '8_diamond': 'static/source_img/8-2.png',
    '8_spade': 'static/source_img/8-3.png', '8_club': 'static/source_img/8-4.png',
    '9_heart': 'static/source_img/9-1.png', '9_diamond': 'static/source_img/9-2.png',
    '9_spade': 'static/source_img/9-3.png', '9_club': 'static/source_img/9-4.png',
    '10_heart': 'static/source_img/10-1.png', '10_diamond': 'static/source_img/10-2.png',
    '10_spade': 'static/source_img/10-3.png', '10_club': 'static/source_img/10-4.png',
    'jack_heart': 'static/source_img/V-1.png', 'jack_diamond': 'static/source_img/V-2.png',
    'jack_spade': 'static/source_img/V-3.png', 'jack_club': 'static/source_img/V-4.png',
    'queen_heart': 'static/source_img/Q-1.png', 'queen_diamond': 'static/source_img/Q-2.png',
    'queen_spade': 'static/source_img/Q-3.png', 'queen_club': 'static/source_img/Q-4.png',
    'king_heart': 'static/source_img/K-1.png', 'king_diamond': 'static/source_img/K-2.png',
    'king_spade': 'static/source_img/K-3.png', 'king_club': 'static/source_img/K-4.png',
    'ace_heart': 'static/source_img/T-1.png', 'ace_diamond': 'static/source_img/T-2.png',
    'ace_spade': 'static/source_img/T-3.png', 'ace_club': 'static/source_img/T-4.png'
}

# сообщения по запросу правил
info_1 = '''```
    <<<Правила>>>
Цель игрока - собрать руку, сумма очков в которой превышает сумму очков у дилера. Важно 
собрать не более 21 очка, в ином случае игрок проиграет (перебор).

Для игры используется колода из 52 карт. Для участия в игре игрок должен сделать ставку. После того 
как все ставки сделаны, дилер раздает игрокам по две карты в открытую, а себе одну открытую и одну закрытую карты.

После того как игрок и дилер завершили брать карты, сравниваются значения финальных рук дилера и игрока. Если сумма 
очков у игрока больше, чем у дилера, то он получает выплату 1 к 1 от своей ставки. Если суммы очков равны (за 
исключением блэкджек), то это ничья и игроку возвращается его ставка. Если же дилер набрал больше очков, 
то игрок проигрывает.

    <<<Блэкджек>>> (пока не реализовано)
Если первые две карты в сумме дают 21 очко,   то такая комбинация называется блэкджек.   Если дилер собрал 
блэкджек, то все игроки проигрывают, кроме  тех, у кого тоже блэкджек. Такой случай   считается ничьей, 
и ставка возвращается игроку. 

Если игрок собрал блэкджек, а дилер нет, то игрок выигрывает и получает выплату 3 к 2 от своей ставки.

Если открытая карта дилера стоит 10 очков, то дилер смотрит свою закрытую карту. В случае если собралась комбинация 
блэкджек, дилер открывает свои карты и раунд игры заканчивается. 

    <<<Действия игрока>>>   
Если у дилера и игрока нет блэкджека, то, получив карты, игрок может выбрать одно из нескольких действий.

“Еще”. Игрок берет дополнительную карту. Это действие можно повторять, пока сумма очков не превышает 21
“Хватит”. Игрок фиксирует свои карты.

Если игрок набрал более 21 очков, то он проигрывает раунд.

    <<<Дилер>>>
После того как игроки зафиксировали свои карты, дилер открывает закрытую карту.

При необходимости дилер берет дополнительные карты до тех пор, пока сумма очков не будет 17 или выше. Если количество
очков дилера превысит 21, то все не выбывшие игроки автоматически выигрывают, вне зависимости от количества очков.
``` '''

info_2 = '''```
    <<<Выплаты>>>
Ставка 1 к 1; 
Блэкджек 3 к 2; (пока не реализовано)
Ничья Ставка возвращается; 
Перебор	Ставка проигрывает;

    <<<Подсчет очков>>>
При подсчете очков учитываются значения карт: карты от 2 до 10 дают количество очков, равное своему 
достоинству, карты J, Q, K дают 10 очков. Туз стоит 11 очков. ```'''

# координаты для карты в "руке"
coord = {
    1: [(752, 233)],
    2: [(530, 233), (979, 233)],
    3: [(82, 233), (530, 233), (979, 233)],
    4: [(82, 233), (530, 233), (979, 233), (1427, 233)]
}

# Список id кнопок-ставок
bet_id = ('bet_10', 'bet_20', 'bet_30', 'bet_40', 'bet_50', 'bet_100', 'bet_200', 'bet_300', 'bet_500', 'bet_1000')
