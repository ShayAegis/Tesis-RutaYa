#include "config.h"
#include "Sim7000.h"


Sim7000G::Sim7000G(const int rxPin,const int txPin,const int PWRKEY): rx(rxPin), tx(txPin), PWRKEY(PWRKEY), serialAT(2) {}

bool Sim7000G::begin() {

    serialAT.begin(115200, SERIAL_8N1, rx, tx);
    delay(1000);

    if(isModemAlive()) {
        Serial.println("[SIM] Debug Modem estaba vivo");
        sendAT("AT+CFUN=1,1");
        delay(2000);
    } else{
        powerOn();
    }

    sendAT("ATE0");

    unsigned long initTime = millis();
    const int initTimeout = 20000;
    while(!isModemAlive() && (millis() - initTime < initTimeout)){
        Serial.print(".");
    }
    Serial.println("");
    return isModemAlive();
}

String Sim7000G::sendATVerbose(const char* cmd, unsigned long timeout_ms){
    sendAT(cmd);
    String response = readAT(timeout_ms);
    Serial.println("[SIM][AT] " + String(cmd) + " -> " + response);
    return response;
}

HTTPResponse Sim7000G::httpsBegin(HTTPRequest request){

    if(request.getBaseUrl().startsWith("https://")){

        sendAT("AT+CSSLCFG=\"sslversion\",1,3");
        readAT(2000);

        sendAT("AT+CSSLCFG=\"ciphersuite\",1,0,0xC02C");
        readAT(2000);

        String sniCmd = "AT+CSSLCFG=\"sni\",1,\"" + request.getHost() + "\"";
        sendAT(sniCmd.c_str());
        readAT(2000);

        sendAT("AT+CSSLCFG=\"ignorertctime\",1,1");
        readAT(2000);

        sendAT("AT+SHSSL=1,\"\"");
        readAT(2000);
    }

    delay(1000);
    String setUrlCmd = "AT+SHCONF=\"URL\",\"" + request.getBaseUrl() + "\"";
    sendAT(setUrlCmd.c_str());
    readAT(2000);

    sendAT("AT+SHCONF=\"BODYLEN\",1024");
    readAT(2000);

    sendAT("AT+SHCONF=\"HEADERLEN\",350");
    readAT(2000);

    sendAT("AT+SHCONF=\"IPVER\",0");
    readAT(2000);

    sendAT("AT+SHCONF=\"TIMEOUT\",30");
    readAT(2000);

    sendAT("AT+SHCONN");
    String connResult = readAT(30000);

    if(connResult.indexOf("OK") == -1){
        Serial.println("[SIM][HTTPS] FALLO DE CONEXION - abortando. Respuesta del módem: " + connResult);
        sendAT("AT+SHDISC");
        readAT(2000);
        return HTTPResponse{"", -1};
    }

    sendAT("AT+SHSTATE?");
    readAT(2000);

    for(const auto& header : request.getHeaders()){
        for(const auto& entry : header){
            String headerCmd = "AT+SHAHEAD=\"" + entry.first + "\",\"" + entry.second + "\"";
            sendAT(headerCmd.c_str());
            readAT(2000);
        }
    }

    if(request.getBody().length() > 0){
        String rawBody = request.getBody();
        int bodySize = rawBody.length();
        String escapedBody = rawBody;
        escapedBody.replace("\"", "\\\"");
        String bodyCmd = "AT+SHBOD=\"" + escapedBody + "\"," + String(bodySize);
        sendAT(bodyCmd.c_str());
        readAT(2000);
    }

    String reqCmd = "AT+SHREQ=\""+ request.getEndpoint() +"\","+ request.getMethod();
    sendAT(reqCmd.c_str());

    String reqResult;

    unsigned long start = millis();

    while (millis() - start < 30000) {

        reqResult += readAT(500);

        if(reqResult.indexOf("+SHREQ:") != -1){
            break;
        }
    }

    int dataLen = 0;
    int statusCode = -1;
    int shreqIdx = reqResult.indexOf("+SHREQ:");
    if(shreqIdx != -1){
        int lastComma = reqResult.lastIndexOf(',');
        dataLen = reqResult.substring(lastComma + 1).toInt();
        int secondLastComma = reqResult.lastIndexOf(',', lastComma - 1);
        statusCode = reqResult.substring(secondLastComma + 1, lastComma).toInt();
    }

    String response = "";
    if(dataLen > 0){
        String readCmd = "AT+SHREAD=0," + String(dataLen);
        sendAT(readCmd.c_str());
        response = readAT(3000);
    }

    sendAT("AT+SHDISC");
    readAT(2000);
    
    int jsonStart = response.indexOf('{');
    int jsonEnd = response.lastIndexOf('}');
    if(jsonStart == -1 || jsonEnd == -1 || jsonEnd < jsonStart) return {"",-1};
    return {response.substring(jsonStart, jsonEnd + 1),statusCode};
}

