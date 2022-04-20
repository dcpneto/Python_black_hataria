import requests
# import re # descomentar para habilitar DVWA
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from pprint import pprint

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36"

# codigo para o DVWA local
# descomentar para habilitar DVWA
# login_payload = {
#     "username": "admin",
#     "password": "password",
#     "Login": "Login",
# }
# # change URL to the login page of your DVWA login URL
# login_url = "http://localhost:8080/DVWA-master/login.php"

# # login
# r = s.get(login_url)
# token = re.search("user_token'\s*value='(.*?)'", r.text).group(1)
# login_payload['user_token'] = token
# s.post(login_url, data=login_payload)


def get_all_forms(url):
    """dada uma URL retorna o conteudo do html"""
    soup = bs(s.get(url).content, "html.parser")
    return soup.find_all("form")


def get_form_details(form):
    """
    obtem informacoes uteis vindas de um form
    """
    details = {}
    # obtem o form do html alvo
    try:
        action = form.attrs.get("action").lower()
    except:
        action = None
    #obtem o metodo do form (POST, GET, etc.)
    method = form.attrs.get("method", "get").lower()
    # obtem os detalhes dos campos
    inputs = []
    for input_tag in form.find_all("input"):
        input_type = input_tag.attrs.get("type", "text")
        input_name = input_tag.attrs.get("name")
        input_value = input_tag.attrs.get("value", "")
        inputs.append({"type": input_type, "name": input_name, "value": input_value})
    # aloca tudo em um dicionario
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details


def is_vulnerable(response):
    """booleando pra testar a resposta"""
    errors = {
        # MySQL
        "you have an error in your sql syntax;",
        "warning: mysql",
        # SQL Server
        "unclosed quotation mark after the character string",
        # Oracle
        "quoted string not properly terminated",
    }
    for error in errors:
        # se deu pau, return True
        if error in response.content.decode().lower():
            return True
    # sem erros
    return False


def scan_sql_injection(url):
    # teste na URL
    for c in "\"'":
        # adiciona quote/double quote char na URL
        new_url = f"{url}{c}"
        print("[!] Trying", new_url)
        # HTTP request
        res = s.get(new_url)
        if is_vulnerable(res):
            # Injecao detectada na URL, 
            # nao precisa extrair, so continuar
            print("[+] SQL Injection vulnerability detected, link:", new_url)
            return
    # teste nos forms
    forms = get_all_forms(url)
    print(f"[+] Detected {len(forms)} forms on {url}.")
    for form in forms:
        form_details = get_form_details(form)
        for c in "\"'":
            # corpo dos dados
            data = {}
            for input_tag in form_details["inputs"]:
                if input_tag["value"] or input_tag["type"] == "hidden":
                    # input com valor ou hidden,
                    # usa no corpo do form
                    try:
                        data[input_tag["name"]] = input_tag["value"] + c
                    except:
                        pass
                elif input_tag["type"] != "submit":
                    # tudo exceto submit
                    data[input_tag["name"]] = f"test{c}"
            # form request URL
            url = urljoin(url, form_details["action"])
            if form_details["method"] == "post":
                res = s.post(url, data=data)
            elif form_details["method"] == "get":
                res = s.get(url, params=data)
            # testa se tem vuln no resultado
            if is_vulnerable(res):
                print("[+] SQL Injection vulnerability detected, link:", url)
                print("[+] Form:")
                pprint(form_details)
                break   

if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    scan_sql_injection(url)
