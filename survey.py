# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

class Survey(object):
    def __init__(self, base_url, cncode):
        if len(cncode) < 16:
            return None
        self._base_url = base_url
        self.cn1 = cncode[:3]
        self.cn2 = cncode[3:6]
        self.cn3 = cncode[6:9]
        self.cn4 = cncode[9:12]
        self.cn5 = cncode[12:15]
        self.cn6 = cncode[15:]
        self._start_url = base_url
        self.current = self._start_url  # get started from base_url
        self.session = None
        self.action = None
        self.ques_num = 0
        self.done = False
        self.resptext = 'na'
    
    def setup_session(self):
        if self.session is None:
            self.session  = requests.session()
            res = self.session.get(self._start_url)
            soup = BeautifulSoup(res.text, 'html.parser')
            dataform = filter(lambda x: x['action'].startswith('Index'), soup.find_all('form'))[0]
            accept_cookie = {'JavaScriptEnabled': '1', 'FIP': 'True', 'AcceptCookies': 'Y', 'NextButton': '继续'}
            res = self.session.post(self._base_url+dataform['action'], accept_cookie)
            #print res.url
            #print res.text
            soup = BeautifulSoup(res.text, 'html.parser')
            self.action = filter(lambda x: x['id'] == 'surveyEntryForm', soup.find_all('form'))[0]['action']

    def submit_cn(self):
        if self.session is None:
            print 'no session found'
            return
        postdata = {'JavaScriptEnabled': '1', 'FIP': 'True', 'AcceptCookies': 'Y', 'NextButton': '继续',
                    'CN1': self.cn1, 'CN2': self.cn2,
                    'CN3': self.cn3, 'CN4': self.cn4,
                    'CN5': self.cn5, 'CN6': self.cn6,
                    'NextButton': 'Start'
        }
        res = self.session.post(self._base_url+self.action, postdata)
        print res.text
        soup = BeautifulSoup(res.text, 'html.parser')
        self.action = filter(lambda x: x['id'] == 'surveyForm', soup.find_all('form'))[0]['action'] # surveyForm
        #manipulate first form data for post
        postednfs = filter(lambda x: x['id'] == 'PostedFNS', soup.find_all('input'))[0]['value']
        ionf = filter(lambda x: x['id'] == 'IoNF', soup.find_all('input'))[0]['value']
        questions = postednfs.split('|')
        self.postdata = {}
        for q in questions:
            self.postdata[q] = '2'
        self.postdata['IoNF'] = ionf
        self.postdata['PostedFNS'] = postednfs 

    def submit_data(self):
        if self.session is None:
            print 'no session found'
            return
        print self.postdata
        res = self.session.post(self._base_url+self.action, self.postdata)
        print res.text
        # manipulate data for next POST
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            self.action = filter(lambda x: x['id'] == 'surveyForm', soup.find_all('form'))[0]['action']
        except:
            # <p class="ValCode">验证代码：18101822</p>
            print 'Survey done, pls record your verification code'
            for p in soup.find_all('p'):
                if p.attrs.has_key('class'):
                    print p.text
                    self.resptext = p.text
                    self.done = True
        else:
            postednfs = filter(lambda x: x['id'] == 'PostedFNS', soup.find_all('input'))[0]['value']
            ionf = filter(lambda x: x['id'] == 'IoNF', soup.find_all('input'))[0]['value']
            questions = postednfs.split('|')
            self.postdata = {}
            for q in questions:
                self.postdata[q] = '2'
            self.postdata['IoNF'] = ionf
            self.postdata['PostedFNS'] = postednfs


if __name__ == '__main__':
    sc = raw_input('survey code:')
    q = Survey('https://tellburgerking.com.cn/', sc)
    try:
        q.setup_session()
        q.submit_cn()
    except Exception as e:
        print 'invalid survey code', e
        raise SystemExit
    for i in range(28):
        q.submit_data()
        if q.done:
            break
