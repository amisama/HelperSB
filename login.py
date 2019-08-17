# -*- coding: utf-8 -*-

from important import *
from subprocess import check_output

defaultJson = livejson.File('defaultJson.json', True, True, 4)

client = LINE(defaultJson['authToken'],appType='IOS')

clientPoll = OEPoll(client)
clientMid = client.profile.mid

userList = {}

def logError(error):
    traceback.print_tb(error.__traceback__)
    print ('++ Error : {error}'.format(error=error))

def command(text):
    pesan = text.lower()
    if defaultJson['setKey']['status']:
        if pesan.startswith(defaultJson['setKey']['key']):
            cmd = pesan.replace(defaultJson['setKey']['key'],'')
        else:
            cmd = 'Undefined command'
    else:
        cmd = text.lower()
    return cmd

def checkScreen(name):
    var = check_output(['screen -ls; true'], shell=True)
    if '.'+name+'\t(' in var.decode('utf-8'):
        return True
    else:
        return False

def copyDirectory(src, dest):
    try:
        shutil.copytree(src, dest)
        return True
    except shutil.Error as error:
        return ('Directory not copied. Error: {}'.format(error))
    except OSError as e:
        return ('Directory not copied. Error: {}'.format(error))

def deleteDirectory(name):
    if os.path.isdir(name):
        os.system('rm -rf ' + name.lower())

def checkMention(contentMetadata):
    if 'MENTION' in contentMetadata.keys() != None:
        mention = ast.literal_eval(contentMetadata['MENTION'])
        mentionees = mention['MENTIONEES']
        if len(mentionees) == 1:
            return mentionees[0]["M"]
        else:
            return None
    else:
        return None

def restartProgram():
    print ('##----- PROGRAM RESTARTED -----##')
    python = sys.executable
    os.execl(python, python, *sys.argv)

def mentionMembers(to, mids=[]):
    if clientMid in mids: mids.remove(clientMid)
    parsed_len = len(mids)//20+1
    result = ' 「 Mention Members 」\n'
    mention = '@kevinxmayu\n'
    no = 0
    for point in range(parsed_len):
        mentionees = []
        for mid in mids[point*20:(point+1)*20]:
            no += 1
            result += ' %i. %s' % (no, mention)
            slen = len(result) - 12
            elen = len(result) + 3
            mentionees.append({'S': str(slen), 'E': str(elen - 4), 'M': mid})
        if result:
            if result.endswith('\n'): result = result[:-1]
            client.sendReplyMessage(msg_id,to, result, {'MENTION': json.dumps({'MENTIONEES': mentionees})}, 0)
        result = ''

def removeCmd(text, key=''):
    if key == '':
        setKey = '' if not defaultJson['setKey']['status'] else defaultJson['setKey']['key']
    else:
        setKey = key
    text_ = text[len(setKey):]
    sep = text_.split(' ')
    return text_[len(sep[0] + ' '):]

