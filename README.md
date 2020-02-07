# The Class Captain
A messenger bot that will notify all student of a class about every notice given by a teacher.

## How to setup
Step 1: You need to create a facebook page  
Step 2: From the developer site create an app for this page  
Step 3: Add a webhook from product option  
Step 4: Generate a token for this page and copy it  
Step 5: Copy this github url and clone it on your machine  
Step 6: Open 'conf.py' file and paste the token in 'BOT_TOKEN' variable  
`BOT_TOKEN = '<facebook_page_token>'`  
Step 7: Create your own app token on the variable 'VERIFY_TOKEN'  
`VERIFY_TOKEN = '<your_app_token>'`  
Step 8: Create a *mysql* database (on your local machine or any other hosted site)  
Step 9: Put your database option in the variable 'db_info'  
`db_info = {  
		'Username': '',  
		'Database': '',  
		'Password': '',  
		'Server': '',  
		'Port': 3306  
	}`  
Step 10: Create a table into the database as given below,  
`CREATE TABLE class_room(id varchar(20) PRIMARY KEY, class_id varchar(20), member_type varchar(20))`  
Step 11: Run the code using  
`python3 main.py`  
Step 12: Put your webhook information in the callback URl  

Now you are ready to go...
