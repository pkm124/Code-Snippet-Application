from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
from datetime import datetime
import random
import textwrap

now = datetime.now()
formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1234",
  database="code_snippet"
)
mycursor = mydb.cursor()

app=Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login_option")
def login_option():
    return render_template("login_option.html")

@app.route("/admin_register", methods=["POST", "GET"])
def admin_register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        sql = "INSERT INTO admin_detail (username, email, password) VALUES (%s, %s, %s)"
        val = (username, email, password)
        mycursor.execute(sql, val)
        mydb.commit()
        if mycursor.rowcount == 1:
           return render_template("admin_login.html") 

    return render_template("admin_register.html")

@app.route("/admin_login", methods=["POST", "GET"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        sql = "select * from admin_detail where username=%s and password=%s"
        val = (username, password)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        print(mycursor.rowcount)
        if int(mycursor.rowcount) == 1:
           return redirect("admin_dashboard") 
        
    return render_template("admin_login.html")

@app.route("/admin_dashboard", methods=["POST", "GET"])
def admin_dashboard():
    mycursor.execute("SELECT grp_no, grp_name, grp_info FROM grp_detail")
    myresult = mycursor.fetchall()
    print(list(myresult))
    return render_template("admin_dashboard.html", myresult=list(myresult))

@app.route("/user_register", methods=["POST", "GET"])
def user_register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        sql = "INSERT INTO user_detail (username, email, password) VALUES (%s, %s, %s)"
        val = (username, email, password)
        mycursor.execute(sql, val)
        mydb.commit()
        if mycursor.rowcount == 1:
           return render_template("user_login.html") 

    return render_template("user_register.html")

@app.route("/user_login", methods=["POST", "GET"])
def user_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        global client_user
        client_user = username
        
        sql = "select * from user_detail where username=%s and password=%s"
        val = (username, password)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        print(mycursor.rowcount)
        if int(mycursor.rowcount) == 1:
           return redirect("index") 
        
    return render_template("user_login.html")

@app.route("/index", methods=["POST", "GET"])
def user_dashboard():
    mycursor.execute("SELECT post_heading, post_info, user_id, post_id FROM post_detail order by id DESC")
    myresult = mycursor.fetchall()
    print(list(myresult))

    myresult1 = []
    for i in list(myresult):
        myresult1.append(list(i)) 
    list(myresult).clear()
    myresult = myresult1

    code_str = []
    for i in list(myresult):
        code_str.append(i[1])
    print("-------------------------")
    print(code_str)
    formatted_code = []
    for i in code_str:
        lines = i.splitlines()
        formatted_code.append(textwrap.indent('\n'.join(lines), '    '))
        # exec(formatted_code[0])

    for i,j in zip(list(myresult), formatted_code):
        i[1] = j
    mycursor.execute("SELECT comment_content, comment_user, post_id FROM post_comment order by id DESC")
    comment_detail = mycursor.fetchall()
    print(list(comment_detail))

    mycursor.execute("SELECT post_id, sum(status) FROM like_function group by post_id")
    like_count = mycursor.fetchall()

    return render_template("index.html", myresult=list(myresult), comment_detail=list(comment_detail), like_count=list(like_count))

@app.route("/user_grp", methods=["POST", "GET"])
def user_grp():
    sql = "SELECT grp_no, grp_name FROM grp_detail where grp_mem_1=%s or grp_mem_2=%s or grp_mem_3=%s or grp_mem_4=%s"
    query = (client_user, client_user, client_user, client_user)
    mycursor.execute(sql, query)
    myresult = mycursor.fetchall()
    print(list(myresult))


    # mycursor.execute("SELECT comment_content, comment_user, post_id FROM post_comment")
    # comment_detail = mycursor.fetchall()
    # print(list(comment_detail))

    return render_template("user_grp.html", myresult=list(myresult))


@app.route("/post_snippet", methods=["POST", "GET"])
def post_snippet():
    if request.method == "POST":    
        post_heading = request.form.get("post_heading")
        post_snippet = request.form.get("post_snippet")
        post_id = str(random.randint(1000, 9999))
        sql = "INSERT INTO post_detail (user_id, post_heading, post_info, post_id) VALUES (%s, %s, %s, %s)"
        val = (client_user, post_heading, post_snippet, post_id)
        mycursor.execute(sql, val)
        mydb.commit()
        if mycursor.rowcount == 1:
           return redirect("index") 
    return redirect("index")

@app.route("/comment_post", methods=["POST", "GET"])
def comment_post():
    if request.method == "POST":    
        post_id = request.form.get("post_id")
        post_comment = request.form.get("post_comment")
        comment_id = str(random.randint(1000, 9999))
        sql = "INSERT INTO post_comment (comment_id, comment_content, comment_user, post_id) VALUES (%s, %s, %s, %s)"
        val = (comment_id, post_comment, client_user, post_id)
        mycursor.execute(sql, val)
        mydb.commit()
        if mycursor.rowcount == 1:
           return redirect("index") 
    return redirect("index")

@app.route("/like_form", methods=["POST", "GET"])
def like_form():
    if request.method == "POST":    
        post_id = request.form.get("post_id")
        print(post_id)

        sql = "select * from like_function where like_user=%s and post_id=%s"
        val = (client_user, post_id)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        print(myresult)
        if int(mycursor.rowcount) == 1:

            check = "select status from like_function where like_user=%s and post_id=%s"
            val_check = (client_user, post_id)
            mycursor.execute(check, val_check)
            myresult = list(mycursor.fetchall())

            if myresult[0][0] == 1:
                sql = "UPDATE like_function SET status=%s WHERE like_user=%s and post_id=%s"
                val = (0, client_user, post_id)
                mycursor.execute(sql, val)
                mydb.commit()
                # return "Already Liked"
            else:
                sql = "UPDATE like_function SET status=%s WHERE like_user=%s and post_id=%s"
                val = (1, client_user, post_id)
                mycursor.execute(sql, val)
                mydb.commit()
                # return "Disliked"
        else:
            sql = "INSERT INTO like_function (like_user, status, post_id) VALUES (%s, %s, %s)"
            val = (client_user, 1, post_id)
            mycursor.execute(sql, val)
            mydb.commit()
            # return 'hello1'
    return redirect("index")

client_user = "user_test"
@app.route("/global_chat", methods=["POST", "GET"])
def global_chat():
    global grp_no
    grp_no = request.args.get('query')
    print(grp_no)
    
    return render_template("global_chat.html", grp_no=grp_no)

@app.route("/send_msg", methods=["POST", "GET"])
def send_msg():
    if request.method == "POST":    

        msg_content = request.form.get("data")
        grp_no = request.form.get("grp_no")
        # print(msg_content, grp_no)

        sql = "INSERT INTO msg_detail (msg_name, msg_content, grp_no) VALUES (%s, %s, %s)"
        val = (client_user, msg_content, grp_no)
        mycursor.execute(sql, val)
        mydb.commit()
        return "msg_sent"
    return "not sent"

def get_data_from_database():
    # grp_no = request.args.get('query')
    sql = "SELECT msg_name, msg_content FROM msg_detail where grp_no=%s"
    query = (grp_no,)
    mycursor.execute(sql, query)
    result = []
    for row in mycursor.fetchall():
        result.append({
            'name': row[0],
            'value': row[1],
        })
    return result

@app.route('/data')
def get_data():
    data = get_data_from_database()
    return jsonify(data)

@app.route('/fetch_data', methods=['GET', 'POST'])
def fetch_data():
    if request.method == 'POST':
        data = request.get_json()
        sql = "SELECT msg_name, msg_content FROM msg_detail"
        mycursor.execute(sql, (data['name'],))
        result = mycursor.fetchone()
        if result:
            return jsonify({'message': result['msg_content']})
        else:
            return jsonify({'message': 'No data found'})



@app.route("/grp_info", methods=["POST", "GET"])
def grp_info():
    if request.method == "POST":    
        grp_no = request.form.get("grp_no")
        grp_name = request.form.get("grp_name")
        grp_info = request.form.get("grp_info")
        grp_mem_1 = request.form.get("grp_mem_1")
        grp_mem_2 = request.form.get("grp_mem_2")
        grp_mem_3 = request.form.get("grp_mem_3")
        grp_mem_4 = request.form.get("grp_mem_4")

        sql = "INSERT INTO grp_detail (grp_no, grp_name, grp_info, grp_mem_1, grp_mem_2, grp_mem_3, grp_mem_4) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (grp_no, grp_name, grp_info, grp_mem_1, grp_mem_2, grp_mem_3, grp_mem_4)
        mycursor.execute(sql, val)
        mydb.commit()
        return render_template("global_chat.html")
    return render_template("grp_info.html")

if __name__=="__main__":
    app.run(debug=True)