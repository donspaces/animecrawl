import numpy as np
from bs4 import BeautifulSoup
import urllib.request
import mysql.connector as cnt
import pandas as pd

class table:

    def __init__(self, urla):
        self.urla = urla
        self.soup = urllib.request.urlopen(urla)
        self.soup = self.soup.read()
        self.raw = BeautifulSoup(self.soup, features="html.parser")
        self.text = self.raw.get_text()
        self.text = [i for i in self.text.split('\n') if i != '']

    def sel(self, info):
        if info in self.text:
            query = self.text.index(info) + 1
            return self.text[query]

        return ''


    def selall(self, values):
        a = {}
        for i in values:
            a.update({i: self.sel(i)})

        return a

    def __str__(self):
        stri = "table created from " + self.urla + "\n"

        return stri

def link(char_name):
    utfname = str(char_name.encode('utf-8'))
    utfname = utfname[2:len(utfname)-1]
    utfname = utfname.split("\\x")
    utfname = '%'.join(utfname).upper()

    urla = "https://baike.baidu.com/item/" + utfname
    print(urla)

    return urla

def main():
    char_name = input("character name: ")
    urla = link(char_name)
    table1 = table(urla)

    subtab1 = table1.selall(["中文名", "生\xa0\xa0\xa0\xa0日", "身\xa0\xa0\xa0\xa0高", "血\xa0\xa0\xa0\xa0型", "虚拟人物血型",
                             "年\xa0\xa0\xa0\xa0龄", "登场作品", "性\xa0\xa0\xa0\xa0别"])
    for i in subtab1.keys():
        print(i, subtab1[i])

    #data = pd.DataFrame([subtab1])
    #print(data)

if __name__ == '__main__':
    main()
