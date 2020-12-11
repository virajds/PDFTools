# -*- coding: utf-8 -*- 

import matplotlib
matplotlib.use('Agg')

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

from operator import itemgetter

import pdfminer
import re
import matplotlib.pyplot as plt
from matplotlib import patches
import argparse
import os
import shutil
import sys
import time


def extract_layout_by_page(pdf_path):
    """
    Extracts LTPage objects from a pdf file.
    """
    laparams = LAParams()

    fp = open(pdf_path, 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)

    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    rsrcmgr = PDFResourceManager()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    layouts = []
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        layouts.append(device.get_result())

    return layouts

TEXT_ELEMENTS = [
    pdfminer.layout.LTTextBox,
    pdfminer.layout.LTTextBoxHorizontal,
    pdfminer.layout.LTTextLine,
    pdfminer.layout.LTTextLineHorizontal
]

def flatten(lst):
    """Flattens a list of lists"""
    return [subelem for elem in lst for subelem in elem]


def extract_characters(element):
    """
    Recursively extracts individual characters from 
    text elements. 
    """
    if isinstance(element, pdfminer.layout.LTChar):
        return [element]

    if any(isinstance(element, i) for i in TEXT_ELEMENTS):
        return flatten([extract_characters(e) for e in element])

    if isinstance(element, list):
        return flatten([extract_characters(l) for l in element])

    return []


def draw_rect_bbox(coordinates, ax, color):
    """
    Draws an unfilled rectable onto ax.
    """
    (x0, y0, x1, y1) = coordinates
    ax.add_patch( 
        patches.Rectangle(
            (x0, y0),
            x1 - x0,
            y1 - y0,
            fill=False,
            color=color
        )    
    )

def print_text(x0,y0, plt, num):
    plt.text(x0, y0, num, fontsize=6)
    
def draw_rect(rect, ax, color="black"):
    draw_rect_bbox(rect.bbox, ax, color)

#global variables
tminx = 10000
tminy = 10000
tmaxx = 0
tmaxy = 0

results_dir = "results"
csv_dir = "csv_files"
json_dir = "./json"

f1 = open('./output.txt', 'w')
#########

def minmax_cal(rt):
    global tminx, tminy, tmaxx, tmaxy
    if rt.x0<tminx:
        tminx = rt.x0
    if rt.y0<tminy:
        tminy = rt.y0
    if rt.x1>tmaxx:
        tmaxx = rt.x1
    if rt.y1>tmaxy:
        tmaxy = rt.y1

def is_inside(rt):
    global tminx, tminy, tmaxx, tmaxy
    if (rt.x0>=tminx and rt.y0>=tminy and rt.x1<=tmaxx and rt.y1<=tmaxy):
        return True
    if (rt.x0>=tminx and rt.y0>=tminy and rt.x0<=tmaxx and rt.y0<=tmaxy):
        return True
    if (rt.x1>=tminx and rt.y1>=tminy and rt.x1<=tmaxx and rt.y1<=tmaxy):
        return True
    return False

def is_inside_box(boxx, rt):
    
    if (rt.x0>=boxx[0] and rt.y0>=boxx[1] and rt.x1<=boxx[2] and rt.y1<=boxx[3]):
        return True
    if (rt.x0>=boxx[0] and rt.y0>=boxx[1] and rt.x0<=boxx[2] and rt.y0<=boxx[3]):
        return True
    if (rt.x1>=boxx[0] and rt.y1>=boxx[1] and rt.x1<=boxx[2] and rt.y1<=boxx[3]):
        return True
    return False

def merge_bbox(coordinates1, coordinates2):
    (p0, q0, r1, s1) = coordinates1
    (x0, y0, x1, y1) = coordinates2
    return min(p0, x0), min(q0, y0), max(r1, x1), max(s1, y1)

