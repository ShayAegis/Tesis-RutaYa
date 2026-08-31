#include "NvsStorage.h"

String NvsStorage::getString(const char* key, const char* defaultValue){
    _preferences.begin(_namespace, true);
    String value = _preferences.getString(key, defaultValue);
    _preferences.end();
    return value;
}

void NvsStorage::putString(const char* key, const char* value){
    _preferences.begin(_namespace, false);
    _preferences.putString(key, value);
    _preferences.end();
}

void NvsStorage::remove(const char* key){
    _preferences.begin(_namespace, false);
    _preferences.remove(key);
    _preferences.end();
}
