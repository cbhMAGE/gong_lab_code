# -*- coding:utf-8 -*-
import pymongo
import threading

# 创建新用户的方法  -- 完成 setNewUser(self, name, id, phone_number, psw, other_info):
# 索引用户的方法  --完成 findUser(self, important_info):
# 修改用户信息的方法  --完成  setUserDirect(self, ID, keys_values):
# 读取用户全部信息的方法  --完成  getUserAll(self, ID):
# 读取用户指定信息的方法  --完成  getUserInfo(self, ID, keys):
# 为用户mailbox插入mail的方法 会自动判重  -- 完成  setMail(self, ID, time, type, Data):
# 索引倒序的若干个目标用户mails的方法  -- 完成  getMail(self, ID, num):
# 根据id索引某个mail的方法 可能没用  --完成  getMailID(self, ID, mailid):
# 创建request  -- 完成  createReq(self, ID, DATE, TIME, PLACE, Player):
# 读取request  --完成  getReq(self, ID):
# 修改request 只能加人  --完成   addReq(self, ID, new_player):
# 写request -- 改人  --完成   setReq(self, ID, PLAYERS):
# request 走人 --完成    remReq(self, ID, name):
# 删除request  --完成   delReq(self, ID):
# 修改request状态  --完成  changeReq(self, ID, state):
# 创建大场地的方法 可以静态后台使用 也可以调用  --完成  createField(self,field_name,field_location,court_number):
# 查看所有场地信息梗概  --完成 findFieldSituation(self):
# 索引指定大场地小场数量的方法   --完成   getFieldnum(self,field_name):
# 索引指定大场某天的小场全部信息   --完成 findField(self, field_name, date):
# 指定大场某天小场整坨写入  --完成 setField(self, field_name, date, Field_array):
# 生成game  --完成  createGame(self, ID, DATE, TIME, PLAYERS):
# 根据ID 获取Game --完成 getGame(self, ID):
# 获取某天以后的（包含本日） 或者全部的Game的id getAllGameID(self, date):
# 创建公告  --完成  createNotice(self):
# 修改公告  --完成  setNotice(self, content):
# 读公告  --完成   readNotice(self):
# 清除公告  --完成  clearNotice(self):

