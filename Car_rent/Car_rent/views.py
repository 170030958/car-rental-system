from django.shortcuts import render, redirect
from django.http.response import HttpResponse, JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from tabulate import tabulate

import mysql.connector
from mysql.connector import Error

import json
import os

import sys
from subprocess import run,PIPE

import mimetypes
from django import forms

from django.conf import settings
from django.core.files.storage import FileSystemStorage
# Create your views here.


import time
from datetime import datetime as dt

def DBLoginPg(request):
	return render(request,'Car_Rent_LoginPage.html')

def register(request):
	reg_usr= request.POST.get('reg_username')
	reg_email= request.POST.get('reg_email')
	reg_pass= request.POST.get('reg_password')
	reg_pass1= request.POST.get('reg_password1')
	fail_creation='Account Created'
	if(reg_pass == reg_pass1):
		try:
			connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='root')                                         
			if connection.is_connected():
				db_Info = connection.get_server_info()
				print("Connected to MySQL Server version ", db_Info)
				cursor = connection.cursor()
				cursor.execute("select database();")
				record = cursor.fetchone()
				print(reg_usr+' '+reg_pass+' '+reg_email)
				insrt_qry='insert into car_rent_login values("'+reg_usr+'","'+reg_pass+'","'+reg_email+'");'
				print(insrt_qry)
				cursor.execute(insrt_qry)
				connection.commit()
		except Error as e:
			print("Error while connecting to MySQL", e)
			usr_exist='Username Already Taken'
			return render(request,'Car_Rent_LoginPage.html',{'fail_creation':usr_exist})
		finally:
			if (connection.is_connected()):
				cursor.close()
				connection.close()
				print("MySQL connection is closed")
		return render(request,'Car_Rent_LoginPage.html',{'fail_creation':fail_creation})
	else:
		pass_not_matched='Both Passwords not matched'
		return render(request,'Car_Rent_LoginPage.html',{'fail_creation':pass_not_matched})

def login_request(request):
	login_usr= request.POST.get('login_username')
	login_pass= request.POST.get('login_password')
	items=[]
	price=[]
	item_path=[]
	dict={}
	login_invalid='UnSuccessful Login'
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='root')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			login_chk_qry='select count(*) from car_rent_login where username="'+login_usr+'" and password="'+login_pass+'";'
			print(login_chk_qry)
			cursor.execute(login_chk_qry)
			record = cursor.fetchone()
			print(record)
			if(record[0]==1):
				return render(request,'DBHomePage.html')
			else:
				login_invalid='Invalid Credentials'
	except Error as e:
		print("Error while connecting to MySQL : ", e)
	return render(request,'Car_Rent_LoginPage.html',{'login_invalid':login_invalid})


def DB_request(request):
	Month1=request.POST.get('Month')
	year1=request.POST.get('year1')
	mon_dict={'January':'01','February':'02','March':'03','April':'04','May':'05','June':'06','July':'07','August':'08','September':'09','October':'10','November':'11','December':'12'}
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='root')                                         
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			print("You're connected to database: ", record)
			query='select c1.cno,c1.c_firstname,c1.c_middlename,c1.c_lastname,c1.c_mobile,c1.c_email,c2.carno,c2.company,c2.modelname,c2.color,c2.no_of_doors,c2.hireRate,r1.reserve_date,r1.returndate,r1.amount from customer c1,car c2,reservation r1 where c1.cno=r1.cno and r1.carno=c2.carno and EXTRACT(YEAR FROM r1.reserve_date)="'+str(year1)+'" and EXTRACT(MONTH FROM r1.reserve_date)="'+str(mon_dict[Month1])+'";'
			print(query)
			cursor.execute(query)
			record = cursor.fetchall()
			columns = cursor.description
	except Error as e:
		print("Error while connecting to MySQL", e)
	headers=[]
	result=''
	for i in range(0,len(columns)):
		result=result+'  '+str(columns[i][0])
		headers.append(columns[i][0])
	list1=[]
	print(headers)
	for i in range(0,len(record)):
		for j in range(0,len(record[i])):
			result=result+' '+str(record[i][j])
			list1.append(str(record[i][j]))
		list1.append(',,,')
		result=result+'\n'
	print(list1)
	list2=[]
	list3=[]
	for i in range(0,len(list1)):
		if(list1[i]==',,,'):
			list2.append(list3)
			list3=[]
		else:
			list3.append(list1[i])
	print(list2)
	result1=tabulate(list2, headers=headers, tablefmt='orgtbl')
	return render(request,'DBdata.html',{'Month_year_user':'Booking Details of '+str(Month1)+', '+str(year1),'output1':result1})

