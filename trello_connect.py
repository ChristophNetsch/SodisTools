# -*- coding: utf-8 -*-

from trello import TrelloClient
from styleframe import StyleFrame
import os
from pathlib import Path
import pandas as pd
from datetime import datetime
import shutil
import slack
from slack.errors import SlackApiError
import numpy as np
import configparser as ConfigParser
from datetime import datetime
from collections import Counter, OrderedDict


#ROOT=r'C:\Users\cnets\Desktop\SodisTools_development'
#COLUMNS=['Board','List','Title','Link','Description','Checklists','Comments','Due','Members']
#os.chdir(r'C:\Users\cnets\Desktop\SodisTools_development')

#Trello authentication keys
def connect_to_trello(KeyFilePath):
    keyParser = ConfigParser.RawConfigParser()   
    keyParser.read(KeyFilePath)
    
    api_key=keyParser.get("Trello Access","API Key").replace(" ", "")
    api_secret=keyParser.get("Trello Access","API Secret").replace(" ", "")
    
    client_trello = TrelloClient(
        api_key=api_key,
        api_secret=api_secret
    )
    return client_trello

#connect to Slack
def connect_to_slack(KeyFilePath):
    keyParser = ConfigParser.RawConfigParser()   
    keyParser.read(KeyFilePath)
    
    app_id = keyParser.get("App Credentials","App ID").replace(" ", "")
    client_id = keyParser.get("App Credentials","Client ID").replace(" ", "")
    client_server = keyParser.get("App Credentials","Client Secret").replace(" ", "")
    signing_secret = keyParser.get("App Credentials","Signing Secret").replace(" ", "")
    verification_token = keyParser.get("App Credentials","Verification Token").replace(" ", "")

    client_slack = slack.WebClient(token=verification_token)
    
    client_slack.chat_postMessage(
        channel="bot-test",
        text="Hello World! :tada:"
    )
    try:
        response = client_slack.chat_postMessage(
            channel="bot-test",
            text="Hello World2! :tada:"
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
  
    return client_slack

"""
#TRELLO ID OVERVIEW
#create txt
txt = "Trello IDs \n"
for board in client.list_boards():
    txt += "\n" + board.name + " : " + board.id +"\n"
    for lst in board.all_lists():
        txt += lst.name + " : " + lst.id +"\n"
t_file =  open(r"documentation/trello_IDs.txt", "w+")
t_file.write(txt)
t_file.close()
"""


"""
REPORT TOOL
"""
client = connect_to_trello(r"keys/trello_access.txt")
#client_slack = connect_to_slack(r"keys/slack_access.txt")
config_name = os.listdir(r"config_folder/")
configFilePath = []
for i in range(1,len(config_name),1):
    configFilePath.append(r"config_folder/" + config_name[i])

def create_report (configFilePath):
    #AUSLESEN DER KONFIGDATEI
    configParser = ConfigParser.RawConfigParser()   
    configParser.read(configFilePath)
    board_id = configParser.get("Section IDs","Boards-IDs").split(",")
    alist_id = configParser.get("Section IDs","Active List-IDs").split(",")
    sflist_id = configParser.get("Section IDs","Semi-Final List-IDs").split(",")
    flist_id = configParser.get("Section IDs","Final List-IDs").split(",")
    list_id_order = configParser.get("Section IDs","List-ID Forward Order").split(",")
    report_repeat = configParser.get("Parameters","repeat")
    report_time = configParser.get("Parameters","report_time")
    ranking_length = int(configParser.get("Parameters","ranking_length"))
    report_name = configParser.get("Parameters","report_name")
        #exclude spaces " "
    
    def exclude_space_in_list_entries(lst):
        for i in range(0,len(lst),1):
            lst[i] = lst[i].replace(" ", "")
        return lst
    exclude_space_in_list_entries(board_id)
    exclude_space_in_list_entries(alist_id)
    exclude_space_in_list_entries(sflist_id)
    exclude_space_in_list_entries(flist_id)
    exclude_space_in_list_entries(list_id_order)

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
                member_dict[org_mem[i].id] = {
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
            username.append(member_dict[member_id]["Username"])
        return username
    
    def id2username (id_m):
        username = (member_dict[id_m]["Name"])
        return username
    
    
    def get_cards_from_list_id (list_ids,time_now,report_time):
        tmp_cards=[]
    
        for tmp_board in client.list_boards():
            if tmp_board.id in board_id:            
               for tmp_list in tmp_board.all_lists(): 
                    if tmp_list.id in list_ids:
                        tmp_cards+=tmp_list.list_cards()
        #exclude final cards older than report time frame
        for card in reversed(tmp_cards):
            if card.idList in flist_id:
                time2 = card.latestCardMove_date
                if time2 == None:
                    time2 = card.date_last_activity
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
        
        for i in range(1,ranking_length+1,1): 
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
    
    def cal_created_cards(cards,time_now):
        created_card_counter = 0
        time_now = time_now.replace(tzinfo=None)
        for card in cards:
            time2 = card.card_created_date
            if time2 is not "":
                time2 = time2.replace(tzinfo=None)
                delta = time_now - time2
                if int(abs(delta.days)) < int(report_time):            
                    created_card_counter += 1
        return created_card_counter
    

    
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
        for cfd in cFD_list:
            if cfd.name == "👤Team":
                tmp_def = cfd
                break
        helper_master_list = []
        shit_counter = 0
        star_card_counter = 0
        cards_wo_member = 0
        
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
                    #if len(card.custom_fields) is not 0:
                    tmp_cf = card.get_custom_field_by_name("👤Team").value
                    if helper_list != tmp_cf:
                        card.set_custom_field(helper_list,tmp_def)
                        star_hel = star_hel[:-1]           
               
            else: 
                star_des.append(False)
    
            if len(card.member_ids) is not 0: 
                star_mem.append(True)
            else: 
                star_mem.append(False) 
                cards_wo_member += 1
            #if due_cate = NONE len(due)=4
            if len(str(card.due)) is not 4: 
                star_due.append(True)
            else: 
                star_due.append(False)
                
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
                star_card_counter += 1
                string_name = (cards[i].name.replace(" ⭐️","")+ " ⭐️")
                string_name = string_name.replace(" 💩","")
                    
                star_mem_here = cards[i].member_ids
                i_mem = len(star_mem_here)
                l = 0
                for member_id in member_dict.values():
                    if member_id["ID"] in  star_mem_here:
                        star_mem_list.append(member_id["ID"])

                        l += 1
                        if l == i_mem:
                            break
                    
            #Shitty-Card-Warning
            if star_counter <= 1:
                shit_counter += 1
                string_name = (cards[i].name.replace(" 💩","") + " 💩")
                string_name = string_name.replace(" ⭐️","")

            if star_counter == 2:
                string_name = (cards[i].name.replace(" 💩",""))
                string_name = string_name.replace(" ⭐️","")
                
            if not cards[i].name == string_name:
                cards[i].set_name(string_name)
            string_name = ""

                        
        star_mem_list = Counter(star_mem_list) 
        star_mem_list = star_mem_list.most_common()   
        #helper_master_list = Counter(str(helper_master_list))
        counted_cards=0
        most_star_member=star_mem_list
            
        return counted_cards, most_star_member, star_card_counter, shit_counter, cards_wo_member
    
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
    
    r_created_card_counter = cal_created_cards(tmp_cards,time_now)
    
    r_most_helpers, input_help_act = cal_helper(tmp_cards)
    
    r_most_responsability, input_resp_act = cal_responsibilities (tmp_cards)
    
    r_most_actives = most_activities_sorted(input_resp_act,input_help_act)
    
    r_most_done, b = cal_responsibilities (tmp_cards[(r_a_cards+r_sf_cards):])
    del b
    ##
    r_counted_cards,  r_most_star_member, r_star_cards, r_shit_counter,r_cards_wo_member = update_star_cards (tmp_cards,r_most_responsability,words_checklist,member_dict,board_id,cFD_list)
    ##
    r_move_forw, r_move_backw, r_not_moved, r_move_stats = analyze_card_movement (tmp_cards)
    
    #PRINT OUTPUT DEFINITION
    def print_report_infos():
        print("Results of Trello Report:",report_name," \n")
        print("[PARAMETER]")
        print ("Report time: last",report_time,"days.")
        print ("Ranking length:",ranking_length,"entries.")
        
        names = ""
        for lst in alist_ob:
            names += lst.name + "\n"
        print ("Active lists: \n",names)
        
        names = ""
        for lst in sflist_ob:
            names += lst.name + "\n"
        print ("Semifinal lists: \n",names)
        
        names = ""
        for lst in flist_ob:
            names += lst.name + "\n"
        print ("Final lists: \n",names)   
        
        names = ""
        for lst in list_ob_order:
            names += lst.name + "\n"
        print("List forward flow: \n",names)
        print("Will repeat report in future:",report_repeat)
        
    def print_active_results(n_cards,a,sf,f):
        p = "-"
        if f != 0:
            p=round(a/n_cards*100,1)
        print("You have",n_cards, "cards in your evaluated lists, seperated in", a, "active (doing) cards (",p,"%)",sf, "semi final (review) cards (",round(sf/n_cards*100,1),"%) and ", f,"final (done) cards (",round(f/n_cards*100,1),"%). \n")
    
    def print_created_cards_count(r_created_card_counter, report_time):
        print("You have created",r_created_card_counter, "cards in the last", report_time, "days. \n")
    
    def print_dueComplete(f,dC):
        p="-"
        if f != 0:
            p=round(dC/f*100,2)
        print("Of all",f, "final cards you have complete",dC, "cards within the due date. That is", p,"% \n")
    
    def print_star_shit_cards(n_cards,star_count,shit_count,r_cards_wo_member):
        print("Of the" ,n_cards, "cards in your evaluated lists, you have", star_count, "star cards(with a description, member and due date (",round(star_count/n_cards*100,1),"%)", "and",shit_count,"(shit cards (with one or less of the quality marks)",round(shit_count/n_cards*100,1),"%) \n")
        print("You have",r_cards_wo_member,"cards without responsible member. \n")
        
    def print_card_movement(n,nM,fo,ba):
        p1="-"
        p2="-"
        if ba+fo !=0:
            p1 = round(fo/(fo+ba)*100,1)
            p2 = round(ba/(fo+ba)*100,1)
        print("Of the cards",round((n-nM)/n*100,2),"% have moved. Of the",(fo+ba),"moves,",fo,"(",p1,"%) were forward moves and",ba,"(",p2,"%)backwards moves. \n")
    
    def print_ranking(names_and_values,t_start, t_middle, stopper, percent = "", t_end = ""):
        i=0
        if names_and_values is not []:
            for nav in names_and_values:
            
                i += 1                
                print(str(i),".",member_dict[nav[0]]["Name"],t_start,nav[1],t_middle,percent,t_end)
                if i == stopper:
                    break
            print("\n")    
        
    def print_most_activities(most_actives, stopper):
        text0 = "Most active Members:"
        text1 = "active on"
        text2 = "cards"
        print (text0)
        print_ranking(most_actives, text1, text2, stopper)     
    
    def print_most_responsibles(most_responsibles, stopper):
        text0 = " - Most responsible Members:"
        text1 = "takes responsibility for"
        text2 = "cards"
        print (text0)
        print_ranking(most_responsibles, text1, text2, stopper)     
    
    def print_most_helping(most_helping, stopper):
        text0 = " - Most helping Members:"
        text1 = "helping on"
        text2 = "cards"
        print (text0)
        print_ranking(most_helping, text1, text2, stopper)    
    
    def print_most_duecomplete(most_duecomplete, stopper):
        text0 = "Members with most due completes:"
        text1 = "with"
        text2 = "cards"
        print (text0)
        print_ranking(most_duecomplete, text1, text2, stopper)
        
    def print_most_done(most_done, stopper):
        text0 = "Members with most final(done) cards:"
        text1 = "takes responsibility for finalizing"
        text2 = "cards"
        print (text0)
        print_ranking(most_done, text1, text2, stopper)
    
    def print_most_stars(most_stars, stopper):
        text0 = "Members with most star cards:"
        text1 = "on"
        text2 = "star cards"
        print (text0)
        print_ranking(most_stars, text1, text2, stopper)
        
    def print_no_activity_cards(max_inactive_time_name, r_max_inactive_time, stopper):
        text0 = "Cards without Activity:"
        text1 = "- inactive since"
        text2 = "days"
        print (text0)
        i=0
        for nav in max_inactive_time_name:
            
            i += 1
            print(str(i),".",nav,text1,r_max_inactive_time[i-1].days,text2)
            if i == stopper:
                break
        print("\n") 
        
        
    #OUTPUT AUSGABE #für Variablenbeschreibung siehe output.txt
    
    print_report_infos()
    
    print("[ACTIVE]")
    print_active_results(r_cards,r_a_cards,r_sf_cards,r_f_cards)
    print_created_cards_count(r_created_card_counter, report_time)
    print_no_activity_cards(r_max_inactive_time_name,r_max_inactive_time,ranking_length)
    print_card_movement(r_cards,r_not_moved,r_move_forw,r_move_backw)
    print_most_activities(r_most_actives, ranking_length)
    
    
    
    print("[RELIABLE]")
    print_most_responsibles(r_most_responsability,ranking_length)
    print_most_done(r_most_done,ranking_length)
    
    
    print("[PUNCTUAL]")
    print_dueComplete(r_f_cards,r_count_dueComplete)
    print_most_duecomplete(r_most_duecomplete,ranking_length)
    
    
    print("[DETAILED]")
    print_star_shit_cards(r_cards,r_star_cards, r_shit_counter,r_cards_wo_member)
    print_most_stars(r_most_star_member, ranking_length)
    
    print("[COLLABORATIVE]")
    print_most_helping(r_most_helpers,ranking_length)

#RUN REPORT
allreports = True
if allreports:    
    for path in configFilePath:
        create_report (path)
else:
        configFilePath = r"config_folder/config_0_gruppentreffen.txt"
        create_report(configFilePath)

#########################CODE CHRISTOPH
"""def get_card_data(card):
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
    
