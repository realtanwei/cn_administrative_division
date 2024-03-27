

from bs4 import BeautifulSoup
from administrative_division import AdministrativeDivision
import requests
import uuid, mysql.connector
from pypinyin import lazy_pinyin, Style
from urllib3.util.retry import Retry  
from requests.adapters import HTTPAdapter

def get_connect() :
    cnx = mysql.connector.connect(user='root', password='123@abcd',  port='6033',
                                host='localhost',  
                                database='administrative_division')  
    return cnx

base_url = 'https://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2023/'

def main():
    home_url = 'https://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2023/index.html'
    session = get_session()
    home_content = request_server(session, home_url)
    
    province_list = []
    
    soup = BeautifulSoup(home_content, 'html.parser')
    provincetr = soup.select('tr.provincetr td')
    ## 所有省份
    for index, provincetd in enumerate(provincetr):
        index = index + 1
        provincea = provincetd.contents[0]
        province_name = provincea.get_text()
        province_href = provincea.attrs['href']
        province_code = province_href[:-5]
        
        provinceObj = AdministrativeDivision(id=get_unique_id(),
                               sup_code='%',
                               data_code=province_code,
                               data_name=province_name,
                               data_level=1,
                               data_order=index)
        provinceObj.gb_code_url = province_href
        province_list.append(provinceObj)
    ## 测试保存到数据库：
    print(len(province_list))
    province_list_child = province_list[30:]
    
    insert_db(province_list=province_list_child)
    two_page(session, province_list_child)
    
 
def insert_db(province_list):
    for p in province_list:
        if isinstance(p, AdministrativeDivision):
            cnx = get_connect()
            cursor = cnx.cursor()
            data_insert = (p.sup_code, p.data_code, p.data_name, chinese_to_pinyin(p.data_name), 
                           p.data_level, p.data_order, p.is_show, p.can_select, p.class_code)
            insert_query = '''INSERT INTO tb_sys_administrative_division (sup_code, data_code, data_name, pinyin_code, data_level, 
                                data_order,is_show, can_select, class_code) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ''' 
            cursor.execute(insert_query, data_insert)
            # 提交事务  
            cnx.commit()  
            
            # 打印成功消息  
            print("Data inserted successfully!")
            cursor.close()  
            cnx.close()

def two_page(session, province_list):
    for province in province_list:
        if isinstance(province, AdministrativeDivision):
            city_list = []
            #url_temp = province.data_code + '.html'
            html_content = request_server(session, base_url + province.gb_code_url)
            soup = BeautifulSoup(html_content, 'html.parser')
            citytr = soup.select('tr.citytr')
            for index, citya in enumerate(citytr):
                index = index + 1
                city_content = citya.contents[1]
                city_e = city_content.next_element
                city_name = city_e.get_text()
                try:
                    city_href = city_e.attrs['href']
                except:
                    city_href = ''
                    city_code = citya.contents[0].get_text()[:4]
                else:
                    city_code = str(city_href[:-5]).split('/')[-1]
                cityObj = AdministrativeDivision(id=get_unique_id(),
                               sup_code=province.data_code,
                               data_code=city_code,
                               data_name=city_name,
                               data_level=2,
                               data_order=index)
                cityObj.gb_code_url = city_href
                city_list.append(cityObj)
            
            insert_db(city_list)
            three_page(session, city_list)
            province.children = city_list
            

def three_page(session, city_list):
    for city in city_list:
        if isinstance(city, AdministrativeDivision):
            county_list = []
            if city.gb_code_url.endswith('.html') == False:
                continue
            base_href = str(city.gb_code_url)[:-5].rstrip(city.data_code)
            html_content = request_server(session, base_url + city.gb_code_url)
            
            soup = BeautifulSoup(html_content, 'html.parser')
            countytr = soup.select('tr.countytr')
            for index, county in enumerate(countytr):
                index = index + 1
                county_code_content = county.contents[0]
                county_name_content = county.contents[1]
                countya = county_name_content.next_element
                county_name = countya.get_text()
                try:
                    county_href = countya.attrs['href']
                except:
                    county_href = ''
                    county_code = county_code_content.get_text()[:6]
                else:
                    county_code = str(county_href[:-5]).split('/')[-1]
                countyObj = AdministrativeDivision(id=get_unique_id(),
                               sup_code=city.data_code,
                               data_code=county_code,
                               data_name=county_name,
                               data_level=3,
                               data_order=index)
                
                countyObj.gb_code_url = base_href + county_href
                county_list.append(countyObj)
            insert_db(county_list)
            four_page(session, county_list)
            city.children = county_list


