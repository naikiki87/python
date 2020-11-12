for i in range(4) : 
    sel_query = "t1.tid"
    gb_query = "GROUP BY t1.iid"
    join_query = ''
    if i == 0 :
        where_query = ''
    elif i >= 1 :
        where_query = "WHERE"
    for j in range(1, i+1, 1) :
        join_query = join_query + "JOIN testdata t" + str(j+1) + " ON t" + str(j+1) + ".tid = t" + str(j) + ".tid "
        where_query = where_query + " t" + str(j+1) + ".iid > t" + str(j) + ".iid AND"
        sel_query = sel_query + ", t" + str(j+1) + ".tid"
        gb_query = gb_query + ", t" + str(j+1) + ".iid"

    if i >= 1 :
        where_query = where_query[0:len(where_query) - 3]       ## 마지막에 AND 문자열 제거

    total_query = "SELECT " + sel_query + ", COUNT(DISTINCT t1.uid) FROM testdata t1 " + join_query + where_query + gb_query

    print(i, ' : ', total_query)