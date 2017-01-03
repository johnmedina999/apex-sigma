import pymongo
import time

from .logger import create_logger


class DatabaseError(Exception):
    pass


class IntegrityError(DatabaseError):
    pass


class Database(object):
    def __init__(self, db_addr):
        self.db = None
        self.log = create_logger('database')

        if db_addr:
            self.connect(db_addr)
        else:
            raise DatabaseError('No database address given!')

    def connect(self, db_addr):
        self.moncli = pymongo.MongoClient(db_addr)
        self.db = self.moncli.aurora

    def insert_one(self, collection, data):
        if self.db:
            self.db[collection].insert_one(data)

    def find(self, collection, data):
        if self.db:
            result = self.db[collection].find(data)
            return result

    def update_one(self, collection, target, data):
        if self.db:
            self.db[collection].update_one(target, data)

    def delete_one(self, collection, data):
        if self.db:
            self.db[collection].delete_one(data)

    def add_stats(self, statname):
        if self.db:
            collection = 'Stats'
            find_data = {
                'Role': 'Stats'
            }
            find_res = self.db[collection].find(find_data)
            count = 0
            for res in find_res:
                try:
                    count = res[statname]
                except:
                    count = 0
            new_count = count + 1
            updatetarget = {"Role": 'Stats'}
            updatedata = {"$set": {statname: new_count}}
            self.db[collection].update_one(updatetarget, updatedata)

    def set_cooldown(self, sid, uid, command):
        if self.db:
            timestamp = int(time.time())
            collection = 'Cooldowns'
            find_data = {
                'ServerID': sid,
                'UserID': uid,
                'Type': command
            }
            find_results = self.db[collection].find(find_data)
            n = 0
            for res in find_results:
                n += 1
            if n == 0:
                data = {
                    'ServerID': sid,
                    'UserID': uid,
                    'Type': command,
                    'LastTimestamp': timestamp
                }
                self.db[collection].insert_one(data)
            else:
                updatetarget = {
                    'ServerID': sid,
                    'UserID': uid,
                    'Type': command}
                updatedata = {"$set": {'LastTimestamp': timestamp}}
                self.db[collection].update_one(updatetarget, updatedata)

    def on_cooldown(self, sid, uid, command, cooldown):
        if self.db:
            collection = 'Cooldowns'
            find_data = {
                'ServerID': sid,
                'UserID': uid,
                'Type': command
            }
            find_results = self.db[collection].find(find_data)
            n = 0
            target = None
            for res in find_results:
                n += 1
                target = res
            if n == 0:
                return False
            else:
                curr_stamp = int(time.time())
                last_stamp = target['LastTimestamp']
                if (last_stamp + cooldown) < curr_stamp:
                    return False
                else:
                    return True

    def get_cooldown(self, sid, uid, command, cooldown):
        if self.db:
            collection = 'Cooldowns'
            find_data = {
                'ServerID': sid,
                'UserID': uid,
                'Type': command
            }
            find_results = self.db[collection].find(find_data)
            n = 0
            target = None
            for res in find_results:
                n += 1
                target = res
            if n == 0:
                return 0
            else:
                curr_stamp = int(time.time())
                last_stamp = target['LastTimestamp']
                cd_time = (last_stamp + cooldown) - curr_stamp
                return cd_time

    def add_points(self, server, user, points):
        if self.db:
            target = None
            n = 0
            collection = 'PointSystem'
            finddata = {
                'UserID': user.id,
                'ServerID': server.id
            }
            insertdata = {
                'UserID': user.id,
                'ServerID': server.id,
                'Points': 0,
                'UserName': user.name,
                'Avatar': user.avatar_url,
                'Level': 0
            }
            finddata_results = self.db[collection].find(finddata)
            for item in finddata_results:
                n += 1
                target = item
            if n == 0:
                self.db[collection].insert_one(insertdata)
            else:
                curr_pts = target['Points']
                add_pts = abs(points)
                new_pts = curr_pts + add_pts
                level = int(new_pts / 1690)
                updatetarget = {"UserID": user.id, "ServerID": server.id}
                updatedata = {"$set": {
                    "Points": new_pts,
                    'UserName': user.name,
                    'Avatar': user.avatar_url,
                    'Level': level
                }}
                self.db[collection].update_one(updatetarget, updatedata)

    def take_points(self, server, user, points):
        if self.db:
            target = None
            n = 0
            collection = 'PointSystem'
            finddata = {
                'UserID': user.id,
                'ServerID': server.id
            }
            insertdata = {
                'UserID': user.id,
                'ServerID': server.id,
                'Points': 0,
                'UserName': user.name,
                'Avatar': user.avatar_url,
                'Level': 0
            }
            finddata_results = self.db[collection].find(finddata)
            for item in finddata_results:
                n += 1
                target = item
            if n == 0:
                self.db[collection].insert_one(insertdata)
            else:
                curr_pts = target['Points']
                rem_pts = abs(points)
                new_pts = curr_pts - rem_pts
                level = int(new_pts / 1690)
                updatetarget = {"UserID": user.id, "ServerID": server.id}
                updatedata = {"$set": {
                    "Points": new_pts,
                    'UserName': user.name,
                    'Avatar': user.avatar_url,
                    'Level': level
                }}
                self.db[collection].update_one(updatetarget, updatedata)

    def get_points(self, server, user):
        if self.db:
            target = None
            n = 0
            collection = 'PointSystem'
            finddata = {
                'UserID': user.id,
                'ServerID': server.id
            }
            search = self.db[collection].find(finddata)
            for res in search:
                n += 1
                target = res
            if n == 0:
                return 0
            else:
                points = target['Points']
                return points

    def init_server_settings(self, servers):
        if self.db:
            for server in servers:
                search = self.db['ServerSettings'].find({'ServerID': server.id})
                n = 0
                for res in search:
                    n += 1
                if n == 0:
                    default_settings = {
                        'ServerID': server.id,
                        'Greet': True,
                        'GreetMessage': 'Hello %user_mention%, welcome to %server_name%',
                        'GreetChannel': server.default_channel.id,
                        'GreetPM': False,
                        'Bye': True,
                        'ByeMessage': '%user_mention% has left the server.',
                        'ByeChannel': server.default_channel.id,
                        'CleverBot': True,
                        'Unflip': False,
                        'ShopEnabled': True,
                        'ShopItems': [],
                        'RandomEvents': False,
                        'EventChance': 1,
                        'ChatAnalysis': True,
                        'MarkovCollect': True,
                        'BlockInvites': False,
                        'AntiSpam': False,
                        'IsBlacklisted': False,
                        'BlacklistedChannels': [],
                        'BlacklistedUsers': [],
                        'AutoRole': None,
                        'SelfRoles': []
                    }
                    self.db['ServerSettings'].insert_one(default_settings)

    def add_new_server_settings(self, server):
        if self.db:
            search = self.db['ServerSettings'].find({'ServerID': server.id})
            n = 0
            for res in search:
                n += 1
            if n == 0:
                default_settings = {
                    'ServerID': server.id,
                    'Greet': True,
                    'GreetMessage': 'Hello %user_mention%, welcome to %server_name%',
                    'GreetChannel': server.default_channel.id,
                    'GreetPM': False,
                    'Bye': True,
                    'ByeMessage': '%user_mention% has left the server.',
                    'ByeChannel': server.default_channel.id,
                    'CleverBot': True,
                    'Unflip': False,
                    'ShopEnabled': True,
                    'ShopItems': [],
                    'RandomEvents': False,
                    'EventChance': 1,
                    'ChatAnalysis': True,
                    'MarkovCollect': True,
                    'BlockInvites': False,
                    'AntiSpam': False,
                    'IsBlacklisted': False,
                    'BlacklistedChannels': [],
                    'BlacklistedUsers': [],
                    'AutoRole': None,
                    'SelfRoles': []
                }
                self.db['ServerSettings'].insert_one(default_settings)

    def get_settings(self, server_id, setting):
        if self.db:
            collection = 'ServerSettings'
            finddata = {
                'ServerID': server_id,
            }
            search = self.db[collection].find(finddata)
            n = 0
            target = None
            for res in search:
                n += 1
                target = res
            if target:
                return target[setting]
            else:
                return None

    def set_settings(self, server_id, setting, setting_variable):
        if self.db:
            collection = 'ServerSettings'
            updatetarget = {'ServerID': server_id}
            updatedata = {'$set': {setting: setting_variable}}
            self.db[collection].update_one(updatetarget, updatedata)