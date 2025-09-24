package com.iflytek.rpa.task.entity.enums;

import java.util.HashMap;
import java.util.Map;
import lombok.Getter;

/**
 * @author keler
 * @date 2021/10/9
 */
@Getter
public enum CycleWeekEnum {
    MON("MON", "星期一"),
    TUE("TUE", "星期二"),
    WED("WED", "星期三"),
    THU("THU", "星期四"),
    FRI("FRI", "星期五"),
    SAT("SAT", "星期六"),
    SUN("SUN", "星期日"),
    ;

    public static Map<Integer, String> weekNumCodeMap = new HashMap<>();

    static {
        initWeekNumCodeMap();
    }

    private final String code;
    private final String name;

    CycleWeekEnum(String code, String name) {
        this.code = code;
        this.name = name;
    }

    public static void initWeekNumCodeMap() {
        weekNumCodeMap.put(1, MON.getCode());
        weekNumCodeMap.put(2, TUE.getCode());
        weekNumCodeMap.put(3, WED.getCode());
        weekNumCodeMap.put(4, THU.getCode());
        weekNumCodeMap.put(5, FRI.getCode());
        weekNumCodeMap.put(6, SAT.getCode());
        weekNumCodeMap.put(0, SUN.getCode());
    }

    public static String getCodeByNum(Integer num) {
        return weekNumCodeMap.getOrDefault(num, MON.getCode());
    }
}
