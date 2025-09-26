import http.client
import json


class xcAgent:
    def __init__(self, api_key, api_secret):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Authorization": "Bearer {}:{}".format(api_key, api_secret),
        }

    def run_flow(self, flow_id, content, is_stream: bool = False):
        data = {
            "flow_id": flow_id,
            "parameters": {"AGENT_USER_INPUT": content},
            "stream": is_stream,
        }
        payload = json.dumps(data)

        conn = http.client.HTTPSConnection("xingchen-api.xf-yun.com", timeout=120)
        conn.request(
            "POST",
            "/workflow/v1/chat/completions",
            payload,
            self.headers,
            encode_chunked=True,
        )
        res = conn.getresponse()

        data = res.readline().decode("utf-8")
        response_json = json.loads(data)
        return response_json["choices"][0]["delta"]["content"]
