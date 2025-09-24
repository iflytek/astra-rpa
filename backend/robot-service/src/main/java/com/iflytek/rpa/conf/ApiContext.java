package com.iflytek.rpa.conf;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Component;

@Component
public class ApiContext {
    public static final String CURRENT_TENANT_ID_KEY = "tenantId";
    public static final String CURRENT_USER_ID_KEY = "userId";
    public static final String CURRENT_TERMINAL_MAC_KEY = "terminalMac";
    public static final String CURRENT_TERMINAL_NAME_KEY = "terminalName";
    private static final Map<String, Object> mContext = new ConcurrentHashMap<>();

    public Long getCurrentTenantId() {
        return (Long) mContext.get(CURRENT_TENANT_ID_KEY);
    }

    public void setCurrentTenantId(String tenantId) {
        mContext.put(CURRENT_TENANT_ID_KEY, tenantId);
    }

    public Long getCurrentUserId() {
        return (Long) mContext.get(CURRENT_USER_ID_KEY);
    }

    public void setCurrentUserId(String userId) {
        mContext.put(CURRENT_USER_ID_KEY, userId);
    }
}