def DBnewreserv(request):
	return render(request,'DBnewreservation.html')

def DB_upd_del(request):
	mnth_yr=request.POST.get('mnth_year')
	print(mnth_yr)
	mnth_yr=mnth_yr.split('of ')[1]
	Month1=mnth_yr.split(',')[0]
	year1=mnth_yr.split(',')[1].strip()
	upd_or_del=request.POST.get('update')
	print(upd_or_del)
	res_id=request.POST.get('res_id')
	tab_data=request.POST.get('tab_data')
	tab_data=tab_data.split('+----------|')[1]
	tab_data_list=tab_data.split('\n')
	print(tab_data_list)
	tab_data_list1=[]
	for i in range(1,len(tab_data_list)):
		l=[]
		print(tab_data_list[i].split('|'))
		for j in range(15):
			l.append(tab_data_list[i].split('|')[1:][j].strip())
		tab_data_list1.append(l)
	print(tab_data_list1)
	mon_dict={'January':'01','February':'02','March':'03','April':'04','May':'05','June':'06','July':'07','August':'08','September':'09','October':'10','November':'11','December':'12'}
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='root')                                         
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			print("You're connected to database: ", record)
			if(upd_or_del=='delete'):
				del_query='delete from reservation where reservationid='+str(res_id)+';'
				cursor.execute(del_query)
				record = cursor.fetchall()
				print(record)
			elif(upd_or_del=='update'):
				for i in tab_data_list1:
					cust_upd='update customer set c_firstname="'+i[1]+'" ,c_middlename="'+i[2]+'" ,c_lastname="'+i[3]+'" ,c_mobile="'+i[4]+'" ,c_email="'+i[5]+'" where cno='+str(i[0])+';'
					car_upd='update car set company="'+i[7]+'" ,modelname="'+i[8]+'" ,color="'+i[9]+'" ,no_of_doors='+str(i[10])+' ,hireRate='+str(i[11])+' where carno="'+i[6]+'";'
					reser_upd='update reservation set reserve_date="'+i[13]+'" ,returndate="'+i[14]+'" where reservationid='+str(i[12])+';'
					print(cust_upd)
					print(car_upd)
					print(reser_upd)
					cursor.execute(cust_upd)
					cursor.execute(car_upd)
					cursor.execute(reser_upd)
			query='select c1.cno,c1.c_firstname,c1.c_middlename,c1.c_lastname,c1.c_mobile,c1.c_email,c2.carno,c2.company,c2.modelname,c2.color,c2.no_of_doors,c2.hireRate,r1.reservationid,r1.reserve_date,r1.returndate,r1.amount from customer c1,car c2,reservation r1 where c1.cno=r1.cno and r1.carno=c2.carno and EXTRACT(YEAR FROM r1.reserve_date)="'+str(year1)+'" and EXTRACT(MONTH FROM r1.reserve_date)="'+str(mon_dict[Month1])+'";'
			print(query)
			cursor.execute(query)
			record = cursor.fetchall()
			columns = cursor.description
	except Error as e:
		print("Error while connecting to MySQL", e)
	headers=[]
	result=''
	for i in range(0,len(columns)):
		result=result+'  '+str(columns[i][0])
		headers.append(columns[i][0])
	list1=[]
	print(headers)
	for i in range(0,len(record)):
		for j in range(0,len(record[i])):
			result=result+' '+str(record[i][j])
			list1.append(str(record[i][j]))
		list1.append(',,,')
		result=result+'\n'
	print(list1)
	list2=[]
	list3=[]
	for i in range(0,len(list1)):
		if(list1[i]==',,,'):
			list2.append(list3)
			list3=[]
		else:
			list3.append(list1[i])
	print(list2)
	result1=tabulate(list2, headers=headers, tablefmt='orgtbl')
	connection.commit()
	return render(request,'DBupdatereservation.html',{'Month_year_user':'Booking Details of '+Month1+', '+year1,'output1':result1})