class Database(object):

    # 多线程的单例方法
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Database, "_instance"):
            with Database._instance_lock:
                if not hasattr(Database, "_instance"):
                    Database._instance = Database(*args, **kwargs)
        return Database._instance

    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017')

        self.db = self.client.basketball
        # 创建用户库 存在则切换至用户库
        self.col_1 = self.db['account']
        # 创建请求库 存在则切换至请求库
        self.col_2 = self.db['request']
        # 创建场地库 存在则切换至场地库
        self.col_3 = self.db['field']
        # 创建游戏库
        self.col_4 = self.db['game']
        # 创建公告库
        self.col_5 = self.db['notice']
        # 统计场地数量
        self.field_count = self.col_3.find({'data_type': 'field'}).count()
        self.col_3.update({'data_type': 'Field_count'}, {'$set': {'Field_count': self.field_count, 'data_type': 'Field_count'}})

    def setNewUser(self, name, id, phone_number, psw, other_info):
        # 插入用户信息
        # 如果用户id存在则不插入
        # 返回值： id不存在插入成功返回True id存在插入失败返回False
        # 功能：创建新用户 名字 id 电话 密码必须有 最后是个字典 没有额外信息填个{}
        # 字典类包含关键字：gender introduction college grade degree point req_game_id public_key
        # private_question private_answer
        # 构造包含上述信息的字典 即会存入数据库 没有的为空
        '''这个是我自己看的 无用
        Userinfo_set = {'name': name, 'id': id, 'phone': phone_number,
                        'personInfo': {'gender': '', 'introduction': '',
                                       'college': '', 'grade': '', 'degree': '',
                                       'point': ''},
                        'mailbox': None,
                        'mailcount': 0,
                        'readcount': 0,
                        'publicInfo': {'req_game_id': '', 'public_key': ''},
                        'privateInfo': {'private_question': signup_info['private_question'],
                                        'private_answer': signup_info['private_answer']},
                        'friendInfo': {'friends': None, 'friends_tbc': None}
                        }'''

        Userinfo_set = {}
        Userinfo_set['name'] = name
        Userinfo_set['id'] = id
        Userinfo_set['phone'] = phone_number
        Userinfo_set['password'] = psw
        Userinfo_set['mailbox'] = []
        Userinfo_set['mailcount'] = 0
        Userinfo_set['readcount'] = 0
        # 默认为空

        for temp in ['gender', 'introduction', 'college', 'grade', 'degree', 'point']:
            Userinfo_set['personInfo.'+temp] = ''
        for temp in ['req_game_id', 'public_key']:
            Userinfo_set['publicInfo.' + temp] = ''
        for temp in ['private_question', 'private_answer']:
            Userinfo_set['privateInfo.' + temp] = ''
        for temp in ['friends', 'friends_tbc']:
            Userinfo_set['friendInfo.' + temp] = ''

        # 其他信息存在
        if other_info:
            for key in other_info.keys():
                if key in ['gender', 'introduction', 'college', 'grade', 'degree', 'point']:
                    Userinfo_set['personInfo.' + key] = other_info[key]
                elif key in ['req_game_id', 'public_key']:
                    Userinfo_set['publicInfo.' + key] = other_info[key]
                elif key in ['private_question', 'private_answer']:
                    Userinfo_set['privateInfo.' + key] = other_info[key]
                elif key in ['friends', 'friends_tbc']:
                    Userinfo_set['friendInfo.' + key] = other_info[key]
                else:
                    Userinfo_set[key] = other_info[key]
        return not self.col_1.update({'id': Userinfo_set['id']}, {'$setOnInsert': Userinfo_set}, True)['updatedExisting']


    def findUser(self, important_info):
        # 根据关键信息找用户
        # 返回值：没找到返回False
        # 功能：根据关键信息找用户 关键信息是个字典
        # 推荐包含 name id phone 三者中的任意几个 几个条件作为并集进行检索 返回用户的全部信息
        # 返回值是个字典 如要id 就返回值['id']
        back = self.col_1.find(important_info)
        if back.count() == 0:
            return False
        else:
            return back[0]


    def setUserDirect(self, ID, keys_values):
        # 修改用户信息
        # 如果用户不存在则返回False
        # 功能： 输入用户ID 与一个包含键值对的字典
        # 字典上同
        Userinfo_set = {}
        for key in keys_values:
            if key in ['gender', 'introduction', 'college', 'grade', 'degree', 'point']:
                Userinfo_set['personInfo.' + key] = keys_values[key]
            elif key in ['req_game_id', 'public_key']:
                Userinfo_set['publicInfo.' + key] = keys_values[key]
            elif key in ['private_question', 'private_answer']:
                Userinfo_set['privateInfo.' + key] = keys_values[key]
            elif key in ['friends', 'friends_tbc']:
                Userinfo_set['friendInfo.' + key] = keys_values[key]
            else:
                Userinfo_set[key] = keys_values[key]
        return self.col_1.update({'id': ID}, {'$set': Userinfo_set}, False)['updatedExisting']


    def getUserAll(self, ID):

        # 读取指定用户id的全部信息
        # 返回值：如果用户存在返回一个字典 如果用户不存在返回False 该字典是原字典 会有层级 不包括mailbox信息
        # 典型值 {'_id': ObjectId('5b1c4ef2aecdfb18e142daf0'), 'id': '张三', 'friendInfo': {'friends': None, 'friends_tbc': None}, 'mailbox': None, 'name': '张三', 'personInfo': {'gender': 1, 'introduction': '开心', 'college': 2, 'grade': 3, 'degree': 4, 'point': 5}, 'phone': 10086, 'publicInfo': {'req_game_id': 13, 'public_key': 666}}
        back = self.col_1.find({'id': ID})
        reinfo = {}
        if back.count() == 0:
            return False
        else:
            for key in ['id','friendInfo','mailcount','name','password','personInfo','phone','privateInfo','publicInfo']:
                reinfo[key] = back[0][key]
            return reinfo


    def getUserInfo(self, ID, keys):
        # 读取用户指定信息
        # 如果用户不存在则返回False
        # 功能： 输入用户ID 与一个包含键名的list或者字典
        # 返回包含上述键名键值对的字典 为单层字典 直接索引
        Info = {}
        back = self.col_1.find({'id': ID})
        if not back.count() == 0:
            for key in keys:
                if key in ['gender', 'introduction', 'college', 'grade', 'degree', 'point']:
                    Info[key] = back[0]['personInfo'][key]
                elif key in ['req_game_id', 'public_key']:
                    Info[key] = back[0]['publicInfo'][key]
                elif key in ['private_question', 'private_answer']:
                    Info[key] = back[0]['privateInfo'][key]
                elif key in ['friends', 'friends_tbc']:
                    Info[key] = back[0]['friendInfo'][key]
                else:
                    Info[key] = back[0][key]
            return Info
        else:
            return False


    def setMail(self, ID, time, type, Data):

        # 为用户添加一个Mail信息
        # 返回值：添加成功返回True 失败返回False
        # 要求信息有用户ID mail的时间 类型 与数据 数据是任何格式即可 整存整取 可以是list什么的

        back = self.col_1.find({'id': ID})
        if not back.count() == 0:
            count_now = back[0]['mailcount']
            if self.col_1.update({'id': ID}, {
                '$push': {'mailbox': {'time': time, 'type': type,
                                     'data': Data, 'mailID': count_now+1, 'data_type': 'mail'}}},
                                     True)['updatedExisting']:
                box = back[0]['mailbox']
                len_num = len(box)
                if box[0] == "":
                    self.col_1.update({'id': ID}, {'$pop': {'mailbox': -1}})
                    len_num = len_num - 1
                box
                return self.col_1.update({'id': ID}, {'$set': {'mailcount': len_num}}, False)['updatedExisting']
            else:
                return False

        else:
            return False


    def getMail(self, ID, num):

        # 读取用户mailbox中的后num个mail
        # 输入量为‘ALL’时 返回全部的mail 倒序 以最近的为第一个元素 的list
        # 输入量超过mailbox总量时同上 返回全部的 不会报错
        # 输入量小于总量时 倒序的返回最后的num封mail
        # 典型返回值[{'mailID': 4, 'type': 'xxx', 'time': 'xxx0601', 'data_type': 'mail'},{'mailID': 3, 'type': 'xxx', 'time': 'xxx0602', 'data_type': 'mail'}]
        user = self.col_1.find({'id': ID})
        if user.count() == 0:
            return False
        if num == 'ALL':
            return list(reversed(user[0]['mailbox']))
        elif num == 'NEW':
            num_now = user[0]['mailcount']
            read_now = user[0]['readcount']
            reInfo = []
            for j in range(read_now+1,num_now+1):
                for mail in user[0]['mailbox']:
                    if mail['mailID'] == j:
                        reInfo.append(mail)
            self.col_1.update({'id': ID},{'$set':{'readcount':num_now}})
            return list(reversed(reInfo))
        elif num >= 1:
            num_now = user[0]['mailcount']
            num_list = []
            reInfo = []
            if num >= num_now:
                return list(reversed(user[0]['mailbox']))
            else:
                for i in range(num):
                    num_list.append(num_now-i)
            for i in num_list:
                for mail in user[0]['mailbox']:
                    if mail['mailID'] == i:
                        reInfo.append(mail)
            return reInfo


    def getMailID(self, ID, mailid):

        # 读取用户mailbox中指定id的mail
        # 一般不用这个功能大概
        # 返回值 [{'mailID': 3, 'type': 'xxx', 'time': 'xxx0602', 'data_type': 'mail'}]
        user = self.col_1.find({'id': ID})
        if user.count() == 0:
            return False
        for mail in user[0]['mailbox']:
            if mail['mailID'] == mailid:
                return mail
        return None

    def checkCount(self, ID):
        user = self.col_1.find({'id': ID})
        if user.count() == 0:
            return False
        else:
            num_now = user[0]['mailcount']
            read_now = user[0]['readcount']
            if num_now == read_now :
                return 'yes'
            else:
                return 'no'

    def getCount(self,ID):
        user = self.col_1.find({'id': ID})
        if user.count() == 0:
            return None
        else:
            return user[0]['readcount']

    def setCount(self, ID, num):
        return self.col_1.update({'id': ID},{'$set':{'readcount':num}},False)['updatedExisting']

    def getMailCount(self, ID, read_num):
        user = self.col_1.find({'id': ID})
        if user.count() == 0:
            return False
        if read_num == 'ALL':
            readcount = user[0]['mailcount']
            if self.col_1.update({'id': ID}, {'$set': {'readcount': readcount}}, False)['updatedExisting']:
                return list(reversed(user[0]['mailbox']))
            else:
                return False
        elif read_num >= 1:
            num_now = user[0]['mailcount']
            num_list = []
            reInfo = []
            if read_num >= num_now:
                readcount = user[0]['mailcount']
                if self.col_1.update({'id': ID}, {'$set': {'readcount': readcount}}, False)['updatedExisting']:
                    return list(reversed(user[0]['mailbox']))
                else:
                    return False
            else:
                for i in range(read_num):
                    num_list.append(num_now - i)
            for i in num_list:
                for mail in user[0]['mailbox']:
                    if mail['mailID'] == i:
                        reInfo.append(mail)
            readcount = user[0]['mailcount']
            if self.col_1.update({'id': ID}, {'$set': {'readcount': readcount}}, False)['updatedExisting']:
                return reInfo
            else:
                return False



    def createReq(self, ID, DATE, TIME, PLACE, Player):

        # 创建一个request
        # 要求输入 ID DATE 时间 ‘20180611’ TIME = [] PlACE 'A' player（ 名字或id 一样的）
        Reqinfo_set = {}
        Reqinfo_set['ID'] = ID
        Reqinfo_set['DATE'] = DATE
        Reqinfo_set['TIME'] = TIME
        Reqinfo_set['PLACE'] = PLACE
        Reqinfo_set['IS_FINDING'] = False
        if isinstance(Player, type('张三')):
            Reqinfo_set['PLAYERS'] = []
            Reqinfo_set['PLAYERS'].append(Player)
        elif isinstance(Player, type(list())):
            Reqinfo_set['PLAYERS'] = Player
        else:
            print('Req Play err')
            return False
        return not self.col_2.update({'ID':ID}, {'$setOnInsert': Reqinfo_set}, True)['updatedExisting']


    def getReq(self, ID):
        # 通过ID获取request
        # 返回一个字典
        # {'_id':fjiafljsvnjaljkABFc, 'ID': 1, 'DATE': '20180611', 'PLACE': 'xxxx' 'PLAYERS':['a','b','c']}
        back = self.col_2.find({'ID': ID})
        if back.count() == 0:
            return False
        else:
            return back[0]


    def addReq(self, ID, new_player):

        # 指定request加人
        # 失败返回FALSE
        Req = self.col_2.find({'ID': ID})
        if Req.count() == 0:
            return False
        else:
            pass
            # Req = Req[0]
        return self.col_2.update({'ID': ID},{'$push':{'PLAYERS': new_player}}, False)['updatedExisting']


    def changeReq(self, ID, state):
        # 通过ID获取request
        # 修改其IS_FINDING状态 True False
        Req = self.col_2.find({'ID': ID})
        if Req.count() == 0:
            return False
        else:
            return self.col_2.update({'ID': ID},{'$set':{'IS_FINDING': state}}, True)['updatedExisting']

    def delReq(self, ID):
        # 给ID 消灭这个req 直接就没了
        self.col_2.remove({'ID': ID}, 1)
        return True

    def setReq(self, ID, PLAYERS):
        # 直接写list 玩家名的接口 要求PLAYERS 是个列表
        if not isinstance(PLAYERS, type(list())):
            return False
        Req = self.col_2.find({'ID': ID})
        if Req.count() == 0:
            return False
        else:
            return self.col_2.update({'ID': ID}, {'$set': {'PLAYERS': PLAYERS}}, True)['updatedExisting']

    def remReq(self, ID, name):
        Req = self.col_2.find({'ID': ID})
        if Req.count() == 0:
            return False
        else:
            players = Req[0]['PLAYERS']
            print(players)
            print(name)
            if isinstance(name, type(list())):
                for nam in name:
                    Flag = False
                    for player in players:
                        print(player)
                        if player == nam:
                            players.remove(nam)
                            Flag = True
                    if Flag == True:
                        continue
                    return False
                self.col_2.update({'ID': ID}, {'$set': {'PLAYERS': players}}, True)['updatedExisting']
                return True
            elif isinstance(name, type('')):
                for player in players:
                    if player == name :
                        players.remove(name)
                        self.col_2.update({'ID': ID}, {'$set': {'PLAYERS': players}}, True)['updatedExisting']
                        return True
                return False

    def getAllReqID(self, date):
        if date == 'ALL':
            back = self.col_2.find({'ID':{'$exists': True}})
            relist = []
            if back.count() == 0:
                return False
            else:
                for req in back:
                    relist.append(req['ID'])
                return relist
        else:
            back = self.col_4.find({'DATE': {'$gte': date}})
            relist = []
            if back.count() == 0:
                return False
            else:
                for req in back:
                    relist.append(req['ID'])
                return relist


    def createField(self,field_name,field_location,court_number):
        field_num_now = self.col_3.find({'Field_count': {'$exists': True }})
        if field_num_now.count() == 0:
            self.col_3.insert({'Field_count': 0})
            field_num_now = 0
        else:
            field_num_now = field_num_now[0]['Field_count']
        # 成功的添加了个大场地
        if not self.col_3.update({'field_name': field_name}, {'$setOnInsert': {'id': field_num_now+1, 'data_type': 'field',  'field_name': field_name,
                                                                                   'field_location': field_location, 'court_number': court_number}}, True)['updatedExisting']:
            # 计数器+1
            self.col_3.update({'Field_count': {'$exists': True }},{'$inc': {'Field_count': 1}})
            # 创建子场地
            Date = []
            for i in range(1, 31):
                if i <=9:
                    Date.append('2018060'+str(i))
                else:
                    Date.append('201806'+str(i))
            childInfo = {}
            # 构造一个大列表 表示场地信息
            for d in Date:
                child = [{'court_id': field_name + str(i + 1),
                          'time_blocks': [{'id': field_name+str(i+1), 'time': j, 'requests': [], 'game_id': ''} for j in
                                          range(8, 21)]} for i in range(court_number)]
                childInfo[d] = child
            # 直接把大列表存入数据库 作为场地文件的子文件
            self.col_3.update({'field_name': field_name}, {'$set': {'child': childInfo}}, True)
            return True
        else:
            return False

    def findFieldSituation(self):
        reinfo = {}
        field = self.col_3.find({'data_type': 'field'})
        if field.count == 0:
            return False
        else:
            for f in field:
                id = f['id']
                info = {'field_name':f['field_name'], 'field_location': f['field_location'], 'court_number': f['court_number'], 'id': id}
                reinfo[f['field_name']] = info
        return reinfo



    def getFieldnum(self,field_name):
        field = self.col_3.find({'field_name': field_name})
        if field.count == 0:
            return False
        else:
            return field[0]['court_number']

    def findField(self, field_name, date):
        field = self.col_3.find({'field_name': field_name})
        if field.count() == 0:
            return False
        else:
            # 大列表
            child = field[0]['child']
            # 日期层
            small_field = child[date]
            return small_field

    def setField(self, field_name, date, Field_array):
        field = self.col_3.find({'field_name': field_name})
        if field.count() == 0:
            return False
        else:
            return self.col_3.update({'field_name': field_name},{'$set': {'child.'+date: Field_array}},False)['updatedExisting']

    def createGame(self, ID, DATE, TIME, PLAYERS):
        # 创建一个GAME 只有写 不删不改
        # 输入 ID ‘20180611’ 一个数
        Gameinfo_set = {}
        Gameinfo_set['ID'] = ID
        Gameinfo_set['DATE'] = DATE
        Gameinfo_set['TIME'] = TIME
        Gameinfo_set['PLAYERS'] = PLAYERS
        if isinstance(PLAYERS, type(list())):
            Gameinfo_set['PLAYERS'] = PLAYERS
            return not self.col_4.update({'ID': Gameinfo_set['ID']}, {'$setOnInsert': Gameinfo_set}, True)[
            'updatedExisting']
        else:
            return False

    def getGame(self, ID):
        # 读取指定用户id的全部信息
        # 返回值：如果用户存在返回一个字典 如果用户不存在返回False 该字典是原字典 会有层级 不包括mailbox信息
        # 典型值 {'_id': ObjectId('5b1c4ef2aecdfb18e142daf0'), 'id': '张三', 'friendInfo': {'friends': None, 'friends_tbc': None}, 'mailbox': None, 'name': '张三', 'personInfo': {'gender': 1, 'introduction': '开心', 'college': 2, 'grade': 3, 'degree': 4, 'point': 5}, 'phone': 10086, 'publicInfo': {'req_game_id': 13, 'public_key': 666}}
        back = self.col_4.find({'ID': ID})
        if back.count() == 0:
            return False
        else:
            return back[0]

    def getAllGameID(self, date):
        #date 可以是ALL 返回所有的id 可以是时间下限 返回包含这天及之后的所有ID
        if date == 'ALL':
            back = self.col_4.find({'ID':{'$exists': True}})
            relist = []
            if back.count() == 0:
                return False
            else:
                for game in back:
                    relist.append(game['ID'])
                return relist
        else:
            back = self.col_4.find({'DATE': {'$gte': date}})
            relist = []
            if back.count() == 0:
                return False
            else:
                for game in back:
                    relist.append(game['ID'])
                return relist


    # 下面是公告类 可以创建 只能建一个 已有就不会再建了
    # 可以清空
    # 可以写入 写啥是啥 字符串数组啥的
    def createNotice(self):
        self.col_5.update({'id': 0000},{'$setOnInsert':{'ID': 0000, 'CONTENT': ''}},True)['updatedExisting']
        return True

    def readNotice(self):
        back = self.col_5.find({'id': 0000})
        if back.count() == 0:
            return False
        else:
            return back[0]['CONTENT']

    def clearNotice(self):
        self.col_5.update({'id': 0000}, {'$set': {'CONTENT': ''}}, True)['updatedExisting']
        return True

    def setNotice(self, content):
        self.col_5.update({'id': 0000}, {'$set': {'CONTENT': content}}, True)['updatedExisting']
        return True


