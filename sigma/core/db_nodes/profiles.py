collection = 'Profile_Links'


def updateDiscordProfileLink(db, uid, profile_type, link):
    if not uid:          raise Exception('db_node/profiles.py : updateDiscordProfileLink | uid = None')
    if not profile_type: raise Exception('db_node/profiles.py : updateDiscordProfileLink | profile_type = None')
    if not link:         raise Exception('db_node/profiles.py : updateDiscordProfileLink | link   = None')
    
    uid = str(uid)
    user_data = db[collection].find_one({ 'UserID': uid })

    if not user_data: 
        user_data = { 'UserID': uid, 'Moderated': False, 'Profiles' : {} }
        db[collection].insert_one(user_data)
        user_data = db[collection].find_one({ 'UserID': uid })

    user_data['Profiles'][profile_type] = link
    db[collection].update_one({ 'UserID': uid },
                              { '$set': {'Profiles' : user_data['Profiles']} })


def removeDiscordProfileLink(db, uid, profile_type=None):
    if not uid: raise Exception('db_node/profiles.py : updateDiscordProfileLink | uid = None')
    
    uid = str(uid)
    user_data = db[collection].find_one({ 'UserID': uid })
    
    if not user_data: return
    if not profile_type: db[collection].delete_one({ 'UserID': uid }); return
    if not profile_type in user_data['Profiles']: return

    db[collection].update_one({ 'UserID': uid },
                              { '$unset': {profile_type : ''} })


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
    db[collection].update_one({ 'UserID': uid },
                              { '$set': {'Moderated' : moderation} })


def isModerationDiscordProfileLink(db, uid):
    if not uid: raise Exception('db_node/profiles.py : updateDiscordProfileLink | uid = None')
    
    uid = str(uid)
    user_data = db[collection].find_one({ 'UserID': uid })

    if not user_data: raise Exception('User does not exist')
    return user_data['Moderated']