import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import codecs
import threading
import time
import datetime
from selenium.webdriver.common.action_chains import ActionChains
import urllib.request

driver=webdriver

googledrive='https://accounts.google.com/signin/v2/identifier?service=wise&passive=true&continue=http%3A%2F%2Fdrive.google.com%2F%3Futm_source%3Dru&utm_medium=button&utm_campaign=web&utm_content=gotodrive&usp=gtd&ltmpl=drive&flowName=GlifWebSignIn&flowEntry=ServiceLogin'


photos=[]

def SetDownloadDirectory():
    with open('directorydownload.txt','r') as f:
        data=f.readlines()

    data=data[0].replace(r'\\',r'\'')
    return  data

def build_profile():
    data=SetDownloadDirectory()
    print(data)
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.dir", "{0}".format(data))
    profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "image/jpeg image/png") #mime type
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.manager.focusWhenStarting", False)
    profile.set_preference("browser.download.useDownloadDir", True)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.manager.alertOnEXEOpen", False)
    profile.set_preference("browser.download.manager.closeWhenDone", True)
    profile.set_preference("browser.download.manager.showAlertOnComplete", False)
    profile.set_preference("browser.download.manager.useWindow", False)
    profile.set_preference("services.sync.prefs.sync.browser.download.manager.showWhenStarting", False)
    profile.set_preference("pdfjs.disabled", True)


    return profile




def PageState(driver):
    f = True
    start = datetime.datetime.now()
    while (driver.execute_script('return document.readyState;') == 'complete') != True:
        proc = datetime.datetime.now()
        delta = proc - start
        if (delta.total_seconds() > 10):
            f = False
            break
    return f

def Start():
    if (PageState(driver)==True):
        driver.get(googledrive)
        return True
    else :
        print('PageState is down (Check your internet connection)')
        return False



def ReadAuthData():
    with open('auth.txt','r') as f:
        data=f.readlines()
    data[0]=data[0][:-1]
    return data


def Login (driver):
    data=ReadAuthData()
    auth = {'login': data[0], 'password': data[1]}


    try:
        #login
        loginsend=driver.find_element_by_id('identifierId')
        loginsend.clear()
        loginsend.send_keys(auth['login'])

        driver.find_element_by_id('identifierNext').click()

        #timer for loading
        time.sleep(5)


        #password
        passsend = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div[1]/div/form/content/section/div/content/div[1]/div/div[1]/div/div[1]/input')
        passsend.clear()
        passsend.send_keys(auth['password'])

        driver.find_element_by_id('passwordNext').click()

        ### here need some check for auth and pagestae
        time.sleep(5)
        return True
    except:
        print ('Errors occured while logining in account')
        return False






# получаем количевстов и имя папок
def getfolders(driver):

    objectFolders=[]
    index=1

    #количевство папок
    while True:
        try :
            tempXpath='/html/body/div[1]/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div[3]/div/div/div/div/c-wiz/div[2]/c-wiz/div[1]/c-wiz/div/c-wiz[2]/div[1]/c-wiz/c-wiz/div/c-wiz[{0}]'.format(index)
            driver.find_element_by_xpath(tempXpath)
        except :
            index -= 1
            break
        index+=1


    #получение имени папок
    while index !=0:
        try:
            tempXpath='/html/body/div[1]/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div[3]/div/div/div/div/c-wiz/div[2]/c-wiz/div[1]/c-wiz/div/c-wiz[2]/div[1]/c-wiz/c-wiz/div/c-wiz[{}]/div/div/div/div[5]'.format(index)
            folder= driver.find_element_by_xpath(tempXpath)
            objectFolders.append([folder.text,tempXpath])
            index -= 1
        except :
            break

    return objectFolders




#получаем заказаную папку
def GetFolder(name):
    objectFolders=getfolders(driver)

    f=False
    i=0
    if len(objectFolders)>0:
      while i!=len(objectFolders):
        if objectFolders[i][0]==name:
           option=driver.find_element_by_xpath(objectFolders[i][1])
           doubleclick = ActionChains(driver)
           doubleclick.double_click(option).perform() ###double click
           f=True
           break
        i+=1
      return f
    else:
       print('No such folder or drive not contain folders!')
       return False




def GetCount(driver):
    time.sleep(5)
    index=1

    #количевсто фото
    while True:
        try:
             tempXpath='/html/body/div[1]/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div[3]/div/div/div[2]/div/c-wiz/div[2]/c-wiz/div[1]/c-wiz/div/c-wiz[2]/div[1]/c-wiz/c-wiz/div/c-wiz[{0}]'.format(index)
             driver.find_element_by_xpath(tempXpath)
        except:
            index-=1
            break
        index+=1

    return index




def GetSrcImage (driver,countPhotos):
        src=[]
        i=1
        while i!=countPhotos+1:
            PhotoXpath='/html/body/div[1]/div[2]/div[1]/div[2]/div/div/div[1]/div/div/div[3]/div/div/div[2]/div/c-wiz/div[2]/c-wiz/div[1]/c-wiz/div/c-wiz[2]/div[1]/c-wiz/c-wiz/div/c-wiz[{0}]'.format(i)


            #нажатие на  картинку
            option = driver.find_element_by_xpath(PhotoXpath)
            doubleclick = ActionChains(driver)
            doubleclick.double_click(option).perform()  ###double click
            time.sleep(2)

            #get name
            name=driver.find_element_by_css_selector('.a-b-K-T.a-b-cg-Zf').text
            src.append(name)



            #download click
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
            time.sleep(4)

            #close picture
            driver.find_element_by_css_selector('.a-b-va-d.a-b-Da-d.h-sb-Ic.a-b-d').click()


            i+=1



        return src





def GetPhotos (index):
    countPhots=GetCount(driver)
    photos={folders[index]:[]}

    if countPhots>0:
        photos[folders[index]]=GetSrcImage(driver,countPhots)
    else :
        photos[folders[index]] = ['nan']
        print('Count of photos = 0!!!')

    return photos


def GetNamesFolders():
    name=driver.find_elements_by_css_selector('.Q5txwe')
    Fold=[]

    index=0
    while index<len(name):
        temp=name[index].text
        Fold.append(temp)
        index+=1
    return Fold



def SaveDictJSON(dict):
    with open('photo_list.json', 'w') as fp:
        json.dump(dict, fp)

if __name__ == '__main__':
    index=0
    PHOTO={}
    folders = []

    try:
        profile = build_profile()
        driver = webdriver.Firefox(executable_path=r"C:\geckodriver.exe", firefox_profile=profile)
        if Start()==True:
           Login(driver)

           time.sleep(5)
           folders = GetNamesFolders()
           while index < len(folders):
                GetFolder(folders[index])
                PHOTO.update(GetPhotos(index))
                driver.get('https://drive.google.com/drive/my-drive')
                time.sleep(3)
                index+=1

        else:
          pass
    except Exception as e:
        print(e)


    SaveDictJSON(PHOTO)
    driver.close()



