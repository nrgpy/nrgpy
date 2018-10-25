#!/usr/bin/python
#
# 2017/11/21 - ipk2lgr.py .............. d.carlson
#                                       edited 2018/09/26
#
#
#            - takes IPK file as input and converts to LGR file
#
#               usage: import ipk2lgr
#                      ipk2lgr.ipk2lgr("path/to/ipkfile")
#               output: ipkfile.lgr # includes network and email settings
#             ...............................................

from datetime import datetime
import os
import sys 

#logfile = 'ipklog.log'


def ipk2lgr(ipkfile): 
    today = datetime.today().strftime('%Y-%m-%d')

    # handle the old and new filenames, abort if filename bad
    filenameroot = ''
    filename     = filenameroot + ipkfile
    lgrfilename  = filename[:-3] + 'lgr'

    if os.path.isfile(filename) == False:
        return "file doesn't exist"

    if os.path.isfile(lgrfilename) == True: #replace existing lgr file
        lgrfile = open(lgrfilename, 'w+')
        lgrfile.truncate()
    else:
        lgrfile = open(lgrfilename, 'w+')



    # read the ipk file into array, map included in comments below
    ipkfile = open(filename, 'r')
    ipkline = []

    for line in ipkfile:
        try:
            int(line)
            ipkline.append(str(int(line)))
        except:        
            ipkline.append(line[1:-2])

    # assign smtp port if older IPK file
    if len(ipkline) < 35:
        smtpport = str(25)
    else:
        smtpport = str(ipkline[35])

    # get iPack type
    try:
        ipacktype, apn = ipackinfo(ipkline[18])
    except:
        ipacktype, apn = ipackinfo_backup(ipkline[0])

    # write the settings into a new lgr file
    try:
        writearray = []
        writearray.append(";Renewable NRG Systems SymphoniePRO & iPack Configuration File")
        writearray.append(";Software Version: x.x.x.x (converted with Python)")
        writearray.append(";Generated: "+today)
        writearray.append("")
        writearray.append("[FileHeader]")
        writearray.append("FormatVersion=1")
        writearray.append("")
        writearray.append("[EmailSchedule]")
        writearray.append("Frequency="+callinterval(int(ipkline[17])))
        writearray.append("Time(UTC)="+calltime(int(ipkline[16])))
        writearray.append("SmtpServer="+ipkline[9])
        writearray.append("SmtpPort="+smtpport)
        writearray.append("SmtpUserName="+ipkline[28])
        writearray.append("Password="+ipkline[29])
        writearray.append("SendersEmail="+ipkline[12])
        writearray.append("SendersName=")
        writearray.append("RecipientsEmail="+ipkline[10])
        writearray.append("RecipientsName="+ipkline[11])
        writearray.append("CCEmail1="+ipkline[25])
        writearray.append("CCEmail2="+ipkline[26])
        writearray.append("Subject="+ipkline[14])
        writearray.append("")
        writearray.append("[TimeService]")
        writearray.append("SntpServer="+ipkline[15])
        writearray.append("UseSntp=On")
        writearray.append("UseGps=On")
        writearray.append("")
        writearray.append("[iPackNetwork]")
        writearray.append("iPackModel="+ipacktype)
        writearray.append("IspUserName="+ipkline[4])
        writearray.append("IspPassword="+ipkline[5])
        if apn == True:
            writearray.append("GsmApn="+ipkline[30])
            writearray.append("Pin=")                #+ipkline[19])
        writearray.append("DialString="+ipkline[0])
        writearray.append("PrimaryDNS="+ipkline[2])
        writearray.append("SecondaryDNS="+ipkline[3])
        writearray.append("")
        writearray.append("[LoggerInitiatedSchedule]")
        writearray.append("Frequency=Disabled")
        writearray.append("Time(UTC)=00:00")
        writearray.append("PrimaryHost=")
        writearray.append("PrimaryPort=30406")
        writearray.append("SecondaryHost=")
        writearray.append("SecondaryPort=30406")
        writearray.append("Backup=On") # enable connections to listener server
        writearray.append("")
        writearray.append("[LoggerListeningSchedule]")
        writearray.append("Frequency="+callinterval(int(ipkline[17])))
        writearray.append("Time(UTC)=12:00")
        writearray.append("Duration=1 Hour")
        # write array to file
        print("\nWriting data to {0}  ...\t\t".format(lgrfilename), end="", flush=True)
        for row in writearray:
            lgrfile.write("%s\n" % row)

        lgrfile.close()
        print("[DONE]")
       
    except: 
        lgrfile.close()
        print("Unable to convert file".format(ipkfile))




def callinterval(original):
    if int(original) < 3600:
        callint = str(original / 60) + " Minutes"
    elif int(original) > 3600 and int(original) < 86400:
        callint = str(original / 3600) + " Hours"
    elif int(original) == 86400:
        callint = "Daily"
    elif int(original) > 86400 and int(original) < 520000:
        callint = str(original / 86400) + " Days"
    elif int(original) > 520000:
        callint = "Weekly"
    return callint
 

def calltime(original):
    return datetime.utcfromtimestamp(int(original)).strftime('%H:%M')