# Userinfo_set = {'personInfo': {'gender': 1, 'introduction': "开心",
#                         'college': 2, 'grade': 3, 'degree': 4,
#                         'point': 5},
#                         'mailbox': None,
#                         'publicInfo': {'req_game_id': 13, 'public_key': 666},
#                         'friendInfo': {'friends': None, 'friends_tbc': None}
#                         }
#
#a = Database.instance()
#a.setNewUser('张三', '张三', 10086, '911', Userinfo_set) #测试成功

#important_info = {}
#important_info['phone'] = 10086
#print(a.findUser(important_info))   #测试成功

#info = {'private_answer': 'lala','private_question': 'poi'}  #测试成功
#print(a.setUserDirect('张三',info))

#print(a.getUserAll('张三'))

#print(a.getUserInfo('张三',['id','mailcount','mailbox','college','private_question'] ))
#{'id': '张三', 'mailcount': 0, 'mailbox': None, 'college': '', 'private_question': 'poi'}
#info = {'private_answer': 'lala','private_question': 'poi'}
#print(a.setMail('张三', '7月', 'create', info))

#print(a.getMail('张三', 'ALL'))
#print(a.getMailID('张三',4))

#player = ['张三']
#print(a.createReq(1,'20180611',[1,2,1],'D',player))
#print(a.getReq(1))

