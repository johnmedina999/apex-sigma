import os
import yaml


def load_alternate_command_names():

    alts = {}
    directory = 'sigma/plugins'

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file != 'plugin.yml': continue
            file_path = (os.path.join(root, file))

            with open(file_path) as plugin_file:
                plugin_data = yaml.safe_load(plugin_file)
                
                if not plugin_data['enabled']: continue
                if 'commands' not in plugin_data: continue
                
                try:
                    for command in plugin_data['commands']:
                        if 'alts' not in command: continue
                    
                        for alt in command['alts']:
                            plugin_name = command['name']
                            alts.update({alt: plugin_name})
                except TypeError:
                    print("[ERROR] Unable to load the " + str(plugin_data['name'] + " plugin"))

                    if plugin_data['commands'] == None:
                        print("        REASON: Commands tag in plugin.py exists but no command is listed")

                    if plugin_data['events'] == None:
                        print("        REASON: Events tag in plugin.py exists but no command is listed")
                        
                    raise
    return alts