bool Sim7000G::connectNetwork(const char* apn){
    
    if(!registerInNetwork()) return false;
    if(checkBearerStatus(1) == BearerStatus_t::BEARER_CLOSED){
        if(!openBearer(1,apn)){
            return false;
        }
    }
    
    String ipAddr = getBearerIp(1);
    Serial.println("[SIM] Info: IP: "+ipAddr);
    if(!isDataActive()){
        Serial.println("[SIM] Debug: Data Enable " + String(enableMobileData(apn) ? "OK" : "ERROR"));
    }
    return ipAddr != "" && ipAddr != "0.0.0.0" && checkBearerStatus(1) ==  BearerStatus_t::BEARER_CONNECTED;
}

bool Sim7000G::mqttConnect(const char* clientId,const char* mqttBrokerUrl,const int mqttPort,const char* username,const char* password){

    unsigned long t = millis();
    while (!isDataActive() && millis() - t < 10000) {
        Serial.print(".");
        delay(500);
    }
    if (!isDataActive()) {
        return false;
    }

    sendAT("AT+SMSTATE?");
    String state = readAT(2000);

        if (state.indexOf("+SMSTATE: 1") != -1) {
        sendAT("AT+SMDISC");
        readAT(3000);
        delay(1000);
    }


    String cmd;

    cmd = "AT+SMCONF=\"CLIENTID\",\"" + String(clientId) + "\"";
    sendAT(cmd.c_str());
    delay(100);

    cmd = "AT+SMCONF=\"URL\",\"" + String(mqttBrokerUrl) + "\",\"" + String(mqttPort) + "\"";
    sendAT(cmd.c_str());
    delay(100);

    sendAT("AT+SMCONF=\"KEEPTIME\",60");
    delay(100);

    sendAT("AT+SMCONF=\"CLEANSS\",1");
    delay(100);

    cmd = "AT+SMCONF=\"USERNAME\",\"" + String(username) + "\"";
    sendAT(cmd.c_str());
    delay(100);

    cmd = "AT+SMCONF=\"PASSWORD\",\"" + String(password) + "\"";
    sendAT(cmd.c_str());
    delay(100);

    sendAT("AT+SMCONN");
    String connResult = readAT(10000);

    return connResult.indexOf("OK") != -1;
}

bool Sim7000G::pubMqtt(const char* topic, const char* payload,int qos){
    int payloadLen = strlen(payload);
    String cmd = "AT+SMPUB=\"" + String(topic) + "\"," + 
            String(payloadLen) + "," + 
            String(qos) + ",0";
    sendAT(cmd.c_str());  

    unsigned long t = millis();
    String response = "";
    while (millis() - t < 5000) {
        while (serialAT.available()) {
            response += (char)serialAT.read();
        }
        if (response.indexOf(">") != -1) break;
    }

    if (response.indexOf(">") == -1) {
        return false;
    }

    serialAT.print(payload);

    String result = readAT(5000);

    return result.indexOf("OK") != -1;
}