def is_number_box(bx):
    strall = bx.get_text()
    if len(strall)<1:
        return False
    if bx.x1-bx.x0>200:# some long lenth boxes for bullet no etc.
        return False

    words = strall.split('\n')
    
    #todo: check for character  
    ustr = u"—"
    truecount, falsecount = 0, 0
    for word in words:
        if (len(word)>0):
            if ( re.match(u"^(?=.*\d)[0-9\s,.(){}\[\]\-%$mbn\/\—]+$", word) or re.match(u"^[\s—]+$", word)):
                truecount += 1
            else:
                falsecount += 1
        
    if (truecount>=falsecount):
        return True
    
    return False

def jsonWrite(inputAr, colCount, filename):
    tbheaders = []
    for i in range(colCount):
        tbheaders.append("")

    f1 = open(filename, 'w') 
    #print("Col count : " + str(colCount))
    isEmptyRow = False
    col1Text = ""
    addPreviousLeftCol = False
    prevCol1Text = ""
    for lineStr in inputAr:
        #print(lineStr)
        words = lineStr.split("|")
        j=0
        isHeader = True
        jsonLine = ""
        
        for word in words:
            #print("j="+ str(j)+ " :"+word+".")           
                
            if j==0: #check the header if first column of row is empty
                if len(word)==0: #header row
                    isHeader = True
                else:
                    isHeader = False
                    col1Text = word
            else: #check empty line
                if len(word)>0:
                    isEmptyRow = False
                    col1Text = ""
                else:
                    isEmptyRow = True                    

            if (isHeader and (j!=0) ):
                tbheaders[j] += " " + word
            else:
                if j==0:
                    if addPreviousLeftCol:
                        word = prevCol1Text + " " + word
                        addPreviousLeftCol = False
                        #print(" Add previous- "+word)
                    jsonLine = "\"" + word + "\" :{ "
                else:
                    jsonLine += "\"" + tbheaders[j] + "\" : \"" + word + "\" , "
            j += 1
        jsonLine += "}"

         #check if previous is empty raw then appen left column
        if (isEmptyRow):
            #word = col1Text + " " + word
            #print('Empty row - '+ col1Text)
            addPreviousLeftCol = True
            prevCol1Text = col1Text

        if ((not isHeader) and (not isEmptyRow)):
            f1.write(jsonLine + "\n")#print(jsonLine)    
    f1.close()

