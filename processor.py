from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from datetime import datetime
import pandas as pd
import re
import os

root = Tk()
root.title("EPT Processor")
root.geometry("400x300")

option = IntVar()
option.set("1")
root.filename = ''


def selectFile():
    Label(root,
        text="Select File").place(x=40, y=20)
    
    Button(root,
        text="Browse File",
        command=getFile).place(x=150, y=20)

def selectOption():
    Label(root,
        text="Select option to process file").place(x=40, y=70)
        
    Label(root,
        text=root.filename).place(x=40, y=90)

    Radiobutton(root, 
        text="All Rows",
        value=1,
        variable=option).place(x=40, y=120)

    Radiobutton(root, 
        text="Select Rows by Municipio",
        value=2,
        variable=option).place(x=40, y=150)

    Button(root,
        text="Next",
        command=loadFile).place(x=300, y=150)
    
def getFile():
    root.filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("xlsx files", "*.xlsx"),("all files", "*.*")))
    selectOption()

def processFile():
    sheets = pd.ExcelFile(root.filename)
    dfo = pd.read_excel(sheets, 'EPT_3G_LTE_OUTDOOR')
    dfi = pd.read_excel(sheets, 'EPT_3G_LTE_INDOOR')
    timestamp = os.path.getatime(root.filename)
    timestamp = datetime.fromtimestamp(timestamp)
    columns = ['AT&T_Site_Name','AT&T_Tech','State','Country','Region','Vendor','CS POOL','PS POOL','REGION CELULAR','Name_List']
    site_names = ['AT&T_Node_Name', 'Node_B_U2000', 'Node B U2000_Anterior']

    dfo = dfo.astype(str)
    dfo = dfo.fillna('')

    dfi = dfi.astype(str)
    dfi = dfi.fillna('')
    
    dfo['Name_List'] = dfo.apply(lambda row: str(row[site_names].tolist()).replace("'",'').replace(' ','')[1:-1], axis=1)
    dfi['Name_List'] = dfi.apply(lambda row: str(row[site_names].tolist()).replace("'",'').replace(' ','')[1:-1], axis=1)

    dfo = dfo[columns]
    dfi = dfi[columns]

    dfo['Vendor_List'] = dfo['Vendor']
    dfo['Vendor'] = dfo['Vendor'].apply(lambda vendor: vendor if '(' not in vendor else vendor[:vendor.find(' (')])
    dfo['Vendor_List'] = dfo['Vendor_List'].apply(lambda vendor: vendor if '(' not in vendor else mapName(vendor[vendor.find('('):]))
    dfi['Vendor_List'] = dfi['Vendor']
    dfi['Vendor'] = dfi['Vendor'].apply(lambda vendor: vendor if '(' not in vendor else vendor[:vendor.find(' (')])
    dfi['Vendor_List'] = dfi['Vendor_List'].apply(lambda vendor: vendor if '(' not in vendor else mapName(vendor[vendor.find('('):]))

    dfo['Type'] = 'Outdoor'
    dfi['Type'] = 'Indor'

    dfo['AT&T_Tech'] = dfo['AT&T_Tech'].apply(lambda tech: tech if 'LTE' != tech else '4G')
    dfi['AT&T_Tech'] = dfi['AT&T_Tech'].apply(lambda tech: tech if 'LTE' != tech else '4G')

    pattern = r'(?:20\d{2}|20[01][0-9]|2020)[-.](?:0[1-9]|1[012])[-.](?:0[1-9]|[12][0-9]|3[01])'

    if re.search(pattern, root.filename):
        fileDate = ''.join(re.findall(pattern, root.filename))
        fileDate = datetime.strptime(fileDate, '%Y-%m-%d').date()
        fileDate = fileDate.strftime('%m/%d/%Y')
        dfo['Date'] = fileDate
        dfi['Date'] = fileDate
    else:
        dfo['Date'] = ''
        dfi['Date'] = ''

    dfo['REGION CELULAR'] = dfo['REGION CELULAR'].apply(lambda r: int(str(r)[:1]))
    dfi['REGION CELULAR'] = dfi['REGION CELULAR'].apply(lambda r: int(str(r)[:1]))

    rename = {
        'CS POOL': "CS_Pool",
        'PS POOL': "PS_Pool",
        'REGION CELULAR': "Region_Cellular",
        'Name_List': "NE_Name_List",
        'Vendor_List': "NE_Vendor_List",
    }

    dfi.rename(columns=rename, inplace=True)
    dfo.rename(columns=rename, inplace=True)

    order = [
        "Date",
        "AT&T_Site_Name",
        "AT&T_Tech",
        "State",
        "Country",
        "Region",
        "Vendor",
        "Region_Cellular",
        "CS_Pool",
        "PS_Pool",
        "NE_Name_List",
        "NE_Vendor_List",
        "Type",
    ]

    dfi = dfi[order]
    dfo = dfo[order]

    df = pd.concat([dfo,dfi])
    df = df.drop_duplicates()

    dir = os.path.dirname(root.filename)

    df.to_excel(dir + '/output.xlsx', sheet_name='EPT', index=False)

    messagebox.showinfo(title='File Processed',
                message=f'Yout file is processed on {dir}/output.xlsx')

