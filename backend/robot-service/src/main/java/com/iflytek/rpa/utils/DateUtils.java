package com.iflytek.rpa.utils;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

public class DateUtils {

    public static SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
    public static SimpleDateFormat sdfday = new SimpleDateFormat("yyyyMMdd");
    public static SimpleDateFormat sdfdaytime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    /**
     * 通过时间秒毫秒数判断两个时间的间隔（不足24小时算0天）
     *
     * @param date1
     * @param date2
     * @return
     */
    public static int differentDaysByMillisecond(Date date1, Date date2) {
        int days = (int) Math.ceil(Double.valueOf((date2.getTime() - date1.getTime()) / (1000 * 3600 * 24)));
        return days;
    }

    /**
     * 通过时间秒毫秒数判断两个时间的间隔（不足24小时算0天）
     *
     * @param date1
     * @param date2
     * @return
     */
    public static int differentHoursByMillisecond(Date date1, Date date2) {
        int days = (int) Math.ceil(Double.valueOf((date2.getTime() - date1.getTime()) / (1000 * 3600)));
        return days;
    }

    /**
     * 通过时间秒毫秒数判断两个时间的间隔（不足24小时算0天）
     *
     * @param date1
     * @param date2
     * @return
     */
    public static int differentMinutesByMillisecond(Date date1, Date date2) {
        int days = (int) Math.ceil(Double.valueOf((date2.getTime() - date1.getTime()) / (1000 * 60)));
        return days;
    }

    /**
     * 通过时间秒毫秒数判断两个时间的间隔（不足24小时算0天）
     *
     * @param date1
     * @param date2
     * @return
     */
    public static int differentSecondsByMillisecond(Date date1, Date date2) {
        int days = (int) Math.ceil(Double.valueOf((date2.getTime() - date1.getTime()) / (1000)));
        return days;
    }

    public static String getDayFormat() {
        return sdfday.format(new Date(System.currentTimeMillis()));
    }

    public static String getDayFormatByDate(Date date) {
        return sdf.format(date);
    }

    public static String getDayTimeFormat(Date date) {
        return sdfdaytime.format(date);
    }

    /*
     * 返回n天前/后的日期
     * */
    public static Date getCalDay(Date date, int calDays) {
        Calendar c = Calendar.getInstance();
        c.setTime(date);
        c.add(Calendar.DATE, calDays);
        return c.getTime();
    }

    /*
     * 返回n天前/后的日期
     * */
    public static Date getCalMinute(Date date, int calMinutes) {
        Calendar c = Calendar.getInstance();
        c.setTime(date);
        c.add(Calendar.MINUTE, calMinutes);
        return c.getTime();
    }

    public static boolean haveToday(Date countTime) throws ParseException {
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy-MM-dd");
        String cTime = simpleDateFormat.format(countTime);
        String nowTime = simpleDateFormat.format(new Date());

        countTime = simpleDateFormat.parse(cTime);
        Date today = simpleDateFormat.parse(nowTime);

        return countTime.compareTo(today) >= 0;
    }

    public static Date getTodayZero() throws ParseException {
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy-MM-dd");
        String nowTime = simpleDateFormat.format(new Date());
        Date today = simpleDateFormat.parse(nowTime);
        return today;
    }

    // 获得某天最大时间 2020-02-19 23:59:59
    public static Date getEndOfDay(Date date) {
        LocalDateTime localDateTime =
                LocalDateTime.ofInstant(Instant.ofEpochMilli(date.getTime()), ZoneId.systemDefault());
        LocalDateTime endOfDay = localDateTime.with(LocalTime.MAX);
        return Date.from(endOfDay.atZone(ZoneId.systemDefault()).toInstant());
    }

    // 获得某天最小时间 2020-02-19 00:00:00
    public static Date getStartOfDay(Date date) {
        LocalDateTime localDateTime =
                LocalDateTime.ofInstant(Instant.ofEpochMilli(date.getTime()), ZoneId.systemDefault());
        LocalDateTime startOfDay = localDateTime.with(LocalTime.MIN);
        return Date.from(startOfDay.atZone(ZoneId.systemDefault()).toInstant());
    }

    public static Date getYesterdayEnd() {
        Date date = new Date();
        return getEndHourTimeOfDay(getCalDay(date, -1));
    }

    // date 转 localDateTime
    public static LocalDateTime convertToLocalDateTimeViaInstant(Date dateToConvert) {
        return dateToConvert.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
    }

    public static String localDateToYyyMdDdStr(LocalDateTime localDateTime) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        return localDateTime.format(formatter);
    }

    public static Date getEndHourTimeOfDay(Date date) {
        return getCalMinute(getEndOfDay(date), -2);
    }

    public static String getStartStrOfDay(Date date) {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
        return dateFormat.format(date) + " 00:00:00"; // 直接拼接 00:00:00
    }

    public static String getEndStrOfDay(Date date) {
        SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
        return dateFormat.format(date) + " 24:00:00"; // 直接拼接 24:00:00
    }

    public static List<String> getStartAndEndOfDay(Date date) {
        // 获取当天的开始时间和结束时间
        String startOfDay = getStartStrOfDay(date);
        String endOfDay = getEndStrOfDay(date);
        List<String> startAndEndOfDay = new ArrayList<>();
        startAndEndOfDay.add(startOfDay);
        startAndEndOfDay.add(endOfDay);
        return startAndEndOfDay;
    }
}
