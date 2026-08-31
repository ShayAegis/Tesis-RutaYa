#pragma once
#include <Preferences.h>

class NvsStorage {
    private:
        Preferences _preferences;
        const char* _namespace;
    public:
        NvsStorage(const char* nvsNamespace) : _namespace(nvsNamespace) {}
        String getString(const char* key, const char* defaultValue = "");
        void putString(const char* key, const char* value);
        void remove(const char* key);
};