def DB_update(request):
	Month1=request.POST.get('Month1')
	year1=request.POST.get('year2')
	print(str(Month1)+','+str(year1))
	mon_dict={'January':'01','February':'02','March':'03','April':'04','May':'05','June':'06','July':'07','August':'08','September':'09','October':'10','November':'11','December':'12'}
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='root')                                         
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			print("You're connected to database: ", record)
			query='select c1.cno,c1.c_firstname,c1.c_middlename,c1.c_lastname,c1.c_mobile,c1.c_email,c2.carno,c2.company,c2.modelname,c2.color,c2.no_of_doors,c2.hireRate,r1.reservationid,r1.reserve_date,r1.returndate,r1.amount from customer c1,car c2,reservation r1 where c1.cno=r1.cno and r1.carno=c2.carno and EXTRACT(YEAR FROM r1.reserve_date)="'+str(year1)+'" and EXTRACT(MONTH FROM r1.reserve_date)="'+str(mon_dict[Month1])+'";'
			print(query)
			cursor.execute(query)
			record = cursor.fetchall()
			columns = cursor.description
	except Error as e:
		print("Error while connecting to MySQL", e)
	headers=[]
	result=''
	for i in range(0,len(columns)):
		result=result+'  '+str(columns[i][0])
		headers.append(columns[i][0])
	list1=[]
	print(headers)
	for i in range(0,len(record)):
		for j in range(0,len(record[i])):
			result=result+' '+str(record[i][j])
			list1.append(str(record[i][j]))
		list1.append(',,,')
		result=result+'\n'
	print(list1)
	list2=[]
	list3=[]
	for i in range(0,len(list1)):
		if(list1[i]==',,,'):
			list2.append(list3)
			list3=[]
		else:
			list3.append(list1[i])
	print(list2)
	result1=tabulate(list2, headers=headers, tablefmt='orgtbl')
	return render(request,'DBupdatereservation.html',{'Month_year_user':('Booking Details of '+Month1+', '+year1),'output1':result1})

