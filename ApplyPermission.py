# -*- encoding:utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import sys, os
import getpass

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
URL = "http://eportal.104.com.tw"
doLoginUrl = URL+"/doLogin.jsp"
applySave_URL = URL+"/bpm/form/perm_applySave.jsp"
eportal_session = requests.session()
header = {
    "Referer":URL+"/index.jsp",
    "User-Agent":userAgent,
    }
applyHeader = {
        "Referer":URL+"/bpm/form/perm_applyStart.jsp?",
        "User-Agent":userAgent,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Accept": "text/html, */*; q=0.01",
        }

def portalLogin(account, password):
    print("登入eportal")
    logingData = {
        "username":account,
        "password":password,
    }

    """POST 登入eportal"""
    # eportal_session.cookies.clear()
    # login_cookie = eportal_session.cookies.get_dict()
    logingResponseRes = eportal_session.post(doLoginUrl, data= logingData, headers = header)
    # print (logingResponseRes.text)    

def apply_request(system_id):
    """POST 選擇項目"""
    eportal_session.post(URL+"/bpm/form/perm_applyGetHandler.jsp", data={'system_id':system_id},headers = applyHeader)

    """form_html使用者欄位顯示"""
    userNameData_List = {
    "def": "emp,使用者帳號,emp,,,是,,,disabled,1",
    }
    applyViewRes = eportal_session.post(URL+"/bpm/form/perm_applyView.jsp", data=userNameData_List ,headers = applyHeader)
    form_html_data = applyViewRes.text

    """申請資料：選單&填寫內容"""
    if system_id == 'JIRA':
        print ("JIRA權限申請開始")
        class1 = 'JIRA'
        perm_name = 'JIRA 帳號與權限申請'
        remark = "新增JIRA帳號，請協助加入104jira-qa, 104jira-users AD group"
    elif system_id == 'DEVMASTER_New':
        print ("DevMaster功能權限申請開始")  
        class1 = 'DevMaster'
        perm_name = 'Devmaster 權限申請'
        remark = "可申請項目包含下列，不需要申請的項目則請刪除\n1.角色申請\n角色：QA"  
    elif system_id == 'DEVMASTER_LOGIN':  
        print ("DevMaster-MOTP權限申請開始")  
        class1 = 'DevMaster'
        perm_name = 'DevMaster-MOTP申請'
        remark = "申請MOTP "   
    elif system_id == 'SLACK_MOD':  
        print ("Slack使用/異動權限申請開始")   
        class1 = 'Slack'
        perm_name = 'Slack使用/異動申請單'
        remark = "1.申請原因 (必填)：新增帳號\n2.使用期間 (必填)：長期使用\n3.申請帳號/Channel Name (必填)："+account
    elif system_id == 'TESTRAIL_ID':  
        print ("Testrail權限申請開始")       
        class1 = 'Testrail'
        perm_name = 'Testrail 帳號/存取project 權限申請'
        remark = "新帳號申請加入，email："+account+"@104.com.tw\n角色：QA" 
    elif system_id == 'STAGING_MAIL':
        print ("Staging信箱權限申請開始")     
        class1 = 'STAGING'
        perm_name = 'Staging信箱申請'
        remark = "申請帳號："+account+"@104.com.tw \n備註:QA測試"
    elif system_id == 'OMS02_LAB':
        print ("Lab權限申請開始")     
        class1 = 'Lab'
        perm_name = 'OMS02 LAB信箱'
        remark = "QA測試用請協助開啟, 謝謝"
    elif system_id == 'GIT_HUB_MOD':
        print ("Github權限申請開始 (由於申請Github使用/異動申請單需要有Github帳號，若無帳號請先自行上Github申請一個) ")    
        while True:
            Github_email = input("請輸入您欲使用的Github帳號：\n")
            Answer = input("確定使用 "+Github_email+" 申請，請輸入Y，或輸入任意鍵重新輸入：\n")
            if Answer == 'Y':
                break  
        class1 = 'GitHub'
        perm_name = 'Github使用/異動申請單'
        remark = "1. 申請原因 (必填)：e.g.,新增/刪除帳號 \n2. GitHub帳號 (必填)："+Github_email  

    """
    利用BeautifulSoup 處理response資料 > 取得使用者資訊 (部門,姓名,員編等)
    將需填寫的內容&使用者資訊 存入applyData 發送request進行申請
    """
    applystartResponse = eportal_session.post(URL+"/bpm/form/perm_applyStart.jsp?")  
    soup = BeautifulSoup(applystartResponse.text, 'html.parser')
    applyData = {    
        "apply_emp_no":soup.find('input',attrs={'name': "apply_emp_no"}).get('value'),
        "apply_emp_name":soup.find('input',attrs={'name': "apply_emp_name"}).get('value'),
        "apply_":"emp_no:"+soup.find('input',attrs={'name': "apply_emp_no"}).get('value'),
        "comp_code":soup.find('input',attrs={'name': "comp_code"}).get('value'),
        "dept_code":soup.find('input',attrs={'name': "dept_code"}).get('value'),
        "dept_name":soup.find('input',attrs={'name': "dept_name"}).get('value'),
        "dept_name_hr":soup.find('input',attrs={'name': "dept_name_hr"}).get('value'),
        "emp":soup.find('input',attrs={'name': "apply_emp_no"}).get('value'),
        "emp_adname":soup.find('input',attrs={'name': "emp_adname"}).get('value'),
        "form_data":"{\"emp\":[\""+soup.find('input',attrs={'name': "apply_emp_no"}).get('value')+"\"]}",
        "class1":class1,
        "system_id":system_id,
        "perm_name":perm_name,
        "remark":remark,
        "form_html":form_html_data,
        }
    
    """
    利用applyData發送儲存申請 
    取得回傳的oid
    """
    applyResponseRes = eportal_session.post(applySave_URL, data= applyData,headers = applyHeader) 
    content = applyResponseRes.text
    json_dict = json.loads(content)
    oid = ''
    for key in json_dict['oid']:
        oid = str(oid)+str(key)

    """
    正式申請需多POST一個apply:1和oid:X參數
    以下為申請發送Request
    """
    applyResponseRes = eportal_session.post(applySave_URL, data= {'apply':'1','oid':str(oid),},headers = applyHeader)
    # print(applyResponseRes.text)

    print (perm_name+'發送成功')

if __name__ =="__main__":
    account = input("請輸入帳號:\n")
    password = getpass.getpass("請輸入密碼:\n")
    portalLogin(account,password)
    print ("請選擇申請項目:\n     1.JIRA帳號與權限申請\n     2.DevMaster權限申請\n     3.DevMaster-MOTP申請\n     4.Slack使用/異動申請單\n     5.Testrail 帳號/存取project 權限申請\n     6.Staging信箱申請\n     7.OMS02 LAB信箱\n     8.GitHub使用/異動申請")
    while True:    
        item = input ("請選擇申請項目，全部申請請輸入\"0\"，各別申請請輸入編號(例如：1.JIRA帳號與權限申請　請輸入\"1\"），離開請輸入\"Q\" : \n")
        if item == '1':
            apply_request('JIRA')
        if item == '2':
            apply_request('DEVMASTER_New')
        if item == '3':
            apply_request('DEVMASTER_LOGIN')
        if item == '4':
            apply_request('STAGING_MAIL')
        if item == '5':
            apply_request('OMS02_LAB')
        if item == '6':
            apply_request('SLACK_MOD')
        if item == '7':
            apply_request('TESTRAIL_ID')
        if item == '8':
            apply_request('GIT_HUB_MOD')
        if item == '0':
            apply_request('JIRA')
            apply_request('DEVMASTER_New')
            apply_request('DEVMASTER_LOGIN')
            apply_request('STAGING_MAIL')
            apply_request('OMS02_LAB')
            apply_request('SLACK_MOD')
            apply_request('TESTRAIL_ID')
            apply_request('GIT_HUB_MOD')    
            break
        if item == 'Q':
            break        
    os.system('pause')
    

