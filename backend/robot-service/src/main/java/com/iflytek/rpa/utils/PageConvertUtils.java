package com.iflytek.rpa.utils;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import java.util.List;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;

/**
 * 分页结果转换工具类
 */
public class PageConvertUtils {

    /**
     * 分页结果转换
     *
     * @param page        源分页对象
     * @param targetClass 目标类型
     * @param <T>         源类型
     * @param <R>         目标类型
     * @return 转换后的分页对象
     */
    public static <T, R> IPage<R> convertPage(IPage<T> page, Class<R> targetClass) {
        if (page == null) {
            return null;
        }

        // 转换记录列表
        List<R> records = page.getRecords().stream()
                .map(source -> {
                    try {
                        R target = targetClass.newInstance();
                        BeanUtils.copyProperties(source, target);
                        return target;
                    } catch (Exception e) {
                        throw new RuntimeException("对象转换失败", e);
                    }
                })
                .collect(Collectors.toList());

        // 创建新的分页对象
        IPage<R> resultPage = new Page<>();
        resultPage.setRecords(records);
        resultPage.setCurrent(page.getCurrent());
        resultPage.setSize(page.getSize());
        resultPage.setTotal(page.getTotal());
        resultPage.setPages(page.getPages());

        return resultPage;
    }

    /**
     * 分页结果转换（使用自定义转换器）
     *
     * @param page      源分页对象
     * @param converter 转换器函数
     * @param <T>       源类型
     * @param <R>       目标类型
     * @return 转换后的分页对象
     */
    public static <T, R> IPage<R> convertPage(IPage<T> page, java.util.function.Function<T, R> converter) {
        if (page == null) {
            return null;
        }

        // 转换记录列表
        List<R> records = page.getRecords().stream().map(converter).collect(Collectors.toList());

        // 创建新的分页对象
        IPage<R> resultPage = new Page<>();
        resultPage.setRecords(records);
        resultPage.setCurrent(page.getCurrent());
        resultPage.setSize(page.getSize());
        resultPage.setTotal(page.getTotal());
        resultPage.setPages(page.getPages());

        return resultPage;
    }
}
