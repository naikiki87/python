# EXCEPT = ["newly", "unrelated", "calls", "early", "surrounded", "despite", "the", "and", "a", "of", "for", "on", "in", "as", "by", 
# "at", "was", "to", "but", "were", "that", "this", "its", 
# "with", "which", "is", "an", "has", "had", "it", "from",
# "2017\t34,350\t4,240\t23,259\t54.99\t74,400"]

EXCEPT = ["newly", "unrelated", "calls", "early", "surrounded", "despite", "the", "and", "a", "of", "for", "on", "in", "as", "by", 
"at", "was", "to", "but", "were", "that", "this", "its", "with", "which", "is", "an", "has", "had", "it", "from",
"2017\t34,350\t4,240\t23,259\t54.99\t74,400", '', 'fell', 'between', 'public', 'fit', 'teaching', 'award', 'up','grew', 'counts', 
'class', 'limited', 'did', '2012\t23,331\t2,211\t15,465\t23.39', 'provided', 'overtime','add', 'siding', '2004', 'before', '2', 'addition', 'owned', 'popular', '5',
'declined', '85', 'receive', 'although', 'rise', 'received', '0.6', 'make', 'subsequently', 'studies', 'start', 'month', 'treats', 'groups', 'does', 'vice', 'allows', 
'direct', '2008\t18,627\t1,883\t12,443\t13.05', 'because', 'together', 
'specifically', 'following', 'effectively', 'settled', 'days', 'amongst', '$437,500', 'countered', 'any', 'directly', 'inadequate', 'annual', '700', 'survey', 'two', 'spoken', 'divesting',
'associated', 'times', 'everyday', '12', 'interest', 'november', 'thicker', 'able', 'special', 'taking', '30', 'environmental', 'treatment', 'prevent', '1980s', 'first', 'weight', 'also', 'january',
"1's", 'print', 'listed', 'done', 'would', 'create', 'imagery', 'when', 'changes;', 'countries', 'particularly', 'ensure', 'dubbed', 'like', 'decreased', 'called', 'due', 'plus', 
'2015\t30,601\t3,273\t21,597\t53.18\t62,600', 'dischord', '2009\t19,176\t1,487\t13,250\t12.14', 'out', 'going', 'operated', "didn't", 'say', 'come', 
'might', 'per', '2018\t36,397\t1,933\t22,536\t72.63\t73,100', 'about', 'still',
'over', 'range', 'all', 'came',  'use', 'under', 'he', 'through', 'saying', 'build', 'featured', 'proved', 'him', '2007\t16,326\t1,492\t10,688\t12.14',
'dispute', 'including', 'around', 'inc', 'while', 'hired', '27%', 'exception', '2005\t13,740\t1,212\t8,794\t8.75', 'generates', 'their', 'another', 'saw', 'bought', 'every',
'yet', 'focusing', 'into', 'maintaining', 'move', 'others','them', '2006\t14,955\t1,392\t9,870\t9.01','own', 'can','puts', 'been', 'we’ve','increase', 'i',
'significant', 'replace',
'produced','used','well','many','heavily','we','useful','previous',"texas's",'effected','briefly','debuted','give','full', 'ties', 'down','push','according', 
'set', '$20,000', 'crop','instead', 'seventh','my',
'quickly','shown', 'further','are','agreed','worn', "users'", 'typically','known', 'usd\temployees', '$190,373', '2006','stopped', '–', 'currently','initially', 'formed',
'stepped','me','(of', 'input','ended', 'improve','since','asked','considered','continue','based','distinct', 'within','just','how','describe','throughout','partnership',
'removed', '(not', 'true', 'suspended','(nke)', 'withdrawn','2010\t19,014\t1,907\t14,419\t16.80', 'unincorporated', '1971–78','well)','upon','36%', 'upcoming','today',
'quarterly', 'remove', 'succeeded', 'sued', 'other', "nike's", '2014\t27,799\t2,693\t18,594\t38.56\t56,500', 'next', '(learn', '2014', 'who', 'faced', 'executed', 
'extended', 'rare', 'recent','least','unlike',
'along','ii','so', 'several','(known','highly','especially','be',
'ltd', 'new','remained','2013\t25,313\t2,472\t17,545\t30.50\t48,000','dollars)','either',
'more','no','go','nearly','uses','away', 'shows', 'praised', '2011\t20,117\t2,133\t14,998\t19.82', 'became','where', '(out', 'meant','contains','during','expected','followed', 
'now', 'only', 'usd\tprice', 'his', "let's", 'paid', '(which', 'end', 'created','even', 'cut', 'b', 'themselves','often','via','becoming', 'some','after','these','please',
'available','message)','eventually', 'most','(brs)', 'among', 'biggest',
'include', 'went',
'extremely','typical','2016\t32,376\t3,760\t21,379\t54.80\t70,700', 'become','said','both','not','gave','began','could','may','too',
'however','such','will','there','then',"don't",'if','or','amid','what','against','sequentially',
'being','ever','mostly','towards','they','j','must',
'those','sold','giving','much','than','includes','given','etc', 'usd\ttotal']


import networkx as nx
## generate Graph G
G = nx.Graph()

SUBJECT = "NIKE_TEST"

filename = SUBJECT + ".txt"
file = open(filename, 'r', encoding='utf8')
s = file.read()
data = s.split('\n')

pre = ''
cur = ''
no_in = 0

for i in range(len(data)) :
    words = data[i].split(' ')
    if words[0] == '' :
        a = 1
    else :
        for j in range(len(words)) :
            words[j] = words[j].strip()         # 공백 제거

            if '[' in words[j] :
                t = words[j].index('[')
                words[j] = words[j][0:t]

            if ']' in words[j] :
                for k in range(len(words[j])) :
                    if words[j][k] == '[' :
                        words[j] = words[j][0:k]
                        break
                    
                    if k == (len(words[j]) - 1) :
                        no_in = 1
                
                if no_in == 1 :
                    no_in = 0
                    continue

            words[j] = words[j].lower()         # make lower character
            words[j] = words[j].strip(',."?!:')         # 공백 제거

            if words[j] in EXCEPT :
                continue
            else :
                G.add_node(words[j])                # add node

                if cur != '' :
                    G.add_edge(cur, words[j])
                    cur = words[j]
                else :
                    cur = words[j]


print("info : ", nx.info(G))