function where username=%s"
        val = (client_user)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        print(mycursor.rowcount)
        if int(mycursor.rowcount) == 1:
           return "Already Liked"
        else:
            sql = "INSERT INTO like_function (like_user, status, post_id) VALUES (%s, %s, %s)"
            val = (client_user, 1, post_id)
            mycursor.execute(sql, val)
            mydb.commit()
            return 'hello1'