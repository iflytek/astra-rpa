package com.iflytek.rpa.auth.service;

import com.fasterxml.jackson.core.type.TypeReference;
import java.io.IOException;
import org.casbin.casdoor.config.Config;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.service.UserService;
import org.casbin.casdoor.util.Map;
import org.casbin.casdoor.util.http.CasdoorResponse;
import org.springframework.stereotype.Service;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/20 10:58
 */
@Service
public class UserExtendService extends UserService {

    public UserExtendService(Config config) {
        super(config);
    }

    public User getUserById(String id) throws IOException {
        CasdoorResponse<User, Object> resp =
                doGet("get-user", Map.of("userId", id), new TypeReference<CasdoorResponse<User, Object>>() {});
        return objectMapper.convertValue(resp.getData(), User.class);
    }

    public User getUserByPhone(String phone) throws IOException {
        CasdoorResponse<User, Object> resp =
                doGet("get-user", Map.of("phone", phone), new TypeReference<CasdoorResponse<User, Object>>() {});
        return objectMapper.convertValue(resp.getData(), User.class);
    }
}
