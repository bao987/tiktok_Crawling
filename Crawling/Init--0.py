from DrissionPage import ChromiumPage
from DrissionPage._configs.chromium_options import ChromiumOptions
# 路径替换为你的谷歌浏览器地址
path = r'C:\Users\bao\AppData\Local\Google\Chrome\Application\Chrome.exe'
ChromiumOptions().set_browser_path(path).save()
