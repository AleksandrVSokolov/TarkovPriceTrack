

### TarkovPriceTrack (ENG)

This repository contains scripts for automated price taking in the game Escape from Tarkov (EFT) (registered trademark fully owned by Battlestate Games), using tarkov.dev API.

Item names are shown in russian as this game is initially designed for the language. To sey scripts to other languages, you need to modify queries submitted to tarkov.dev API (field "lang").

#### Requirements

 - Working python environment that is compatible with packages below
 - pandas
 - mplfinance
 - matplotlib
 - requests
 - time
 - numpy
 - datetime
 - os
 - openpyxl
 - tqdm
 - To run .ipynb, you would need local installation of Jupyter Notebook


#### Functionalities
Please see the helper_functions.py script for and Tarkov_price_tracking.ipynb for detailed descriptions.
Briefly, theses scripts allow tracking historical price changes for any item in EFT during last 7 days. It could be used to identify items that are currently undervalued or overvalued. Additionally, script also allows identify reselling opportunities of trader items to the flea market and the minimal profitable price to resell the item at.

#### Considerations
Since we are not modifying any game files/data, not doing anything to negatively affect other players, and only use public data from the web, this is not cheating. This set of tools could make you more informed when you trade items at the flea market. Additionally, it makes flea market more efficient. UNDER ANY CIRCUMSTANCES, DO NOT MAKE TRADING BOTS WITH THIS SOFTWARE. AUTHOR HAS NO RESPONSIBILITY IF Battlestate Games bans your account for whatever reason.


### TarkovPriceTrack (RUS)

Этот репозиторий содержит скрипты для автоматического получения цен в игре Escape from Tarkov (EFT) (зарегистрированная торговая марка, полностью принадлежащая Battlestate Games), использующий API tarkov.dev.

Названия предметов отображаются на русском языке, так как игра изначально разработана для этого языка. Чтобы использовать скрипты на других языках, вам необходимо изменить запросы, отправленные в API tarkov.dev (поле "lang").

#### Требования

- Рабочая среда Python, совместимая с пакетами ниже
- pandas
- mplfinance
- matplotlib
- requests
- time
- numpy
- datetime
- os
- openpyxl
- tqdm
- Для запуска .ipynb вам потребуется локальная установка Jupyter Notebook

#### Функциональность
Подробные описания см. в скрипте helper_functions.py и Tarkov_price_tracking.ipynb.

Вкратце, эти скрипты позволяют отслеживать исторические изменения цен на любой предмет в EFT за последние 7 дней. Его можно использовать для определения предметов, которые в настоящее время недооценены или переоценены. Кроме того, скрипт также позволяет определять выгодные возможности перепродажи товаров трейдеров на барахолке и минимальную прибылбную цену для перепродажи предмета.

#### Соображения
Поскольку мы не изменяем никакие игровые файлы/данные, не делаем ничего, что могло бы негативно повлиять на других игроков, и используем только общедоступные данные из Интернета, это не является читерством. Этот набор скриптов поможет вам быть более информированными при торговле предметами на барахолке в EFT. Кроме того, он делает блошиный рынок более эффективным. НИ ПРИ КАКИХ ОБСТОЯТЕЛЬСТВАХ НЕ СОЗДАВАЙТЕ ТОРГОВЫХ БОТОВ С ПОМОЩЬЮ ДАННОГО ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ. АВТОР НЕ НЕСЕТ ОТВЕТСТВЕННОСТИ, если Battlestate Games заблокирует ваш аккаунт по какой-либо причине.