#!/usr/bin/env python
# encoding: utf-8

import unittest
from django.test import TestCase as djangoTestCase
from Vsite.forms import AuthenticationForm
from Vsite.forms import NewUserForm
from Vsite import userHelper
from django.contrib.auth.models import User

class AccountViewsTestCase(djangoTestCase):
	def testLoginView(self):
		# Test getting view returns correct template with empty form
		response = self.client.get('/accounts/login/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'login.html')
		self.assertEqual(response.context[0]['form'].general_error, "")

		# Test no username
		response = self.client.post('/accounts/login/', 
						{'username':'',
						 'password':'test'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'login.html')
		self.checkErrorOnField(response.context[0]['form'], 'username')

		# Test no password
		response = self.client.post('/accounts/login/', 
						{'username':'test',
						 'password':''})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'login.html')
		self.checkErrorOnField(response.context[0]['form'], 'password')

		# Test invalid username & password
		response = self.client.post('/accounts/login/', 
						{'username':'test',
						 'password':'test123'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'login.html')
		self.assertNotEqual(response.context[0]['form'].general_error, "")

		# Test inactive account
		response = self.client.post('/accounts/login/', 
						{'username':'MyInactive',
						 'password':'test'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'login.html')
		self.assertNotEqual(response.context[0]['form'].general_error, "")

		# Test successful login & redirection
		response = self.client.post('/accounts/login/', 
						{'username':'test',
						 'password':'test'})
		self.assertEqual(response.status_code, 302)


	def testNewUserView(self):
		# Test getting view returns correct template with empty form
		response = self.client.get('/accounts/new/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'newUser.html')
		self.assertEqual(response.context[0]['form'].general_error, "")

		# Test no username
		response = self.client.post('/accounts/new/',
				  {'username':'',
				   'password':'test',
				   'password_confirm':'test',
				   'email':'test@worldofv.com'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'newUser.html')
		self.checkErrorOnField(response.context[0]['form'], 'username')

		# Test no password
		# TODO: Find out why this doesn't work
		response = self.client.post('/accounts/new/',
				  {'username':'noExist',
				   'password':'e',
				   'password_confirm':'test',
				   'email':'test@worldofv.com'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'newUser.html')
		self.checkErrorOnField(response.context[0]['form'], 'password_confirm')

		# Test no email
		response = self.client.post('/accounts/new/',
				  {'username':'noExist',
				   'password':'test',
				   'password_confirm':'test',
				   'email':''})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'newUser.html')
		self.checkErrorOnField(response.context[0]['form'], 'email')

		# Test password mismatch
		response = self.client.post('/accounts/new/',
				  {'username':'noExist',
				   'password':'test',
				   'password_confirm':'test123',
				   'email':'test@worldofv.com'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'newUser.html')
		self.checkErrorOnField(response.context[0]['form'], 'password_confirm')
	
		# Test existing user
		response = self.client.post('/accounts/new/',
				  {'username':'test',
				   'password':'test',
				   'password_confirm':'test',
				   'email':'test@worldofv.com'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.template[0].name, 'newUser.html')
		self.checkErrorOnField(response.context[0]['form'], 'username')

		# Test successful creation & redirection
		self.assertEqual(User.objects.filter(username__exact='nonExist').count(), 0)
		response = self.client.post('/accounts/new/',
				  {'username':'noExist',
				   'password':'test',
				   'password_confirm':'test',
				   'email':'test@worldofv.com'})		
		self.assertEqual(response.status_code, 302)
		self.assertEqual(User.objects.filter(username__exact='noExist').count(), 1)

	def checkErrorOnField(self,form, fieldName):
		self.assertTrue(len(form[fieldName].errors) > 0)


class AccountHelpersTestCase(djangoTestCase):
	def testUserHelperNewUser(self):
		#Test form w/ no data
		f = NewUserForm({'username':'',
				   'password':'',
				   'password_confirm':'',
				   'email':''})
		self.assertFalse(userHelper.newUser(f))

		#Test form w/ no username
		f = NewUserForm({'username':'',
				   'password':'test',
				   'password_confirm':'test',
				   'email':'test@worldofv.com'})
		self.assertFalse(userHelper.newUser(f))

		#Test form w/ no password
		f = NewUserForm({'username':'nonExist',
				   'password':'',
				   'password_confirm':'',
				   'email':'test@worldofv.com'})
		self.assertFalse(userHelper.newUser(f))

		#Test form w/ mismatch passwords
		f = NewUserForm({'username':'nonExist',
				   'password':'test',
				   'password_confirm':'test2',
				   'email':'test@worldofv.com'})
		self.assertFalse(userHelper.newUser(f))

		#Test existing user
		f = NewUserForm({'username':'test',
				   'password':'test',
				   'password_confirm':'test',
				   'email':'test@worldofv.com'})
		self.assertFalse(userHelper.newUser(f))

		#Test for success
		f = NewUserForm({'username':'nonExist',
				   'password':'test',
				   'password_confirm':'test',
				   'email':'test@worldofv.com'})
		self.assertTrue(userHelper.newUser(f))
		self.assertEqual(User.objects.filter(username__exact='nonExist').count(), 1)
	
	def testUserHelperLoginUser(self):
		# Test form w/ no username
		f = AuthenticationForm({'username':'',
					   'password':'test'})
		self.assertFalse(userHelper.loginUser(f))

		# Test form w/ no password
		f = AuthenticationForm({'username':'test',
					   'password':''})
		self.assertFalse(userHelper.loginUser(f))

		# Test invalid username/password
		f = AuthenticationForm({'username':'test',
					   'password':'test12'})
		self.assertFalse(userHelper.loginUser(f))
		self.assertTrue(len(f.general_error) > 0)

		# Test disabled account
		f = AuthenticationForm({'username':'MyInactive',
					   'password':'test'})
		self.assertFalse(userHelper.loginUser(f))
		self.assertTrue(len(f.general_error) > 0)

		# Test for success
		f = AuthenticationForm({'username':'test',
					   'password':'test'})
		self.assertTrue(userHelper.loginUser(form=f,bypassRequest=True))
		
		self.assertEqual(len(f.general_error),0)

class AccountFormsTestCase(unittest.TestCase):
	def testAuthenticationForm(self):
		#Test form w/ no data
		f = AuthenticationForm({'username':'',
					   'password':''})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'username')
		self.checkErrorOnField(f, 'password')

		#Test form w/ no username
		f = AuthenticationForm({'username':'',
					   'password':'test'})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'username')

		#Test form w/ no password
		f = AuthenticationForm({'username':'test',
					   'password':''})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'password')

		#Test successful form
		f = AuthenticationForm({'username':'test',
					   'password':'test'})
		self.assertTrue(f.is_valid())

	def testNewUserForm(self):
		# Test form w/ no data
		f = NewUserForm({'username':'',
				   'password':'',
				   'password_confirm':'',
				   'email':''})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'username')
		self.checkErrorOnField(f, 'password')
		self.checkErrorOnField(f, 'password_confirm')
		self.checkErrorOnField(f, 'email')

		# Test form w/ no username
		f = NewUserForm({'username':'',
				   'password':'test',
				   'password_confirm':'test',
				   'email':'test@test.com'})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'username')

		# Test form w/ no password	
		f = NewUserForm({'username':'nonExist',
				   'password':'',
				   'password_confirm':'',
				   'email':'test@test.com'})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'password')

		# Test form w/ mismatch password	
		f = NewUserForm({'username':'nonExist',
				   'password':'test',
				   'password_confirm':'test345',
				   'email':'test@test.com'})
		self.assertFalse(f.is_valid())
		self.checkErrorOnField(f, 'password_confirm')

		# Test successful form
		f = NewUserForm({'username':'nonExist',
				   'password':'test',
				   'password_confirm':'test',
				   'email':'nonexist@worldofv.com'})
		self.assertTrue(f.is_valid())
	
	def checkErrorOnField(self,form, fieldName):
		self.assertTrue(len(form[fieldName].errors) > 0)

if __name__ == '__main__':
	unittest.main()
