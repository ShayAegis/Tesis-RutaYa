#pragma once
#include "domain/models/models.h"
#include <Arduino.h>
#include <HardwareSerial.h>
#include <time.h>
#include <vector>
#include <map>

enum HTTPMethod_t {
    GET = 1,
    PUT = 2,
    POST = 3,
    PATCH = 4,
    HEAD = 5,
};


class HTTPRequest{
    protected:
        const char* _baseUrl;
        const char* _endpoint;
        HTTPMethod_t _httpMethod;
        std::vector<std::map<String, String>> _headers;

    public:
        void setBaseUrl(const char* baseUrl){
            _baseUrl = baseUrl;
        }

        String getBaseUrl(){
            return String(_baseUrl);
        }

        String getHost(){
            String host = String(_baseUrl);

            int schemeEnd = host.indexOf("://");
            if(schemeEnd != -1){
                host = host.substring(schemeEnd + 3);
            }

            int pathStart = host.indexOf('/');
            if(pathStart != -1){
                host = host.substring(0, pathStart);
            }

            int portStart = host.indexOf(':');
            if(portStart != -1){
                host = host.substring(0, portStart);
            }

            return host;
        }

        void setMethod(HTTPMethod_t method){
            _httpMethod = method;
        }

        String getMethod(){
            return String(_httpMethod);
        }

        void setEndpoint(const char* endpoint){
            _endpoint = endpoint;
        }

        String getEndpoint(){
            return _endpoint;
        }

        void addHeader(const char* key, const char* value){
            std::map<String, String> header;
            header[String(key)] = String(value);
            _headers.push_back(header);
        }

        std::vector<std::map<String, String>> getHeaders(){
            return _headers;
        }

        HTTPRequest(const char* baseUrl, const char* endpoint, HTTPMethod_t method): _baseUrl(baseUrl), _endpoint(endpoint), _httpMethod(method){}
};

struct HTTPResponse {
    String content;
    int statusCode;
};

enum BearerStatus_t {
    ERROR = -1,
    BEARER_CONNECTING = 0,
    BEARER_CONNECTED = 1,
    BEARER_CLOSING = 2,
    BEARER_CLOSED = 3
};

class Sim7000G{
    private:
        const int rx;
        const int tx;
        const int PWRKEY;
        HardwareSerial serialAT;
        GpsData_t _cachedGpsData;
        void powerOn();
        void sendAT(const char* cmd);
        String readAT(unsigned long timeout_ms);
        String readUntil(const char* token, unsigned long timeout_ms);
        bool isModemAlive();
        bool registerInNetwork();
        BearerStatus_t checkBearerStatus(int cid);
        bool openBearer(int cid,const char* apn);
        String getBearerIp(int cid);
        bool isDataActive();
        bool enableMobileData(const char* apn);
        String getRawGps();
        GpsData_t parseGps(String rawGpsData);
    public:
        bool begin();
        bool connectNetwork(const char* apn);
        bool mqttConnect(const char* clientId,const char* mqttBrokerUrl,const int mqttPort);
        bool pubMqtt(const char* topic,const char* payload,int qos);
        bool gpsBegin(bool aGps);
        bool syncNTP(const char* ntpServer);
        String getSimNumber();
        String getImei();
        String getIccid();
        time_t getTimestamp();
        float getRSSI();
        void updateGps();
        bool isGpsFixed();
        LatLng_t getLatLng();
        float getSpeed();
        float getAzimuth();
        HTTPResponse httpsBegin(HTTPRequest request);
        Sim7000G(const int rxPin,const int txPin,const int PWRKEY);
};