def ipackinfo(typeint):
    ipackdefs = (["OTHER","?", 0, False],
        ["CM900", "CM900", 1, False],
        ["GSM","GSM", 2, True],
        ["CERMETEK","Dial-up", 3, False],
        ["DOCOMO","DoCoMo", 4, False],
        ["CDMA","CDMA", 5, False],
        ["IRIDIUM","Iridium", 6, False],
        ["GLOBALSTAR","GlobalStar", 7, False],
        ["DIRECT", "iPackACCESS (7169)", 8, False],
        ["CDMA_C1", "iPackGPS CDMA (4621)", 9, False],
        ["GSM_G2_R1", "iPackGPS GSM (4622)", 10, True],
        ["GSM_3G", "iPackGPS 3G (7984)", 11, True],
        ["CDMA_C2", "iPackGPS CDMA (4621)", 12, False],
        ["2G_GSM_G3", "iPackGPS GSM (4622)", 13, True],
        ["LTE_TDD", "iPackGPS LTE-TDD (9388)", 14, True],
        ["LTE_VZW", "iPackGPS LTE-VZW (9390)", 15, True],
        ["LTE_ATT", "iPackGPS LTE-ATT (9389)", 16, True])

    ipacktype = ipackdefs[typeint][1]
    apn       = ipackdefs[typeint][3]

    return ipacktype, apn


def ipackinfo_backup(phonestr):
    if phonestr[:3] == "*99":
        ipacktype = "iPackGPS GSM (4622)"
        apn       = True
    elif phonestr[:4] == "#777":
        ipacktype = "iPackGPS CDMA (4621)"
        apn       = False
    else:
        ipacktype = "iPackACCESS (7169)"
        apn       = True

    return ipacktype, apn


if __name__ == "__main__":
   ipk2lgr(sys.argv[1])
 

    #     #     #     #     #     #     # 
    # iPack file Line assignment (0 indexed)
    # 
    # 0 = Primary ISP Phone Number
    # 1 = Secondary ISP Phone Number (hidden)
    # 2 = Primary DNS number
    # 3 = Secondary DNS number
    # 4 = ISP User name
    # 5 = ISP Password
    # 6 = POP Mailbox Name
    # 7 = POP Mailbox Password
    # 8 = POP3 server
    # 9 = SMTP server
    # 10 = Recipient's E-Mail Address
    # 11 = Recipient's Name
    # 12 = Sender's E-Mail Address
    # 13 =
    # 14 = E-Mail Subject Line
    # 15 = Internet Time Server
    # 16 = Next Call Time (seconds since 1970)
    # 17 = Call Interval (seconds)
    # 18 = iPack type:
		# 0 = OTHER
		# 1 = AMPS
		# 2 = GSM/GPRS
		# 3 = Dial-up
		# 4 = DoCoMo
		# 5 = CDMA
		# 6 = Satellite ... etc...
    # 19 = GSM pin
    # 20 =
    # 21 = 
    # 22 = 
    # 23 = 
    # 24 = Patch Password
    # 25 = CC E-Mail Address 
    # 26 = CC E-Mail Address 2
    # 27 = My SMTP Server requires authentication 1/0
    # 28 = SMTP Login
    # 29 = SMTP Password
    # 30 = APN Name (GPRS Only)
    # 31 = Download partial files 255/0
    # 32 = Check POP mailbox 255/0
    # 33 = Enable SMTP 255/0
    # 34 = POP Port
    # 35 = SMTP Port
    # 36 = Enable Modbus? 1/0
    # 37 = Modbus Slave Address (1-255)
    # 38 = Modpus Port (1-65535)
    # 39 = Enable DHCP? 1/0
    # 40 = Static IP Address
    # 41 = Subnet Mask
    # 42 = Gateway IP Address
    # 43 = Statistical Data Interval (seconds)
    # 44 = Stale Data Timeout (seconds)
    # 45 = Use Secure IP Address 1/0
    # 46 - 55 = Allowed IP Address 1 - 10
    #     #     #     #     #     # 
    # LGR file comms line assignment
    # 1 = ;Renewable NRG Systems SymphoniePRO & iPack Configuration File (comment)
    # 2 = ;Software Version: 2.2.0.3 (build 27564 (modified) 2016-09-08) (comment)
    # 3 = ;Generated: 2016-11-21 10:02:29 (comment)
    # 4 =
    # 5 = [FileHeader]
    # 6 = FormatVersion=1
    # 7 =
    # 8 = [EmailSchedule]
    # 9 = Frequency=Daily
    # 10 = Time(UTC)=12:10
    # 11 = SmtpServer=
    # 12 = SmtpPort=
    # 13 = SmtpUserName=
    # 14 = Password=
    # 15 = SendersEmail=
    # 16 = SendersName=
    # 17 = RecipientsEmail=
    # 18 = CCEmail1=
    # 19 = CCEmail2=
    # 21 = Subject=
    # 22 =
    # 23 = [TimeService]
    # 24 = SntpServer=ntp.ubuntu.com
    # 25 = UseSntp=Off
    # 26 = UseGps=On
    # 27 = 
    # 28 = [iPackNetwork]
    # 29 = iPackModel=iPackGPS CDMA (4621) OR
    #      iPackModel=iPackACCESS (7169)
    #      iPackModel=iPackGPS DoCoMo (4623) *USES APN & PIN
    #      iPackModel=iPackGPS 3G (7984)     *USES APN & PIN
    #      iPackModel=iPackGPS GSM (4622)    *USES APN & PIN


    # 30 = IspUserName=web
    # 31 = IspPassword=web

    # 32 = GsmApn=
    # 33 = Pin=
    # 34 = DialString=#777 or *99***1#
    # 35 = PrimaryDNS=0.0.0.0
    # 36 = SecondaryDNS=0.0.0.0
    # 37

                 