def sort2rows(tbltexts, pageno, tbleno):
    #set column, row order
    #assume we get top,left always first
    if tbltexts:
        
        col1x0, col1y0, col1x1, col1y1 = 0, 0, 999, 0        
        col2x0, col2y0, col2x1, col2y1 = 0, 0, 999, 0        
        col3x0, col3y0, col3x1, col3y1 = 0, 0, 999, 0

        newlist = tbltexts[:]
        
        #find the left most textbox. past this to function. dont calculate in here
        #todo
        leftrect = tbltexts[0]
        for tb in tbltexts:
            if tb.x0<leftrect.x0:
                leftrect = tb
        
        col1x1 = leftrect.x1
        color = ['green','blue']
        index = 1
        tabledata = []
        tablerowpos = []

        while len(newlist):
            
            leftcol = []
            rightcol = []
            #print(index)
            #print(len(newlist))
            #print(col1x1)
            rightmin = 999
            for tx in newlist:
              
                if tx.x0>col1x1:
                    #find right most box for next round
                    if (tx.x1<rightmin):
                        rightmin = tx.x1
                        #leftrect = tx
                    #print('col 2')
                    #print(tx)
                    rightcol.append(tx)
                else:
                    #print('col 1')
                    #print(tx)
                    leftcol.append(tx)
          
            # for ts in leftcol:
            #     draw_rect(ts, ax, color[index%2])
            index += 1
            col1x1 = rightmin
            newlist = rightcol[:]

            #sort column and add to table
            slist = sorted(leftcol, key=lambda x: x.y0, reverse=True)
            
            #divid into rows
            rowlst = []                        
            lineTxt = ""
            isFirstCh = True
            
            #get the text line by line
            for line in slist:
                words = line.get_text().split('\n')
                
                #print(words)
                for word in words:
                    if (len(word)>0):
                        rowlst.append(word) 

            #rowlst.append(lineTxt)    
            tabledata.append(rowlst)

            #find the row position of each line by looking at character postions
            columchrs = extract_characters(slist)
            rowpos = []
            lineY = 1000
            for ch in columchrs:
                x = int(round(ch.y0))
                if lineY-x>4:#x<lineY: #new row
                    rowpos.append(x)
                lineY = x
            
            tablerowpos.append(rowpos)
            #break
        
        noofcols = index-1
        #merge columns to row number
        #find rows top to bottom. top y has max value
        #print("sort rows ...")
        tabledata2 = tabledata[:]

        #write table to file        
        filename = csv_dir + '/page'+ str(pageno) + '-'+ str(tbleno)+'.csv'
        f2 = open(filename, 'w')  

        tablejsoninput = []
        while True:
            rowstr = ""
            toprowlst = []
            for rowy in tablerowpos:
                if (len(rowy)):
                    toprowlst.append(rowy[0])
            toprow = max(toprowlst)
            #print(toprow)
            for x in range(0, noofcols):
                if (len(tablerowpos[x]) and (toprow-tablerowpos[x][0]<4) ):
                    val = tablerowpos[x].pop(0)
                    try:
                        valstr = tabledata2[x].pop(0)
                        rowstr += valstr.encode('utf-8')+"|"
                    except:
                        print("Fix this!")
                else:
                    rowstr += "|"                    
            #print(rowstr)
            f2.write(rowstr + "\n")
            rowstr = rowstr[:-1] # remove last  |
            tablejsoninput.append(rowstr)

            #check if atleast one column data exist
            isCont = False
            for rowy2 in tablerowpos:
                if (len(rowy2)):
                    isCont = True
            if not isCont:
                break
        f2.close()
        #make json
        jsonfilename = json_dir + '/page'+ str(pageno) + '-'+ str(tbleno)+'.json'
        jsonWrite(tablejsoninput, noofcols, jsonfilename)

        return '&nbsp;<a href="' + filename + '">csv</a>&nbsp; and &nbsp;' + '<a href="' + jsonfilename+ '">json</a>&nbsp;&nbsp;'