def processMun():
    Label(root,
        text='Select Municipality').place(x=40, y=180)

    sheets = pd.ExcelFile(root.filename)
    dfo = pd.read_excel(sheets, 'EPT_3G_LTE_OUTDOOR')
    dfi = pd.read_excel(sheets, 'EPT_3G_LTE_INDOOR')

    municipality = dfo['Municipio'].tolist()
    municipality.extend(dfi['Municipio'])
    municipality = list(set(municipality))

    deselect = []
    pany = 180
    for idx, val in enumerate(municipality):
        op = StringVar()
        op.set(val)
        deselect.append(op)
        pany += 20
        Checkbutton(root,
                text=val,
                variable=deselect[idx],
                onvalue=val,
                offvalue='').place(x=40, y=pany)

    Button(root,
        text='Process now',
        command=lambda: processSelectedMun(sheets, deselect)).place(x=300, y=200)

def processSelectedMun(sheets, deselect):
    dfo = pd.read_excel(sheets, 'EPT_3G_LTE_OUTDOOR')
    dfi = pd.read_excel(sheets, 'EPT_3G_LTE_INDOOR')

    selectedMun = [name.get() for name in deselect if name.get() != '']

    dfo = dfo[dfo['Municipio'].isin(selectedMun)]
    dfi = dfi[dfi['Municipio'].isin(selectedMun)]
    timestamp = os.path.getatime(root.filename)
    timestamp = datetime.fromtimestamp(timestamp)
    columns = ['AT&T_Site_Name','AT&T_Tech','State','Country','Region','Vendor','CS POOL','PS POOL','REGION CELULAR','Name_List']
    site_names = ['AT&T_Node_Name', 'Node_B_U2000', 'Node B U2000_Anterior']

    dfo['Name_List'] = dfo.apply(lambda row: str(row[site_names].tolist()).replace("'",'').replace(' ','')[1:-1], axis=1)
    dfi['Name_List'] = dfi.apply(lambda row: str(row[site_names].tolist()).replace("'",'').replace(' ','')[1:-1], axis=1)

    dfo = dfo[columns]
    dfi = dfi[columns]

    dfo['AT&T_Tech'] = dfo['AT&T_Tech'].apply(lambda tech: tech if 'LTE' != tech else '4G')
    dfi['AT&T_Tech'] = dfi['AT&T_Tech'].apply(lambda tech: tech if 'LTE' != tech else '4G')

    dfo['Vendor_List'] = dfo['Vendor']
    dfo['Vendor'] = dfo['Vendor'].apply(lambda vendor: vendor if '(' not in vendor else vendor[:vendor.find(' (')])
    dfo['Vendor_List'] = dfo['Vendor_List'].apply(lambda vendor: vendor if '(' not in vendor else mapName(vendor[vendor.find('('):]))
    dfi['Vendor_List'] = dfi['Vendor']
    dfi['Vendor'] = dfi['Vendor'].apply(lambda vendor: vendor if '(' not in vendor else vendor[:vendor.find(' (')])
    dfi['Vendor_List'] = dfi['Vendor_List'].apply(lambda vendor: vendor if '(' not in vendor else mapName(vendor[vendor.find('('):]))

    dfo['Type'] = 'Outdoor'
    dfi['Type'] = 'Indor'

    pattern = r'(?:19\d{2}|20[01][0-9]|2020)[-.](?:0[1-9]|1[012])[-.](?:0[1-9]|[12][0-9]|3[01])'

    if re.search(pattern, root.filename):
        fileDate = ''.join(re.findall(pattern, root.filename))
        fileDate = datetime.strptime(fileDate, '%Y-%m-%d').date()
        fileDate = fileDate.strftime('%m/%d/%Y')
        dfo['Date'] = fileDate
        dfi['Date'] = fileDate
    else:
        dfo['Date'] = ''
        dfi['Date'] = ''

    dfo['REGION CELULAR'] = dfo['REGION CELULAR'].apply(lambda r: int(str(r)[:1]))
    dfi['REGION CELULAR'] = dfi['REGION CELULAR'].apply(lambda r: int(str(r)[:1]))

    rename = {
        'CS POOL': "CS_Pool",
        'PS POOL': "PS_Pool",
        'REGION CELULAR': "Region_Cellular",
        'Name_List': "NE_Name_List",
        'Vendor_List': "NE_Vendor_List",
    }

    dfi.rename(columns=rename, inplace=True)
    dfo.rename(columns=rename, inplace=True)

    order = [
        "Date",
        "AT&T_Site_Name",
        "AT&T_Tech",
        "State",
        "Country",
        "Region",
        "Vendor",
        "Region_Cellular",
        "CS_Pool",
        "PS_Pool",
        "NE_Name_List",
        "NE_Vendor_List",
        "Type",
    ]

    dfi = dfi[order]
    dfo = dfo[order]

    df = pd.concat([dfo,dfi])
    df = df.drop_duplicates()

    dir = os.path.dirname(root.filename)

    df.to_excel(dir + '/output.xlsx', sheet_name='EPT', index=False)

    messagebox.showinfo(title='File Processed',
                message=f'Yout file is processed on {dir}/output.xlsx')
    

def loadFile():

    if option.get() == 1:
        processFile()
    elif option.get() == 2:
        processMun()

selectFile()

def mapName(vendor):
    result = []
    if 'H' in vendor:
        result.append('Huawei')
    if 'S' in vendor:
        result.append('Samsung')
    if 'N' in vendor:
        result.append('Nokia')
    return ','.join(result)

root.mainloop()
