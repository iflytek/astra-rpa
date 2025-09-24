package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.AtomLike;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface AtomLikeDao extends BaseMapper<AtomLike> {

    @Select("select * " + "from atom_like "
            + "where is_deleted = 0 and creator_id = #{userId} and tenant_id = #{tenantId} and like_id = #{likeId}")
    AtomLike getAtomLikeById(
            @Param("userId") String userId, @Param("tenantId") String tenantId, @Param("likeId") Long likeId);

    @Select("select count(1) " + "from atom_like "
            + "where is_deleted = 0 and creator_id = #{userId} and atom_key = #{atomKey}")
    Integer getAtomLikeByUserIdAtomKey(@Param("userId") String userId, @Param("atomKey") String atomKey);

    @Select("select * " + "from atom_like "
            + "where is_deleted = 0 and creator_id = #{userId} and tenant_id = #{tenantId}")
    List<AtomLike> getAtomLikeList(@Param("userId") String userId, @Param("tenantId") String tenantId);
}
