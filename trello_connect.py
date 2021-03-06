# -*- coding: utf-8 -*-

from trello import TrelloClient
#from styleframe import StyleFrame
import os
#from pathlib import Path
#import pandas as pd
from datetime import datetime
#import shutil
import slack
from slack.errors import SlackApiError
#import numpy as np
import configparser as ConfigParser
from collections import Counter
import openpyxl

#from pydrive.auth import GoogleAuth
#from pydrive.drive import GoogleDrive

def connect_to_gdrive (KeyFilePath):
    #gauth = GoogleAuth()
    #gauth.LocalWebserverAuth()

    #drive = GoogleDrive(gauth)
    #return drive
    a=1
    
#Trello authentication keys
def connect_to_trello(KeyFilePath):
    #not in use
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
    oauth_access_token = keyParser.get("App Credentials","Bot User OAuth Access Token").replace(" ", "")

    client_slack = slack.WebClient(token=oauth_access_token)
    
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


#TRELLO ID OVERVIEW
def create_trello_id_overview(): 
    #create txt
    txt = "Trello IDs \n"
    for board in client.list_boards():
        txt += "\n" + board.name + " : " + board.id +"\n"
        for lst in board.all_lists():
            txt += lst.name + " : " + lst.id +"\n"
    t_file =  open(r"documentation/trello_IDs.txt", "w+")
    t_file.write(txt)
    t_file.close()

def connect_to_trello_env(enviroment_list):
    try:
        api_key = os.environ['API_KEY']
        api_secret = os.environ['API_SECRET']
        
        client_trello = TrelloClient(
            api_key=api_key,
            api_secret=api_secret
        )
        
    except:
        print('ERROR: Report aborted. Please provide Trello and Slack credentials in env.list-file.')
    return client_trello


"""
REPORT TOOL
"""

