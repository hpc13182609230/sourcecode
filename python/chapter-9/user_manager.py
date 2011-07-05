###############################################
# RabbitMQ in Action
# Chapter 9 - RMQ User Manager
###############################################
# 
#   USAGE: 
#       # user_vhost_manager.py "host" "auth_user" "auth_pass" create 'user' 'password' 'true/false'
#                               "host" "auth_user" "auth_pass" delete 'user'
#                               "host" "auth_user" "auth_pass" list
#                               "host" "auth_user" "auth_pass" show 'user'
# 
# Author: Jason J. W. Williams
# (C)2011
###############################################
import sys, json, httplib, base64

base_path = "/api/users"

#/(uvm.1) Assign arguments
if len(sys.argv) < 5:
    print "USAGE: user_vhost_manager.py server_name:port auth_user auth_pass",
    print "ACTION RESOURCE [PARAMS...]"
    sys.exit(1)

server, port = sys.argv[1].split(":")
username = sys.argv[2]
password = sys.argv[3]
action = sys.argv[4]

if len(sys.argv) > 5:
    res_params = sys.argv[5:]
else:
    res_params = []

#/(uvm.2) Connect to server
conn = httplib.HTTPConnection(server, port)

#/(uvm.3) Build API path
if action == "list":
    path = base_path
    method = "GET"
if action == "create":
    path = base_path + "/" + res_params[0]
    method = "PUT"
if action == "delete":
    path = base_path + "/" + res_params[0]
    method = "DELETE"
if action == "show":
    path = base_path + "/" + res_params[0]
    method = "GET"


#/(uvm.4) Build JSON arguments
json_args = ""
if action == "create":
    json_args = {"password" : res_params[1],
                 "administrator" : json.loads(res_params[2])}
    json_args = json.dumps(json_args)

#/(uvm.5) Issue API request
credentials = base64.b64encode("%s:%s" % (username, password))
conn.request(method, path, json_args,
             {"Content-Type" : "application/json",
              "Authorization" : "Basic " + credentials})
response = conn.getresponse()
if response.status > 299:
    print "Error executing API call (%d): %s" % (response.status,
                                                 response.read())
    sys.exit(2)

#/(uvm.6) Parse and display response
resp_payload = response.read()
if action in ["list", "show"]:
    resp_payload = json.loads(resp_payload)
    
    #/(uvm.7) Process 'list' results
    if action == "list":
        print "Count: %d" % len(resp_payload)
        for user in resp_payload:
            print "User: %(name)s" % user
            print "\tPassword: %(password_hash)s" % user
            print "\tAdministrator: %(administrator)s\n" % user
    
    #/(uvm.8) Process 'show' results
    if action == "show":
        print "User: %(name)s" % resp_payload
        print "\tPassword: %(password_hash)s" % resp_payload
        print "\tAdministrator: %(administrator)s\n" % resp_payload
else:
    print "Completed request!"

sys.exit(0)