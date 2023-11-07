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
    
    return jsonify({
        "IP": ip_address[0],
        "DKIM": dkim,
        "SPF": spf,
        "DMARC": dmarc}), 200 

@app.route('/ip_reputation', methods=['POST'])
def getIpReputation():
    data = request.get_json()
    ip = data.get("ip")
    url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}&maxAgeInDays=90&verbose"

    headers = {
        "Key": "",
        "Accept": "application/json"
    }

    reputation = requests.get(url, headers=headers)
    reputation_data = reputation.json()
    return jsonify(reputation_data)



if __name__ == "__main__":
    app.run(debug=True)