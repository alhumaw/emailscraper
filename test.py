from flask import Flask, request, jsonify
import platform,socket,re,uuid,json,psutil,logging
import requests
import os
from dotenv import load_dotenv
app = Flask(__name__)

@app.route('/get_info', methods=['GET'])
def getInfo():
    operating_system = platform.system()
    release = platform.release()
    version = platform.version()
    ip = socket.gethostbyname(socket.gethostname())
    load_dotenv()
    KEY = os.getenv("API_KEY")
    return jsonify({
        "OS": operating_system,
        "Release": release,
        "Version": version,
        "IP": ip
        })

@app.route('/scrape',methods=["POST"])
def scrape():
    file = request.files['file']
    contents = file.read().decode("UTF-8")
    big_list = contents.split(" ")
    for items in big_list:
        if "client-ip=" in items:
            block = items.split("=")
            ip_address_semi = block[1]
            ip_address = ip_address_semi.split(";")
        if "dkim=" in items:
            dkim = items
        if "spf=" in items:
            spf = items
        if "dmarc=" in items:
            dmarc = items
    
    resp = {
        "DKIM": dkim,
        "SPF": spf,
        "DMARC": dmarc,
        "IP": ip_address[0],
        "REPUTATION": getIpReputation(ip_address[0])
    }
    return resp

def getIpReputation(ip):
    url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}&maxAgeInDays=90&verbose"
    KEY = os.getenv("API_KEY")
    headers = {
        "Key": KEY,
        "Accept": "application/json"
    }

    reputation = requests.get(url, headers=headers)
    reputation_data = reputation.json()
    data = reputation_data["data"]
    abuseScore = data['abuseConfidenceScore']
    country = data['countryName']
    isPublic = data['isPublic']
    isp = data['isp']
    dataRet = {
        "abuseScore": abuseScore,
        "country": country,
        "isPublic": isPublic,
        "ISP": isp
    }

    return dataRet



if __name__ == "__main__":
    app.run(debug=True)