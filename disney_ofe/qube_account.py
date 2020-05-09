import json
import time
import os
import sys
import copy
from autologging import logged, traced
from flask import request, redirect, make_response

sys.path.append(".")

from mockserver import MockServer, mockWrapper
import config

DEFAULT_LOG_FOLDER = os.path.dirname(__file__)
DEFAULT_LOG_FILE_NAME = "qube_account"
portConfig = config.Config(service = "ports")

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../api_mock/mock_data/qube_account/distributors_admin.json"))
#path = "distributors.json"  #Path to Mock Data - Distributors.json

@traced
@logged
class QubeAccountMock(MockServer):

    def __init__(self, service, host = "0.0.0.0", port = portConfig.qubeAccountMock, results = None):

        self.results = results
        if self.results is None:
            self.results = {"resultAttachments": {}, "output": "", "executedWithWarnings": False}

        logFilePath = os.path.abspath(os.path.join(DEFAULT_LOG_FOLDER, "{0}.log".format(DEFAULT_LOG_FILE_NAME)))
        self.results["resultAttachments"].update({'qube_account_mock.log': logFilePath})

        super().__init__(host = host, port = port, logDir = DEFAULT_LOG_FOLDER, logFileName = DEFAULT_LOG_FILE_NAME)
        #self.config = self.readFile(path = "{}/{}.json".format(path, service))
        self.config = self.readFile(path=path)
        self.service = service

        self.initialise()

    def readFile(self, path):
        """
        reads the input json file
        :return: json file object
        """
        with open(path, "rb") as f:
            configFile = f.read()
            return json.loads(configFile)

    @mockWrapper
    def onGetUsersMe(self, **kwargs):
        """
        callback function for the route GET: /v2/users/me
        Authorization token format - CompanyID_UserID
        """
        print("onGetUsersMe")
        tokenInfo = request.headers["Authorization"].replace("Bearer ", "").split("_")
        print(tokenInfo)
        if len(tokenInfo) < 2:
            return make_response("Unauthorized", 401)

        companyId = tokenInfo[0]
        userId = tokenInfo[1]
        companies = self.config["companies"]
        if companyId in companies:
            companyDetail = companies[companyId]
            usersList = companies[companyId]["users"]
            userDetail = list(filter(lambda user: user["id"] == userId, usersList))
            if userDetail:
                userInfo = copy.deepcopy(userDetail)[0]
                userInfo["service_roles"] = []
                userInfo["service_roles"].append(userInfo["services"][0]["roles"][0])
                userInfo.pop("services")
                userInfo["company"] = {}
                userInfo["company"].update({"id": companyDetail["id"], "legal_name": companyDetail["legal_name"],
                                            "display_name": companyDetail["display_name"],
                                            "number": companyDetail["number"], "verified": companyDetail["verified"],
                                            "updated_at": companyDetail["updated_at"]})
                return json.dumps(userInfo)
            else:
                return make_response("Unauthorized", 401)
        else:
            return make_response("Unauthorized", 401)

    @mockWrapper
    def OnV1GetUsersMe(self, **kwargs):
        """
        callback function for the route GET: /v1/users/me
        Authorization token format - CompanyID_UserID
        """

        tokenInfo = request.headers["Authorization"].replace("Bearer ", "").split("_")
        if len(tokenInfo) < 2:
            return make_response("Unauthorized", 401)

        userId = tokenInfo[1]
        userDetails = self.config["users"]

        if userId in userDetails:
            userInfo = copy.deepcopy(userDetails[userId])
            return json.dumps(userInfo)
        else:
            return make_response("Unauthorized", 401)

    @mockWrapper
    def onGetTokenInfo(self, **kwargs):
        """
        callback function for the route GET: /api/tokeninfo
        Authorization token format - CompanyID_UserID
        """

        tokenInfo = request.args.get("access_token").split("_")
        if len(tokenInfo) < 2:
            return make_response("Unauthorized", 401)

        tokenDetail = self.config["tokenInfo"]
        scopeInfo = copy.deepcopy(tokenDetail[self.service])

        return json.dumps(scopeInfo)

    @mockWrapper
    def onGetCompaniesMine(self, **kwargs):
        """
        callback function for the route GET: v2/companies/mine
        Authorization token format - CompanyID_UserID
        """

        tokenInfo = request.headers["Authorization"].replace("Bearer ", "").split("_")
        if len(tokenInfo) < 2:
            return make_response("Unauthorized", 401)

        companyId = tokenInfo[0]
        userId = tokenInfo[1]
        companies = self.config["companies"]
        if companyId in companies:
            companyInfo = copy.deepcopy(companies[companyId])
            usersList = companyInfo["users"]
            userDetail = list(filter(lambda user: user["id"] == userId, usersList))
            if userDetail:
                userInfo = copy.deepcopy(userDetail)[0]
                companyInfo["service_roles"] = []
                companyInfo["service_roles"].append(userInfo["services"][0]["roles"][0])
                companyInfo["role_in_company"] = userInfo["role_in_company"]
                companyInfo.pop("users")
                return json.dumps(companyInfo)
            else:
                return make_response("Unauthorized", 401)
        else:
            return make_response("Unauthorized", 401)

    @mockWrapper
    def onGetUserDetail(self, **kwargs):
        """
        callback function for the route GET: /api/v1/users/<userId>
        This routes uses static token. So we will get required information from kwargs
        """

        userId = kwargs.get("userId")
        companies = self.config["companies"]
        for company, companyDetails in companies.items():
            for users in companies[company]["users"]:
                if users["id"] == userId:
                    userResponse = copy.deepcopy(users)
                    userResponse["user_id"] = userResponse.pop("id")
                    userResponse["email"] = userResponse["contact"].pop("email")
                    userResponse["country_code"] = userResponse["contact"].pop("country_code")
                    userResponse["mobile"] = userResponse["contact"].pop("phone_number")
                    userResponse.pop("address")
                    userResponse.pop("role_in_company")
                    userResponse.pop("services")
                    return json.dumps(userResponse)
        return make_response("Unauthorized", 401)

    @mockWrapper
    def onGetUserInfo(self, **kwargs):
        """
        callback function for the route GET: /api/userinfo
        Authorization token format - CompanyID_UserID
        """

        tokenInfo = request.headers["Authorization"].replace("Bearer ", "").split("_")
        if len(tokenInfo) < 2:
            return make_response("Unauthorized", 401)

        companyId = tokenInfo[0]
        userId = tokenInfo[1]
        companies = self.config["companies"]
        if companyId in companies:
            companyInfo = copy.deepcopy(companies[companyId])
            usersList = companyInfo["users"]
            userDetail = list(filter(lambda user: user["id"] == userId, usersList))
            if userDetail:
                userResponse = copy.deepcopy(userDetail)[0]
                userResponse["user_id"] = userResponse.pop("id")
                userResponse["email"] = userResponse["contact"].pop("email")
                userResponse["country_code"] = userResponse["contact"].pop("country_code")
                userResponse["mobile"] = userResponse["contact"].pop("phone_number")
                userResponse["verified"] = companyInfo["verified"]
                userResponse.update({"referer_code": None, "active": True})
                userResponse.pop("contact")
                userResponse.pop("address")
                userResponse.pop("role_in_company")
                userResponse.pop("services")
                return json.dumps(userResponse)
            else:
                return make_response("Unauthorized", 401)
        else:
            return make_response("Unauthorized", 401)

    @mockWrapper
    def onGetCompaniesUserInfo(self, **kwargs):
        """
        callback function for the route GET: /v2/companies/<companyId>/users
        This routes uses static token. So we will get required information from kwargs
        """

        companyId = kwargs.get("companyId")
        companies = self.config["companies"]
        if companyId in companies:
            companyInfo = copy.deepcopy(companies[companyId])
            companyInfo.pop("address")
            companyInfo.pop("contact")
            return json.dumps(companyInfo)
        else:
            return make_response("Unauthorized", 401)

    @mockWrapper
    def onGetCompaniesInfo(self, **kwargs):
        """
        callback function for the route GET: /v1/companies/<companyId>
        This routes uses static token. So we will get required information from kwargs
        """

        companyId = kwargs.get("companyId")
        companies = self.config["companies"]
        if companyId in companies:
            companyInfo = copy.deepcopy(companies[companyId])
            for user in companyInfo["users"]:
                if user.get("services"):
                    user["role_in_products"] = user["services"][0]["roles"][0]
                    user.pop("services")
            return json.dumps(companyInfo)
        else:
            return make_response("Unauthorized", 401)

    @mockWrapper
    def onGetAllCompaniesInfo(self, **kwargs):
        """
        callback function for the route GET: /v1/companies
        Authorization token format - CompanyID_UserID
        """

        allCompaniesResponse = []
        companies = self.config["companies"]
        for company, companyDetails in companies.items():
            allCompaniesResponse.append(companies[company])
        return json.dumps(allCompaniesResponse)

    @mockWrapper
    def dialogAuthorize(self, **kwargs):
        """
        callback function for the route GET: /dialog/authorize
        URL format: http://54.193.90.192:7004/dialog/authorize?response_type=code&product_id=686e8a53-bf21-42e0-8b5d-25\
            2d95049f81&redirect_uri=https%3A%2F%2Fapi.automation.qubewire.com%2Fv1%2Fweb%2Fauth%2Fcallback&client_id=\
            8ff03e5cc86547b4a64d4321a6ad4fbc
        """

        url = "https://account.staging.qube.in/dialog/authorize?{0}".format(
            kwargs["request"].query_string.decode("utf-8"))
        return redirect(url, code = 302)

    def initialise(self):
        print("Hit qubeaccount.py Initialise method")
        self.daemon = True
        self.start()
        # adding little sleep as start & shutdown mock server very often creates connection problems
        time.sleep(0.5)
        self.add_response_callback(url = "/v2/users/me", callback = self.onGetUsersMe, methods = ["GET"])
        self.add_response_callback(url = "/v1/users/me", callback = self.OnV1GetUsersMe, methods = ["GET"])
        self.add_response_callback(url = "/api/tokeninfo", callback = self.onGetTokenInfo, methods = ["GET"])
        self.add_response_callback(url = "/v2/companies/mine", callback = self.onGetCompaniesMine, methods = ["GET"])
        self.add_response_callback(url = "/v2/companies/<companyId>/users", callback = self.onGetCompaniesUserInfo,
                                   methods = ["GET"])
        self.add_response_callback(url = "/v1/companies/<companyId>", callback = self.onGetCompaniesInfo,
                                   methods = ["GET"])
        self.add_response_callback(url = "/api/v1/users/<userId>", callback = self.onGetUserDetail, methods = ["GET"])
        self.add_response_callback(url = "/api/userinfo", callback = self.onGetUserInfo, methods = ["GET"])
        self.add_response_callback(url = "/v1/companies", callback = self.onGetAllCompaniesInfo, methods = ["GET"])
        self.add_response_callback(url = "/dialog/authorize", callback = self.dialogAuthorize, methods = ["GET"])


if __name__ == "__main__":

    QubeAccountMock(service = "distributors")
    while True:
        time.sleep(0.1)