def find_table_in_page(page, pno):
    numtexts = []
    rects = []
    lines = []
    textstr = []    
    pagenos = []       
    numTextCount, lineCount = 0, 0
    isLandscape = False
    page_link = ''

    global tminx
    global tminy
    global tmaxx
    global tmaxy
    tminx, tminy, tmaxx, tmaxy =1000, 1000, 0, 0
   

    xmin, ymin, xmax, ymax = page.bbox
    size = 12
    print(xmin, ymin, xmax, ymax)

    f1.write("page no " + str(pno) + " *************************\r\n")
    f1.write("page size " + str(page.bbox) + "\r\n")

    if (xmax>ymax):
        print("landscape page.")
        isLandscape = True
        #return
    
    #1. first find number text boxes and rectangles/lines.
    # seperate text and rectangle elements
    pnum = 0
    for e in page:
        pnum += 1
        area = (e.x1-e.x0) * (e.y1-e.y0)
        if isinstance(e, pdfminer.layout.LTTextBoxHorizontal):
            strall = e.get_text()
            #todo: check for character  
            ustr = u"—"
            if is_number_box(e):#( re.match(u"^(?=.*\d)[0-9\s,.(){}\[\]\-%\$mbn\—]+$", strall) ):
                #minmax_cal(e) # calculate only numeric text boxes                
                # if (e.y0<80 or e.y1>ymax-80 or e.x1<80):# and e.y1-e.y0<30: #check page no textbox, left side line no
                #     pagenos.append(e)
                #     f1.write( "page no box: "+ str(e.bbox) + ": "+ e.get_text().encode('utf-8') + "\r\n")
                # else:
                numtexts.append(e)
                numTextCount += 1
                f1.write( "num box: "+ str(e.bbox) + ": "+ e.get_text().encode('utf-8') +"\r\n")# 
            else:
                textstr.append(e)
                
        elif isinstance(e, pdfminer.layout.LTRect) or isinstance(e, pdfminer.layout.LTLine):
            #filter out page borders
            if (e.x0<100 and e.y0<100 and e.x1>xmax-100 and e.y1>ymax-100):#full page border
                continue        
            if e.y0>ymax-100 and e.y1>ymax-100:#top horizontal line
                continue
            
            rects.append(e)
            #minmax_cal(e)
            lineCount += 1
   

    #add text only text boxes which are left to number text boxes. we dont wont to miss left columns of table

    #remove any numbers only text box which stands alone in a row. get rid of page number
    
    alltexts = numtexts + textstr
    #do something
    tabletexts = []
    tabletexts = numtexts

    numtextboxes = []
    for nbs in numtexts:
        numtextboxes.append(nbs.bbox)

    #merege number boxes to columns
    i = 0
    isDone = False
    colboxlist = []
    colm = []
    while not isDone and len(numtextboxes)>0:
        if i==0:
            initLen = len(numtextboxes)
            #f1.write("box count 1 - "+ str(len(numtextboxes))+ "\r\n")
        nb = numtextboxes[i]
        
        
        j = i + 1
        doNext = True
        #f1.write("Round " + str(i)+ "\r\n")
        while doNext and j<len(numtextboxes):
            nb2 = numtextboxes[j]
            
            #check same vertical line
            midx = (nb2[0]+ nb2[2])/2
            midx2 = (nb[0]+ nb[2])/2
            #f1.write("box 1 - "+ str(nb) + " box 2 - "+ str(nb2)+ " Mid - " +str(midx) + "\r\n")
            if (midx>nb[0]  and midx<nb[2]) or (midx2>nb2[0]  and midx2<nb2[2]):
                #check gap is close to merge 
                if abs(nb[1]-nb2[3])<30 or abs(nb2[1]-nb[3])<30:
                    #we got a merge!
                    #f1.write("Merge found!"+ "\r\n")
                    colm.append(merge_bbox(nb, nb2))
                    #merge boxes
                    #remove the merge box from list
                    del numtextboxes[j]
                    doNext = False
            j +=1
            if j>=len(numtextboxes):
                break
                        
        if doNext:
            #no merge happens
            colm.append(nb)
        

        i += 1
        if i>=len(numtextboxes):
            #check if no merge happens we are done.
            #f1.write("box count colm - "+ str(len(colm))+ "\r\n")
            if initLen==len(colm):
                #f1.write("break ! \r\n")
                colboxlist = colm[:]
                break
            numtextboxes = colm[:]
            del colm[:]
            i = 0
            

    if len(colboxlist)<0:
        return

    colboxlistCpy = colboxlist[:]
    #merge header text boxes
    textboxrects = []
    for ts in textstr:
        textboxrects.append(ts.bbox)

    i = 0
    isDone = False
    colboxlistfinal = []
    del colm[:] #colm = []
    while not isDone and len(colboxlistCpy)>0:
        if i==0:
            initLen = len(textboxrects)
            #f1.write("box count 1 - "+ str(len(textboxrects))+ "\r\n")
        nb = colboxlistCpy[i]
        
        
        j = i + 1
        doNext = True
        #f1.write("Round " + str(i)+ "\r\n")
        while doNext and j<len(textboxrects):
            nb2 = textboxrects[j]
            
            #check same vertical line
            midx = (nb2[0]+ nb2[2])/2
            #midx2 = (nb[0]+ nb[2])/2
            #f1.write("box 1 - "+ str(nb) + " box 2 - "+ str(nb2)+ " Mid - " +str(midx) + "\r\n")
            #  and get of rid of large boxes. less than twice the width of numbe box
            if (nb2[2]-nb2[0]<(nb[2]-nb[0])*2):
                if (midx>nb[0]  and midx<nb[2]):             
                    #check gap is close to merge 
                    if abs(nb[1]-nb2[3])<30 or abs(nb2[1]-nb[3])<30:
                        #we got a merge!
                        #f1.write("Merge found!"+ "\r\n")
                        colm.append(merge_bbox(nb, nb2))
                        #merge boxes
                        #remove the merge box from list
                        del textboxrects[j]
                        #del colboxlistCpy[i]
                    
                        doNext = False
            j +=1
            if j>=len(textboxrects):
                break
                        
        if doNext:
            #no merge happens
            colm.append(nb)
        

        i += 1
        if i>=len(colboxlistCpy):
            #check if no merge happens we are done.
            #f1.write("box count colm - "+ str(len(colm))+ "\r\n")
            if initLen==len(textboxrects):
                #f1.write("break ! \r\n")
                colboxlistfinal = colm[:]
                break
            colboxlistCpy = colm[:]
            del colm[:]
            i = 0

    #group number boxes to tables
    colboxlistfinalCpy = colboxlistfinal[:]
    tmpTable = []
    
    isCont = True
    while isCont:
        isMerge = False
        initLen = len(colboxlistfinalCpy)
        i=0
        
        #for bx in colboxlistfinalCpy:
        while True and i<len(colboxlistfinalCpy):
            bx = colboxlistfinalCpy[i]
            #after merge simply add
            if isMerge:
                #f1.write("append \r\n")
                tmpTable.append(bx)
            else:         
                #for bx2 in colboxlistfinalCpy:
                j=i+1
                while True and j<len(colboxlistfinalCpy):
                    bx2 = colboxlistfinalCpy[j]
                    leny = bx[3]-bx[1]
                    leny2 = bx2[3]-bx2[1]
                    diffx = max(bx[0],bx2[0]) - min(bx[2],bx2[2])
                    #f1.write("boxes "+str(diffx)+ " "+str(bx) + " " + str(bx2) +" \r\n")
                    if leny<leny2:
                        midy = (bx[3]+bx[1])/2
                        if midy>bx2[1] and midy<bx2[3] and diffx<100:# and diffx<50
                            #merge
                            tmpTable.append(merge_bbox(bx, bx2))
                            del colboxlistfinalCpy[j]
                            #f1.write("merge 1 \r\n")
                            isMerge = True
                    else:
                        midy = (bx2[3]+bx2[1])/2
                        if midy>bx[1] and midy<bx[3]  and diffx<100:# and diffx<50
                            #merge
                            tmpTable.append(merge_bbox(bx, bx2))
                            del colboxlistfinalCpy[j]
                            #f1.write("merge 2 \r\n")
                            isMerge = True
                    j += 1                    
                    if isMerge:
                        #f1.write("break 3 ! \r\n")              
                        break
                    if j>=len(colboxlistfinalCpy):
                        #f1.write("break 0 ! \r\n")
                        break
            if not isMerge:
                tmpTable.append(bx)
            i += 1
            if i>=len(colboxlistfinalCpy):
                isMerge = False
                #f1.write("break 1 ! \r\n")
                break
        if (initLen==len(colboxlistfinalCpy)):
            #f1.write("break 2 ! \r\n")
            break
        colboxlistfinalCpy = tmpTable[:]
        del tmpTable[:]
        
    #find left most colum of tables
    #now we have the right side of tables in the page. lets find the left most column
    tableCompleted = []
    leftcoltextboxes = []
    
    for fx in colboxlistfinalCpy:
        tmpLeftBoxes = []
        for s in textstr:#check if textbox in left side 
            midxx = (s.y0+s.y1)/2
            if midxx>=fx[1] and midxx<=fx[3] and s.x1<fx[0]:
                tmpLeftBoxes.append(s)
        #remove multiple left side boxes. boxes not related to table
        tmpLeftBoxes2 = tmpLeftBoxes[:]
        for tb in tmpLeftBoxes:
            for tb2 in tmpLeftBoxes:
                if max(tb.x0, tb2.x0)>min(tb.x1, tb2.x1):
                    #remove left most
                    if tb.x0<tb2.x0:
                        try:
                            tmpLeftBoxes2.remove(tb)
                        except ValueError:
                            print("Item rem err")
                    else:
                        try:
                            tmpLeftBoxes2.remove(tb2)
                        except ValueError:
                            print("Item rem err")

        leftcoltextboxes.append(tmpLeftBoxes)
        if (len(tmpLeftBoxes2)>0):
            leftx = tmpLeftBoxes2[0].x0
            tableCompleted.append((leftx,fx[1],fx[2],fx[3]))
        else:
            tableCompleted.append(fx)
       
    tableboxes = []
    tableCompletedRemovedSmall = []
    htmllink = ''
    for tb in tableCompleted:
        #find rects inside
        if tb[2]-tb[0]>20 and tb[3]-tb[1]>20:# get rid of small boxes            
            index = 0
            for et in alltexts:
                if is_inside_box(tb, et):
                    tableboxes.append(et)
            #sort to rows
            htmllink += sort2rows(tableboxes, pno, i)
            tableCompletedRemovedSmall.append(tb)
            
        i += 1

    #dont save image if no table
    if len(tableCompletedRemovedSmall)==0:
        return ""

    #***************draw table*****************************************
    fig, ax = plt.subplots(figsize = (size, size * (ymax/xmax)))
    
    if isLandscape:
        fig, ax = plt.subplots(figsize = (size * (xmax/ymax), size))
        
    # for ix in colboxlistfinal:
    #     draw_rect_bbox(ix, ax, 'green')
    # for tr in textboxrects:
    #     draw_rect_bbox(tr, ax, 'yellow')
    for fx in tableCompleted:
        draw_rect_bbox(fx, ax, 'red')
    
  
    # for s in numtexts:#InTble2ndFilter
    #     draw_rect(s, ax, "blue")
   
    alltable = numtexts + tableboxes #numtextsInTble + textstrInTble2ndFilter
    characters = extract_characters(alltable) 
    for c in characters:#texts:#
        #draw_rect(c, ax, "blue")
        print_text(c.x0, c.y0, plt, c.get_text())


    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    #plt.show()
    try:
        path = results_dir + '/page' + str(pno) + '.png'
        plt.savefig(path)
        htmlfulllink = 'Page no -&nbsp;' + str(pno) + '&nbsp;<a href="' + path + '">page</a>&nbsp;' + htmllink
        fi.write(htmlfulllink+ '<br>\n')
    except:
        print("Unexpected error:", sys.exc_info()[0])

    
    plt.close(fig)
    fig.clf()
   
    return htmlfulllink #tableCompleted #return table boxes


