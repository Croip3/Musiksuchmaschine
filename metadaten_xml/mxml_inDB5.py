import mysql.connector
import re
from music21 import *




#Verbindung zum Server
mydb = mysql.connector.connect(
        host="localhost",
        user="MusikDBNutzer",
        password="test",
        database="musiksuchmaschine"
    )
#öffnet xml oder mxml und wandelt es in einen music21 Stream

files=["1Certon-A_ce_matin.mxl",
"1Chap-fear.mxl",
"1Compere-Va-t-en,_regret.mxl",
"1Fair,_if_you_expect_admiring.mxl",
"1Farewell,_my_joy.mxl",
"1Farewell_disdainful_Morley.mxl",
"1Fear_no_more_MacFarren.mxl",
"1Fr.Caccini-E_tra_i_pomi.mxl",
"1Giovannelli-Va_canzonetta_humile.mxl",
"1Marenzio-La_farfalla.mxl",
"1Nh_ZöllnerKH_Psalm121.mxl",]

#bildet eine Liste mit allen Künstlern und ihren IDs
mycursor = mydb.cursor()
sql = "SELECT * FROM kuenstler"
#val = (varComposer,)
mycursor.execute(sql,)
artistList = mycursor.fetchall()
artistList = str(artistList)

#bildet eine Liste mit allen Musikstücken für Vergleich
#in Zukunft URL vielleicht besser 
mycursor = mydb.cursor()
sql = "SELECT * FROM musikstueck"
#val = (varComposer,)
mycursor.execute(sql,)
musikstuecktList = mycursor.fetchall()
musikstuecktList = str(musikstuecktList)





for file in files:
    score = converter.parse(file)

#das Stream Objekt verfügt über Metadaten print nur für den fall von fehlern als kontrolle
#https://web.mit.edu/music21/doc/moduleReference/moduleMetadata.html?#module-music21.metadata
#print(score.metadata.title)
#print(score.metadata.composer)
#print(score.metadata.date)
#print(score.metadata.all())
#print(score.duration)

#einzelen Variablen mit den entsprechenden Metadaten befüllen
    varTitle = score.metadata.title
    varComposer = score.metadata.composer
    varSonstiges = score.metadata.all()
    varSonstiges = str(varSonstiges)

#secondsMap zeigt alles an, was in Sekdunen angegeben wurde
#print(score.secondsMap)

# zeigt alles an, was irgendwie mit dem Tempo zu tun hat
#print(score.metronomeMarkBoundaries())
#print(varTitle)



#trägt Komponisten in DB ein, wenn sie nicht schon da sind
    if varComposer != None and varComposer not in artistList:
        mycursor = mydb.cursor()
        sql = "INSERT INTO kuenstler (ID, Name) VALUES (NULL, %s)"
        val = (varComposer,)
        mycursor.execute(sql, val,)
        mydb.commit()

    # findet ID des Kuenstlers des aktuellen Stückes heraus
    #funktioniert noch nicht so ganz, weil er einen Touple rauswirft
    if varTitle != None:
        mycursor = mydb.cursor()
        sql = "SELECT ID FROM kuenstler WHERE Name = %s"
        val = (varComposer,)
        mycursor.execute(sql, val, )
        myresult = mycursor.fetchall()
        #myresult = myresult(0) #hier statt String einfach nur auf Tupel zugreifen
        myresult = str(myresult) #wandelt den tupel in string
        #der nächste schritt entfernt alle, Kommas und Klammern des String, damit dieser in der DB keine Probleme
        #verursacht
        myresult = myresult.replace(',', '',).replace('(','').replace(')','').replace('[','').replace(']','')



    #Trägt Titel in DB ein sofern er nicht schon da ist
    #in zukünftiger Version lieber URL zum Vergleichen nehmen
    if varTitle != None and varTitle not in musikstuecktList:
        mycursor = mydb.cursor()
        sql = "INSERT INTO musikstueck (ID,Name,Kuenstler_ID, Sonstiges) VALUES (Null, %s, %s, %s)"
        val = (varTitle,myresult, varSonstiges)
        mycursor.execute(sql, val,)
        mydb.commit()

    #wie regeln wir es, dass Künstler nicht doppelt eingetragen werden?
    #BPM, Länge 