def DB_insert(request):
	cust_frst_name=request.POST.get('cust_frst_name')
	cust_middle_name=request.POST.get('cust_middle_name')
	cust_last_name=request.POST.get('cust_last_name')
	cust_Gender=request.POST.get('Gender')
	DOB_day1=request.POST.get('day1')
	DOB_Month=request.POST.get('Month')
	DOB_year=request.POST.get('year')
	cust_street=request.POST.get('street')
	cust_city=request.POST.get('city')
	cust_state=request.POST.get('state')
	cust_zipcode=request.POST.get('zipcode')
	cust_mobile=request.POST.get('mobile')
	cust_email=request.POST.get('email')
	cust_sel_car=request.POST.get('sel_car')
	reser_day2=request.POST.get('day2')
	reser_Month2=request.POST.get('Month2')
	reser_Month2=reser_Month2[:len(reser_Month2)-1]
	reser_year2=request.POST.get('year2')
	ret_day3=request.POST.get('day3')
	ret_Month3=request.POST.get('Month3')
	ret_Month3=ret_Month3[:len(ret_Month3)-1]
	ret_year3=request.POST.get('year3')
	mon_dict={'January':'01','February':'02','March':'03','April':'04','May':'05','June':'06','July':'07','August':'08','September':'09','October':'10','November':'11','December':'12'}
	try:
		connection = mysql.connector.connect(host='localhost',database='Jarvis',user='root',password='root')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			print("Connected to MySQL Server version ", db_Info)
			cursor = connection.cursor()
			cursor.execute("select database();")
			record = cursor.fetchone()
			cust_check='select cno from customer where c_lastname="'+cust_last_name+'" and c_gender="'+cust_Gender+'" and c_mobile="'+cust_mobile+'" and c_street="'+cust_street+'";'
			print(cust_check)
			cursor.execute(cust_check)
			record = cursor.fetchone()
			print(record)
			print(cust_sel_car)
			carno_qry='select carno,hireRate from car where company="'+cust_sel_car.split(' ')[0]+'" and modelname="'+cust_sel_car.split(' ')[1]+'";'
			print(carno_qry)
			cursor.execute(carno_qry)
			record1=cursor.fetchone()
			print(record1)
			d1=reser_year2+'/'+reser_Month2+'/'+reser_day2
			d2=ret_year3+'/'+ret_Month3+'/'+ret_day3
			print(d1)
			print(d2)
			res = (dt.strptime(d2, "%Y/%B/%d") - dt.strptime(d1, "%Y/%B/%d")).days
			amt=res*record1[1]
			print(str(res)+':'+str(amt))
			#print(record[0])
			print(record1[0])
			print(amt)
			cno_max=0
			res_max1=0
			reser_date=reser_year2+'/'+mon_dict[reser_Month2]+'/'+reser_day2
			ret_date=ret_year3+'/'+mon_dict[ret_Month3]+'/'+ret_day3
			if(record is None):
				dob_cust=DOB_year+'/'+mon_dict[DOB_Month]+'/'+DOB_day1
				print(dob_cust)
				print(cust_frst_name)
				print(cust_middle_name)
				print(cust_last_name)
				print(cust_Gender+','+dob_cust+','+cust_street+','+cust_city+','+cust_state+','+cust_zipcode+','+cust_mobile+','+cust_email)
				max_cust='select max(cno) from customer;'
				cursor.execute(max_cust)
				record5=cursor.fetchone()
				print(record5)
				if(record5[0] is not None):
					cno_max=record5[0]+1
				else:
					cno_max=1
				print(cno_max)
				cust_insert='insert into customer values('+str(cno_max)+',"'+cust_frst_name+'","'+cust_middle_name+'","'+cust_last_name+'","'+cust_Gender+'","'+dob_cust+'","'+cust_street+'","'+cust_city+'","'+cust_state+'","'+cust_zipcode+'","'+cust_mobile+'","'+cust_email+'");'
				print(cust_insert)
				cursor.execute(cust_insert)
				record4=cursor.fetchone()
				print(record4)
				reser_max='select max(reservationid) from reservation;'
				print(reser_max)
				cursor.execute(reser_max)
				record7=cursor.fetchone()
				print(record7)
				if(record7[0] is not None):
					res_max1=record7[0]+1
				else:
					res_max1=1
				print(res_max1)
				insrt_qry='insert into reservation values('+str(res_max1)+', "'+reser_date+'","'+ret_date+'",'+str(cno_max)+',"'+str(record1[0])+'",'+str(amt)+');'
				print(insrt_qry)
				cursor.execute(insrt_qry)
				record3 = cursor.fetchone()
				print(record3)
			else:
				reser_max='select max(reservationid) from reservation;'
				print(reser_max)
				cursor.execute(reser_max)
				record7=cursor.fetchone()
				print(record7[0])
				print('Hi')
				if(record7[0] is not None):
					print('no')
					res_max1=record7[0]+1
				else:
					res_max1=1
				#print(res_max1+','+reser_date+','+ret_date)
				insrt_qry='insert into reservation values('+str(res_max1)+', "'+reser_date+'","'+ret_date+'",'+str(record[0])+',"'+str(record1[0])+'",'+str(amt)+');'
				print(insrt_qry)
				cursor.execute(insrt_qry)
				record3 = cursor.fetchone()
				print(record3)
		connection.commit()
	except:
		pass
	return render(request,'DBnewreservation.html')

