# -*- coding: utf-8 -*-
"""
Spyder Editor

Dies ist eine temporäre Skriptdatei.
"""

from trello import TrelloClient
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

ROOT=r'C:\Users\cnets\Desktop\SodisTools_development'
COLUMNS=['Board','List','Title','Link','Description','Checklists','Comments','Due','Members']
os.chdir(r'C:\Users\cnets\Desktop\SodisTools_development')


#get authentication
with open (r"keys\trello_API_key.txt", "r") as file:
    api_key=file.readlines()
with open (r"keys\trello_API_secret.txt", "r") as file:
    api_secret=file.readlines()

#connect to Trello
timestamp=datetime.today().strftime('%Y%m%d')
client = TrelloClient(
    api_key=api_key,
    api_secret=api_secret
)
all_boards=client.list_boards()


def get_card_data(card):
    def _list2str(a_list):
        string=''
        for a_string in a_list:
            string+='-'+a_string+'\n'
        return string
    
    def _translate_member_ids():
        pass
    card_dict={'Board':str(card.board.name),
            'List':str(card.get_list().name),
            'Title':str(card.name),
            'Link':str(card.url),
            'Description':str(card.description),
            #'Checklists':str(_list2str(card.checklists)),
            #'Comments':str(_list2str(card.comments)),
            'Due':str(card.due),
            #'Members':str(_list2str(card.member_ids))
            }
    return card_dict


def export2excel():
    Path(fr'temp\{timestamp}').mkdir(parents=True, exist_ok=True)
    for board in all_boards:
        df_trello=pd.DataFrame(columns=COLUMNS)
        for i,card in enumerate(board.all_cards()):
            df_trello=df_trello.append(get_card_data(card),ignore_index=True)
        
        board_name=board.name
        for char in board_name: #remove forbidden characters from filename
            if char in " ?.!/;:":
                board_name.replace(char,'')        
        df_trello.to_excel(fr'temp\{timestamp}\{board_name}.xlsx')   

if __name__=='__main__':
    export2excel()
        
    
    
    
