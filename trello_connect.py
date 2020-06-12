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
from datetime import datetime
from collections import Counter, OrderedDict

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
sflist_id = configParser.get("Section IDs","Semi-Final List-IDs").split(",")
flist_id = configParser.get("Section IDs","Final List-IDs").split(",")
list_id_order = configParser.get("Section IDs","List-ID Forward Order").split(",")
report_repeat = configParser.get("Parameters","repeat")
report_time = configParser.get("Parameters","report_time")

#INITIALISIERUNG
time_now = datetime.now().astimezone()
words_checklist = ["agenda","todo"]

#FUNKTIONEN
def get_cards_from_list_id (list_ids,time_now,report_time):
    tmp_cards=[]

    for tmp_board in client.list_boards():
        if tmp_board.id in board_id:            
           for tmp_list in tmp_board.all_lists(): 
                if tmp_list.id in list_ids:
                    tmp_cards+=tmp_list.list_cards()
    #exclude final cards older than report time frame
    for card in tmp_cards:
        if card.idList in flist_id:
            time2 = card.latestCardMove_date
            if time2 == None:
                time2 = time_now
            delta = time_now - time2
            if int(delta.days) > int(report_time):
                    tmp_cards.remove(card)
    return tmp_cards

"""
    #GET 3 MAX VALUES OF SOMETHING
def get_maxXscore (fillname,a,X):
    b=a
    maxX_values = []
    maxX_pos = []
    
    for i in range(1,X+1,1):
        val = max(b)
        pos = a.index(val)
        
        maxX_values.append(val)
        maxX_pos.append(fillname)
        b -= b
    return maxX_values, maxX_pos
"""

def cal_inactive_cards (cards,time_now):
    tmp_inactive_time = []
    tmp_inactive_time_name = []
    max_inactive_time = []
    max_inactive_time_name = []
    
    for card in cards:
        time2 = card.date_last_activity
        inactive_time = time_now-time2
        tmp_inactive_time.append(inactive_time)
        tmp_inactive_time_name.append(card.id) 
        
    tmp_inactive_time2 = tmp_inactive_time
    
    for i in range(1,4,1): 
        val = max(tmp_inactive_time2)
        pos = tmp_inactive_time.index(val)
        
        max_inactive_time.append(val)
        max_inactive_time_name.append(cards[pos].name)
        tmp_inactive_time2[pos] -= tmp_inactive_time2[pos]
    return max_inactive_time, max_inactive_time_name, tmp_inactive_time

    #Count and get cards
def cal_active_cards (alist_id,sflist_id,flist_id,time_now,report_time):
    tmp_cards = get_cards_from_list_id (alist_id,time_now,report_time)
    r_a_cards = len(tmp_cards)
    tmp_cards += get_cards_from_list_id (sflist_id,time_now,report_time)
    r_sf_cards = len(tmp_cards) - r_a_cards
    tmp_cards += get_cards_from_list_id (flist_id,time_now,report_time)
    r_f_cards = len(tmp_cards) - r_sf_cards - r_a_cards
    r_cards = len(tmp_cards)
    return r_a_cards, r_sf_cards, r_f_cards, r_cards, tmp_cards

    #Count cards completed within dueDate
def cal_count_dueComplete (cards):
    dueComplete_members = []
    count1 = 0
    for card in cards:
        if card._json_obj.get("dueComplete"):
            count1 += 1
            for id in card.idMembers:
                dueComplete_members.append(id)
    dueComplete_members = Counter(dueComplete_members)
    dueComplete_members2 = dueComplete_members.most_common()
    return count1, dueComplete_members2

def cal_responsibilities (cards):
    actives = []
    most_actives = []
    most_helping = []
    
    for card in cards:
        for ids in card.idMembers:
            actives.append(ids)
    actives = Counter(actives)
    most_actives = actives.most_common()
    
    
    return most_actives, most_helping

def update_star_cards (cards,most_actives,words_checklist):
    star_des = []
    star_mem = []
    star_due = []
    star = []
    helper_list = []
    #for b_id in board_id:
     #   member_name_list = b_id.

    for card in cards:

        if len(card.description) is not 0: 
            star_des.append(True)
            #FIND USERNAME IN DESCRIPTION - COUNT HELFER noch ausstehend
            #for member in most_actives:
             #   helper_m = card.description.find(str(member))
              #  if helper_m is -1:
               #     helper_list.append(,card)
        else: 
            star_des.append(False)

        if len(card.member_ids) is not 0: 
            star_mem.append(True)
        else: 
            star_mem.append(False) 

        if len(str(card.due)) is not 0: 
            star_due.append(True)
        else: 
            star_due.append(False)
        
        for word in words_checklist:
            if card.checklist.find(word) is not -1:
                print ("gefunden")
            else:
                print("nicht gedunfen")
            
    for i in range(0,len(star_des)-1,1):

            #clean card names with following line:
        cards[i].set_name((cards[i].name.replace(" ⭐️","")))

        star.append(star_des[i]*star_mem[i]*star_due[i])
        if star[i] == True:
            if not cards[i].name.endswith(" ⭐️"):
                cards[i].set_name((cards[i].name + " ⭐️"))
            #cards[i].set_custom_field()

    counted_cards=0
    most_star_member=0
    return counted_cards, most_star_member, helper_list

#BERECHNUNG DER PARAMETER
    #[Sektion Active]
r_a_cards, r_sf_cards, r_f_cards, r_cards, tmp_cards = cal_active_cards (alist_id,sflist_id,flist_id,time_now,report_time)

r_count_dueComplete, r_most_duecomplete = cal_count_dueComplete (tmp_cards)

r_max_inactive_time, r_max_inactive_time_name, tmp_inactive_time = cal_inactive_cards (tmp_cards,time_now)

r_most_actives, r_most_helping = cal_responsibilities (tmp_cards)

r_most_done, b1 = cal_responsibilities (tmp_cards[(r_a_cards+r_sf_cards):])
del b1

r_counted_cards, r_most_star_member, helper_list = update_star_cards (tmp_cards,r_most_actives,words_checklist)

#OUTPUT AUSGABE #für Variablenbeschreibung siehe output.txt
print("You have ",r_cards, " cards in your evaluated lists, seperated in ", r_a_cards, " active (doing) cards, ",r_sf_cards, " semi final (review) cards and ", r_f_cards," final (done) cards \n")
print("Of all ",r_f_cards, " cards you have complete ",r_count_dueComplete, " cards within the due date. \n")
print("Cards without Activity: \n","1.",r_max_inactive_time_name[0],"- inactive since ", r_max_inactive_time[0].days," days \n","2.",r_max_inactive_time_name[1],"- inactive since ", r_max_inactive_time[1].days," days \n","3.", r_max_inactive_time_name[2],"- inactive since ", r_max_inactive_time[2].days," days \n")
print("Most active Members: \n","1.",r_most_actives[0],"responsibility for cards \n","2.",r_most_actives[1],"responsibility for cards\n","3.",r_most_actives[2],"responsibility for cards \n")
print("Members with most due completes: \n","1.",r_most_duecomplete[0],"cards \n","2.",r_most_duecomplete[1],"cards \n","3.",r_most_duecomplete[2],"cards \n")
print("Members with most final(done) cards: \n","1.",r_most_done[0],"responsibility for final cards \n","2.",r_most_done[1],"responsibility for final cards\n","3.",r_most_done[2],"responsibility for final cards \n")
    
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
    
