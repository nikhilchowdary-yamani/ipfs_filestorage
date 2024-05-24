from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import datetime
import ipfsApi
import os
import json
from web3 import Web3, HTTPProvider
from django.core.files.storage import FileSystemStorage
import pickle
from ecies.utils import generate_eth_key, generate_key
from ecies import encrypt, decrypt
import time
import matplotlib.pyplot as plt
import numpy as np
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
import timeit
from hashlib import sha256
import matplotlib.pyplot as plt
import io
import base64
import numpy as np


api = ipfsApi.Client(host='http://127.0.0.1', port=5001)
global details, username
global enc_time, dec_time, extension_enc_time


#function to generate public and private keys for Chebyshev polynomial algorithm
def ChebyshevGenerateKeys():
    if os.path.exists("pvt.key"):
        with open("pvt.key", 'rb') as f:
            private_key = f.read()
        f.close()
        with open("pri.key", 'rb') as f:
            public_key = f.read()
        f.close()
        private_key = private_key.decode()
        public_key = public_key.decode()
    else:
        secret_key = generate_eth_key()
        private_key = secret_key.to_hex()  # hex string
        public_key = secret_key.public_key.to_hex()
        with open("pvt.key", 'wb') as f:
            f.write(private_key.encode())
        f.close()
        with open("pri.key", 'wb') as f:
            f.write(public_key.encode())
        f.close()
    return private_key, public_key

#Chebyshev will encrypt data using plain text adn public key
def ChebyshevEncrypt(plainText, public_key):
    cpabe_encrypt = encrypt(public_key, plainText)
    return cpabe_encrypt

#Chebyshev will decrypt data using private key and encrypted text
def ChebyshevDecrypt(encrypt, private_key):
    cpabe_decrypt = decrypt(private_key, encrypt)
    return cpabe_decrypt

