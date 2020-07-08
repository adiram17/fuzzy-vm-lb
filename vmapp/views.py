from django.shortcuts import render
import requests
from django.http import JsonResponse

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

#Set up fuzzy logic controller
def setUpFuzzyLogic():
    # New Antecedent/Consequent objects hold universe variables and membership
    # functions
    cpu = ctrl.Antecedent(np.arange(0, 100, 11), 'cpu')
    memory = ctrl.Antecedent(np.arange(0, 100, 11), 'memory')
    disk = ctrl.Antecedent(np.arange(0, 100, 11), 'disk')

    status = ctrl.Consequent(np.arange(0, 100, 11), 'status')

    # Custom membership functions can be built interactively with a familiar,
    # Pythonic API
    cpu['low'] = fuzz.trapmf(cpu.universe, [0, 0, 30, 45])
    cpu['medium'] = fuzz.trapmf(cpu.universe, [30, 45, 75, 90])
    cpu['high'] = fuzz.trapmf(cpu.universe, [75, 90, 100, 100])

    memory['low'] = fuzz.trapmf(memory.universe, [0, 0, 30, 45])
    memory['medium'] = fuzz.trapmf(memory.universe, [30, 45, 75, 90])
    memory['high'] = fuzz.trapmf(memory.universe, [75, 90, 100, 100])

    disk['low'] = fuzz.trapmf(disk.universe, [0, 0, 30, 45])
    disk['medium'] = fuzz.trapmf(disk.universe, [30, 45, 75, 90])
    disk['high'] = fuzz.trapmf(disk.universe, [75, 90, 100, 100])

    status['very low'] = fuzz.trapmf(status.universe, [0, 0, 10, 30])
    status['low'] = fuzz.trimf(status.universe, [10, 30, 50])
    status['medium'] = fuzz.trimf(status.universe, [30, 50, 70])
    status['high'] = fuzz.trimf(status.universe, [50, 70, 90])
    status['very high'] = fuzz.trapmf(status.universe, [70, 90, 100, 100])

    rule1 = ctrl.Rule(cpu['low'] & memory['low'] & disk['low'], status['very low'])
    rule2 = ctrl.Rule(cpu['low'] & memory['low'] & disk['medium'], status['very low'])
    rule3 = ctrl.Rule(cpu['low'] & memory['low'] &disk['high'], status['low'])
    rule4 = ctrl.Rule(cpu['low'] & memory['medium'] & disk['low'], status['very low'])
    rule5 = ctrl.Rule(cpu['low'] & memory['medium'] & disk['medium'], status['medium'])
    rule6 = ctrl.Rule(cpu['low'] & memory['medium'] & disk['high'], status['medium'])
    rule7 = ctrl.Rule(cpu['low'] & memory['high'] & disk['low'], status['low'])
    rule8 = ctrl.Rule(cpu['low'] & memory['high'] & disk['medium'], status['medium'])
    rule9 = ctrl.Rule(cpu['low'] & memory['high'] & disk['high'], status['high'])
    rule10 = ctrl.Rule(cpu['medium']  & memory['low'] & disk['low'], status['very low'])
    rule11 = ctrl.Rule(cpu['medium']  & memory['low'] & disk['medium'], status['medium'])
    rule12 = ctrl.Rule(cpu['medium']  & memory['low'] & disk['high'], status['medium'])
    rule13 = ctrl.Rule(cpu['medium']  & memory['medium'] & disk['low'], status['medium'])
    rule14 = ctrl.Rule(cpu['medium']  & memory['medium'] & disk['medium'], status['medium'])
    rule15 = ctrl.Rule(cpu['medium']  & memory['medium'] & disk['high'], status['high'])
    rule16 = ctrl.Rule(cpu['medium']  & memory['high'] & disk['low'], status['medium'])
    rule17 = ctrl.Rule(cpu['medium']  & memory['high'] & disk['medium'], status['high'])
    rule18 = ctrl.Rule(cpu['medium']  & memory['high'] & disk['high'], status['very high'])
    rule19 = ctrl.Rule(cpu['high'] & memory['low'] & disk['low'], status['low'])
    rule20 = ctrl.Rule(cpu['high'] & memory['low'] & disk['medium'], status['medium'])
    rule21 = ctrl.Rule(cpu['high'] & memory['low'] & disk['high'], status['high'])
    rule22 = ctrl.Rule(cpu['high'] & memory['medium'] & disk['low'], status['medium'])
    rule23 = ctrl.Rule(cpu['high'] & memory['medium'] & disk['medium'], status['high'])
    rule24 = ctrl.Rule(cpu['high'] & memory['medium'] & disk['high'], status['very high'])
    rule25 = ctrl.Rule(cpu['high'] & memory['high'] & disk['low'], status['very high'])
    rule26 = ctrl.Rule(cpu['high'] & memory['high'] & disk['medium'], status['very high'])
    rule27 = ctrl.Rule(cpu['high'] & memory['high'] & disk['high'], status['very high'])

    server_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26, rule27])
    server_ctrl_simulation = ctrl.ControlSystemSimulation(server_ctrl)
    return server_ctrl_simulation

#Calculate fuzzy logic
def calculateFuzzy(cpu, memory, disk):
    server = setUpFuzzyLogic()
    server.input['cpu'] = cpu
    server.input['memory'] = memory
    server.input['disk'] = disk
    server.compute()
    score=server.output['status']
    return score

#Check VM Server Status 
def getCpuMemoryDisk(ipportserver):
    cpu=None
    memory=None
    disk=None
    url = "http://"+ipportserver+"/getCpuMemoryDisk/"
    response = requests.request("GET", url)
    if (response.status_code==200):
        cpu=response.json().get('cpu')
        memory=response.json().get('memory')
        disk=response.json().get('disk')
    return cpu, memory, disk

#Check VM Server Status 
def getMessageFromWebServer(ipportserver):
    ipaddress=None
    hostname=None
    url = "http://"+ipportserver+"/getMessage/"
    response = requests.request("GET", url)
    statusCode=response.status_code
    if (response.status_code==200):
        ipaddress=response.json().get('ipaddress')
        hostname=response.json().get('hostname')
    return ipaddress, hostname, statusCode



#Get Response Server 
def getMessage(request):
    ipportservers=['192.168.1.6:8001', '192.168.1.6:8002', '192.168.1.6:8003']
    choosenServer=None
    scoreTemp=100
    #check VM server status and choose the lowest score
    for ipportserver in ipportservers:
        cpu, memory, disk = getCpuMemoryDisk(ipportserver)
        if (cpu!=None and memory!=None and disk!=None):
            score = calculateFuzzy(cpu, memory, disk)
            print("Server: "+ipportserver, 'cpu: '+str(cpu),'memory: '+str(memory),'disk: '+str(disk), 'score: '+str(score))
            if score<=scoreTemp:
                scoreTemp=score
                choosenServer=ipportserver
    if (choosenServer!=None):
        ipaddress, hostname, statusCode = getMessageFromWebServer(choosenServer)
        print("Redirect to server: "+choosenServer)
    response_data = {}
    response_data['ipaddress'] = ipaddress
    response_data['hostname'] = hostname
    response_data['statusCode'] = statusCode
    return JsonResponse(response_data)