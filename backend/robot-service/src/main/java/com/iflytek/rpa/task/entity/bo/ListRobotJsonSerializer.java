package com.iflytek.rpa.task.entity.bo;

import com.alibaba.fastjson.JSONObject;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.SerializerProvider;
import java.io.IOException;
import java.util.List;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

public class ListRobotJsonSerializer extends JsonSerializer<String> {

    @Override
    public void serialize(String str, JsonGenerator jsonGenerator, SerializerProvider serializerProvider)
            throws IOException {
        if (!StringUtils.isEmpty(str)) {
            List<TaskRobotBo> robotBos = JSONObject.parseArray(str, TaskRobotBo.class);
            if (!CollectionUtils.isEmpty(robotBos)) {
                jsonGenerator.writeObject(robotBos);
            } else {
                String[] strArr = new String[0];
                jsonGenerator.writeArray(strArr, -1, 0);
            }
        } else {
            jsonGenerator.writeNull();
        }
    }
}
