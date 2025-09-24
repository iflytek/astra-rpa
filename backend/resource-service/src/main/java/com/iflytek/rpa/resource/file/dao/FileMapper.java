package com.iflytek.rpa.resource.file.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.resource.file.entity.File;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 文件表 Mapper 接口
 *
 * @author system
 * @since 2024-01-01
 */
@Mapper
public interface FileMapper extends BaseMapper<File> {

    @Select("select * from file where deleted = 0 and file_id = #{fileId}")
    File getFile(@Param("fileId") String fileId);
}
