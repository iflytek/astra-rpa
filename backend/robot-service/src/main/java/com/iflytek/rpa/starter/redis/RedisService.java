package com.iflytek.rpa.starter.redis;

import org.springframework.data.redis.core.RedisTemplate;

/**
 * @author keler
 * @date 2021/7/26
 */
public class RedisService {
    private final RedisTemplate<String, Object> redisTemplate;

    // ~ value set & get
    // -----------------------------------------------------------------------------------------------------------------

    public RedisService(RedisTemplate<String, Object> redisTemplate) {
        RedisUtils.redisTemplate = redisTemplate;
        this.redisTemplate = redisTemplate;
    }

    public RedisTemplate<String, Object> getRedisTemplate() {
        return redisTemplate;
    }
}
