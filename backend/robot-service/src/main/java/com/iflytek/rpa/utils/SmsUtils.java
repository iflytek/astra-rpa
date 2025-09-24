package com.iflytek.rpa.utils;

import com.alibaba.fastjson.JSONObject;
import com.iflytek.rpa.starter.utils.StringUtils;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import java.util.*;
import org.apache.commons.codec.digest.Md5Crypt;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

/**
 * @author jqfang3
 * @since 2025-08-21
 */
@Component
public class SmsUtils {
    @Value("${sms.apiUrl:https://dripsms.xfpaas.com/sms}")
    public String apiSendSms;

    @Value("${sms.secretKey:9a530169680ac3428c7ae3125391b5e8}")
    public String secretKey;

    @Value("${sms.appId:KVQ8D5K11R}")
    public String appId;

    @Value("${sms.tid:16696}")
    public String tid;

    /**
     * 发送短信
     *
     * @param phone 手机号，多个用“,”隔开，不留空格
     * @param text  需要发送的内容
     */
    public AppResponse send(String phone, String text) {
        // 校验手机号是否为空
        if (StringUtils.isEmpty(phone)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "手机号码为空");
        }
        Map<String, Object> tpMap = new HashMap<>();
        tpMap.put("sendContent", text);
        return sendSms(phone, tid, tpMap);
    }

    /**
     * 发送短信
     *
     * @param phone 手机号，多个用“,”隔开，不留空格
     * @param tid   短信模板ID
     * @param tpMap 短信模板参数
     * @return SmsResponse
     */
    public AppResponse sendSms(String phone, String tid, Map<String, Object> tpMap) {
        // 拆分手机号
        String[] phoneArr = phone.split(",");
        String tpJson = JSONObject.toJSONString(tpMap);

        return sendSms(phoneArr, tid, tpJson);
    }

    /**
     * 发送短信
     *
     * @param phone 手机号，多个用“,”隔开，不留空格
     * @param tid   短信模板ID
     * @param tp    短信模板参数
     * @return SmsResponse
     */
    public AppResponse sendSms(String[] phone, String tid, String tp) {
        Map<String, Object> params = new HashMap<>();
        params.put("appid", appId);
        params.put("phone", phone);
        params.put("tid", tid);
        params.put("tp", tp);
        String sign = getSign(params);
        params.put("sign", sign);
        RestTemplate restTemplate = new RestTemplate();
        HttpHeaders headers = new HttpHeaders();
        HttpMethod method = HttpMethod.POST;
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<String> requestEntity = new HttpEntity<>(JSONObject.toJSONString(params), headers);
        ResponseEntity<String> response = restTemplate.exchange(apiSendSms, method, requestEntity, String.class);
        return JSONObject.parseObject(response.getBody(), AppResponse.class);
    }

    /**
     * 获取签名
     * 第一步，设发送数据为集合 M，将集合 M 内满足条件的参数按照参数名 ASCII 码从小到大排序（字典序），
     * 使用 URL 键值对的格式（即 key1=value1&key2=value2…）拼接成字符串 stringRequest。
     * 特别注意以下重要规则：
     * • 参数值为空的不参与签名；
     * • sign 参数本身不参与签名；
     * • 参数名区分大小写。
     * 第二步，在 stringRequest 最后拼接上 API 密钥 key 得到 stringSignRequest 字符串，
     * 并对 stringSignRequest 进行 MD5 运算，再将得到的字符串所有字符转换为大写，
     * 得到 sign 值 signValue。API 密钥需要在短信管理台进行申请配置
     *
     * @param params 请求参数
     * @return String
     */
    private String getSign(Map<String, Object> params) {
        // 请求参数转字符串
        String stringRequest = getRequestString(params);
        // 拼接密钥
        String signStr = stringRequest + "key=" + secretKey;
        // Md5 + 全部转大写
        return Md5Crypt.apr1Crypt(signStr.getBytes()).toUpperCase();
    }

    /**
     * 请求参数转字符串
     * 设发送数据为集合 M，将集合 M 内满足条件的参数按照参数名 ASCII 码从小到大排序（字典序），
     * 使用 URL 键值对的格式（即 key1=value1&key2=value2…）拼接成字符串 stringRequest。
     * 特别注意以下重要规则：
     * • 参数值为空的不参与签名；
     * • sign 参数本身不参与签名；
     * • 参数名区分大小写。
     *
     * @param params 请求参数
     * @return String
     */
    private String getRequestString(Map<String, Object> params) {
        if (params == null) {
            return null;
        }
        if (params.get("sign") != null) {
            params.remove("sign");
        }
        List<String> keyList = new ArrayList<>(params.keySet());
        Collections.sort(keyList);
        StringBuilder sb = new StringBuilder();
        for (String key : keyList) {
            String value = params.get(key).toString();
            sb.append(key).append("=").append(value).append("&");
        }
        return sb.toString();
    }
}
