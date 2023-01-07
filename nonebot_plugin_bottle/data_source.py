import json
import random
import requests
import time
from pathlib import Path
from typing import List
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot
from .config import api_key,secret_key

class Bottle(object):
    def __init__(self) -> None:
        self.data_path = Path("data/bottle/data.json").absolute()
        self.data_dir = Path("data/bottle").absolute()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.__data: List[dict] = []
        self.__load()

    def __load(self):
        if self.data_path.exists() and self.data_path.is_file():
            with self.data_path.open("r", encoding="utf-8") as f:
                data: List[dict] = json.load(f)

            for i in data:
                #旧版json兼容
                isOldVersion = False
                commentnew = []
                for index, value in enumerate(i['comment']):
                    if isinstance(value,str):
                        isOldVersion = True
                        commentnew.append([0,value])
                if isOldVersion:
                    i['comment'] = commentnew
                try:
                    self.__data.append({
                        'del': i['del'],
                        "user": i["user"],
                        "group": i['group'],
                        "user_name": i['user_name'],
                        "group_name": i["group_name"],
                        "text": i['text'],
                        "report": i['report'],
                        "picked": i['picked'],
                        "comment": i['comment']
                    })
                except:
                    self.__data.append({})
        else:
            self.__data = 'E'
            with self.data_path.open('w+', encoding='utf-8') as f:
                f.write("[]")
            logger.success(f"在 {self.data_path} 成功创建漂流瓶数据库")
            self.__load()

    def __save(self) -> None:
        with self.data_path.open('w+', encoding='utf-8') as f:
            json.dump(self.__data, f, ensure_ascii=False, indent=4)

    def print_all(self):
        '''
        打印读取`data文件`
        '''
        with self.data_path.open('r', encoding='utf-8') as f:
            logger.info(f.read())

    def check(self, key) -> bool:
        '''
        检查是否存在重复内容
        '''
        if not self.__data:
            return False
        for i in self.__data:
            if key == i:
                return True
        return False

    def add(self,bot:Bot, user: str, group: str, text,user_name,group_name) -> int:
        '''
        新增一个漂流瓶  
        `user`: 用户QQ  
        `group`: 群号  
        `text`: 漂流瓶内容
        '''
        temp = {
            'user': user,
            'group': group,
            'user_name': user_name,
            'group_name': group_name,
            'text': text,
            'report': 0,
            'picked': 0,
            'del': 0,
            'comment': []
        }
        if not self.check(temp):
            self.__data.append(temp)
            self.__save()
            return self.__data.index(temp)
        else:
            logger.warning("添加失败！")
            return 0

    def select(self):
        '''
        抽取漂流瓶
        '''
        if self.__data:
            index = random.randint(0, len(self.__data)-1)
            if self.__data[index]['del']:
                return self.select()
            self.__data[index]['picked'] += 1
            self.__save()
            return [index, self.__data[index]]
        else:
            return []

    def clear(self):
        '''
        清空漂流瓶
        '''
        self.__data = []
        self.__save()

    def report(self, index: int, timesMax: int = 5) -> int:
        '''
        举报漂流瓶  
        `index`: 漂流瓶编号
        `timesMax`: 到达此数值自动处理

        返回  
        0 举报失败
        1 举报成功
        2 举报成功并且已经自动处理
        3 已经删除
        '''
        if index > len(self.__data)-1 or index < 0:
            return 0
        try:
            self.__data[index]['report'] += 1
        except:
            self.__data[index]['report'] = 1

        if self.__data[index]['del'] == 1:
            return 3

        if self.__data[index]['report'] >= timesMax:
            try:
                self.remove(index)
                self.__save()
                return 2
            except:
                return 0
        else:
            self.__save()
            return 1

    def check_report(self, index: int) -> int:
        '''
        返回漂流瓶被举报次数
        `index`: 漂流瓶编号
        '''
        return self.__data[index]['report']

    def comment(self, index: int,user:str, com):
        '''
        评论漂流瓶
        `index`: 漂流瓶编号  
        `user`: QQ号  
        `com`: 评论内容
        '''
        com = [user,com]
        try:
            if not com in self.__data[index]['comment']:
                self.__data[index]['comment'].append(com)
        except:
            self.__data[index]['comment'] = [com]
        self.__save()

    def check_comment(self, index: int):
        '''
        查看评论
        `index`: 漂流瓶编号
        '''
        try:
            return [value[1] for value in self.__data[index]['comment']]
        except:
            try:
                self.__data[index]['comment'] = []
            except:
                pass
            return []

    def remove_comment(self,index: int,user: int):
        '''
        删除指定漂流瓶里某人的所有评论
        `index`: 漂流瓶编号  
        `user`: QQ号  
        '''
        user = int(user)
        self.__data[index]['comment'] = [i for i in self.__data[index]['comment'] if i[0] != user]
        self.__save()
        return True

    def check_bottle(self,index:int):
        '''
        获取漂流瓶信息
        `index`: 漂流瓶编号
        '''
        if 0<=index<len(self.__data):
            return self.__data[index]
        else:
            return {}

    def remove(self,index:int):
        '''
        直接移除漂流瓶
        `index`: 漂流瓶编号
        '''
        try:
            self.__data[index]['del'] = 1
            self.__save()
            return True
        except:
            logger.warning('删除错误！')
            return False
