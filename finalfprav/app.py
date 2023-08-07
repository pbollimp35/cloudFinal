from flask import Flask, request, render_template, session
import pymysql, boto3

app = Flask(__name__,)
app.secret_key = "secret key"

Access_Key = 'AKIAUWKGGSRXKOC4O3MX'
Secret_Key = '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'
Region = 'us-east-1'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/signup',  methods = ['GET', 'POST'])
def signup():
    email = request.form['gmail']
    passw = request.form['password']
    NameofDatabase = "defaultdb"
    NameofDatabaseUser = "admin"
    PasswordofDatabase = "multiweekdb"
    EndpointofDatabse = "multiweekdb.clnopyq3sfwe.us-east-1.rds.amazonaws.com"
    connection = pymysql.connect(host=EndpointofDatabse, user=NameofDatabaseUser, password=PasswordofDatabase, database=NameofDatabase)
    cursor = connection.cursor()
    query = "INSERT INTO Details (useremailaddress, userpassword) VALUES (%s, %s);"
    cursor.execute(query, (email, passw))
    connection.commit()
    connection.close()
    return render_template("index.html", done = "Account Creating Click on Login to Login ")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/check', methods=['GET', 'POST'])
def check():
    email = request.form['gmail']
    passw = request.form['password']
    NameofDatabase = "defaultdb"
    NameofDatabaseUser = "admin"
    PasswordofDatabase = "multiweekdb"
    EndpointofDatabse = "multiweekdb.clnopyq3sfwe.us-east-1.rds.amazonaws.com"
    connection = pymysql.connect(host=EndpointofDatabse, user=NameofDatabaseUser, password=PasswordofDatabase, database=NameofDatabase)
    cursor = connection.cursor()
    query = "SELECT userpassword From  Details WHERE useremailaddress = (%s);"
    cursor.execute(query, (email))
    temp = cursor.fetchone()
    if passw == temp[0]:
        session['temp_user'] = email
        return render_template("emailandfile.html")
    else:
        return render_template("login.html", issue="please check your password")
    
@app.route('/emailfile', methods=['GET', 'POST'])
def emailfile():
    users = {}
    uploadedfile = request.files['formFile']
    users['user1'] = request.form['Username1']
    users['user2'] = request.form['Username2']
    users['user3'] = request.form['Username3']
    users['user4'] = request.form['Username4']
    users['user5'] = request.form['Username5']
    S3Bucket = boto3.client('s3', aws_access_key_id = Access_Key, aws_secret_access_key=Secret_Key, region_name=Region)
    S3Bucket.upload_fileobj(uploadedfile, "poojabucket881", uploadedfile.filename)
    limit = 4000
    bucketUrl = S3Bucket.generate_presigned_url('get_object', Params={'Bucket': 'poojabucket881', 'Key': uploadedfile.filename}, ExpiresIn=limit)
    generateTopic = boto3.client('sns',aws_access_key_id = Access_Key, aws_secret_access_key=Secret_Key, region_name=Region)
    createTopic = generateTopic.create_topic(Name="emailTopic")
    print(users)
    #lambda function
    for user in users.keys():
        if users[user] != "":
            email_ARN = createTopic['TopicArn']
            protocal = 'email'
            endpoint = users[user]
            response =  generateTopic.subscribe(TopicArn = email_ARN, Protocol=protocal, Endpoint=endpoint, ReturnSubscriptionArn=True)['SubscriptionArn']
            generateTopic.publish(TopicArn = email_ARN, Subject="Hello There Click on the link to download the file ", Message = bucketUrl) 
    NameofDatabase = "defaultdb"
    NameofDatabaseUser = "admin"
    PasswordofDatabase = "multiweekdb"
    EndpointofDatabse = "multiweekdb.clnopyq3sfwe.us-east-1.rds.amazonaws.com"
    connection = pymysql.connect(host=EndpointofDatabse, user=NameofDatabaseUser, password=PasswordofDatabase, database=NameofDatabase)
    cursor = connection.cursor()
    query = "INSERT INTO Files (uploadedfile, useremailaddress) VALUES (%s, %s);"
    email = session['temp_user'] 
    cursor.execute(query, (uploadedfile.filename, email))
    connection.commit()
    connection.close()
    NameofDatabase = "defaultdb"
    NameofDatabaseUser = "admin"
    PasswordofDatabase = "multiweekdb"
    EndpointofDatabse = "multiweekdb.clnopyq3sfwe.us-east-1.rds.amazonaws.com"
    connection = pymysql.connect(host=EndpointofDatabse, user=NameofDatabaseUser, password=PasswordofDatabase, database=NameofDatabase)
    cursor = connection.cursor()
    query = "SELECT useremailaddress, uploadedfile FROM Files"
    cursor.execute(query)
    temp =cursor.fetchall()
    userfile = {}
    for user in temp:
        userfile[user[0]] = user[1]
    return render_template("billingtable.html", data = userfile)






    

if __name__ == "__main__":
    app.run(debug=True)