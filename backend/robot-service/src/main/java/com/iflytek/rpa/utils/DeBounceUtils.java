package com.iflytek.rpa.utils;

import static com.iflytek.rpa.starter.redis.RedisUtils.redisTemplate;

import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import java.util.concurrent.TimeUnit;

/**
 * 防抖相关
 */
public class DeBounceUtils {

    /**
     * redis进行防抖处理
     *
     * @param createLikeKey
     * @return
     */
    public static void deBounce(String createLikeKey, Long deBounceWindow) {
        Boolean b = redisTemplate.hasKey(createLikeKey);
        if (b != null && b) {
            // 已经存在了
            redisTemplate.expire(createLikeKey, deBounceWindow, TimeUnit.MILLISECONDS);
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "操作太快了，稍后再试");
        }
        // 不存在
        redisTemplate.opsForValue().set(createLikeKey, "1", deBounceWindow, TimeUnit.MILLISECONDS);
    }
}