bottle = Bottle()

class Audit(object):
    bannedMessage = ''
    def __init__(self) -> None:
        self.data_path = Path("data/bottle/permissionsList.json").absolute()
        self.data_dir = Path("data/bottle").absolute()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.__data = {
            'enableCooldown': True,
            'cooldownTime': 30,
            'bannedMessage': '',
            'user': [],
            'group':[],
            'cooldown':{},
            'whiteUser':[],
            'whiteGroup': [],
        }
        self.__load()

    def __load(self):
        try:
            with self.data_path.open("r+", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            with self.data_path.open('w+', encoding='utf-8') as f:
                json.dump(self.__data, f)
            logger.success(f"在 {self.data_path} 成功创建漂流瓶黑名单数据库")
        else:
            self.__data.update(data)
            self.bannedMessage = self.__data['bannedMessage']
            

    def __save(self) -> None:
        with self.data_path.open('w+', encoding='utf-8') as f:
            f.write(json.dumps(self.__data, ensure_ascii=False, indent=4))

    def add(self,mode,num):
        '''
        添加权限  
        `mode`:  
            `group`: 群号
            `user`: QQ号
            `cooldown`: 暂时冷却QQ号  
            `whiteUser`: 白名单QQ号  
            `whiteGroup`: 白名单群号  
        `num`: QQ/QQ群号
        '''
        num = str(num)
        try:
            if mode != 'cooldown' and num not in self.__data[mode]:
                self.__data[mode].append(num)
            elif not (self.checkWhite('whiteUser',num) or self.check('whiteGroup',num)) and self.__data['enableCooldown'] and mode == 'cooldown':
                self.__data['cooldown'][num] = int(time.time()) + self.__data['cooldownTime']
            else:
                return False
            self.__save()
            return True
        except Exception as e:
            print(e)
            return False
        
    def remove(self,mode,num):
        '''
        移除黑名单  
        `mode`:  
            `group`: 群号
            `user`: QQ号
            `whiteUser`: 白名单QQ号  
            `whiteGroup`: 白名单群号  
        `num`: QQ/QQ群号
        '''
        num = str(num)
        try:
            self.__data[mode].remove(num)
            self.__save()
            return True
        except:
            return False
    
    def verify(self,user,group):
        '''
        返回是否通过验证(白名单优先)  
        `user`: QQ号
        `group`: 群号

        返回：  
            `True`: 通过  
            `False`: 未通过  
        '''
        if not (self.checkWhite('whiteUser',user) or self.checkWhite('whiteGroup',group)):
            if self.check('user',user) or self.check('group',group) or self.check('cooldown',user):
                return False
        return True

    def check(self,mode,num):
        
        '''
        查找是否处于黑名单
        `mode`:  
            `group`: 群号
            `user`: QQ号
            `cooldown`: 暂时冷却QQ号  
        `num`: QQ/QQ群号
        '''
        num = str(num)
        if mode in ['group','user']:
            if num in self.__data[mode]:
                return True
        else:
            if num in self.__data[mode]:
                if time.time() <= self.__data[mode][num]:
                    return True
        return False
    
    def checkWhite(self,mode,num:str):
        '''
        检查是否为白名单  
        `mode`:  
            `whiteUser`: 白名单QQ号  
            `whiteGroup`: 白名单群号  
        `num`: QQ/QQ群号
        '''
        num = str(num)
        if mode == 'whiteUser' and num in self.__data['whiteUser']:
            return True
        elif mode == 'whiteGroup' and num in self.__data['whiteGroup']:
            return True
        else:
            return False
ba = Audit()

cursepath = Path("data/bottle/curse.json").absolute()
def text_audit(text:str,ak = api_key,sk = secret_key):
    '''
    文本审核(百度智能云)  
    `text`: 待审核文本
    `ak`: api_key
    `sk`: secret_key
    '''
    if (not api_key) or (not secret_key):
        # 未配置key 进行简单违禁词审核
        try: 
            with cursepath.open('r',encoding='utf-8') as f:
                for i in json.load(f):
                    if i in text:
                        return {
                            'conclusion': '不合规',
                            'data': [
                                {
                                    'msg': f'触发违禁词 {i}'
                                }
                            ]
                        }
                    else:
                        return 'pass'
        except:
            if not cursepath.exists():
                with cursepath.open('w+',encoding='utf-8') as f:
                    f.write("[]")
                return 'pass'
            else:
                return 'Error'
    # access_token 获取
    host = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ak}&client_secret={sk}'
    response = requests.get(host)
    if response:
        access_token = response.json()['access_token']
    else:
        # 未返回access_token 返回错误
        return 'Error'
    
    request_url = "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined"
    params = {"text":text}
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        return response.json()
    else:
        # 调用审核API失败
        return 'Error'
