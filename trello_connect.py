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
#COLUMNS=['Board','List','Title','Link','Description','Checklists','Comments','Due','Members']
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

#Wichtige FEHLER: # Function".GET_CARD" DOES NOT CONTAIN CUSTOM VALUES!!!!!!!!

# DEFINITION

def get_lists_from_ids(ids_list):
    list_object = []
    #get_name = "get_" + object_type
    for id_counter in range (0,len(ids_list),1):
        list_object.append(client.get_list(ids_list[id_counter]))
    return list_object
    
def get_boards_from_ids(ids_list):
    list_object = []
    #get_name = "get_" + object_type
    for id_counter in range (0,len(ids_list),1):
        list_object.append(client.get_board(ids_list[id_counter]))
    return list_object

def get_members_from_board_ids():
    member_dict = {}
    
    for org in client.list_organizations():
        org_mem = org.get_members()
        for i in range(0,len(org_mem),1):
            (firstWord, *_) = org_mem[i].full_name.split(maxsplit=1)
            member_dict[i] = {
                "First Name": firstWord,
                'Name':org_mem[i].full_name,
                "Username":org_mem[i].username,
                'ID':org_mem[i].id
                }    
    return member_dict


def get_custom_field_ids_from_board_ids (board_id):
 
    cFD_dict = {}
    cFD_list = []
                
    for tmp_board in client.list_boards():
        for b_id in board_id:
            if (b_id == tmp_board.id):
                tmp_def = tmp_board.get_custom_field_definitions()
                for i in range(0,len(tmp_def),1):
                    cFD_dict[i] = {'Board' : b_id,
                    'ID':tmp_def[i].id,
                    'Name':tmp_def[i].name,
                    }
                    cFD_list.append(tmp_def[i])
                
    return cFD_dict,cFD_list

def done_list_emoji (final_list_ob):
    for lst in  final_list_ob:
        if  "🎉" not in lst.name:
            lst.set_name(lst.name + " 🎉")

def id2member (id_list):
    members=[]
    for member_id in id_list:
        members.append(client.get_member(member_id))
    return members

def ids2username (id_list):
    username=[]
    for member_id in id_list:
        username.append(client.get_member(member_id).username)
    return username

def id2username (id_m):
    username = (client.get_member(id_m).username)
    return username


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
            for id_m in card.idMembers:
                dueComplete_members.append(id_m)
    dueComplete_members = Counter(dueComplete_members)
    dueComplete_members2 = dueComplete_members.most_common()
    return count1, dueComplete_members2

def cal_responsibilities (cards):
    responsibility = []
    most_responsibility = []
    
    for card in cards:
        for ids in card.idMembers:
            responsibility.append(ids)
    most_responsibility = Counter(responsibility)
    most_responsibility = most_responsibility.most_common()
    
    return most_responsibility,responsibility

def most_activities_sorted(responsibilites_list, helping_list):
    most_active = responsibilites_list + helping_list
    most_active = Counter(most_active)
    most_active =most_active.most_common()
    return most_active


def listToString(s):  
    
    # initialize an empty string 
    str1 = ""  
    s = sorted(s)
    # traverse in the string   
    for ele in s:  
        str1 += ele
        str1 += ", "
    str1 = str1[:-2]
    # return string   
    return str1  

def cal_helper(cards):
    helper = []
    most_helper = []
    
    for card in cards:
        r_tag = []
        tags = card.description
        k_y = "Username"
        r_tag = {tag.strip("@") for tag in tags.split() if tag.startswith("@")}
        for tag_user in r_tag:
                for member_id in member_dict.values():
                    if tag_user ==  member_id[k_y]:
                        helper.append(member_id["ID"])
                        break
    most_helper = Counter(helper)
    most_helper = most_helper.most_common()
    return most_helper,helper 

