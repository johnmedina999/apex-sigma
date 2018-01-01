collection = 'Profile_Links'


def updateDiscordProfileLink(db, uid, profile_type, link):
    if not uid:          raise Exception('db_node/profiles.py : updateDiscordProfileLink | uid = None')
    if not profile_type: raise Exception('db_node/profiles.py : updateDiscordProfileLink | profile_type = None')
    if not link:         raise Exception('db_node/profiles.py : updateDiscordProfileLink | link   = None')
    
    uid = str(uid)
    user_data_out    = { 'UserID': uid, 'Moderated': False, 'Profiles' : {} }
    profile_data_out = { 'ProfileType': profile_type, 'Link': link }

    user_data_in = db[collection].find_one({ 'UserID': uid })
    if not user_data_in: db[collection].insert_one(user_data_out)

    user_data_out = db[collection].find_one({ 'UserID': uid })
    user_data_out['Profiles'][profile_type] = link

    db[collection].update_one({'UserID': uid},
                              {'$set': user_data_out})


def removeDiscordProfileLink(db, uid, profile_type=None):
    if not uid: raise Exception('db_node/profiles.py : updateDiscordProfileLink | uid = None')
    
    uid = str(uid)
    user_data = db[collection].find_one({ 'UserID': uid })
    
    if not user_data: return
    if not profile_type: db[collection].delete_one({ 'UserID': uid }); return
    if not profile_type in user_data['Profiles']: return

    user_data['Profiles'].remove(profile_type)
    db[collection].update_one({'UserID': uid},
                              {'$set': user_data})


def getDiscordProfileLink(db, uid, profile_type=None):
    if not uid: raise Exception('db_node/profiles.py : updateDiscordProfileLink | uid = None')

    uid = str(uid)
    user_data = db[collection].find_one({ 'UserID': uid })
    
    if not user_data: return None
    if not profile_type: return user_data['Profiles']
    if not profile_type in user_data['Profiles']: return None
    
    return { profile_type : user_data['Profiles'][profile_type] }


def setModerationDiscordProfileLink(db, uid, moderation):
    if not uid: raise Exception('db_node/profiles.py : updateDiscordProfileLink | uid = None')
    
    uid = str(uid)
    user_data = db[collection].find_one({ 'UserID': uid })

    if not user_data: raise Exception('User does not exist')
    user_data['Moderated'] = moderation

    db[collection].update_one({'UserID': uid},
                              {'$set': user_data})


def isModerationDiscordProfileLink(db, uid):
    if not uid: raise Exception('db_node/profiles.py : updateDiscordProfileLink | uid = None')
    
    uid = str(uid)
    user_data = db[collection].find_one({ 'UserID': uid })

    if not user_data: raise Exception('User does not exist')
    return user_data['Moderated']