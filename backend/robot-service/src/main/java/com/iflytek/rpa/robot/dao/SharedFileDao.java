package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.SharedFile;
import com.iflytek.rpa.robot.entity.SharedFileTag;
import com.iflytek.rpa.robot.entity.dto.SharedFilePageDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface SharedFileDao extends BaseMapper<SharedFile> {
    Integer isTenantAdmin(
            @Param("userId") String userId,
            @Param("tenantId") String tenantId,
            @Param("databaseName") String databaseName);

    Integer deleteBatchSharedFile(@Param("ids") List<String> fileIds, @Param("tenantId") String tenantId);

    List<SharedFileTag> selectTags(String tenantId);

    @Select(
            "SELECT COUNT(*) FROM shared_file_tag WHERE tag_name = #{tagName} AND tenant_id = #{tenantId} AND deleted = 0")
    Integer selectTagsCountByName(String tagName, String tenantId);

    Integer addTag(@Param("entity") SharedFileTag newTag);

    // 在 SharedFileDao 接口中添加
    Integer updateTagById(
            @Param("tagId") Long tagId,
            @Param("tagName") String tagName,
            @Param("updaterId") String updaterId,
            @Param("tenantId") String tenantId);

    @Select(
            "SELECT EXISTS(SELECT 1 FROM shared_file_tag WHERE tag_id = #{tagId} AND tenant_id = #{tenantId} AND deleted = 0)")
    boolean containsTagById(@Param("tagId") Long tagId, @Param("tenantId") String tenantId);

    @Select("select * " + "from shared_file_tag "
            + "where tag_id = #{tagId} and tenant_id = #{tenantId} and deleted = 0")
    SharedFileTag selectTagById(Long tagId, String tenantId);

    List<SharedFile> selectFilesByTag(@Param("tagName") String tagName, @Param("tenantId") String tenantId);

    Integer updateFileTagById(@Param("fileId") String fileId, @Param("tags") String tags);

    Integer deletedTagById(@Param("tagId") Long tagId, @Param("tenantId") String tenantId);

    List<SharedFileTag> selectTagsByIds(@Param("tagIds") List<Long> tagIds, @Param("tenantId") String tenantId);

    IPage<SharedFile> selectSharedFilePageList(
            IPage<SharedFile> page, @Param("queryDto") SharedFilePageDto queryDto, @Param("tenantId") String tenantId);

    SharedFile selectFileByName(String fileName, String userId, String tenantId);
}