def update_star_cards (cards,most_actives,words_checklist,member_dict,board_id,cFD_list):

    star_des = []
    star_mem = []
    star_due = []
    star_hel = []
    star = []
    tmp_def= cFD_list[1]
    helper_master_list = []
    #for b_id in board_id:
     #   member_name_list = b_id.

    for card in cards:
        star_hel.append(False)
        helper_list = []

        if len(card.description) is not 0: 
            star_des.append(True)
            
            #FIND USERNAME IN DESCRIPTION - COUNT HELFER
            r_tag = []
            tags = card.description
            k_y = "Username"
            r_tag = {tag.strip("@") for tag in tags.split() if tag.startswith("@")}
            
            #ALSO FIND NAMED TEAM IN CHECKLISTS AND COMMENTS
            #
            
            for tag_user in r_tag:
                for member_id in member_dict.values():
                    
                    if tag_user ==  member_id[k_y]:
                            helper_list.append(member_id["First Name"])
                            star_hel.append(True)
                            helper_master_list.append(helper_list)

                            break
            if len(helper_list) is not 0:
                helper_list = listToString(helper_list)
                if len(card.custom_fields) is not 0:
                    tmp_cf = card.get_custom_field_by_name("👤Team").value
                    if helper_list != tmp_cf:
                        card.set_custom_field(helper_list,tmp_def)
                        star_hel = star_hel[:-1]
           #
           
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
            
    star_shit_list = []
    star_mem_list = []
    
    for i in range(0,len(star_des)-1,1):
        

            #clean card names with following line:
        star_counter = 0
        
        if star_des[i] == True:
            star_counter += 1
        if star_mem[i] == True:
            star_counter += 1
        if star_due[i] == True:
            star_counter += 1

        star.append(star_counter)

        #Star Reward        
        if star_counter == 3:
            string_name = (cards[i].name.strip(" ⭐️") + " ⭐️")
            if not cards[i].name == string_name:
                cards[i].set_name(string_name)
                
            star_mem_here = cards[i].member_ids
            for member_id in member_dict.values():
                if member_id["ID"] in  star_mem_here:
                    star_mem_list.append(member_id["ID"])
                    break
            
        #Shitty-Card-Warning
        if star_counter <= 1:
            string_name = (cards[i].name.strip(" 💩") + " 💩")
            if not cards[i].name == string_name:
                cards[i].set_name(string_name)
                
            star_shit_here = cards[i].member_ids
            for member_id in member_dict.values():
                if member_id["ID"] in  star_shit_here:
                    star_shit_list.append(member_id["ID"])
                    break
    star_shit_list = Counter(star_shit_list) 
    star_shit_list = star_shit_list.most_common()
    
    star_mem_list = Counter(star_mem_list) 
    star_mem_list = star_mem_list.most_common()   
    #helper_master_list = Counter(str(helper_master_list))
    counted_cards=0
    most_star_member=star_mem_list
    most_shit_member=star_shit_list
    return counted_cards, most_star_member,most_shit_member

def analyze_card_movement (cards):
    move_stats = []
    move_forw_t = 0
    move_backw_t = 0
    not_moved_t = 0
    
    for card in cards:
        move_forw = 0
        move_backw = 0
        not_moved = False
        moves = card.list_movements()
        
        for move in moves:
            if move["source"]["id"] in list_id_order:
                pos_source = list_id_order.index(move["source"]["id"])
            else:
                pos_source =-1
            
            if move["destination"]["id"] in list_id_order:
                pos_destination = list_id_order.index(move["destination"]["id"])
            else:
                pos_source =-1
                
            if (pos_destination != -1) and (pos_source!= -1):
                if pos_destination > pos_source:
                    move_forw +=1
                else:
                    move_backw +=1
        move_forw_t += move_forw
        move_backw_t += move_backw
        if (move_forw == 0) and (move_backw == 0):
            not_moved = True
            not_moved_t += 1
            
        move_dict = {
        "forward" : move_forw,
        "backwards" : move_backw,
        "not moved" : not_moved
        }
        move_stats.append(move_dict)
    return move_forw_t, move_backw_t, not_moved_t, move_stats

#Spielerei, kann weg. Ohne das auslesen der Custom Fields (weiß nicht, warum es geht. Denke es liegt an Trello) geht nicht mehr
"""
def update_custom_field_date (board_id,name_team,name_allday,name_start):
    boards = client.list_boards()
    for board in boards:
        if board.id in board_id:
            cards = board.all_cards()
            for card in cards:
                cfd_team = card.get_custom_field_by_name(name_team)
                cfd_allday = card.get_custom_field_by_name(name_allday)
                cfd_start = card.get_custom_field_by_name(name_start)
                cfd_value = cfd_allday.value
                #:
                #   card.set_due(due1.replace(hour = 21,minute=59))
##############FIx TIMEZONES, HERE ITS HARDCODED "21"
            
    a=1
    return a                 
"""

#BERECHNUNG DER PARAMETER

    #[Sektion Init.]
boards_ob = get_boards_from_ids(board_id)
alist_ob = get_lists_from_ids(alist_id)
flist_ob = get_lists_from_ids(flist_id)
sflist_ob = get_lists_from_ids(sflist_id)
list_ob_order = get_lists_from_ids(list_id_order)

member_dict = get_members_from_board_ids()

done_list_emoji(flist_ob)  

    #[Sektion Active]
