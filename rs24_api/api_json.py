import requests
import json

from . import auth


HEADERS = {
    'Authorization': auth.get_auth_token()
}


def get_storages():
    """Данный метод используется для получения актуального справочника складов.
    Идентификатор склада необходимо будет указывать для получения списка позиций и
    получения информации об остатках по определенной позиции.
    Поля:
    <ORGANIZATION_ID> – идентификатор склада.
    <NAME> – наименование склада.
    """

    storages_url = 'https://cdis.russvet.ru/rs/stocks'
    resp = requests.get(url=storages_url, headers=HEADERS)
    return json.loads(resp.content)


def get_storage_by_city(city):
    storages = get_storages()
    storage = [i for i in storages['Stocks'] if i['NAME'] == city][0]
    return storage


def _get_positions(storage_id, category, page=0):
    """Данный метод используется для получения списка позиций.
    Параметр «категория позиций» определяет, какие позиции будут выгружаться в ответе.
    Если указать значение «custom», то мы получаем список позиций, которые привозятся под заказ.
    Если указать значение «instock», то в списке будут отображены позиции, относящиеся к складской
    номенклатуре на выбранном складе.
    Поля:
    <CODE> – артикул позиции Русского Света
    <NAME> – наименование позиции
    <BRAND> – бренд
    <CATEGORY> – категория позиции (складская/заказная/новинка/…)
    <rows count> – количество позиций
    <last_page > – номер последней страницы
    """

    positions_url = f"https://cdis.russvet.ru/rs/position/{storage_id}/{category}?page={page}"
    resp = requests.get(url=positions_url, headers=HEADERS)
    return json.loads(resp.content)


def get_positions_in_stock(storage_id, page=0):
    """Данный метод используется для получения списка позиций относящиеся к складской
    номенклатуре на выбранном складе.
    Поля:
    <CODE> – артикул позиции Русского Света
    <NAME> – наименование позиции
    <BRAND> – бренд
    <CATEGORY> – категория позиции (складская/заказная/новинка/…)
    <rows count> – количество позиций
    <last_page > – номер последней страницы
    """

    return _get_positions(storage_id, 'instock', page)


def get_positions_by_order(storage_id, page=0):
    """Данный метод используется для получения списка позиций
    которые привозятся под заказ.
    Поля:
    <CODE> – артикул позиции Русского Света
    <NAME> – наименование позиции
    <BRAND> – бренд
    <CATEGORY> – категория позиции (складская/заказная/новинка/…)
    <rows count> – количество позиций
    <last_page > – номер последней страницы
    """

    return _get_positions(storage_id, 'custom', page)


def get_prices(position_code):
    """Данный метод используется для получения информации о ценах по выбранной позиции.
    Поля:
    <Personal> – Цена клиента с учетом скидок без НДС
    <Retail> – Розничная цена без НДС
    """

    prices_url = f"https://cdis.russvet.ru/rs/price/{position_code}"
    resp = requests.get(url=prices_url, headers=HEADERS)
    return json.loads(resp.content)


def get_remainder(storage_id, position_code):
    """Данный метод используется для получения информации о доступном количестве выбранной позиции на выбранном складе.
    Поля:
    <Residue> – свободное количество
    <UOM> – единица измерения
    """

    remainder_url = f"https://cdis.russvet.ru/rs/residue/{storage_id}/{position_code}"
    resp = requests.get(url=remainder_url, headers=HEADERS)
    return json.loads(resp.content)


def get_specs(position_code):
    """Данный метод используется для получения основной информации о позиции а также
    технических характеристик в формате ETIM и ссылок на изображения без водяных знаков.
    Поля:
    Info – блок с основной информацией
    <DESCRIPTION> – наименование позиции
    <PRIMARY_UOM> – единица измерения
    <MULTIPLICITY> – кратность заказа у производителя. Используется для заказных позиций,
    которых нет в наличии на складах РС.
    <ITEMS_PER_UNIT> – количество штук в упаковке
    <ETIM_CLASS> – код класса ETIM
    <ETIM_CLASS_NAME> – наименование класса ETIM
    <ETIM_GROUP> – код группы ETIM
    <ETIM_GROUP_NAME> – наименование группы ETIM
    barcode – информация о штрихкодах
    <EAN> – штрихкод
    <DESCRIPTION> – описание штрихкода
    specs – технические характеристики
    <NAME> – наименование характеристики
    <VALUE> – значение характеристики
    <UOM> – единица измерения
    img – ссылки на изображения
    <URL> – ссылка на изображение
    """

    specs_url = f"https://cdis.russvet.ru/rs/specs/{position_code}"
    resp = requests.get(url=specs_url, headers=HEADERS)
    return json.loads(resp.content)