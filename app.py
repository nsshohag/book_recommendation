# import all libraries
import difflib
import json
from flask import Flask, render_template , request , redirect, session , url_for
import os
import mysql.connector
import pickle
import pandas as pd
import numpy as np

# load kortechi pickle files
popular_df = pickle.load(open('popular_df.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
all_books_with_avg_num=pickle.load(open('all_books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

# mysql connection koretchi
connection = mysql.connector.connect(host="localhost", user="root", password="1123", database="login")
cursor = connection.cursor()


app = Flask(__name__)
# sesseion stoarge e kahini
app.secret_key = os.urandom(24)


## home page
@app.route('/home')
def home_func():
    if 'user_id' in session:
        if "username" in session:
            username= session["username"]


        # book read list theke user ki ki boi read korche ta database theke fetch kortechi
        cursor.execute("""SELECT *FROM `book_read_list` WHERE `username` LIKE '{}'""".format(username))
        book_read_list = cursor.fetchall()

        # readlist boi er isbn
        read_isbn_list = [tup[1] for tup in book_read_list]
        # popular all books er isbn
        isbn = list(popular_df['ISBN'].values)


        if isbn[0] in read_isbn_list:
            print("Popular book1 user er read_list e acahe")
        return render_template('home.html',
                               book_name=list(popular_df['Book-Title'].values),
                               book_author=list(popular_df['Book-Author'].values),
                               book_image=list(popular_df['Image-URL-M'].values),
                               book_votes=list(popular_df['num_rating'].values),
                               book_avg_rating=list(np.around(popular_df['avg_rating'].values, 2)),
                               isbn=list(popular_df['ISBN'].values),
                               username=username,
                               read_isbn_list=read_isbn_list
                               )
    else:
        return redirect('/')


## recommend page
@app.route('/recommend')
def recommend_func():
    if 'user_id' in session:
        username = session["username"]
        return render_template('recommend.html', username = username)
    else:
        return redirect('/')


## recommended books page
@app.route('/recommend_books', methods=['post'])
def recommend():
    if 'user_id' in session:
        username = session["username"]

        # user er kach theke boi er nam nicchi
        user_input_book = request.form.get('user_input_book')

        # all the unique books name are here
        list_of_all_books_names = books['Book-Title'] # books object e ache tai porer line e frame e convert korchi
        list_of_all_books_names = list_of_all_books_names.to_frame() # converted to frame from object
        list_of_all_books_names.drop_duplicates('Book-Title', inplace=True) # drop duplicates
        list_of_all_books_names = list_of_all_books_names['Book-Title'].tolist() # list e conversion

        # finding close match user input e deya nam er sapekkhe
        close_match_book_list = difflib.get_close_matches(user_input_book, list_of_all_books_names)
        size = len(close_match_book_list)


        data = []
        if size == 0:
            print("Close match book 0 ta ")
            return redirect('/recommend')

        # close match book theke 1 ta book nicchi
        close_match = close_match_book_list[0]
        user_input_book = close_match

        # zodi user er deya input book similarity score er jonno ze 700*700 er moto ze matrix e na thake tahole return kore dicchi recommend page ei

        # check if any element is true

        boolean_list=list(pt.index == user_input_book)
        result = any(boolean_list)
        # zodi user er deya boi oi 700*700 matrix e thake
        if result==True:
            # similarit basis e
            index = np.where(pt.index == user_input_book)[0][0]
            distances = similarity_scores[index]
            similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]
            data = []
            for i in similar_items:
                item = []
                # to have all the information of the book
                temp_df = all_books_with_avg_num[all_books_with_avg_num['Book-Title'] == pt.index[i[0]]]
                temp_df = temp_df.drop_duplicates('Book-Title')
                item.extend(list(temp_df['Book-Title'].values))
                item.extend(list(temp_df['Book-Author'].values))
                item.extend(list(temp_df['Image-URL-M'].values))
                item.extend(list(temp_df['num_rating'].values))
                item.extend(list(np.around(temp_df['avg_rating'].values, 2)))
                item.extend(list(temp_df['ISBN'].values))
                data.append(item)



            # book read list theke user ki ki boi read korche ta database theke fetch kortechi
            cursor.execute("""SELECT *FROM `book_read_list` WHERE `username` LIKE '{}'""".format(username))
            book_read_list = cursor.fetchall()

            # readlist boi er isbn
            read_isbn_list = [tup[1] for tup in book_read_list]

            return render_template('recommend.html',
                                   data=data,
                                   read_isbn_list=read_isbn_list,
                                   username=username
                                   )
        else:
            return redirect('/recommend')

## books page
@app.route('/all_books')
def all_books():
    if 'user_id' in session:
        username= session["username"]

        # popular book gulai dichi
        isbn = list(popular_df['ISBN'].values)

        # database theke user ki ki boi porch etar list anlam
        cursor.execute("""SELECT *FROM `book_read_list` WHERE `username` LIKE '{}'""".format(username))
        book_read_list = cursor.fetchall()
        read_isbn_list = [tup[1] for tup in book_read_list]


        return render_template('all_books.html',
                               book_name=list(popular_df['Book-Title'].values),
                               book_author=list(popular_df['Book-Author'].values),
                               book_image=list(popular_df['Image-URL-M'].values),
                               book_votes=list(popular_df['num_rating'].values),
                               book_avg_rating=list(np.around(popular_df['avg_rating'].values, 2)),
                               username=username,
                               read_isbn_list=read_isbn_list,
                               isbn=isbn
                               )
    else:
        return redirect('/')

## searched book page
@app.route('/searched_books', methods=['post'])
def searched_books():
    if 'user_id' in session:
        username= session["username"]

        isbn = list(popular_df['ISBN'].values)
        search_user_input_book = request.form.get('search_user_input_book')
        print(search_user_input_book)
        list_of_all_book_names = all_books_with_avg_num['Book-Title']  # here the books are in object dtpe
        list_of_all_book_names = list_of_all_book_names.to_frame()  # here the books are converted to frame
        list_of_all_book_names.drop_duplicates('Book-Title', inplace=True)  # also frames without duplicates
        list_of_all_book_names = list_of_all_book_names['Book-Title'].tolist()  # converted to list
        close_match_book_list = difflib.get_close_matches(search_user_input_book, list_of_all_book_names,10)  # kaorn convert kora lage difflib calaite gele frame er upor hoy na
        close_match_book_list = pd.DataFrame(close_match_book_list, columns=['Book-Title'])
        close_match_book_list = close_match_book_list.merge(all_books_with_avg_num, on='Book-Title').drop_duplicates('Book-Title')[['Book-Title', 'Book-Author', 'Image-URL-M','num_rating', 'avg_rating','ISBN']]
        print(close_match_book_list)

        # database theke user ki ki boi porch etar list anlam
        cursor.execute("""SELECT *FROM `book_read_list` WHERE `username` LIKE '{}'""".format(username))
        book_read_list = cursor.fetchall()
        read_isbn_list = [tup[1] for tup in book_read_list]


        return render_template('all_books.html',
                               book_name=list(close_match_book_list['Book-Title'].values),
                               book_author=list(close_match_book_list['Book-Author'].values),
                               book_image=list(close_match_book_list['Image-URL-M'].values),
                               book_votes=list(close_match_book_list['num_rating'].values),
                               book_avg_rating=list(np.around(close_match_book_list['avg_rating'].values, 2)),
                               username=username,
                               read_isbn_list=read_isbn_list,
                               isbn=list(close_match_book_list['ISBN'].values)
                               )
    else:
        return redirect('/')

## readlist page
@app.route('/read_list')
def read_list():

    if 'user_id' in session:
        username = session["username"]


        cursor.execute("""SELECT *FROM `book_read_list` WHERE `username` LIKE '{}'""".format(username))
        all_isbn = cursor.fetchall()

        isbn_list = [book[1] for book in all_isbn] # blchal tupple theke list e convert korchi kivabe korchi jani na .chatgpt re jigaichi boila diche
        isbn_frame = pd.DataFrame(isbn_list, columns=['ISBN'])
        all_read_book_list = isbn_frame.merge(all_books_with_avg_num, on='ISBN').drop_duplicates('Book-Title')[['Book-Title', 'Book-Author', 'Image-URL-M','num_rating','avg_rating','ISBN']]


        username = username
        return render_template('read_list.html',
                               book_name = list(all_read_book_list['Book-Title'].values),
                               book_author=list(all_read_book_list['Book-Author'].values),
                               book_image=list(all_read_book_list['Image-URL-M'].values),
                               book_votes=list(all_read_book_list['num_rating'].values),
                               book_avg_rating=list(np.around(all_read_book_list['avg_rating'].values, 2)),
                               isbn=list(all_read_book_list['ISBN'].values),
                               username = username
                               )
    else:
        return redirect('/')

@app.route('/book')
def book():

    username = session["username"]
    book_name = request.args.get('book_name')
    book_author = request.args.get('book_author')
    book_image = request.args.get('book_image')
    isbn = request.args.get('isbn')


    book_votes=list(all_books_with_avg_num[all_books_with_avg_num['ISBN']==isbn]['num_rating'].values)
    book_avg_rating = list(all_books_with_avg_num[all_books_with_avg_num['ISBN'] == isbn]['avg_rating'].values)
    book_votes=book_votes[0]
    book_avg_rating=book_avg_rating[0]
    book_avg_rating=np.around(book_avg_rating, 2)

    print(book_votes)
    print(type(book_votes))

    cursor.execute("""SELECT *FROM `comment` WHERE `isbn` LIKE '{}' ORDER BY `idcomment` DESC """.format(isbn))
    all_comments = cursor.fetchall()
    comments = [item[3] for item in all_comments]
    user_names = [item[1] for item in all_comments]

    cursor.execute("""SELECT *FROM `review` WHERE `isbn` LIKE '{}' ORDER BY `idreview` DESC """.format(isbn))
    all_reviews = cursor.fetchall()
    user_names_review = [item[2] for item in all_reviews]
    review_titles = [item[3] for item in all_reviews]
    review_contents = [item[4] for item in all_reviews] # in list conversion

    print(all_reviews)


    # simmiliar books khujtechi

    boolean_list = list(pt.index == book_name)
    result = any(boolean_list)

    if result==True:
        index = np.where(pt.index == book_name)[0][0]
        distances = similarity_scores[index]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            # to have all the information of the book
            temp_df = all_books_with_avg_num[all_books_with_avg_num['Book-Title'] == pt.index[i[0]]]
            temp_df = temp_df.drop_duplicates('Book-Title')
            item.extend(list(temp_df['Book-Title'].values))
            item.extend(list(temp_df['Book-Author'].values))
            item.extend(list(temp_df['Image-URL-M'].values))
            item.extend(list(temp_df['num_rating'].values))
            item.extend(list(np.around(temp_df['avg_rating'].values, 2)))
            item.extend(list(temp_df['ISBN'].values))
            data.append(item)
        return render_template('book.html',
                               book_name=book_name,
                               book_author=book_author,
                               book_image=book_image,
                               isbn=isbn,
                               book_votes=book_votes,
                               book_avg_rating=book_avg_rating,
                               username=username,
                               comments=comments,
                               user_names=user_names,
                               user_names_review=user_names_review,
                               review_titles=review_titles,
                               review_contents=review_contents,
                               data=data
                               )
    else:
        data=[]
        return render_template('book.html',
                               book_name=book_name,
                               book_author=book_author,
                               book_image=book_image,
                               isbn=isbn,
                               book_votes=book_votes,
                               book_avg_rating=book_avg_rating,
                               username=username,
                               comments=comments,
                               user_names=user_names,
                               user_names_review=user_names_review,
                               review_titles=review_titles,
                               review_contents=review_contents,
                               data=data
                               )

@app.route('/book_rated')
def book_rated():
    username = session["username"]
    book_name = request.args.get('book_name')
    book_author = request.args.get('book_author')
    book_image = request.args.get('book_image')
    isbn = request.args.get('isbn')

    comment = request.form.get('comment')
    print(comment)

    return render_template('book.html',
                           book_name=book_name,
                           book_author=book_author,
                           book_image=book_image,
                           isbn=isbn,
                           username=username
                           )


# @app.route('/book_page/<dynamic_url>/<book_author>/<book_image>')
# def book_pagex(dynamic_url,book_author,book_image):
#    return render_template('book.html',
#                           book_name=dynamic_url,
#                           book_author=book_author
#
#                           )

@app.route('/')
def login_page():
    if 'user_id' in session:
        return redirect('/home')
    else:
        return render_template('login.html')

@app.route('/register')
def register_page():
    if 'user_id' in session:
        return redirect('/home')
    else:
        return render_template('register.html')

@app.route('/login_validation', methods=['post'])
def login_validation():
    username=request.form.get('username')
    password=request.form.get('password')

    cursor.execute("""SELECT *FROM `users` WHERE `username` LIKE '{}' AND `password` LIKE '{}' """.format(username, password))
    users = cursor.fetchall()
    if len(users)>0:
        # ekta function theke xxx jhamela
        session['user_id']=users[0][0]
        session["username"]=username;
        #return redirect(url_for('home_func')) same shit
        return redirect('/home')
        '''return render_template('/feedx.html', book_name =list(popular_df['Book-Title'].values),
                           book_author=list(popular_df['Book-Author'].values),
                           book_image=list(popular_df['Image-URL-M'].values),
                           book_votes=list(popular_df['num_rating'].values),
                           book_avg_rating=list(np.around(popular_df['avg_rating'].values, 2))
                           )
        '''
    else:
        return redirect('/')

@app.route('/register_val', methods=['post'])
def register_val():
    username=request.form.get('username')

    password=request.form.get('password')

    cursor.execute("""SELECT *FROM `users` WHERE `username` LIKE '{}'""".format(username))
    users = cursor.fetchall()
    print(len(users))
    if len(users)>0:
        # return render_template('register.html')
        return redirect('/register')
    else:

        cursor.execute("""INSERT INTO `users` (`username`,`password`) VALUES('{}','{}')""".format(username, password))
        connection.commit()
        ### here create another session

        cursor.execute("""SELECT *FROM `users` WHERE `username` LIKE '{}'""".format(username))
        users = cursor.fetchall()
        session['user_id'] = users
        session['user_id'] = users[0][0]
        session["username"] = username;
        return redirect('/home')
        '''return render_template('/feedx.html', book_name=list(popular_df['Book-Title'].values),
                               book_author=list(popular_df['Book-Author'].values),
                               book_image=list(popular_df['Image-URL-M'].values),
                               book_votes=list(popular_df['num_rating'].values),
                               book_avg_rating=list(np.around(popular_df['avg_rating'].values, 2))
                               )'''

@app.route('/logout')
def logout():
    session.pop('user_id')
    session.pop('username')
    return redirect('/')

@app.route('/processRating/<string:userRating>', methods=['POST'])
def processRating(userRating):

    userRating = json.loads(userRating)

    print('UserRating Received')
    print(f"isbn_no: {userRating['isbn_no']}")

    isbn = userRating['isbn_no']
    username = userRating['username']
    rating = userRating['rating']

    cursor.execute(
        """SELECT *FROM `user_rating` WHERE `username` LIKE '{}' AND `isbn` LIKE '{}' """.format(username, isbn))
    isbn_useranme = cursor.fetchall()

    if (len(isbn_useranme) > 0):
        cursor.execute("""UPDATE  `user_rating` SET `rating` = '{}' WHERE `username` = '{}' AND `isbn` = '{}' """.format(rating,username, isbn))
        connection.commit()
        return 'Rating UPdated'
    else:
        cursor.execute("""INSERT INTO `user_rating` (`username`,`isbn`,`rating`) VALUES('{}','{}','{}')""".format(username,isbn,rating))
        connection.commit()
        return 'Rating inserted in the database'



@app.route('/processUserInfo/<string:userInfo>', methods=['POST'])
def processUserInfo(userInfo):
    userInfo = json.loads(userInfo)
    print('UserInfo Received')
    print(f"isbn_no: {userInfo['isbn_no']}")

    isbn = userInfo['isbn_no']
    username = userInfo['username']

    cursor.execute("""SELECT *FROM `book_read_list` WHERE `username` LIKE '{}' AND `isbn` LIKE '{}' """.format(username, isbn))
    isbn_useranme = cursor.fetchall()

    if(len(isbn_useranme)>0):
        return 'Info recieved succesfully and it already in readlist exist in the database'
    else:
        cursor.execute("""INSERT INTO `book_read_list` (`isbn`,`username`) VALUES('{}','{}')""".format(isbn, username))
        connection.commit()
        return 'Info recieved succesfully and inserted into the database'


@app.route('/processUserComment/<string:userComment>', methods=['POST'])
def processUserComment(userComment):
    userComment = json.loads(userComment)
    print('UserInfo Received')
    print(f"comment {userComment['comment']}")
    print(f"isbn: {userComment['isbn_no']}")
    print(f"username: {userComment['username']}")

    isbn = userComment['isbn_no']
    username = userComment['username']
    comment = userComment['comment']

    print(isbn)
    print(username)
    print(comment)

    cursor.execute("""INSERT INTO `comment` (`username`,`isbn`,`comment`) VALUES('{}','{}','{}')""".format(username, isbn, comment))
    connection.commit()

    return 'comment uploadedd succesfully'

@app.route('/processUserReview', methods=['POST'])
def processUserReview():

    userReview = request.get_json(force=True)
    print('UserInfo Received')

    print(userReview)

    isbn = userReview['isbn_no']
    username = userReview['username']
    review_title = userReview['review_title']
    review_content = userReview['review_content']
    print(review_content)
    print( "insert into review(username, isbn, review_title, review_content) values('"+username+"', '"+isbn+"', '"+review_title+"', '"+review_content+"');")
    cursor.execute("insert into review(username, isbn, review_title, review_content) values('"+username+"', '"+isbn+"', '"+review_title+"', '"+review_content+"');")
    connection.commit()

    return 'review uploadedd succesfully'

@app.route('/deleteFromReadList', methods=['POST'])
def processDeleteFromReadList():

    userInformation = request.get_json(force=True)
    print('UserInfo Received')

    isbn = userInformation['isbn']
    username = userInformation['username']


    cursor.execute("""delete from `book_read_list` where `username` = '{}' and `isbn` = '{}' """.format(username, isbn,))
    connection.commit()

    return 'Book deleted from readList succesfully'

if __name__== '__main__':
    app.run(debug=True)