r_a_cards, r_sf_cards, r_f_cards, r_cards, tmp_cards = cal_active_cards (alist_id,sflist_id,flist_id,time_now,report_time)


cfd_dict, cFD_list = get_custom_field_ids_from_board_ids (board_id)

#a =  update_custom_field_date (board_id,"👤Team","📆 Ganztägig","⏱Start")


r_count_dueComplete, r_most_duecomplete = cal_count_dueComplete (tmp_cards)

r_max_inactive_time, r_max_inactive_time_name, tmp_inactive_time = cal_inactive_cards (tmp_cards,time_now)

r_most_helpers, input_help_act = cal_helper(tmp_cards)

r_most_responsability, input_resp_act = cal_responsibilities (tmp_cards)

r_most_actives = most_activities_sorted(input_resp_act,input_help_act)

r_most_done, b = cal_responsibilities (tmp_cards[(r_a_cards+r_sf_cards):])
del b
##
r_counted_cards,  r_most_star_member,r_most_shit_member = update_star_cards (tmp_cards,r_most_responsability,words_checklist,member_dict,board_id,cFD_list)
##
r_move_forw, r_move_backw, r_not_moved, r_move_stats = analyze_card_movement (tmp_cards)
                           
#OUTPUT AUSGABE #für Variablenbeschreibung siehe output.txt
print("Results of Trello Report:")
print("You have ",r_cards, "cards in your evaluated lists, seperated in", r_a_cards, "active (doing) cards (",round(r_a_cards/r_cards*100,2),"%)",r_sf_cards, "semi final (review) cards (",round(r_sf_cards/r_cards*100,2),"%) and ", r_f_cards,"final (done) cards (",round(r_f_cards/r_cards*100,2),"%) \n")
print("Of all",r_f_cards, "final cards you have complete",r_count_dueComplete, "cards within the due date. That is", round(r_count_dueComplete/r_f_cards*100,2),"% \n")
print("Of the cards",round((r_cards-r_not_moved)/r_cards*100,2),"% have moved. Of the",(r_move_forw+r_move_backw),"moves,",r_move_forw,"were forward moves and",r_move_backw,"backwards moves \n")
print("Cards without Activity: \n","1.",r_max_inactive_time_name[0],"- inactive since ", r_max_inactive_time[0].days," days \n","2.",r_max_inactive_time_name[1],"- inactive since ", r_max_inactive_time[1].days,"days \n","3.", r_max_inactive_time_name[2],"- inactive since ", r_max_inactive_time[2].days,"days \n")
print("Most active Members: \n","1.",client.get_member(r_most_actives[0][0]).full_name,"active on",r_most_actives[0][1],"cards"" \n","2.",client.get_member(r_most_actives[1][0]).full_name,"active on",r_most_actives[1][1],"cards\n","3.",client.get_member(r_most_actives[2][0]).full_name,"active on",r_most_actives[2][1],"cards \n")
print(" - Most responsible Members: \n","1.",client.get_member(r_most_responsability[0][0]).full_name,"takes responsibility for",r_most_responsability[0][1],"cards"" \n","2.",client.get_member(r_most_responsability[1][0]).full_name,"takes responsibility for",r_most_responsability[1][1],"cards\n","3.",client.get_member(r_most_responsability[2][0]).full_name,"takes responsibility for",r_most_responsability[2][1],"cards \n")
print(" - Most helping Members: \n","1.",client.get_member(r_most_helpers[0][0]).full_name,"helping on",r_most_helpers[0][1],"cards \n","2.",client.get_member(r_most_helpers[1][0]).full_name,"helping on",r_most_helpers[1][1],"cards\n","3.",client.get_member(r_most_helpers[2][0]).full_name,"helping on",r_most_helpers[2][1],"cards \n")
print("Members with most due completes: \n","1.",client.get_member(r_most_duecomplete[0][0]).full_name,"with",r_most_duecomplete[0][1],"cards done within the due date \n","2.",client.get_member(r_most_duecomplete[1][0]).full_name,"with",r_most_duecomplete[1][1],"cards done within the due date \n","3.",client.get_member(r_most_duecomplete[2][0]).full_name,"with",r_most_duecomplete[2][1],"cards done within the due date \n")
print("Members with most final(done) cards: \n","1.",client.get_member(r_most_done[0][0]).full_name,"takes responsibility for finalizing cards \n","2.",client.get_member(r_most_done[1][0]).full_name,"responsibility for finalizing cards\n","3.",client.get_member(r_most_done[2][0]).full_name,"responsibility for finalizing cards \n")

#########################CODE CHRISTOPH
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
################################

#client.get_member(r_most_done[0][0]).full_name


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
    
