package com.iflytek.rpa.starter.redis;

import com.iflytek.rpa.starter.utils.LoggerUtils;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.util.CollectionUtils;

public class RedisUtils {
    public static RedisTemplate<String, Object> redisTemplate;

    public RedisUtils() {}

    public static boolean expire(String key, long time) {
        try {
            if (time > 0L) {
                redisTemplate.expire(key, time, TimeUnit.SECONDS);
            }

            return true;
        } catch (Exception var4) {
            LoggerUtils.error("redis操作异常", var4);
            return false;
        }
    }

    public static long getExpire(String key) {
        return redisTemplate.getExpire(key, TimeUnit.SECONDS);
    }

    public static boolean hasKey(String key) {
        try {
            return redisTemplate.hasKey(key);
        } catch (Exception var2) {
            LoggerUtils.error("redis操作异常", var2);
            return false;
        }
    }

    public static void del(String... key) {
        if (key != null && key.length > 0) {
            if (key.length == 1) {
                redisTemplate.delete(key[0]);
            } else {
                redisTemplate.delete(CollectionUtils.arrayToList(key));
            }
        }
    }

    public static Object get(String key) {
        return key == null ? null : redisTemplate.opsForValue().get(key);
    }

    public static boolean set(String key, Object value) {
        try {
            redisTemplate.opsForValue().set(key, value);
            return true;
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return false;
        }
    }

    public static boolean set(String key, Object value, long time) {
        try {
            if (time > 0L) {
                redisTemplate.opsForValue().set(key, value, time, TimeUnit.SECONDS);
            } else {
                set(key, value);
            }

            return true;
        } catch (Exception var5) {
            LoggerUtils.error("redis操作异常", var5);
            return false;
        }
    }

    public static long incr(String key, long delta) {
        if (delta < 0L) {
            throw new RuntimeException("递增因子必须大于0");
        } else {
            return redisTemplate.opsForValue().increment(key, delta);
        }
    }

    public static long decr(String key, long delta) {
        if (delta < 0L) {
            throw new RuntimeException("递减因子必须大于0");
        } else {
            return redisTemplate.opsForValue().increment(key, -delta);
        }
    }

    public static Object hget(String key, String item) {
        return redisTemplate.opsForHash().get(key, item);
    }

    public static Map<Object, Object> hmget(String key) {
        return redisTemplate.opsForHash().entries(key);
    }

    public static boolean hmset(String key, Map<String, Object> map) {
        try {
            redisTemplate.opsForHash().putAll(key, map);
            return true;
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return false;
        }
    }

    public static boolean hmset(String key, Map<String, Object> map, long time) {
        try {
            redisTemplate.opsForHash().putAll(key, map);
            if (time > 0L) {
                expire(key, time);
            }

            return true;
        } catch (Exception var5) {
            LoggerUtils.error("redis操作异常", var5);
            return false;
        }
    }

    public static boolean hset(String key, String item, Object value) {
        try {
            redisTemplate.opsForHash().put(key, item, value);
            return true;
        } catch (Exception var4) {
            LoggerUtils.error("redis操作异常", var4);
            return false;
        }
    }

    public static boolean hset(String key, String item, Object value, long time) {
        try {
            redisTemplate.opsForHash().put(key, item, value);
            if (time > 0L) {
                expire(key, time);
            }

            return true;
        } catch (Exception var6) {
            LoggerUtils.error("redis操作异常", var6);
            return false;
        }
    }

    public static void hdel(String key, Object... item) {
        redisTemplate.opsForHash().delete(key, item);
    }

    public static boolean hHasKey(String key, String item) {
        return redisTemplate.opsForHash().hasKey(key, item);
    }

    public static double hincr(String key, String item, double by) {
        return redisTemplate.opsForHash().increment(key, item, by);
    }

    public static double hdecr(String key, String item, double by) {
        return redisTemplate.opsForHash().increment(key, item, -by);
    }

    public static Set<Object> sGet(String key) {
        try {
            return redisTemplate.opsForSet().members(key);
        } catch (Exception var2) {
            LoggerUtils.error("redis操作异常", var2);
            return null;
        }
    }

    public static boolean sHasKey(String key, Object value) {
        try {
            return redisTemplate.opsForSet().isMember(key, value);
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return false;
        }
    }

    public static long sSet(String key, Object... values) {
        try {
            return redisTemplate.opsForSet().add(key, values);
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return 0L;
        }
    }

    public static long sSetAndTime(String key, long time, Object... values) {
        try {
            Long count = redisTemplate.opsForSet().add(key, values);
            if (time > 0L) {
                expire(key, time);
            }

            return count;
        } catch (Exception var5) {
            LoggerUtils.error("redis操作异常", var5);
            return 0L;
        }
    }

    public static long sGetSetSize(String key) {
        try {
            return redisTemplate.opsForSet().size(key);
        } catch (Exception var2) {
            LoggerUtils.error("redis操作异常", var2);
            return 0L;
        }
    }

    public static long setRemove(String key, Object... values) {
        try {
            Long count = redisTemplate.opsForSet().remove(key, values);
            return count;
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return 0L;
        }
    }

    public static List<Object> lGet(String key, long start, long end) {
        try {
            return redisTemplate.opsForList().range(key, start, end);
        } catch (Exception var6) {
            LoggerUtils.error("redis操作异常", var6);
            return null;
        }
    }