def four_page(session, county_list):
    for county in county_list:
        if isinstance(county, AdministrativeDivision):
            town_list = []
            if county.gb_code_url.endswith('.html') == False:
                continue
            base_href = str(county.gb_code_url)[:-5].rstrip(county.data_code)
            html_content = request_server(session, base_url + county.gb_code_url)
            soup = BeautifulSoup(html_content, 'html.parser')
            towntr = soup.select('tr.towntr')
            for index, town in enumerate(towntr):
                index = index + 1
                town_code_content = town.contents[0]
                town_name_content = town.contents[1]
                towna = town_name_content.next_element
                town_name = towna.get_text()
                try:
                    town_href = towna.attrs['href']
                except:
                    town_href = ''
                    town_code = town_code_content.get_text()[:9]
                else:
                    town_code = str(town_href[:-5]).split('/')[-1]
                townObj = AdministrativeDivision(id=get_unique_id(),
                               sup_code=county.data_code,
                               data_code=town_code,
                               data_name=town_name,
                               data_level=4,
                               data_order=index)
                townObj.gb_code_url = base_href + town_href
                town_list.append(townObj)
            insert_db(town_list)
            five_page(session, superior_list=town_list, select_tr='tr.villagetr', level=5)
            county.children = town_list

def five_page(session, superior_list, select_tr, level, next=None):
    for superior in superior_list:
        if isinstance(superior, AdministrativeDivision):
            cur_list = []
            if superior.gb_code_url.endswith('.html') == False:
                continue
            html_content = request_server(session, base_url + superior.gb_code_url)
            soup = BeautifulSoup(html_content, 'html.parser')
            select = soup.select(selector=select_tr)
            for index, cur_val in enumerate(select):
                index = index + 1
                cur_code_content = cur_val.contents[0]
                cur_classification_code_content = cur_val.contents[1]
                cur_name_content = cur_val.contents[2]
                cur_classification_code = cur_classification_code_content.get_text()
                cur_name = cur_name_content.get_text()
                cur_code = cur_code_content.get_text()
                curObj = AdministrativeDivision(id=get_unique_id(),
                               sup_code=superior.data_code,
                               data_code=cur_code,
                               data_name=cur_name,
                               data_level=level,
                               data_order=index)
                curObj.class_code = cur_classification_code
                cur_list.append(curObj)
            insert_db(cur_list)
            if next is not None:
                next()
            superior.children = cur_list

def get_session():
    retries = Retry(total=5,  # 总共重试次数  
            backoff_factor=0.1,  # 回退因子，在两次重试之间等待的时间  
            status_forcelist=[ 500, 502, 503, 504 ]  # 对哪些HTTP状态码进行重试  
            )
    session = requests.Session()  
    session.mount('http://', HTTPAdapter(max_retries=retries))  
    session.mount('https://', HTTPAdapter(max_retries=retries)) 
    return session

def request_server(session, url):
    
    try:  
        response = session.get(url=url)
        response.encoding = 'utf-8'
        response.raise_for_status()  # 如果请求失败，这里会抛出HTTPError异常  
        html_content = response.text
    except requests.exceptions.RequestException as e:  
        print(f"请求失败: {e}")
    return html_content            

def convert_to_json(obj):  
    if isinstance(obj, AdministrativeDivision):  
        return obj.to_dict()  
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)  

def chinese_to_pinyin(chinese_text):  
    pinyin_list = lazy_pinyin(chinese_text, style=Style.FIRST_LETTER)
    pinyin_str = ''.join(pinyin_list).upper()
    return pinyin_str 

def get_unique_id():
    return str(uuid.uuid4()).replace('-', '')

if __name__ == '__main__':
    main()