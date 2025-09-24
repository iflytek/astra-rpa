package com.iflytek.rpa.starter.utils;

import java.time.LocalDate;
import org.springframework.util.DigestUtils;

/**
 * @author keler
 * @date 2020/5/6
 */
public class StringUtils extends org.springframework.util.StringUtils {

    /**
     * 获取gateway token
     *
     * @return String
     */
    public static String getGlobalToken() {
        int month = LocalDate.now().getMonthValue() + 1;
        int day = LocalDate.now().getDayOfMonth();

        String key = LocalDate.now().toString() + month * day % 100;
        return DigestUtils.md5DigestAsHex(key.getBytes());
    }

    /**
     * 下划线 转 驼峰
     *
     * @param string 待转字符串
     */
    public static String underscore2CamelCase(String string) {
        StringBuilder sb = new StringBuilder();

        if (string != null && string.length() > 0) {
            boolean flag = false;
            char underscore = '_';

            for (int i = 0; i < string.length(); i++) {
                char ch = string.charAt(i);
                // 首字母大写
                if (i == 0 && underscore != ch) {
                    sb.append(Character.toUpperCase(string.charAt(0)));
                } else {
                    if (underscore == ch) {
                        flag = true;
                    } else {
                        if (flag) {
                            sb.append(Character.toUpperCase(ch));
                            flag = false;
                        } else {
                            sb.append(ch);
                        }
                    }
                }
            }
        }

        return sb.toString();
    }

    /**
     * 下划线 转 驼峰
     * 首字母小写
     *
     * @param string 待转字符串
     */
    public static String underscore2CamelCaseFirstLower(String string) {
        StringBuilder sb = new StringBuilder();

        if (string != null && string.length() > 0) {
            boolean flag = false;
            char underscore = '_';

            for (int i = 0; i < string.length(); i++) {
                char ch = string.charAt(i);
                // 首字母大写
                if (i == 0 && underscore != ch) {
                    sb.append(Character.toLowerCase(string.charAt(0)));
                } else {
                    if (underscore == ch) {
                        flag = true;
                    } else {
                        if (flag) {
                            sb.append(Character.toUpperCase(ch));
                            flag = false;
                        } else {
                            sb.append(ch);
                        }
                    }
                }
            }
        }

        return sb.toString();
    }
}
