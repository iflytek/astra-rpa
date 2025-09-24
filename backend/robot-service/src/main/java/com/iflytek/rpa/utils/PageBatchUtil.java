package com.iflytek.rpa.utils;

import java.util.function.BiConsumer;

public class PageBatchUtil {
    /**
     * 批处理分页处理方法
     *
     * @param total     总记录数
     * @param batchSize 每页大小
     * @param consumer  处理函数，接收 limit 和 offset
     */
    public static void process(int total, int batchSize, BiConsumer<Integer, Integer> consumer) {
        // todo offset改成long
        if (total < 0 || batchSize <= 0) {
            throw new IllegalArgumentException("Total must be non-negative and batchSize must be positive.");
        }
        if (total == 0) {
            return; // 没有数据，直接返回
        }

        int pages = (int) Math.ceil((double) total / batchSize);
        for (int page = 0; page < pages; page++) {
            int offset = page * batchSize;
            int limit = Math.min(batchSize, total - offset);
            consumer.accept(limit, offset);
        }
    }
}