bool Sim7000G::enableMobileData(const char* apn){
    const String enableDataCmd = "AT+CNACT=1,\"" + String(apn) + "\"";
    sendAT(enableDataCmd.c_str());
    delay(500);
    String enableDataResponse = readAT(2000);
    return enableDataResponse.indexOf("OK") != -1;
}

bool Sim7000G::isDataActive() {

    sendAT("AT+CNACT?");
    String response = readAT(2000);

    int statusStart = response.indexOf("+CNACT:");
    if (statusStart == -1) {
        return false;
    }

    int valueStart = response.indexOf(":", statusStart) + 1;
    int commaIndex = response.indexOf(",", valueStart);

    String statusText = response.substring(valueStart, commaIndex);
    statusText.trim();

    int status = statusText.toInt();

    return status == 1;
}

bool Sim7000G::registerInNetwork(){
    /*-- Realizando registro en red --*/
    sendAT("AT+CREG=0");

    unsigned long start = millis();
    const unsigned long registerTimeout = 60000;

    do {
        sendAT("AT+CREG?");
        String regResponse = readAT(2000);

        if (regResponse.indexOf("+CREG: 0,1") != -1 ||
            regResponse.indexOf("+CREG: 0,5") != -1) {
            return true;
        }
    } while (millis() - start < registerTimeout);

    Serial.println("[SIM] Error: sin registro en red");
    return false;
}

bool Sim7000G::openBearer(int cid, const char* apn){
    const String setApnCmd = "AT+SAPBR=3," + String(cid) + ",\"APN\",\"" + String(apn) + "\"";
    sendAT(setApnCmd.c_str());
    String openBearerCmd = "AT+SAPBR=1,"+String(cid);
    sendAT(openBearerCmd.c_str());

    delay(1000);

    String brResponse = readAT(2000);
    return brResponse.indexOf("OK") != -1 && checkBearerStatus(1) == BearerStatus_t::BEARER_CONNECTED;
}

String Sim7000G::getSimNumber(){
    sendAT("AT+CNUM");
    String response = readAT(2000);
    int cnumStart = response.indexOf("+CNUM:");
    if(cnumStart == -1) return "";
    int firstQuote = response.indexOf('"', cnumStart);
    int secondQuote = response.indexOf('"', firstQuote + 1);
    int numStart = response.indexOf('"', secondQuote + 1);
    int numEnd = response.indexOf('"', numStart + 1);
    if(numStart == -1 || numEnd == -1) return "";
    return response.substring(numStart + 1, numEnd);
}

String Sim7000G::getImei(){
    const char* cmd = "AT+GSN";
    sendAT(cmd);
    String response = readAT(2000);
    int beginIndex = response.indexOf(cmd);
    int okIndex = response.indexOf("OK");
    if(okIndex == -1) return "";
    String imei = response.substring(beginIndex+String(cmd).length(), okIndex);
    imei.trim();
    return imei;
}

String Sim7000G::getIccid(){
    const char* cmd = "AT+CCID";
    sendAT(cmd);
    String response = readAT(2000);
    int labelIndex = response.indexOf(cmd);
    int okIndex = response.indexOf("OK");
    if(okIndex == -1) return "";
    String iccid = response.substring(labelIndex+String(cmd).length(), okIndex);

    iccid.trim();
    return iccid;
}

BearerStatus_t Sim7000G::checkBearerStatus(int cid){
    String cmd = "AT+SAPBR=2," + String(cid);
    sendAT(cmd.c_str());
    String bearerQuery = readAT(2000);
    int iResponse = bearerQuery.indexOf("+SAPBR: ");
    if(iResponse != -1){
        int firstComma = bearerQuery.indexOf(",",iResponse);
        int secondComma = bearerQuery.indexOf(",",firstComma+1);
        int status = bearerQuery.substring(firstComma+1,secondComma).toInt();
        return (BearerStatus_t) status;
    }
    return BearerStatus_t::ERROR;
}

