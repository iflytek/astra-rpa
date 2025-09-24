package com.iflytek.rpa.utils;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;

public class PrePage<T> extends Page<T> implements IPage<T> {

    protected long preNum;

    public PrePage() {
        super();
    }

    public PrePage(long preNum) {
        this.preNum = preNum;
    }

    public PrePage(long current, long size, boolean isSearchCount) {
        super(current, size, isSearchCount);
    }

    public long offset() {
        return this.getCurrent() > 0L ? (this.getCurrent() - 1L) * this.getSize() - this.preNum : 0L;
    }
}