#delete images, csv, json folders
dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'results')   
#create dir
if os.path.exists(filename):
    shutil.rmtree(filename)
time.sleep(5)
os.makedirs(filename)

filename = os.path.join(dir, 'csv_files')    
#create dir
if os.path.exists(filename):
    shutil.rmtree(filename)
time.sleep(5)
os.makedirs(filename)

filename = os.path.join(dir, 'json')    
#create dir
if os.path.exists(filename):
    shutil.rmtree(filename)
time.sleep(5)
os.makedirs(filename)      

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", required=True,
	help="path to pdf file")
ap.add_argument("-p", "--pageno", required=False,
	help="page no")
args = vars(ap.parse_args())

example_file = args["filename"]#"simple2.pdf"
page_no = args["pageno"]

page_layouts = extract_layout_by_page(example_file)
print(len(page_layouts))

pno = 1

filename = 'index.html'
fi = open(filename, 'w')  

for page_layout in page_layouts:
    objects_on_page = set(type(o) for o in page_layout)
    print(objects_on_page)
    linktext = find_table_in_page(page_layout, pno)
   
    pno += 1

# current_page = page_layouts[32]
# objects_on_page = set(type(o) for o in current_page)
# print objects_on_page
# tablerects = find_table_in_page(current_page, 32)
# sort2rows(tablerects)
f1.close()
fi.close()