def clientBot(op):
    try:
        print ('[Operation] : [{}] {}'.format(op.type, OpType._VALUES_TO_NAMES[op.type].replace('_', ' ')))
        if op.type == 13:
            if op.param3 in clientMid and op.param2 in defaultJson['role']['admin'] or op.param2 in defaultJson['role']['user']:
                client.acceptGroupInvitation(op.param1)
        if op.type == 18:
            if op.param2 in defaultJson['role']['admin']:
                try:client.findAndAddContactsByMid(op.param2)
                except:pass
                client.inviteIntoGroup(op.param1,[op.param2])
        if op.type == 19:
            if op.param3 in defaultJson['role']['admin']:
                if op.param2 not in defaultJson['role']['admin']:
                    client.kickoutFromGroup(op.param1,[op.param2])
                    try:client.findAndAddContactsByMid(op.param3)
                    except:pass
                    client.inviteIntoGroup(op.param1,[op.param3])
                else:
                    try:client.findAndAddContactsByMid(op.param3)
                    except:pass
                    client.inviteIntoGroup(op.param1,[op.param3])
        if op.type in [25, 26]:
            msg             = op.message
            text            = str(msg.text)
            msg_id          = msg.id
            receiver         = msg.to
            sender          = msg._from
            to              = sender if not msg.toType and sender != clientMid else receiver
            txt             = text.lower()
            cmd             = command(text)
            setKey          = defaultJson['setKey']['key'] if defaultJson['setKey']['status'] else ''
            if msg.contentType == 0:
                if cmd == 'restart':
                    if sender in defaultJson['role']['owner']:
                        client.sendMessage(to," 「 Restart 」\nType: Restart Program\nRestarting...")
                        defaultJson['restartPoint'] = to
                        restartProgram()
                elif cmd == 'bye':
                    if sender in defaultJson['role']['owner'] or defaultJson['role']['admin'] or clientMid:
                        client.leaveGroup(to)
                elif cmd == 'help':
                    if sender in defaultJson['role']['user'] or sender in defaultJson['role']['admin']:
                        helpMessage = '「 Help Message 」'
                        if sender in defaultJson['role']['user']:
                            helpMessage += '\n• {key}GetToken <AppName>'
                            helpMessage += '\n• {key}LoginSb'
                            helpMessage += '\n• {key}LoginSb <AppName>'
                            helpMessage += '\n• {key}ListAppName'
                        if sender in defaultJson['role']['admin']:
                            helpMessage += '\n• {key}AddUserSb <name>|<day expire>|<@mention target>'
                            helpMessage += '\n• {key}DelUserSb <@mention target>'
                        client.sendMessage(to, str(helpMessage).format(key=setKey.title()))
                    else:
                        helpMessage = '「 Help Message 」'
                        helpMessage += "\n• {key}Mentionall"
                        helpMessage += "\n• {key}GetToken <AppName>"
                        client.sendMessage(to,str(helpMessage).format(key=setKey.title()))
                elif cmd == 'listappname':
                    listAppName = '「 List AppName 」'
                    if sender in defaultJson['role']['admin'] or defaultJson['role']['user'] or clientMid:
                        listAppName += '\n• CHROMEOS'
                        listAppName += '\n• DESKTOPMAC'
                        listAppName += '\n• DESKTOPWIN'
                        listAppName += '\n• IOSIPAD'
                        listAppName += '\n• WIN10'
                        client.sendMessage(to, str(listAppName))
                elif cmd == "mentionall":
                    members = []
                    if msg.toType == 1:
                        room = client.getCompactRoom(to)
                        members = [mem.mid for mem in room.contacts]
                    elif msg.toType == 2:
                        group = client.getCompactGroup(to)
                        members = [mem.mid for mem in group.members]
                    else:
                        return client.sendReplyMessage(msg_id,to, 'Failed mentionall members, use this command only on room or group chat')
                    if members:
                        mentionMembers(to, members)
                elif cmd.startswith("unsend "):
                    if sender in defaultJson['role']['admin'] or clientMid:
                        res = removeCmd(text,setKey)
                        cond = res.split(" ")
                        j = int(cond[0])
                        M = client.getRecentMessagesV2(to, 1001)
                        MId = []
                        for ind,i in enumerate(M):
                            if i._from == clientMid:
                                MId.append(i.id)
                                if len(MId) == j:
                                    break
                        for i in MId:
                            client.unsendMessage(i)
                elif cmd.startswith("exec"):
                    if sender in defaultJson['role']['admin'] or clientMid:
                        res = removeCmd(text,setKey)
                        key = res.replace(res.split("\n")[0],"")
                        try:exec(str(key))
                        except Exception as e:client.sendReplyMessage(msg_id,to,f"Error : {e}")
                elif cmd == "grouplist":
                    gids = client.getGroupIdsJoined()
                    res = ' 「 Group List 」'
                    no = 0
                    for group in gids:
                        no+=1
                        groupp = client.getGroup(group)
                        res +="\n{}. {}//{}".format(no,str(groupp.name),str(len(groupp.members)))
                    client.sendMessage(to,str(res))
                elif cmd.startswith('addme'):
                    if sender in defaultJson['role']['admin'] or defaultJson['role']['owner']:
                        res = removeCmd(text, setKey)
                        cond = res.split(" ")
                        userName = cond[0]
                        userTime = date.today() + timedelta(days=1)
                        nowDay = date.today()
                        if sender not in defaultJson['role']['user']:
                            defaultJson['role']['user'][sender] = userName
                            defaultJson['role']['info'][userName] = {'mid': sender, 'from': str(nowDay), 'expire': str(userTime), 'authToken':'', 'json': '', 'group': to, 'appType': ''}
                            client.sendMessage(to, ' 「 Service 」\nType: Add Service\nStatus: Success add user as : {}'.format(userName))
                        else:client.sendMessage(to," 「 Service 」\nType: Add Service\nStatus: Error\nInfo:\n   Sorry, you'r a user")
                elif cmd == "delme":
                    if sender in defaultJson['role']['user']:
                        name = defaultJson['role']['user'][sender]
                        if checkScreen(name) == True:os.system("screen -R {} -X quit".format(name))
                        del defaultJson['role']['info'][name]
                        del defaultJson['role']['user'][sender]
                        client.sendMessage(to," 「 Service 」\nType: Delete Service\nStatus: Success delete !")
                    else:client.sendMessage(to," 「 Service 」\nType: Delete Service\nStatus: Error\nInfo:\n   Sorry you'r not a user")
                elif cmd.startswith('update'):
                    if sender in defaultJson['role']['admin'] or clientMid:
                        res = removeCmd(text, setKey)
                        cond = res.split(" ")
                        userName = cond[0]
                        if int(cond[1]) >= 50:
                            if sender not in defaultJson['role']['admin']:
                                return client.sendReplyMessage(msg_id,to,"Kebanyakan goblok !")
                        userTime = date.today() + timedelta(int(cond[1]))
                        if userName in defaultJson['role']['info']:
                            defaultJson['role']['info'][userName].update({'expire': str(userTime)})
                            client.sendMessage(to," 「 Service 」\nType: Update Service\nUser: {}\nStatus: Success update service".format(userName))
                        else:client.sendMessage(to," 「 Service 」\nType: Update Service\nStatus: Error\nInfo:\n   Sorry, {} not in list user".format(userName))
                elif cmd.startswith('renew '):
                    if sender in defaultJson['role']['admin'] or defaultJson['role']['user'] or clientMid:
                        if checkMention(msg.contentMetadata) != None:
                            userMid = checkMention(msg.contentMetadata)
                            if userMid in defaultJson['role']['user']:
                                userName = defaultJson['role']['user'][userMid]
                                userJson = defaultJson['role']['info'][userName]
                                if userJson['expire'] == str(date.today()):
                                    return client.sendMentionV3(msg_id,to," 「 Service 」\nType: Login Service\nUser: {}\nStatus: Expired !\nSorry, @! service has been expired".format(userName),[userMid])
                                client.sendMessage(to," 「 Service 」\nType: Restart Session\nTrying to restart session user...")
                                if checkScreen(userName) == True:
                                    os.system('screen -R {} -X quit'.format(str(userName)))
                                    os.system('screen -S {} -dm python3 selfbot.py -u {}'.format(userName,userName))
                                else:
                                    os.system('screen -S {} -dm python3 selfbot.py -u {}'.format(userName,userName))
                                if checkScreen(userName) == True:
                                    client.sendMentionV2(to," 「 Service 」\nType: Restart Session\nStatus: Success Restart Session User @!",[userMid])
                                else:
                                    client.sendMentionV2(to," 「 Service 」\nType: Restart Session\nStatus: Error\nInfo:\n   Failed to restart session user @!", [userMid])
                            else:client.sendMentionV3(msg_id,to," 「 Service 」\nType: Restart Session\nStatus: Error\nInfo:\n   Sorry, @! not in list user",[userMid])
                        else:
                            res = removeCmd(text, setKey)
                            cond = res.split(' ')
                            userName = cond[0]
                            if userName in defaultJson['role']['info']:
                                userJson = defaultJson['role']['info'][userName]
                                if userJson['expire'] == str(date.today()):
                                    return client.sendMentionV3(msg_id,to," 「 Service 」\nType: Login Service\nUser: {}\nStatus: Expired !\nSorry, @! service has been expired".format(userName),[userJson['mid']])
                                client.sendMessage(to," 「 Service 」\nType: Restart Session\nTrying to restart session user....")
                                if checkScreen(userName) == True:
                                    os.system('screen -R {} -X quit'.format(str(userName)))
                                    os.system('screen -S {} -dm python3 selfbot.py -u {}'.format(userName,userName))
                                else:
                                    os.system('screen -S {} -dm python3 selfbot.py -u {}'.format(userName,userName))
                                if checkScreen(userName) == True:
                                    client.sendMessage(to," 「 Service 」\nType: Restart Session\nUser: {}\nStatus: Success restart session".format(userName))
                                else:
                                    client.sendMessage(to," 「 Service 」\nType: Restart Session\nUser: {}\nStatus: Error\nInfo:\n   Failed to restart session".format(userName))
                            else:client.sendMessage(to," 「 Service 」\nType: Restart Session\nStatus: Error\nInfo:\n   Sorry, {} not in list user".format(userName))
                elif cmd.startswith('checkuser'):
                    if sender in defaultJson['role']['admin'] or clientMid:
                        if checkMention(msg.contentMetadata) != None:
                            userMid = checkMention(msg.contentMetadata)
                            if userMid in defaultJson['role']['user']:
                                nama = defaultJson['role']['user'][userMid]
                                userJson = defaultJson['role']['info'][nama]
                                if checkScreen(nama) == True:statusScreen="Active"
                                else:statusScreen="Non Active"
                                if userJson['expire'] == str(date.today()):statusExpired="Expired"
                                else:a=datetime.strptime(userJson['expire'],"%Y-%m-%d").date();statusExpired=str(a - date.today()).split(",")[-2]
                                ret = " 「 Service 」\nType: Check User\nUserStatus:\n   User: @!\n   UserName: {}\n   Screen: {}\n   Add to service at: {}\n   Expired at: {}\n   Expired: {}".format(nama,statusScreen,userJson['from'],userJson['expire'],statusExpired)
                                client.sendMentionV2(to,str(ret),[userMid])
                            else:client.sendMentionV3(msg_id,to," 「 Service 」\nType: Check User\nStatus: Error\nInfo:\n   Sorry, @! not in list user",[userMid])
                        else:
                            res = removeCmd(text, setKey)
                            cond = res.split(' ')
                            name = cond[0]
                            if name in defaultJson['role']['info']:
                                userJson = defaultJson['role']['info'][name]
                                if checkScreen(name) == True:statusScreen="Active"
                                else:statusScreen="Non Active"
                                if userJson['expire'] == str(date.today()):statusExpired="Expired"
                                else:a=datetime.strptime(userJson['expire'],"%Y-%m-%d").date();statusExpired=str(a - date.today()).split(",")[-2]
                                ret = " 「 Service 」\nType: Check User\nUserStatus:\n   User: @!\n   UserName: {}\n   Screen: {}\n   Add to service at: {}\n   Expired at: {}\n   Expired: {}".format(name,statusScreen,userJson['from'],userJson['expire'],statusExpired)
                                client.sendMentionV2(to,str(ret),[userJson['mid']])
                            else:client.sendMessage(to," 「 Service 」\nType: Check User\nStatus: Error\nInfo:\n   Sorry, {} not in list user".format(name))
                elif cmd == "list user":
                    if sender in defaultJson['role']['admin']:
                        if defaultJson['role']['user'] == {}:
                            return client.sendMessage(to,"Tidak ada user terdaftar")
                        listMid = [a for a in defaultJson['role']['user']]
                        k = len(listMid)//20
                        for aa in range(k+1):
                            anu = listMid[aa*20 : (aa+1)*20]
                            if aa==0:ret=" 「 Service 」\nType: List Service\nList:";no=aa
                            else:ret="";no=aa*20
                            for a in anu:
                                no+=1
                                name = defaultJson['role']['user'][a]
                                userJson = defaultJson['role']['info'][name]
                                if userJson['expire'] == str(date.today()) or userJson['expire'] <= str(date.today()):status="Expired"
                                else:a = datetime.strptime(userJson['expire'], "%Y-%m-%d").date();status=str(a - date.today()).split(",")[-2]
                                ret+="\n   {}. @!\n      User Name: {}\n      Expired: {}\n      From: {}\n      Status Expire: {}\n".format(no,name,userJson['expire'],userJson['from'],status)
                            client.sendMentionV2(to,str(ret),anu)
                elif cmd.startswith("addadmin"):
                    if sender in defaultJson['role']['owner'] or clientMid:
                        if checkMention(msg.contentMetadata) != None:
                            userMid = checkMention(msg.contentMetadata)
                            if userMid not in defaultJson['role']['admin']:
                                defaultJson['role']['admin'].append(userMid)
                                client.sendMessage(to,' 「 Service 」\nType: Add Admin\nStatus: Success')
                            else:client.sendMentionV3(msg_id,to,' 「 Service 」\nType: Add Admin\nStatus: Error\nInfo:\n   Sorry, @! is a admin',[userMid])
                elif cmd.startswith('deladmin'):
                    if sender in defaultJson['role']['owner'] or clientMid:
                        if checkMention(msg.contentMetadata) != None:
                            userMid = checkMention(msg.contentMetadata)
                            if userMid in defaultJson['role']['admin']:
                                defaultJson['role']['admin'].remove(userMid)
                                client.sendMessage(to,' 「 Service 」\nType: Delete Admin\nStatus: Success')
                            else:client.sendMentionV3(msg_id,to," 「 Service 」\nType: Delete Admin\nStatus: Error\nInfo:\n   Sorry, @! not a admin",[userMid])
                elif cmd == "list admin":
                    if sender in defaultJson['role']['owner'] or clientMid:
                        if defaultJson['role']['admin'] != []:
                            ret = " 「 Service」\nType: List Admin\nList:";no=0
                            for i in defaultJson['role']['admin']:
                                no+=1
                                ret+="\n   {}. @!".format(no)
                            client.sendMentionV2(to,str(ret),defaultJson['role']['admin'])
                elif cmd.startswith('addusersb'):
                    if sender in defaultJson['role']['admin'] or clientMid:
                        res = removeCmd(text, setKey)
                        cond = res.split('|')
                        userName = cond[0]
                        userTime = date.today() + timedelta(int(cond[1]))
                        nowDay = date.today()
                        if checkMention(msg.contentMetadata) != None:
                            userMid = checkMention(msg.contentMetadata)
                            if userMid not in defaultJson['role']['user']:
                                defaultJson['role']['user'][userMid] = userName
                                defaultJson['role']['info'][userName] = {'mid': userMid, 'from': str(nowDay), 'expire': str(userTime), 'authToken': '', 'json': '','group':to, 'appType': ''}
                                client.sendMentionV3(msg_id,to," 「 Service 」\nType: Add User Service\nUserName: {}\nStatus: Success add @!".format(userName),[userMid])
                            else:
                                client.sendMentionV3(msg_id,to," 「 Service 」\nType: Add User Service\nStatus: Error\nInfo:\n   Sorry, @! is a user",[userMid])
                elif cmd.startswith('delusersb'):
                    if sender in defaultJson['role']['admin'] or clientMid:
                        if checkMention(msg.contentMetadata) != None:
                            userMid = checkMention(msg.contentMetadata)
                            if userMid in defaultJson['role']['user']:
                                name = defaultJson['role']['user'][userMid]
                                if checkScreen(name) == True:os.system("screen -R {} -X quit".format(name))
                                del defaultJson['role']['info'][name]
                                del defaultJson['role']['user'][userMid]
                                os.system("rm -rf user/{}.json".format(str(name)))
                                client.sendMentionV3(msg_id,to," 「 Service 」\nType: Delete User Service\nUser: {}\nStatus: Sucess delete @!".format(name),[userMid])
                            else:
                                client.sendMentionV2(to," 「 Service 」\nType: Delete User Service\nStatus: Error\nInfo:\n   Sorry, @! not in list user",[userMid])
                        else:
                            res = removeCmd(text, setKey)
                            cond = res.split(' ')
                            name = cond[0]
                            if name in defaultJson['role']['info']:
                                if checkScreen(name) == True:os.system("screen -R {} -X quit".format(name))
                                userMid = defaultJson['role']['info'][name]['mid']
                                del defaultJson['role']['user'][userMid]
                                del defaultJson['role']['info'][name]
                                os.system("rm -rf user/{}.json".format(str(name)))
                                client.sendMessage(to,' 「 Service 」\nType: Delete User Service\nUser: {}\nStatus: Success delete'.format(name))
                            else:client.sendMessage(to,' 「 Service 」\nType: Delete User Service\nStatus: Error\nInfo:\n   Sorry, {} not in list user'.format(name))
                elif cmd.startswith('loginsb'):
                    if cmd == 'loginsb':
                        if sender in defaultJson['role']['user']:
                            userName = defaultJson['role']['user'][sender]
                            userJson = defaultJson['role']['info'][userName]
                            if userJson['expire'] == str(date.today()):
                                return client.sendMentionV3(msg_id,to," 「 Service 」\nType: Login Service\nUser: {}\nStatus: Expired !\nSorry @!, Your selfbot has been expire".format(userName),[sender])
                            userJson['json'] = 'user/{}.json'.format(userName)
                            userJson['appType'] = 'WIN10'
                            if userJson['authToken'] == '':
                                if sender not in userList:
                                    userList[sender] = {}
                                userList[sender]['currentProcess'] = LineAuth('WIN10')
                                userList[sender]['startProcess'] = time.time()
                                qrCode = userList[sender]['currentProcess'].generateQrCode()
                                client.sendMessage(to, " 「 QRCode 」\nType: Login Service\nAppType: WIN10\nUser: {}\nQRCode: {}".format(userName,str(qrCode)))
                                if userList[sender]['currentProcess'] != None:
                                    if time.time() - userList[sender]['startProcess'] >= 120:
                                        userList[sender]['currentProcess'] = None
                                        userList[sender]['startProcess'] = None
                                        client.sendMessage(to, ' 「 QRCode 」\nType: Login Service\nAppType: WIN10\nUser: {}\nQRCode: Expired'.format(userName))
                                resultToken = userList[sender]['currentProcess'].generateAuthToken()
                                userJson['authToken'] = resultToken
                                if checkScreen(userName) == True:
                                    os.system('screen -R {} -X quit'.format(str(userName)))
                                    os.system('screen -S {} -dm python3 selfbot.py -u {}'.format(userName,userName))
                                else:
                                    os.system('screen -S {} -dm python3 selfbot.py -u {}'.format(userName,userName))
                                time.sleep(2)
                                if checkScreen(userName) == True:
                                    client.sendMessage(to, ' 「 Service 」\nType: Login Service\nUser: {}\nStatus: Success login !'.format(userName))
                                else:
                                    client.sendMessage(to, ' 「 Service 」\nType: Login Service\nUser: {}\nStatus: Failed login !'.format(userName))
                            else:
                                if checkScreen(userName) == True:
                                    os.system('screen -R {} -X quit'.format(str(userName)))
                                    os.system('screen -S {} -dm python3 selfboy.py -u {}'.format(userName,userName))
                                else:
                                    os.system('screen -S {} -dm python3 selfbot.py -u {}'.format(userName,userName))
                                time.sleep(2)
                                if checkScreen(userName) == True:
                                    client.sendMessage(to, ' 「 Service 」\nType: Login Service\nUser: {}\nStatus: Success login !'.format(userName))
                                else:
                                    client.sendMessage(to, ' 「 Service 」\nType: Login Service\nUser: {}\nStatus: Failed login !'.format(userName))
                    else:
                        res = removeCmd(text, setKey)
                        if sender in defaultJson['role']['user']:
                            userName = defaultJson['role']['user'][sender]
                            userJson = defaultJson['role']['info'][userName]
                            if userJson['expire'] == str(date.today()):
                                return client.sendMentionV3(msg_id,to," 「 Service 」\nType: Login Service\nUser: {}\nStatus: Expired !Sorry @!, Your selfbot has been expire".format(userName),[sender])
                            userJson['json'] = 'user/{}.json'.format(userName)
                            userJson['appType'] = res.upper()
                            if sender not in userList:
                                userList[sender] = {}
                            userList[sender]['currentProcess'] = LineAuth(res.upper())
                            userList[sender]['startProcess'] = time.time()
                            qrCode = userList[sender]['currentProcess'].generateQrCode()
                            client.sendMessage(to, " 「 QRCode 」\nType: Login Service\nAppType: {}\nUser: {}\nQRCode: {}".format(res.upper(),userName,str(qrCode)))
                            if userList[sender]['currentProcess'] != None:
                                if time.time() - userList[sender]['startProcess'] >= 120:
                                    userList[sender]['currentProcess'] = None
                                    userList[sender]['startProcess'] = None
                                    client.sendMessage(to, ' 「 QRCode 」\nType: Login Service\nAppType: {}\nUser: {}\nQRCode: Expired'.format(res.upper(),userName))
                            resultToken = userList[sender]['currentProcess'].generateAuthToken()
                            userJson['authToken'] = resultToken
                            if checkScreen(userName) == True:
                                os.system('screen -R {} -X quit'.format(str(userName)))
                                os.system('screen -S {} -dm python3 selfbot.py -u {}'.format(userName,userName))
                            else:
                                os.system('screen -S {} -dm python3 selfbot.py -u {}'.format(userName,userName))
                            time.sleep(2)
                            if checkScreen(userName) == True:
                                client.sendMessage(to, ' 「 Service 」\nType: Login Service\nUser: {}\nStatus: Success login !'.format(userName))
                            else:
                                client.sendMessage(to, ' 「 Service 」\nType: Login Service\nUser: {}\nStatus: Failed login !'.format(userName))
                elif cmd.startswith('gettoken'):
                        res = removeCmd(text, setKey)
                        if sender not in userList:
                            userList[sender] = {}
                        userList[sender]['currentProcess'] = LineAuth(res.upper())
                        userList[sender]['startProcess'] = time.time()
                        qrCode = userList[sender]['currentProcess'].generateQrCode()
                        client.sendMessage(to, " 「 QRCode 」\nType: Get Token\nAppType: {}\nQRCode: {}".format(res.upper(),str(qrCode)))
                        if userList[sender]['currentProcess'] != None:
                            if time.time() - userList[sender]['startProcess'] >= 120:
                                userList[sender]['currentProcess'] = None
                                userList[sender]['startProcess'] = None
                                client.sendMessage(to, " 「 QRCode 」\nType: Get Token\nAppType: {}\nQRCode: Expired".format(res.upper()))
                        resultToken = userList[sender]['currentProcess'].generateAuthToken()
                        client.sendMessage(to, " 「 QRCode 」\nType: Get Token\nAppType: {}\nAuthToken: {}".format(res.upper(),str(resultToken)))

    except TalkException as talk_error:
        logError(talk_error)
        if talk_error.code in [7, 8, 20]:
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit('##---- KEYBOARD INTERRUPT -----##')
    except Exception as error:
        logError(error)

def clientRun():
    if defaultJson['restartPoint'] is not None:
        try:
            client.sendMessage(defaultJson['restartPoint'], ' 「 Restart 」\nType: Restart Program\nSuccess Restart !')
        except TalkException:
            pass
        defaultJson['restartPoint'] = None
    while True:
        try:
            ops = clientPoll.singleTrace(count=50)
            if ops:
                for op in ops:
                    t1=Thread(target=clientBot,args=(op,))
                    t1.start()
                    clientPoll.setRevision(op.revision)
        except TalkException as talk_error:
            logError(talk_error)
            if talk_error.code in [7, 8, 20]:
                sys.exit(1)
            continue
        except KeyboardInterrupt:
            sys.exit('##---- KEYBOARD INTERRUPT -----##')
        except Exception as error:
            logError(error)
            continue

if __name__ == '__main__':
    clientRun()

