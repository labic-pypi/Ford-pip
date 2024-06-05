#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains the function for identifying
the gender of a given name string, optimized to portuguese.

Based on the Perl script available at:
    http://search.cpan.org/~kcarnut/Lingua-PT-Gender-1.03/Gender.pm
'''

import re
# import unicodedata
# from unidecode import unidecode

def gender_identify(name):
    '''
    Try and identify name gender.
    '''
    # name = unicode(name,"utf-8")
    # name = unidecode(name).lower()
    #nameRGX = re.compile(name)   quase certeza que mão serve pra nada mas não me lembro
    n = name.split()
    out = 'F'

    if (n[0][-1] == """a""") :
           out = 'F'

           if(re.search("""wilba$|rba$|vica$|milca$|meida$|randa$|uda$|
            rrea$|afa$|^ha$|cha$|oha$|apha$|natha$|^elia$|rdelia$|
            remia$|aja$|rja$|aka$|kka$|^ala$|gla$|tila$|vila$|cola$|
            orla$|nama$|yama$|inima$|jalma$|nma$|urma$|zuma$|gna$|
            tanna$|pna$|moa$|jara$|tara$|guara$|beira$|veira$|ira$|
            uira$|pra$|jura$|mura$|tura$|asa$|assa$|ussa$|^iata$|
            onata$|irata$|leta$|preta$|jota$|ista$|aua$|dua$|hua$|
            qua$|ava$|dva$|^iva$|silva$|ova$|rva$|wa$|naya$|ouza$""",n[0])):
                        out = 'M'

    elif (n[0][-1] == """b""") :
        out = 'M'
        if (re.search("""inadab$""",n[0])) :
                out = 'F'

    elif (n[0][-1] == """c""") :
        out = 'M'
        if( re.search("""lic$|tic$""",n[0])) :
            out = 'F'

    elif (n[0][-1] == """d""") :
        out = 'M'
        if( re.search("""edad$|rid$""",n[0])) :
            out = 'F'

    elif (n[0][-1] == """e""") :
        out=0
        if( re.search("""dae$|jae$|kae$|oabe$|ube$|lace$|dece$|
                        felice$|urice$|nce$|bruce$|dade$|bede$|
                        ^ide$|^aide$|taide$|cide$|alide$|vide$|
                        alde$|hilde$|asenilde$|nde$|ode$|lee$|
                        ^ge$|ege$|oge$|rge$|uge$|phe$|bie$|
                        elie$|llie$|nie$|je$|eke$|ike$|olke$|
                        nke$|oke$|ske$|uke$|tale$|uale$|vale$|
                        cle$|rdele$|gele$|tiele$|nele$|ssele$|
                        uele$|hle$|tabile$|lile$|rile$|delle$|
                        ole$|yle$|ame$|aeme$|deme$|ime$|lme$|
                        rme$|sme$|ume$|yme$|phane$|nane$|ivane$|
                        alvane$|elvane$|gilvane$|ovane$|dene$|
                        ociene$|tiene$|gilene$|uslene$|^rene$|
                        vaine$|waine$|aldine$|udine$|mine$|
                        nine$|oine$|rtine$|vanne$|renne$|hnne$|
                        ionne$|cone$|done$|eone$|fone$|ecione$|
                        alcione$|edione$|hione$|jone$|rone$|
                        tone$|rne$|une$|ioe$|noe$|epe$|ipe$|
                        ope$|ppe$|ype$|sare$|bre$|dre$|bere$|
                        dere$|fre$|aire$|hire$|ore$|rre$|tre$|
                        dse$|ese$|geise$|wilse$|jose$|rse$|
                        esse$|usse$|use$|aete$|waldete$|iodete$|
                        sdete$|aiete$|nisete$|ezete$|nizete$|
                        dedite$|uite$|lte$|ante$|ente$|arte$|
                        laerte$|herte$|ierte$|reste$|aue$|
                        gue$|oue$|aque$|eque$|aique$|inique$|
                        rique$|lque$|oque$|rque$|esue$|osue$|
                        ozue$|tave$|ive$|ove$|we$|ye$|^ze$|
                        aze$|eze$|uze$""",n[0])) :
            out = 'M'

    elif (n[0][-1] == """f""") :
        out = 'M'

    elif (n[0][-1] == """g""") :
        out = 'M'
        if( re.search("""eig$|heng$|mping$|bong$|jung$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """h""") :
        out = 'M'
        if( re.search("""kah$|nah$|rah$|sh$|beth$|reth$|seth$|
          lizeth$|rizeth$|^edith$|udith$|ruth$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """i""") :
        out = 'M'
        if( re.search("""elai$|anai$|onai$|abi$|djaci$|glaci$|
                        maraci$|^iraci$|diraci$|loraci$|ildeci$|
                        ^neci$|aici$|arici$|^elci$|nci$|oci$|
                        uci$|kadi$|leidi$|ridi$|hudi$|hirlei$|
                        sirlei$|^mei$|rinei$|ahi$|^ji$|iki$|
                        isuki$|^yuki$|gali$|rali$|ngeli$|ieli$|
                        keli$|leli$|neli$|seli$|ueli$|veli$|
                        zeli$|ili$|helli$|kelli$|arli$|wanderli$|
                        hami$|iemi$|oemi$|romi$|tmi$|ssumi$|
                        yumi$|zumi$|bani$|iani$|irani$|sani$|
                        tani$|luani$|^vani$|^ivani$|ilvani$|
                        yani$|^eni$|ceni$|geni$|leni$|ureni$|
                        ^oseni$|veni$|zeni$|cini$|eini$|lini$|
                        jenni$|moni$|uni$|mari$|veri$|hri$|
                        aori$|ayuri$|lsi$|rsi$|gessi$|roti$|
                        sti$|retti$|uetti$|aui$|iavi$|^zi$|
                        zazi$|suzi$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """j""") :
        out = 'M'

    elif (n[0][-1] == """k""") :
        out = 'M'
        if( re.search("""nak$|lk$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """l""") :
        out = 'M'
        if( re.search("""mal$|^bel$|mabel$|rabel$|sabel$|zabel$|
                        achel$|thel$|quel$|gail$|lenil$|mell$|
                        ol$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """m""") :
        out = 'M'
        if( re.search("""liliam$|riam$|viam$|miram$|eem$|uelem$|
                        mem$|rem$|mim""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """n""") :
        out = 'M'
        if( re.search("""lilian$|lillian$|marian$|irian$|yrian$|
                        ivian$|elan$|rilan$|usan$|nivan$|arivan$|
                        iryan$|uzan$|ohen$|cken$|elen$|llen$|
                        men$|aren$|sten$|rlein$|kelin$|velin$|
                        smin$|rin$|istin$|rstin$|^ann$|ynn$|
                        haron$|kun$|sun$|yn$|min""",n[0])) :
            out = 'F'

    elif (n[0][-1] == """o""") :
        out = 'M'
        if( re.search("""eicao$|eco$|mico$|tico$|^do$|^ho$|
                        ocio$|ako$|eko$|keiko$|seiko$|chiko$|
                        shiko$|akiko$|ukiko$|miko$|riko$|tiko$|
                        oko$|ruko$|suko$|yuko$|izuko$|uelo$|
                        stano$|maurino$|orro$|jeto$|mento$|
                        luo$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """p""") :
        out = 'M'
        if( re.search("""yip$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """r""") :
        out = 'M'
        if( re.search("""lar$|lamar$|zamar$|ycimar$|idimar$|
                        eudimar$|olimar$|lsimar$|lzimar$|erismar$|
                        edinar$|iffer$|ifer$|ather$|sther$|
                        esper$|^ester$|madair$|eclair$|olair$|
                        ^nair$|glacir$|^nadir$|ledir$|^vanir$|
                        ^evanir$|^cenir$|elenir$|zenir$|ionir$|
                        fior$|eonor$|racyr$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """s""") :
        out = 'M'
        if( re.search("""unidas$|katias$|rces$|cedes$|oides$|
                        aildes$|derdes$|urdes$|leudes$|iudes$|
                        irges$|lkes$|geles$|elenes$|gnes$|
                        ^ines$|aines$|^dines$|rines$|pes$|
                        deres$|^mires$|amires$|ores$|neves$|
                        hais$|lais$|tais$|adis$|alis$|^elis$|
                        ilis$|llis$|ylis$|ldenis$|annis$|ois$|
                        aris$|^cris$|^iris$|miris$|siris$|
                        doris$|yris$|isis$|rtis$|zis$|heiros$|
                        dys$|inys$|rys$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """t""") :
        out = 'M'
        if( re.search("""bet$|ret$|^edit$|git$|est$|nett$|itt$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """u""") :
        out = 'M'
        if( re.search("""^du$|alu$|^miharu$|^su$""",n[0])) :
          out = 'F'

    elif (n[0][-1] == """v""") :
        out = 'M'

    elif (n[0][-1] == """w""") :
        out = 'M'

    elif (n[0][-1] == """x""") :
        out = 'M'

    elif (n[0][-1] == """y""") :
        out = 'M'
        if( re.search("""may$|anay$|ionay$|lacy$|^aracy$|^iracy$|
                        doracy$|vacy$|aricy$|oalcy$|ncy$|nercy$|
                        ucy$|lady$|hedy$|hirley$|raney$|gy$|
                        ahy$|rothy$|taly$|aely$|ucely$|gely$|
                        kely$|nely$|sely$|uely$|vely$|zely$|
                        aily$|rily$|elly$|marly$|mony$|tamy$|iany$|
                        irany$|sany$|uany$|lvany$|wany$|geny$|
                        leny$|ueny$|anny$|mary$|imery$|smery$|
                        iry$|rory$|isy$|osy$|usy$|ty$""",n[0])) :
            out = 'F'

    elif (n[0][-1] == """z""") :
        out = 'M'
        if( re.search("""^inez$|rinez$|derez$|liz$|riz$|uz$""",n[0])) :
          out = 'F'

    return out