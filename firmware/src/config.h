#pragma once

constexpr int simPwrkey = 4;
constexpr int simRx = 26;
constexpr int simTx = 27;
constexpr const char* serialTracker = "RY-TR-2026-0001";

constexpr const char* apn = "internet.tigo.co.com";

constexpr const char* mqttBrokerUrl =  "tracking.tesis.rutaya.xyz";
constexpr const char* mqttTopicBase = "buses/";
constexpr int mqttPort = 1883;
constexpr int mqttQos = 1;

constexpr const char* busApiBaseUrl = "https://api.tesis.rutaya.xyz";
constexpr const char* busApiEndpoint = "/rastreadores/me";
constexpr const char* provisionEndpoint = "/rastreadores/aprovisionar";

constexpr const char* nvsNamespace = "rutaya";
constexpr const char* nvsSecretKey = "secreto";