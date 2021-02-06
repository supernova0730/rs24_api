import requests
import xml.etree.ElementTree as ET

from rs24_api import auth


URL = 'https://rs24.ru/webservices/rest/XXRSV_I1085_ITEM_PKG/GET_INFO/'

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/xml',
    'Authorization': auth.get_auth_token()
}


def _get_raw_request_body():
    return """
    <GET_Input xmlns:ns="http://xmlns.oracle.com/apps/fnd/soaprovider/plsql/rest/XXRSV_I1085_ITEM_PKG/GET_INFO/"
           xmlns:ns1="http://xmlns.oracle.com/apps/fnd/soaprovider/plsql/rest/XXRSV_I1085_ITEM_PKG/header/">
        <RESTHeader>
            <Responsibility>IBE_FIL_022</Responsibility>
            <RespApplication>IBE</RespApplication>
            <SecurityGroup>STANDARD</SecurityGroup>
            <NLSLanguage>RUSSIAN</NLSLanguage>
        </RESTHeader>
        <InputParameters>
            <P_VERSION>2.0</P_VERSION>
            <P_PARAMETER_TBL>
                <P_PARAMETER_TBL_ITEM>
                    <PARAMETER_NAME>P_SITE_USE_ID</PARAMETER_NAME>
                    <PARAMETER_VALUE></PARAMETER_VALUE>
                </P_PARAMETER_TBL_ITEM>
                <P_PARAMETER_TBL_ITEM>
                    <PARAMETER_NAME>P_ITEM_NUM</PARAMETER_NAME>
                    <PARAMETER_VALUE></PARAMETER_VALUE>
                </P_PARAMETER_TBL_ITEM>
                <P_PARAMETER_TBL_ITEM>
                    <PARAMETER_NAME>P_INFO_TYPE</PARAMETER_NAME>
                    <PARAMETER_VALUE></PARAMETER_VALUE>
                </P_PARAMETER_TBL_ITEM>
            </P_PARAMETER_TBL>
        </InputParameters>
    </GET_Input>
    """


def _get_request_body(p_item_num, p_site_use_id=1324787, p_info_type='FULL'):
    """Parses request body file, changes values to params, returns xml"""

    # parsing from file
    # tree = ET.parse('req_body_v2.xml')
    # root = tree.getroot()

    root = ET.fromstring(_get_raw_request_body())

    parameters = root.find('InputParameters').find('P_PARAMETER_TBL').findall('P_PARAMETER_TBL_ITEM')

    parameters[0][1].text = str(p_site_use_id)
    parameters[1][1].text = str(p_item_num)
    parameters[2][1].text = p_info_type

    return ET.tostring(root)


def get_product(p_item_num):
    """Pequests product by code
    <UOM> - единица измерения товара
    <CURRENCY_CODE> - кодвалюты
    Блок <RELATED_ITEMS> - сопутствующие товары/комплектующие
    Блок <ANALOGS> - аналоги запрошенного товара
    <DRK> - количество на складе компании вналичии
    <CLIENT_PRICE> - Ваша цена со скидкой (без НДС)
    <BASE_PRICE> - розничная цена (без НДС)
    Блок <IMAGES> -ссылка на изображение товара (с водяным знаком)
    Блоки <TECH_FEATURES_ITEM> - техническое описание товара
    <ETIM_CATALOG> - путь к товару в каталоге на сайте компании
    <MULTIPLICITY>- кратность товара(если возвращено два числа, разделенных запятой, то второе – это количество штук в упаковке)
    <VENDOR_ITEM> - артикул
    <BARCODES_ITEM> - штрих-код
    <X_RETURN_STATUS> - статус выполнения запроса
    <X_ERROR_MESSAGE xsi:nil="true"/> - сообщение об ошибке
    """

    request_body = _get_request_body(p_item_num)
    resp = requests.post(URL, data=request_body, headers=HEADERS)
    root = ET.fromstring(resp.text)

    ns = {
        'api_path': 'http://xmlns.oracle.com/apps/xxrsv/rest/XXRSV_I1085_ITEM_PKG/get_info/'
    }

    item_info = root.find('api_path:X_ITEM_INFO_REC', ns)

    tech_features_el = item_info.find('api_path:TECH_FEATURES', ns)
    tech_features = []
    for feature in tech_features_el.findall('api_path:TECH_FEATURES_ITEM', ns):
        feature_item = {
            'feature_name': feature.find('api_path:FEATURE_NAME', ns).text,
            'feature_code': feature.find('api_path:FEATURE_CODE', ns).text,
            'feature_value': feature.find('api_path:FEATURE_VALUE', ns).text,
            'feature_uom': feature.find('api_path:FEATURE_UOM', ns).text
        }
        tech_features.append(feature_item)

    return {
        'uom': item_info.find('api_path:UOM', ns).text,
        'currency': item_info.find('api_path:CURRENCY_CODE', ns).text,

        'related_items': [int(item.text) for item in
                          item_info.find('api_path:RELATED_ITEMS', ns).findall('api_path:RELATED_ITEMS_ITEM', ns)],

        'analogs': [int(item.text) for item in
                    item_info.find('api_path:RELATED_ITEMS', ns).findall('api_path:RELATED_ITEMS_ITEM', ns)],

        'quantity': int(item_info.find('api_path:DRK', ns).text),
        'client_price': float(item_info.find('api_path:CLIENT_PRICE', ns).text),
        'base_price': float(item_info.find('api_path:BASE_PRICE', ns).text),
        'images': [image.text for image in item_info.find('api_path:IMAGES', ns).findall('api_path:IMAGES_ITEM', ns)],
        'tech_features': tech_features,
        'catalog': item_info.find('api_path:ETIM_CATALOG', ns).text,
        'multiplicity': item_info.find('api_path:MULTIPLICITY', ns).text,
        'vendor': item_info.find('api_path:VENDOR_NAME', ns).text,
        'vendor_item': item_info.find('api_path:VENDOR_ITEM', ns).text,
        'status': root.find('api_path:X_RETURN_STATUS', ns).text,
        'error_msg_el': root.find('api_path:X_ERROR_MESSAGE', ns)
    }

