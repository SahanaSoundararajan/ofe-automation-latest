#import view
import unittest
import logging
import csv
import os
from autologging import logged, traced
import start_mock
from distributors_admin import oauth as distributorAdminOAuth

TOKEN_JSON_ADMIN = os.path.abspath('../DistributorsAdminTokens.json')


@traced
@logged
class Practice:

    def __init__(self, *args, **kwargs):
        self.results = {"resultAttachments": {}, "output": "", "executedWithWarnings": False}
        #super(TestCase, self).__init__(*args, **kwargs)
        self.logging = logging.getLogger(__name__)
        self.setUpDone = False

    def setUp(self):

        if not self.setUpDone:

            print("Before startmock")
            self.mock = start_mock.StartMock(service = "distributors_admin", results = self.results)
            print("After startmock")

            self.timezone = "Asia/Kolkata"

            distributorAdminTokenObj = distributorAdminOAuth.OAuth(userAccount = "admin1",
                                                                   results = self.results, useMock = True,
                                                                   tokenJsonFile = TOKEN_JSON_ADMIN,
                                                                   oauthType = "polling")

            self.distributorsAdminToken = distributorAdminTokenObj.token
            print(self.distributorsAdminToken)
            self.setUpDone = True
            
            

            

p1 = Practice()
p1.setUp()
            
    