    public static long lGetListSize(String key) {
        try {
            return redisTemplate.opsForList().size(key);
        } catch (Exception var2) {
            LoggerUtils.error("redis操作异常", var2);
            return 0L;
        }
    }

    public static boolean lSet(String key, Object value) {
        try {
            redisTemplate.opsForList().rightPush(key, value);
            return true;
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return false;
        }
    }

    public static boolean lSet(String key, Object value, long time) {
        try {
            redisTemplate.opsForList().rightPush(key, value);
            if (time > 0L) {
                expire(key, time);
            }

            return true;
        } catch (Exception var5) {
            LoggerUtils.error("redis操作异常", var5);
            return false;
        }
    }

    public static boolean lSet(String key, List<Object> value) {
        try {
            redisTemplate.opsForList().rightPushAll(key, value);
            return true;
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return false;
        }
    }

    public static boolean lSet(String key, List<Object> value, long time) {
        try {
            redisTemplate.opsForList().rightPushAll(key, value);
            if (time > 0L) {
                expire(key, time);
            }

            return true;
        } catch (Exception var5) {
            LoggerUtils.error("redis操作异常", var5);
            return false;
        }
    }

    public static boolean lUpdateIndex(String key, long index, Object value) {
        try {
            redisTemplate.opsForList().set(key, index, value);
            return true;
        } catch (Exception var5) {
            LoggerUtils.error("redis操作异常", var5);
            return false;
        }
    }

    public static long lRemove(String key, long count, Object value) {
        try {
            return redisTemplate.opsForList().remove(key, count, value);
        } catch (Exception var5) {
            LoggerUtils.error("redis操作异常", var5);
            return 0L;
        }
    }

    public static Boolean zAdd(String key, Object value, double score) {
        try {
            return redisTemplate.opsForZSet().add(key, value, score);
        } catch (Exception var5) {
            LoggerUtils.error("redis操作异常", var5);
            return false;
        }
    }

    public static Long zCard(String key) {
        try {
            return redisTemplate.opsForZSet().size(key);
        } catch (Exception var2) {
            LoggerUtils.error("redis操作异常", var2);
            return null;
        }
    }

    public static Long zCount(String key, double min, double max) {
        try {
            return redisTemplate.opsForZSet().count(key, min, max);
        } catch (Exception var6) {
            LoggerUtils.error("redis操作异常", var6);
            return null;
        }
    }

    public static Double zIncrementScore(String key, Object value, double delta) {
        try {
            return redisTemplate.opsForZSet().incrementScore(key, value, delta);
        } catch (Exception var5) {
            LoggerUtils.error("redis操作异常", var5);
            return null;
        }
    }

    public static Set<Object> zRange(String key, long start, long end) {
        try {
            return redisTemplate.opsForZSet().range(key, start, end);
        } catch (Exception var6) {
            LoggerUtils.error("redis操作异常", var6);
            return null;
        }
    }

    public static Set<Object> zRangeByScore(String key, double min, double max) {
        try {
            return redisTemplate.opsForZSet().rangeByScore(key, min, max);
        } catch (Exception var6) {
            LoggerUtils.error("redis操作异常", var6);
            return null;
        }
    }

    public static Long zRank(String key, Object value) {
        try {
            return redisTemplate.opsForZSet().rank(key, value);
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return null;
        }
    }

    public static Long zRemove(String key, Object... values) {
        try {
            return redisTemplate.opsForZSet().remove(key, values);
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return null;
        }
    }

    public static Long zRemoveRange(String key, long start, long end) {
        try {
            return redisTemplate.opsForZSet().removeRange(key, start, end);
        } catch (Exception var6) {
            LoggerUtils.error("redis操作异常", var6);
            return null;
        }
    }

    public static Long zRemoveRangeByScore(String key, double min, double max) {
        try {
            return redisTemplate.opsForZSet().removeRangeByScore(key, min, max);
        } catch (Exception var6) {
            LoggerUtils.error("redis操作异常", var6);
            return null;
        }
    }

    public static Set<Object> zReverseRange(String key, long start, long end) {
        try {
            return redisTemplate.opsForZSet().reverseRange(key, start, end);
        } catch (Exception var6) {
            LoggerUtils.error("redis操作异常", var6);
            return null;
        }
    }

    public static Long zReverseRank(String key, Object value) {
        try {
            return redisTemplate.opsForZSet().reverseRank(key, value);
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return null;
        }
    }

    public static Double zScore(String key, Object value) {
        try {
            return redisTemplate.opsForZSet().score(key, value);
        } catch (Exception var3) {
            LoggerUtils.error("redis操作异常", var3);
            return null;
        }
    }

    public static Long zUnionAndStore(String key, String otherKey, String destKey) {
        try {
            return redisTemplate.opsForZSet().unionAndStore(key, otherKey, destKey);
        } catch (Exception var4) {
            LoggerUtils.error("redis操作异常", var4);
            return null;
        }
    }

    public static Long zIntersectAndStore(String key, String otherKey, String destKey) {
        try {
            return redisTemplate.opsForZSet().intersectAndStore(key, otherKey, destKey);
        } catch (Exception var4) {
            LoggerUtils.error("redis操作异常", var4);
            return null;
        }
    }

    public Object lGetIndex(String key, long index) {
        try {
            return redisTemplate.opsForList().index(key, index);
        } catch (Exception var5) {
            LoggerUtils.error("redis操作异常", var5);
            return null;
        }
    }
}