String Sim7000G::getBearerIp(int cid){
    String cmd = "AT+SAPBR=2," + String(cid);
    sendAT(cmd.c_str());
    String bearerQuery = readAT(2000);
    String ip = "";
    int firstQuote = bearerQuery.indexOf('"');
    int secondQuote = bearerQuery.indexOf('"', firstQuote + 1);
    if(firstQuote != -1 && secondQuote != -1){
        ip = bearerQuery.substring(firstQuote+1,secondQuote);
        ip.trim();
    }
    return ip;
}

bool Sim7000G::gpsBegin(bool aGps) {
    sendAT("AT+CGNSPWR=1");
    String pwrResult = readAT(2000);
    if (pwrResult.indexOf("OK") == -1) {
        Serial.println("[SIM] Error: no se pudo encender GPS");
        return false;
    }

    sendAT("AT+CGNSCOLD");
    readAT(2000);

    sendAT("AT+CGPIO=0,48,1,1");
    readAT(2000);

    if (aGps) { 
        sendAT("AT+HTTPTOFS=\"http://xtrapath1.izatcloud.net/xtra3grc.bin\",\"/customer/xtra3grc.bin\"");
        
        unsigned long t = millis();
        String httpResult = "";
        while (millis() - t < 60000) {
            httpResult += readAT(2000);
            if (httpResult.indexOf("+HTTPTOFS:") != -1) break;
        }
        
        if (httpResult.indexOf("+HTTPTOFS: 200") == -1) {
            Serial.println("[AGPS] Warning: descarga AGPS falló, continuando sin AGPS");
        }
        else {
            sendAT("AT+CGNSCPY");
            sendAT("AT+CGNSXTRA=1");
        }
    }

    sendAT("AT+CGNSPWR?");
    String stateResult = readAT(2000);

    return stateResult.indexOf("+CGNSPWR: 1") != -1;
}

LatLng_t Sim7000G::getLatLng(){
    return _cachedGpsData.latLng;
}

float Sim7000G::getSpeed(){
    return _cachedGpsData.speed;
}

float Sim7000G::getAzimuth(){
    return _cachedGpsData.azimuth;
}


bool Sim7000G::isGpsFixed(){
    return _cachedGpsData.fixStatus;
}

void Sim7000G::updateGps(){
    _cachedGpsData = parseGps(getRawGps());
}

GpsData_t Sim7000G::parseGps(String rawGpsData){
    if(rawGpsData == "ERROR" || rawGpsData.isEmpty())
        return {};
    int commaPos[20]={-1};
    int commaCount = 0;
    for(int i=0;i<rawGpsData.length() && commaCount<20;i++){
        if(rawGpsData[i] == ','){
            commaPos[commaCount++] = i;
        }
    }
    const bool fixStatus = (bool) rawGpsData.substring(commaPos[0] + 1, commaPos[1]).toInt();
    const String dateTime = rawGpsData.substring(commaPos[1] + 1,commaPos[2]);
    const float lat      = rawGpsData.substring(commaPos[2] + 1, commaPos[3]).toFloat();
    const float lon      = rawGpsData.substring(commaPos[3] + 1, commaPos[4]).toFloat();
    const float speed    = rawGpsData.substring(commaPos[5] + 1, commaPos[6]).toFloat();
    const float azimuth = rawGpsData.substring(commaPos[6]+1, commaPos[7]).toFloat();

    Serial.println("[SIM] Fix: " + String(fixStatus) +
                " DateTime: " + dateTime +
                " Lat: " + String(lat, 6) +
                " Lon: " + String(lon, 6) +
                " Speed: " + String(speed, 2) +
                " Azimuth: " + String(azimuth));

    return {fixStatus,dateTime,{lat,lon},speed,azimuth};
}

