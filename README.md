# polarisationSurveyWebapp
### This is the survey application where you can put your thought about PM Narendra Modi and it will remain completely anonymous. No one will be able to connect your responses to you personally.

## Deployment instructions using DigitalOcean
* Make sure you have uploaded the code in github.
* Follow the link and login/register "https://cloud.digitalocean.com/"
* Create a new project if you don't have by clicking "+New Project"
* Create a app by clicking create button and select Apps
* You have to link to your project repository and allowed permission to your repository.
* Now, you can select the linked repository in dropdown after select click  on Next button.
* Change the plan if needed by clicking Edit Plan button, click on next button.
* Do some modifications if you want and click on next and atlast click Create Resource button.
* Now, you can see your app is building after that you can follow the link and check your weApp.
* For refrence, Please follow the below link:
* https://docs.digitalocean.com/tutorials/app-deploy-django-app/

## After clone or unzip the code please create the virtual environment and activate it.
for ubuntu/Linux
```
python3 -m venv venv
source venv/bin/activate
```

## Install the dependencies make sure you are inside the project
```
pip install -r requirements.txt
```

## Create the database and gave the permission using below command
```
sudo -u postgres psql
create database <database_name>;
create user myuser with encrypted password <password>;
grant all privileges on database database_name to myuser;
```
## Provide your database credentials in setting.py in DATABASES section.
## Migrate and create the superuser to login admin panel.
```
python manage.py migrate
python manage.py createsuperuser
```

## Follow the link and login to admin panel "localhost:8000/admin"
* Follow this link to insert data nodes in table "localhost:8000/fillSchema"
* Now you can go to the admin panel and select treatment table.
* With the help of "Start Session" button you can start all the session.
* With the help of "Stop Session" button you can stop all the session and download the participant data in zip format.
* To insert nodes in a tree you have to provide the values of "depth"(in the depth input) and "nodes"(in the nodes input), select a table from the dropdown and click the submit button to insert the nodes in a tree.

## User Guide follow the link "localhost:8000"
* Firstly you have to provide your upi id and upi domain.
* In second page you have to answer three questions.
* In third page you have to answer all 13 questions.
* In fourth page you have to click next basically in this page there is a paragraph to read.
* After that a Nodes will be assigned to you.
* Read the paragraph and click on next button
* In newsresponse page, A social media post shown to you and according to post you have to answer true/false about the post.
* In quizTask you have to answer three questions.
* In earning page you can see your winning price.
* After clicking Finish Experiment button you can finish the survey.

## While attempting the survey make sure to follow this
* Make sure you have started the session before starting the survey.
* In second page don't choose "Neither Like nor Dislike" answer for question number three else you will be kicked out.
* Please don't take too much time to answer the question in newsResponse page else you will be kicked out and will also loose participant money.
* Please read all the paragrah and answer the question accordingly. 


## File structure of the code
* polarisation is the name of the project which contains settings, routes etc files in it.
* survey is one of the app that this project contains where all the urls, views and models exists.
* Templates directory contains all the templates related to the project.
* Staic directory contains all the staic files like images related to the project.
* All the views are written inside the survey/views.py.
* All the urls are defined inside survey/urls.py.
* All the tables are define inside survey/models.py.
* All the input forms are written inside survey/forms.py.
* All the Database table pre input are define inside survey/dbSchema.py.
* All the states and cities data are define inside survey/places.py.
* All the supporting function of views is define inside survey/utils.py.
* All the Nodes/Session related logics are define inside survey/utils_allotmentLogic.py.
* In survey/admin.py we have register all the models which admin can see in admin panel.