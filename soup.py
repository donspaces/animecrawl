import sys

import numpy as np
from bs4 import BeautifulSoup
import urllib.request
import mysql.connector as cnt
import pandas as pd
from datetime import *

class table:

    def __init__(self, urla):
        self.urla = urla
        self.soup = urllib.request.urlopen(urla)
        self.soup = self.soup.read()
        self.raw = BeautifulSoup(self.soup, features="html.parser")
        self.text = self.raw.get_text()
        self.text = [i for i in self.text.split('\n') if i != '']

    def sel(self, info):
        '''
        Simulating sql single select from html soup
        '''
        if info in self.text:
            query = self.text.index(info) + 1
            return self.text[query]

        return ''


    def selall(self, values):
        '''
        :param values: list of select col names
        :return: A list of selected values
        sql select for html
        '''
        a = {}
        for i in values:
            a.update({i: self.sel(i)})

        a = subtable(a)
        return a

    def __str__(self):
        stri = "table created from " + self.urla + "\n"

        return stri

class subtable:
    def __init__(self, table):
        self.table = table

    def cast(self, term, typ, agecov=False):
        '''
        :param term: term inside dictionary
        :param typ: type the var needs cast into
        :param agecov: convert age
        :return: casted values
        Value casting
        '''
        if(type(self.table[term]) == str and self.table[term] != ""):
            numsoup = ""
            for i in range(len(self.table[term])):
                cur = self.table[term][i:i+1]
                if(cur.isnumeric() or cur == "."):
                    numsoup += cur
                else:
                    numsoup += " "

            numsoup = numsoup.strip(" ")
            nums = [i for i in numsoup.split(" ") if i != ""]
            print(nums)

            ima = datetime.now()
            kyu = ima.date()
            res = []
            if(typ == int or typ == float):
                for i in nums:
                    res.append(typ(i))

            elif(typ == date):

                if(agecov == True):
                    age = self.cast("age", int)
                    yearb = kyu.year - age[0]
                    nums.insert(0, str(yearb))

                assert len(nums) <= 3, "Not date\n"
                res = ["/".join(nums)]

            elif(typ == datetime):

                if (agecov == True):
                    age = self.cast("age", int)
                    yearb = ima.year - age[0]
                    nums.insert(0, str(yearb))

                assert len(nums) <= 6, "Not datetime\n"
                dat = "/".join(nums[:3])
                tim = ":".join(nums[3:6])
                res = [dat + " " + tim]

            else:
                res = [self.table[term]]

            if(res != [] or res != None):
                self.table[term] = res[0]
            return res

    def castall(self, termdict):
        '''
        Cast values of subtable
        '''
        agecov = False
        if (self.table["age"] != "" and "age" in self.table.keys()):
            agecov = True
        for i in termdict.keys():
            if i in self.table.keys():
                self.cast(i, termdict[i], agecov)

        return self.table

    def proj(self, coln, term):
        '''
        rename project
        '''
        self.table[coln] = self.table.pop(term)

        return self.table[coln]

    def projall(self, coll, terms):
        '''
        :param coll: all columns to cast
        :param terms: all columns be cast
        :return: subtable project
        project
        '''
        i = 0
        for item in coll:
            self.proj(item, terms[i])
            i += 1

        return self.table

    def sql_ins(self, selcol, cur, db, insall=True):
        '''
        :param selcol: select columns
        :param insall: insert all (bool)
        :return: subtable
        sql insert
        '''
        if(insall == True):
            selcol = self.table.keys()

        try:
            cur.execute("INSERT INTO characters (anime, name, height, bloodtype, birthdate, sex) values "
                        "(\"{0[anime]}\", \"{0[name]}\", \"{0[height]}\", \"{0[bloodtype]}\", \"{0[birthdate]}\", \"{0[sex]}\");".format(self.table))

            db.commit()
            print("commit success\n")
        except Exception as e:
            db.rollback()
            print(e.args, file=sys.stderr)

        return cur





    def __str__(self):
        stri = ""
        for i in self.table.keys():
            stri += i + " " + str(self.table[i]) + "\n"

        return stri


def link(char_name):
    utfname = str(char_name.encode('utf-8'))
    utfname = utfname[2:len(utfname)-1]
    utfname = utfname.split("\\x")
    utfname = '%'.join(utfname).upper()

    urla = "https://baike.baidu.com/item/" + utfname
    print(urla)

    return urla

config = {
        'host': 'localnet',
        'port': 3306,
        'database': 'animecrawl',
        'user': 'donspace',
        'password': ':)',
        'charset': 'utf8',
        'use_unicode': True,
        'get_warnings': True,
    }

def main():

    db1 = cnt.connect(**config)
    cur = db1.cursor()

    char_name = ""

    while(char_name != '.exit'):
        char_name = input("character name: ")
        urla = link(char_name)
        table1 = table(urla)

        subtab1 = table1.selall(["中文名", "生\xa0\xa0\xa0\xa0日", "身\xa0\xa0\xa0\xa0高", "血\xa0\xa0\xa0\xa0型", "虚拟人物血型",
                                 "年\xa0\xa0\xa0\xa0龄", "登场作品", "性\xa0\xa0\xa0\xa0别"])

        #result = subtab1.cast("生\xa0\xa0\xa0\xa0日", date, True)
        print(subtab1)
        subtab1.projall(["name", "birthdate", "height", "bloodtype", "bloodtype", "age", "anime", "sex"],
                        list(subtab1.table.keys()))
        if(subtab1.table["age"] == ""):
            subtab1.table["age"] = "12"

        casttable = {"birthdate": date, "height": float, "age": int}

        subtab1.castall(casttable)
        print(subtab1)

        subtab1.sql_ins(subtab1.table.keys(), cur, db1)

        #data = pd.DataFrame([subtab1])
        #print(data)

if __name__ == '__main__':
    main()