if __name__=='__main__':
    #drive = connect_to_gdrive (r"keys/google_drive_access.json")
    client = connect_to_trello(r"keys/trello_access.txt")
    #client = connect_to_trello_env(r"keys/env.list")
    #client_slack = connect_to_slack(r"keys/slack_access.txt")

    create_trello_id_overview()
    
    config_name = os.listdir(r"config_folder/")
    configFilePath = []
    
    for i in range(0,len(config_name),1):
        name = (r"config_folder/" + config_name[i])
        name2 = "config_folder/.DS_Store"
        if name != name2:
            configFilePath.append(r"config_folder/" + config_name[i])
        else:
            ii = i 
    if ii:
        del(config_name[ii])
    
    def update_cards (config_name,configFilePath):
        aaa=1
        
    def create_report (config_name,configFilePath):
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
            if tmp_inactive_time2 != []:
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
        
        def update_star_cards (cards,most_actives,member_dict,board_id,cFD_list):
        
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
                        pos_destination = -1
                        
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
        #boards_ob = get_boards_from_ids(board_id)
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
        r_counted_cards,  r_most_star_member, r_star_cards, r_shit_counter,r_cards_wo_member = update_star_cards (tmp_cards,r_most_responsability,member_dict,board_id,cFD_list)
        ##
        r_move_forw, r_move_backw, r_not_moved, r_move_stats = analyze_card_movement (tmp_cards)
        
        #PRINT OUTPUT DEFINITION
        def print_excel(path):
            book = openpyxl.load_workbook('trello_report_vorlage.xlsx')
            sheet = book.active
            def print_ranking_excel(names_and_values, stopper, start_cell_column,start_cell_row):
                i=0
                alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                
                if names_and_values is not []:
                    for nav in names_and_values:
                        cell_number = str(start_cell_row+i)
                        next_cell_column = alphabet[alphabet.find(start_cell_column)+1]
                        
                        sheet[start_cell_column + cell_number].value = member_dict[nav[0]]["Name"]
                        sheet[next_cell_column + cell_number].value = nav[1]
                        i += 1
                        if i == stopper:
                            break
            def print_ranking_excel_single_line(names_and_values, stopper, start_cell_column,start_cell_row):
                i=0            
                if names_and_values is not []:
                    for nav in names_and_values:
                        cell_number = str(start_cell_row+i)
                        sheet[start_cell_column + cell_number].value = nav
                        i += 1
                        if i == stopper:
                            break      
            def print_ranking_excel_single_line_with_zero(names_and_values, stopper, start_cell_column,start_cell_row):
                i=0            
                if names_and_values is not []:
                    for nav in names_and_values:
                        cell_number = str(start_cell_row+i)
                        sheet[start_cell_column + cell_number].value = nav
                        i += 1
                        if i == stopper:
                            break
                    if i <= 5:
                        for j in range(i,5,1):
                           cell_number = str(start_cell_row+j)
                           sheet[start_cell_column + cell_number].value = 0
                           j += 1 
            def print_ranking_excel_names_and_values_single_lines(names_and_values, stopper, start_cell_column,start_cell_row):
                i=0            
                if names_and_values is not []:
                    for nav in names_and_values:
                        cell_number = str(start_cell_row+i)
                        sheet[start_cell_column + cell_number].value = member_dict[nav[0]]["Name"]
                        number = i+5
                        cell_number = str(start_cell_row + number)
                        sheet[start_cell_column + cell_number].value = nav[1]
                        i += 1
                        if i == stopper:
                            break
                    if i <= 5:
                        for j in range(i,5,1):
                           cell_number = str(start_cell_row+j)
                           sheet[start_cell_column + cell_number].value = 0
                           cell_number = str(start_cell_row+(j+5))
                           sheet[start_cell_column + cell_number].value = 0
                    
            sheet['B2'] = report_name
            sheet['B7'] = str(report_time) + " Tage"
            sheet["F7"] = str(ranking_length) + " Einträge"
            
            
            alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            names = ""
            ij = 0
            start_cell_row = 9
            start_cell_column = "A"
            for lst in alist_ob:
                next_number = str(start_cell_row+ij)
                cell_name = start_cell_column+str(next_number)
                sheet[cell_name] = lst.name
                ij+=1
            
            names = ""
            ij = 0
            start_cell_row = 9
            start_cell_column = "C"
            for lst in sflist_ob:
                next_number = str(start_cell_row+ij)
                cell_name = start_cell_column+str(next_number)
                sheet[cell_name] = lst.name
                ij+=1
            
            names = ""
            ij = 0
            start_cell_row = 9
            start_cell_column = "E"
            for lst in flist_ob:
                next_number = str(start_cell_row+ij)
                cell_name = start_cell_column+str(next_number)
                sheet[cell_name] = lst.name
                ij+=1  
            
            names = ""
            for lst in list_ob_order:
                names += lst.name + "\n"
            print("List forward flow: \n",names)
            print("Will repeat report in future:",report_repeat)
            
            sheet['C17'] = r_cards
            sheet['C18'] = str(r_created_card_counter)
            
            sheet['G17'] = r_a_cards
            sheet['G18'] = r_sf_cards
            sheet['G19'] = r_f_cards
            
            sheet['D19'] = str(r_move_backw + r_move_forw)
            if r_cards != 0:
                sheet['D20'] = str(round((r_not_moved/r_cards*100),1)) + "% der Karten"
            
            sheet['A21'] = r_move_backw
            sheet['B21'] = r_move_forw
            print_ranking_excel_single_line(r_max_inactive_time_name, 5, "B",27)
            days=[]
            for entry in r_max_inactive_time:
                days.append(entry.days)
            print_ranking_excel_single_line(days, 5, "C",27)
            
            print_ranking_excel(r_most_actives, 5, "B", 35)
            print_ranking_excel(r_most_responsability, 5, "E", 39)
            print_ranking_excel(r_most_helpers, 5, "E", 50)
            
            print_ranking_excel(r_most_done, 5, "B", 48)
            
            print_ranking_excel(r_most_duecomplete, 5, "A", 60)
            sheet['G60'] = r_f_cards
            sheet['G61'] = r_count_dueComplete
            
            print_ranking_excel(r_most_star_member, 5, "F", 70)
    
            sheet['B70'] = r_cards
            sheet['B71'] = r_star_cards
            sheet['B73'] = r_shit_counter
            
            sheet['F34'] = r_cards_wo_member
            if r_cards != 0:
                sheet['G34'] = "("+str(round(r_cards_wo_member/r_cards*100,1))+"%)"
            
            
            name = path.strip(".txt")
            name = name.replace("config", "report") + ".xlsx"
            book.save(name)
            print("Saved as excel file")
            
            
            
            
            
            
            #Create Record in Report-Overview
            wb = openpyxl.load_workbook('results_overview.xlsx')
            c=0
            for s in wb.worksheets:
                if s.title in config_name :
                    sheet = s
                    c=1
            if c == 0:
                sheet = wb.copy_worksheet(wb.worksheets[0])
                sheet.title = config_name[0:30]
    
            dim = sheet.dimensions
            sheet.move_range((dim), rows=0, cols=1)
    
            #Write Entries
            sheet['A1'] = report_name
            sheet['A2'] = report_time
            sheet["A3"] = ranking_length
            
            sheet['A4'] = r_cards
            sheet['A5'] = r_created_card_counter
            
            sheet['A6'] = r_a_cards
            sheet['A7'] = r_sf_cards
            sheet['A8'] = r_f_cards        
            
            sheet['A9'] = r_move_backw + r_move_forw
            
            if r_cards != 0:
                sheet['A10'] = round((r_not_moved/r_cards*100),1)
            else:
                sheet['A10'] = 0
                
            sheet['A11'] = r_move_backw
            sheet['A12'] = r_move_forw
            print_ranking_excel_single_line_with_zero(r_max_inactive_time_name, 5, "A",13)
            days=[]
            
            for entry in r_max_inactive_time:
                days.append(entry.days)
            print_ranking_excel_single_line_with_zero(days, 5, "A",18)
            
            print_ranking_excel_names_and_values_single_lines(r_most_actives, 5, "A", 23)
            print_ranking_excel_names_and_values_single_lines(r_most_responsability, 5, "A", 33)
            print_ranking_excel_names_and_values_single_lines(r_most_helpers, 5, "A", 43)
            
            print_ranking_excel_names_and_values_single_lines(r_most_done, 5, "A", 53)
            
            print_ranking_excel_names_and_values_single_lines(r_most_duecomplete, 5, "A", 63)
            
            print_ranking_excel_names_and_values_single_lines(r_most_star_member, 5, "A", 73)
            sheet['A83'] = r_count_dueComplete
    
            sheet['A84'] = r_star_cards
            sheet['A85'] = r_shit_counter
            
            sheet['A86'] = r_cards_wo_member
            
            if r_cards != 0:
                sheet['A87'] = round(r_cards_wo_member/r_cards*100,1)
            else:
                sheet['A87'] = 0
            sheet['A88'] = datetime.now().astimezone()
            
            
            wb.save('results_overview.xlsx')
            print("Saved results in overview file")
            
            """
            #SAVE TO GDRIVE
            file_metadata = {'name': 'results_overview.xlsx'}
            media = GoogleDrive.MediaFileUpload('results_overview.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            file = drive.files().create(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()
            print ('File ID: %s' % file.get('id'))    
            """
            
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
            if n_cards != 0:
                print("You have",n_cards, "cards in your evaluated lists, seperated in", a, "active (doing) cards (",p,"%)",sf, "semi final (review) cards (",round(sf/n_cards*100,1),"%) and ", f,"final (done) cards (",round(f/n_cards*100,1),"%). \n")
        
        def print_created_cards_count(r_created_card_counter, report_time):
            print("You have created",r_created_card_counter, "cards in the last", report_time, "days. \n")
        
        def print_dueComplete(f,dC):
            p="-"
            if f != 0:
                p=round(dC/f*100,2)
            print("Of all",f, "final cards you have complete",dC, "cards within the due date. That is", p,"% \n")
        
        def print_star_shit_cards(n_cards,star_count,shit_count,r_cards_wo_member):
            if n_cards != 0:
                print("Of the" ,n_cards, "cards in your evaluated lists, you have", star_count, "star cards(with a description, member and due date (",round(star_count/n_cards*100,1),"%)", "and",shit_count,"(shit cards (with one or less of the quality marks)",round(shit_count/n_cards*100,1),"%) \n")
                print("You have",r_cards_wo_member,"cards without responsible member. \n")
            
        def print_card_movement(n,nM,fo,ba):
            p1="-"
            p2="-"
            if ba+fo !=0:
                p1 = round(fo/(fo+ba)*100,1)
                p2 = round(ba/(fo+ba)*100,1)
            if n != 0:
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
        
        #CREATE EXCEL DOCUMENT
        print_excel(path)
    
    #RUN REPORT
    allreports = True
    p=1 
    if allreports:
        co=0    
        for path in configFilePath:
             create_report (config_name[co],path)
             print("-- "+ str(p)+" of "+str(len(configFilePath))+" reports done"+"--")
             p+=1
             co+=1
    else:
            configFilePath = r"config_folder/config_0_gruppentreffen.txt"
            create_report(config_name,configFilePath)
            print("-- test report done --")
            

