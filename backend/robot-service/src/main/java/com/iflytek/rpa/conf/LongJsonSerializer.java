package com.iflytek.rpa.conf;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.SerializerProvider;
import java.io.IOException;

public class LongJsonSerializer extends JsonSerializer<Long> {

    @Override
    public void serialize(Long aLong, JsonGenerator jsonGenerator, SerializerProvider serializerProvider)
            throws IOException {
        String text = (aLong == null ? null : String.valueOf(aLong));
        if (text != null) {
            jsonGenerator.writeString(text);
        }
    }
}