#a.delReq(1)
#new = '王五'
#print(a.addReq(1,new))

#print(a.changeReq(1,True))

#print(a.setReq(1,['力','里' ,'拉' ]))

#print(a.remReq(1,['力','里']))
#print(a.createField('D','la',2))
#print(a.findFieldSituation())
#{'A': {'field_name': 'A', 'field_location': '东区', 'court_number': 4, 'id': 1}, 'B': {'field_name': 'B', 'field_location': '西区', 'court_number': 4, 'id': 2}, 'C': {'field_name': '

#print(a.getFieldnum('C'))
#print(a.findField('A','20180610'))
#ceshi = [[{'REQUESTING_ID': [], 'GAME_ID': True}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}], [{'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}], [{'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}], [{'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}, {'REQUESTING_ID': [], 'GAME_ID': False}]]
#print((a.setField('A','20180610',ceshi)))
#print(a.createNotice())
#print(a.setNotice(['了解一下','aabb','一个消息']))
#print(a.readNotice())
#print(a.clearNotice())
#print(a.createGame(1,'20180613',[3],['6','2','1']))
#print(a.getAllGameID('20180615'))
#print(a.getGame(5))
# {'_id': ObjectId('5b1f349daecdfb18e1430e38'), 'ID': 5, 'DATE': '20180619', 'PLAYERS': ['6', '4', '3'], 'TIME': [3]}