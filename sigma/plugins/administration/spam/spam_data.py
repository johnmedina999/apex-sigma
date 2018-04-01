import arrow

class SpamInfo():
    PERSISTANCE = 0
    TIER        = 1
    MUTED       = 2
    CHECK_TIME  = 3


    def __init__(self):
        
        ''' Format:
        {
            server : { 
                channel : [ message, message, ... ],
                channel : [ message, message, ... ],
                ...
            },
            server : { 
                channel : [ message, message, ... ],
                channel : [ message, message, ... ],
            ...
            },
            ...
            }
        '''
        self.spam_info = {}


    def reset_info(self, ev, guild_id, channel_id):
        try: self.spam_info[guild_id][channel_id] = [0, 1, False, arrow.utcnow().timestamp]
        except:
            try: 
                self.spam_info[guild_id] = {}
                self.spam_info[guild_id][channel_id] = [0, 1, False, arrow.utcnow().timestamp]
            except: 
                ev.log.info('[SPAM MONITOR] Unable to record spam info for channel id ' + channel_id + ' in guild id' + guild_id)


    def ensure_data_existance(self, ev, guild_id, channel_id):
        try: self.spam_info[guild_id][channel_id]
        except: self.reset_info(ev, guild_id, channel_id)


    # How persistant spam is on a server (persistance, tier)
    def add_info(self, ev, guild_id, channel_id):
        self.ensure_data_existance(ev, guild_id, channel_id)

        if self.spam_info[guild_id][channel_id][self.PERSISTANCE] == 3:
            self.spam_info[guild_id][channel_id][self.PERSISTANCE] = 0
            self.spam_info[guild_id][channel_id][self.TIER] += 1
        else:
            self.spam_info[guild_id][channel_id][self.PERSISTANCE] += 1
        

    def set_spam_tier(self, ev, guild_id, channel_id, tier):          self.ensure_data_existance(ev, guild_id, channel_id); self.spam_info[guild_id][channel_id][self.TIER]        = tier
    def set_persistance(self, ev, guild_id, channel_id, persistance): self.ensure_data_existance(ev, guild_id, channel_id); self.spam_info[guild_id][channel_id][self.PERSISTANCE] = persistance
    def update_check_time(self, ev, guild_id, channel_id):            self.ensure_data_existance(ev, guild_id, channel_id); self.spam_info[guild_id][channel_id][self.CHECK_TIME]  = arrow.utcnow().timestamp
    def set_muted_status(self, ev, guild_id, channel_id, status):     self.ensure_data_existance(ev, guild_id, channel_id); self.spam_info[guild_id][channel_id][self.MUTED]       = status


    def get_spam_tier(self, ev, guild_id, channel_id):    self.ensure_data_existance(ev, guild_id, channel_id); return self.spam_info[guild_id][channel_id][self.TIER]
    def get_persistance(self, ev, guild_id, channel_id):  self.ensure_data_existance(ev, guild_id, channel_id); return self.spam_info[guild_id][channel_id][self.PERSISTANCE]
    def get_muted_status(self, ev, guild_id, channel_id): self.ensure_data_existance(ev, guild_id, channel_id); return self.spam_info[guild_id][channel_id][self.MUTED]
    def get_check_time(self, ev, guild_id, channel_id):   self.ensure_data_existance(ev, guild_id, channel_id); return self.spam_info[guild_id][channel_id][self.CHECK_TIME]



class MessageInfo():

    def __init__(self):
        # Contains spam_sample_time's worth of message from all channels in all guilds
        self.message_sample = {}


    def reset_info(self, ev, guild_id, channel_id):
        try: self.message_sample[guild_id][channel_id] = []
        except:
            self.message_sample[guild_id] = {}
            self.message_sample[guild_id][channel_id] = []


    def ensure_data_existance(self, ev, guild_id, channel_id):
        try: self.message_sample[guild_id][channel_id]
        except: self.reset_info(ev, guild_id, channel_id)

    
    def add_to_message_sample(self, ev, message):
        try:    self.ensure_data_existance(ev, message.guild.id, message.channel.id)
        except: ev.log.info('[SPAM MONITOR] Unable to record message sample for channel' + message.channel.name + ' in ' + message.guild.name)
        else:   self.message_sample[message.guild.id][message.channel.id].append(message)


    def get_message_sample(self, guild_id, channel_id):
        return self.message_sample[guild_id][channel_id]
        