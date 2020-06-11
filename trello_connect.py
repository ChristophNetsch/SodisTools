# -*- coding: utf-8 -*-

from trello import TrelloClient
from styleframe import StyleFrame
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import shutil
from slack import WebClient
from slack.errors import SlackApiError
import numpy as np
import configparser as ConfigParser

#ROOT=r'C:\Users\cnets\Desktop\SodisTools_development'
COLUMNS=['Board','List','Title','Link','Description','Checklists','Comments','Due','Members']
#os.chdir(r'C:\Users\cnets\Desktop\SodisTools_development')


#get authentication

with open (r"keys/trello_API_key.txt", "r") as file:
    api_key=file.readlines()
with open (r"keys/trello_API_secret.txt", "r") as file:
    api_secret=file.readlines()

#connect to Trello
timestamp=datetime.today().strftime('%Y%m%d')
client = TrelloClient(
    api_key=api_key,
    api_secret=api_secret
)
del api_key
del api_secret


"""
REPORT TOOL
"""
#TRELLO OBJEKT ERSTELLEN

#AUSLESEN DER KONFIGDATEI
configParser = ConfigParser.RawConfigParser()   
configFilePath = r"report_test_folder/config.txt"
configParser.read(configFilePath)
board_id = configParser.get("Section IDs","Boards-IDs").split(",")
alist_id = configParser.get("Section IDs","Active List-IDs").split(",")
flist_id = configParser.get("Section IDs","Final List-IDs").split(",")
dlist_id = configParser.get("Section IDs","Done List-IDs").split(",")
list_id_order = configParser.get("Section IDs","List-ID Forward Order").split(",")
report_repeat = configParser.get("Parameters","repeat")
report_time = configParser.get("Parameters","report_time")

#INITIALISIERUNG

def get_cards_from_list_id (list_ids):
    tmp_cards=[]
    for tmp_board in client.list_boards():
        if tmp_board.id in board_id:
            for tmp_list in tmp_board.all_lists(): 
                if tmp_list.id in list_ids:
                    tmp_cards+=tmp_list.list_cards()
    return tmp_cards
tmp_cards = get_cards_from_list_id (alist_id) + get_cards_from_list_id (flist_id)

    
#BERECHNUNG DER PARAMETER


#OUTPUT AUSGABE



#########################
def get_card_data(card):
    def _check_data(entry):
        if type(entry)==list:
            string=''
            for sub_entry in entry:
                string+=str(sub_entry)+', \n'
        else:
            string=entry
        return str(string)
    
    def _translate_member_ids(member_ids):
        entry=''
        for member_id in member_ids:
            entry+=card.client.get_member(member_id).full_name + ', \n'
        return entry
    
    def _merge_checklists(checklists):
        merged_lists=[]
        for checklist in checklists:
            for item in checklist.items:
                merged_lists.append(item['name'])
        return merged_lists
    
                        
    card_dict={'Board':_check_data(card.board.name),
            'List':_check_data(card.get_list().name),
            'Title':_check_data(card.name),
            'Link':_check_data(card.short_url),
            'Description':_check_data(card.description),
            'Checklists':_check_data(_merge_checklists(card.checklists)),
            'Comments':_check_data(card.comments),
            'Due':_check_data(card.due),
            'Members':_check_data(_translate_member_ids(card.member_ids))
            }
    return card_dict


"""
EXPORT TOOL VON CHRISTOPH
def export2excel():
    try:
        subdir=fr'temp\{timestamp}'
        Path(subdir).mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        shutil.rmtree(subdir)
        Path(subdir).mkdir(parents=True, exist_ok=False)
        
    for board in all_boards[0:1]:
        df_trello=pd.DataFrame(columns=COLUMNS)
        for i,card in enumerate(board.all_cards()):
            df_trello=df_trello.append(get_card_data(card),ignore_index=True)
        
        board_name=board.name
        for char in board_name: #remove forbidden characters from filename
            if char in " ?.!/;:":
                board_name.replace(char,'')   
        #sf = StyleFrame(df_trello) #excel customization, see: https://styleframe.readthedocs.io/en/latest/usage_examples.html
        df_trello.to_excel(fr'temp/{timestamp}/{board_name}.xlsx',sheet_name='trello_export')   



if __name__=='__main__':
    speed_eval=True
    if speed_eval:
        import pstats
        import io
        import cProfile
        pr = cProfile.Profile()
        pr.enable()
        
    export2excel() #operation deactivated
    
    if speed_eval:
        pr.disable()
        result = io.StringIO()
        pstats.Stats(pr,stream=result).print_stats()
        result=result.getvalue()
        # chop the string into a csv-like buffer
        result='ncalls'+result.split('ncalls')[-1]
        result='\n'.join([','.join(line.rstrip().split(None,5)) for line in result.split('\n')])
        # save it to disk
        
        with open(fr'temp/speed_eval.csv', 'w+') as f:
            #f=open(result.rsplit('.')[0]+'.csv','w')
            f.write(result)
            f.close()
            
            speed_eval = pd.read_csv(fr'temp/speed_eval.csv')
"""
    