def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'SmartContract.json' #Blockchain SmartContract calling code
    deployed_contract_address = '0xD1CE63114Ad554b1d0168C39B5f82f0882f3546F' #hash address to access Shared Data contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'signup':
        details = contract.functions.getSignup().call()
    if contract_type == 'attribute':
        details = contract.functions.getAccess().call()
    if contract_type == 'permission':
        details = contract.functions.getPermission().call()      
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'SmartContract.json' #Blockchain contract file
    deployed_contract_address = '0xD1CE63114Ad554b1d0168C39B5f82f0882f3546F' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'signup':
        details+=currentData
        msg = contract.functions.setSignup(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'attribute':
        details+=currentData
        msg = contract.functions.setAccess(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'permission':
        details+=currentData
        msg = contract.functions.setPermission(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)

def updateDataBlockChain(currentData):
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'SmartContract.json' #SmartContract file
    deployed_contract_address = '0xD1CE63114Ad554b1d0168C39B5f82f0882f3546F' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    msg = contract.functions.setPermission(currentData).transact()
    tx_receipt = web3.eth.waitForTransactionReceipt(msg)        

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def SharedData(request):
    if request.method == 'GET':
       global username       
       return render(request, 'SharedData.html', {})

def DownloadFileDataRequest(request):
    if request.method == 'GET':
        global dec_time
        hashcode = request.GET.get('hash', False)
        filename = request.GET.get('file', False)
        access = request.GET.get('access', False)
        readDetails('attribute')
        arr = details.split("\n")
        start_times = time.time()
        decrypted = None
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            share_user = array[6].split(",")
            if array[0] == 'post' and array[3] == hashcode:
                content = api.get_pyobj(array[3])
                private_key, public_key = ChebyshevGenerateKeys()
                decrypted = ChebyshevDecrypt(content, private_key)
                break
        end_times = time.time()
        dec_time = end_times - start_times
        if access == 'Private' or access == 'Public' or access == 'download':
            response = HttpResponse(decrypted,content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename='+filename
            return response
        else:
            #print("inline")
            #response['Content-Disposition'] = 'inline; filename='+filename
            #response = HttpResponse(decrypted,content_type='application/octet-stream')
            #response['Content-Disposition'] = 'inline; filename='+filename
            context = {'data': decrypted}
            return render(request, 'UserScreen.html', context)
            

def Permission(request):
    if request.method == 'GET':
        global username
        requester = request.GET.get('requester', False)
        owner = request.GET.get('owner', False)
        filename = request.GET.get('filename', False)
        permission = request.GET.get('permission', False)
        readDetails('permission')
        arr = details.split("\n")
        temp = ""
        selected = ""
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[0] == requester and array[1] == owner and array[2] == filename:
                selected = array[0]+"#"+array[1]+"#"+array[2]+"#"+array[3]+"#"+array[4]+"#"+permission+"\n"
                temp += selected
            else:
                temp += arr[i]+"\n"
        updateDataBlockChain(temp)
        context= {'data':filename+" permission set to "+permission+" for requester "+requester}
        return render(request, 'UserScreen.html', context)

def ViewRequest(request):
    if request.method == 'GET':
        global username
        strdata = '<table border=1 align=center width=100%><tr><th><font size="" color="black">Requester Name</th><th><font size="" color="black">Owner Name</th>'
        strdata+='<th><font size="" color="black">Filename</th><th><font size="" color="black">Hashcode</th>'
        strdata+='<th><font size="" color="black">Access Control</th><th><font size="" color="black">Permissions</th></tr>'
        readDetails('permission')
        arr = details.split("\n")
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[1] == username and array[5] == "Pending":
                strdata+='<tr><td><font size="" color="black">'+str(array[0])+'</td><td><font size="" color="black">'+array[1]+'</td><td><font size="" color="black">'+str(array[2])+'</td>'
                strdata+='<td><font size="" color="black">'+str(array[3])+'</td>'
                strdata+='<td><font size="" color="black">'+str(array[4])+'</td>'
                strdata+='<td><a href=\'Permission?requester='+array[0]+'&owner='+array[1]+'&filename='+array[2]+'&permission=read\'><font size=3 color=black>Read</font></a>'
                strdata+='&nbsp;&nbsp;<a href=\'Permission?requester='+array[0]+'&owner='+array[1]+'&filename='+array[2]+'&permission=download\'><font size=3 color=black>Download</font></a>'
                strdata+='</td></tr>'                
        context= {'data':strdata}
        return render(request, 'ViewSharedMessages.html', context)    
        
def SendRequest(request):
    if request.method == 'GET':
        global username
        owner = request.GET.get('owner', False)
        hashcode = request.GET.get('hash', False)
        filename = request.GET.get('file', False)
        access = request.GET.get('access', False)
        readDetails('permission')
        arr = details.split("\n")
        status = "none"
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[0] == username and array[1] == owner and array[2] == filename:
                status = "Your request for "+filename+" already posted to owner "+array[1]
                break
        if status == "none":
            data = username+"#"+owner+"#"+filename+"#"+hashcode+"#"+access+"#Pending\n"
            saveDataBlockChain(data,"permission")
            status = "Request Sent to owner "+owner            
        output = 'Shared Data saved in Blockchain with below hashcodes & Image file saved in IPFS.<br/>'+str(hashcode)
        context= {'data':status}
        return render(request, 'UserScreen.html', context)              

def getPermission(username, owner, filename):
    permission = "none"
    readDetails('permission')
    arr = details.split("\n")
    for i in range(len(arr)-1):
        array = arr[i].split("#")
        if array[0] == username and array[1] == owner and array[2] == filename:
            if array[5] == 'download':
                permission = "download"
                break
            if array[5] == 'read':
                permission = "read"
                break
    return permission    

def ViewSharedMessages(request):
    if request.method == 'GET':
        global enc_time, dec_time, username
        dec_time = 0
        strdata = '<table border=1 align=center width=100%><tr><th><font size="" color="black">Data Owner</th><th><font size="" color="black">Shared Message</th>'
        strdata+='<th><font size="" color="black">IPFS File Address</th><th><font size="" color="black">Shared Date Time</th>'
        strdata+='<th><font size="" color="black">Shared File Name</th><th><font size="" color="black">Access Control</th>'
        strdata+='<th><font size="" color="black">Download File</th></tr>'
        readDetails('attribute')
        arr = details.split("\n")
        start_times = time.time()
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[0] == 'post':
                strdata+='<tr><td><font size="" color="black">'+str(array[1])+'</td><td><font size="" color="black">'+array[2]+'</td><td><font size="" color="black">'+str(array[3])+'</td>'
                strdata+='<td><font size="" color="black">'+str(array[4])+'</td>'
                strdata+='<td><font size="" color="black">'+str(array[5])+'</td>'
                strdata+='<td><font size="" color="black">'+str(array[6])+'</td>'
                if  (array[6] == 'Private' or array[6] == 'Public') and array[1] == username:
                    strdata+='<td><a href=\'DownloadFileDataRequest?hash='+array[3]+'&file='+array[5]+'&access='+array[6]+'\'><font size=3 color=black>Download File</font></a></td></tr>'
                elif array[6] == 'Public' and array[1] != username:
                    strdata+='<td><a href=\'DownloadFileDataRequest?hash='+array[3]+'&file='+array[5]+'&access='+array[6]+'\'><font size=3 color=black>Download File</font></a></td></tr>'
                elif array[6] == 'Private' and array[1] != username:
                    permission = getPermission(username, array[1], array[5])
                    if permission == "none":
                        strdata+='<td><a href=\'SendRequest?owner='+array[1]+'&hash='+array[3]+'&file='+array[5]+'&access='+array[6]+'\'><font size=3 color=black>Send Request</font></a></td></tr>'
                    if permission == "download":
                        strdata+='<td><a href=\'DownloadFileDataRequest?hash='+array[3]+'&file='+array[5]+'&access=download\'><font size=3 color=black>Download File</font></a></td></tr>'
                    if permission == "read":
                        strdata+='<td><a href=\'DownloadFileDataRequest?hash='+array[3]+'&file='+array[5]+'&access=read\'><font size=3 color=black>Read File</font></a></td></tr>'
        end_times = time.time()
        dec_time = end_times - start_times
        context= {'data':strdata}
        return render(request, 'ViewSharedMessages.html', context)        
         

def LoginAction(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        readDetails('signup')
        arr = details.split("\n")
        status = "none"
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[1] == username and password == array[2]:
                status = "Welcome "+username
                break
        if status != 'none':
            file = open('session.txt','w')
            file.write(username)
            file.close()   
            context= {'data':status}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'Login.html', context)

        
def SharedDataAction(request):
    if request.method == 'POST':
        global enc_time, username, extension_enc_time
        post_message = request.POST.get('t1', False)
        access = request.POST.get('t3')
        filename = request.FILES['t2'].name
        start = time.time()
        myfile = request.FILES['t2'].read()
        myfile = pickle.dumps(myfile)
        private_key, public_key = ChebyshevGenerateKeys()
        cheb_encrypt = ChebyshevEncrypt(myfile, public_key)
        print(type(cheb_encrypt))
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        user = username
        hashcode = api.add_pyobj(cheb_encrypt)
        data = "post#"+user+"#"+post_message+"#"+str(hashcode)+"#"+str(current_time)+"#"+filename+"#"+access+"\n"
        end = time.time()
        enc_time = end - start

        start = timeit.default_timer()
        key = get_random_bytes(32)
        cipher = ChaCha20.new(key=key)
        ciphertext = cipher.encrypt(myfile)
        end = timeit.default_timer()
        extension_enc_time = end - start
        saveDataBlockChain(data,"attribute")
        output = 'Shared Data saved in Blockchain with below hashcodes & Image file saved in IPFS.<br/>'+str(hashcode)
        output += '<br/>Propose Chebyshev Encryption Time : '+str(enc_time)+'<br/>'
        output += 'Extension CHACHA Algorithm Encryption Time : '+str(extension_enc_time)+'<br/>' 
        context= {'data':output}
        return render(request, 'SharedData.html', context)
        

def SignupAction(request):
    if request.method == 'POST':
        global details
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        gender = request.POST.get('t4', False)
        email = request.POST.get('t5', False)
        address = request.POST.get('t6', False)
        output = "Username already exists"
        readDetails('signup')
        arr = details.split("\n")
        status = "none"
        for i in range(len(arr)-1):
            array = arr[i].split("#")
            if array[1] == username:
                status = username+" already exists"
                break
        if status == "none":
            details = ""
            data = "signup#"+username+"#"+password+"#"+contact+"#"+gender+"#"+email+"#"+address+"\n"
            saveDataBlockChain(data,"signup")
            context = {"data":"Signup process completed and record saved in Blockchain"}
            return render(request, 'Signup.html', context)
        else:
            context = {"data":status}
            return render(request, 'Signup.html', context)

def Graph(request):
    if request.method == 'GET':
        global username
        global enc_time, dec_time, extension_enc_time
        height = [enc_time, dec_time, extension_enc_time]
        bars = ('ABE Communication Overhead', 'Propose Communication Overhead', 'Extension CHA CHA Encryption')
        y_pos = np.arange(len(bars))
        plt.bar(y_pos, height)
        plt.xticks(y_pos, bars)
        plt.title("Communication Overhead Graph")
        plt.show()
        context = {"data":"Welcome "+username}
        return render(request, 'UserScreen.html', context)