String Sim7000G::getRawGps(){
    sendAT("AT+CGNSINF");
    String rawGpsResponse = readAT(2000);
    int iRawGpsStart = rawGpsResponse.indexOf("+CGNSINF:");
    if(iRawGpsStart == -1)
        return "ERROR";
    int iRawGpsEnd = rawGpsResponse.indexOf("OK");
    String rawGps = rawGpsResponse.substring(iRawGpsStart+9,iRawGpsEnd);
    rawGps.trim();
    return rawGps;
}

bool Sim7000G::syncNTP(const char* ntpServer) {
    sendAT("AT+CNTPCID=1");
    readAT(2000);

    String cmd = "AT+CNTP=\"" + String(ntpServer) + "\",0,1";
    sendAT(cmd.c_str());
    readAT(2000);

    sendAT("AT+CNTP");

    unsigned long t = millis();
    String result = "";
    while (millis() - t < 10000) {
        result += readAT(2000);
        if (result.indexOf("+CNTP:") != -1) break;
    }
    return result.indexOf("+CNTP: 1") != -1;
}

time_t Sim7000G::getTimestamp() {
    sendAT("AT+CCLK?");
    String response = readAT(2000);

    int quote = response.indexOf('"');
    if (quote == -1) {
        Serial.println("[SIM] Error: no se pudo leer hora");
        return 0;
    }

    String dt = response.substring(quote + 1, response.indexOf('"', quote + 1));

    struct tm t = {};
    t.tm_year = dt.substring(0, 2).toInt() + 100;
    t.tm_mon  = dt.substring(3, 5).toInt() - 1;
    t.tm_mday = dt.substring(6, 8).toInt();
    t.tm_hour = dt.substring(9, 11).toInt();
    t.tm_min  = dt.substring(12, 14).toInt();
    t.tm_sec  = dt.substring(15, 17).toInt();
    t.tm_isdst = 0;

    time_t timestamp = mktime(&t);
    return timestamp;
}

float Sim7000G::getRSSI(){

    sendAT("AT+CSQ");
    String csqResponse = readAT(2000);
    int csqStart = csqResponse.indexOf("+CSQ:");
    if(csqStart == -1){
        return 99.0f;
    }
    int rssiComma = csqResponse.indexOf(",",csqStart+5);
    String rssiValue = csqResponse.substring(csqStart+5,rssiComma+2);
    rssiValue.trim();
    float rssi = rssiValue.toFloat();
    if(rssi == 99 || rssi == 0){
        return 99.0f;
    }
    float rssidBm = (rssi * 2) - 113; 
    return rssidBm;
}

bool Sim7000G::isModemAlive() {
    while (serialAT.available()) serialAT.read();
    sendAT("AT");
    String ATResponse = readAT(2000);
    return ATResponse.indexOf("OK") != -1;
}

void Sim7000G::powerOn(){
    pinMode(PWRKEY, OUTPUT);
    digitalWrite(PWRKEY,HIGH);
    delay(100);
    digitalWrite(PWRKEY,LOW);
    delay(1000);
    digitalWrite(PWRKEY,HIGH);
}

void Sim7000G::sendAT(const char* cmd) {
    while (serialAT.available()) serialAT.read();
    serialAT.print(String(cmd) + "\r\n");
    delay(100);
}

String Sim7000G::readAT(unsigned long timeout_ms) {
    String response = "";
    unsigned long start = millis();

    while (millis() - start < timeout_ms) {
        while (serialAT.available()) {
            char c = (char)serialAT.read();
            response += c;
        }

        if (response.endsWith("OK\r\n") || response.endsWith("ERROR\r\n")) break;
    }

    response.trim();
    return response;
}

String Sim7000G::readUntil(const char* token, unsigned long timeout_ms) {
    String response = "";
    unsigned long start = millis();

    while (millis() - start < timeout_ms) {
        while (serialAT.available()) {
            response += (char)serialAT.read();
        }

        if (response.indexOf(token) != -1 || response.endsWith("ERROR\r\n")) break;
    }

    response.trim();
    return response;
}