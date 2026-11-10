import json
import time
import requests
import websocket

class CDPTab:
    """Controls a Chrome browser tab via Chrome DevTools Protocol (CDP)."""

    def __init__(self, filter_url_or_title: str = "", cdp_base_url: str = "http://127.0.0.1:9222"):
        self.cdp_base_url = cdp_base_url.rstrip("/")
        self.filter = filter_url_or_title.lower()
        self.ws_url = None
        self.target_id = None
        self.ws = None
        self._msg_id = 0
        self._connect()

    def _connect(self):
        resp = requests.get(f"{self.cdp_base_url}/json", timeout=5)
        tabs = [t for t in resp.json() if t.get("type") == "page"]
        
        target = None
        if self.filter:
            for t in tabs:
                u = t.get("url", "").lower()
                title = t.get("title", "").lower()
                if self.filter in u or self.filter in title:
                    target = t
                    break
        
        if not target and tabs:
            target = tabs[0]
            
        if not target:
            raise ConnectionError(f"No matching Chrome page found for filter: '{self.filter}'")
            
        self.ws_url = target["webSocketDebuggerUrl"]
        self.target_id = target["id"]
        self.ws = websocket.create_connection(self.ws_url, timeout=20)
        self.call("Page.enable")
        self.call("DOM.enable")

    def call(self, method: str, **params):
        self._msg_id += 1
        payload = {"id": self._msg_id, "method": method, "params": params}
        self.ws.send(json.dumps(payload))
        
        start_time = time.time()
        while time.time() - start_time < 20:
            raw = self.ws.recv()
            data = json.loads(raw)
            if data.get("id") == self._msg_id:
                if "error" in data:
                    raise RuntimeError(f"CDP Error ({method}): {data['error']}")
                return data.get("result", {})
        raise TimeoutError(f"CDP call {method} timed out.")

    def js(self, expr: str, return_by_value: bool = True):
        res = self.call("Runtime.evaluate", expression=expr, returnByValue=return_by_value, awaitPromise=True)
        return res.get("result", {}).get("value")

    def navigate(self, url: str, wait_seconds: float = 3.0):
        self.call("Page.navigate", url=url)
        time.sleep(wait_seconds)

    def close(self):
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass

    def set_file_input(self, selector: str, file_paths: list[str]):
        """Injects file paths into an HTML file input element."""
        doc = self.call("DOM.getDocument")
        root_node_id = doc["root"]["nodeId"]
        node = self.call("DOM.querySelector", nodeId=root_node_id, selector=selector)
        node_id = node.get("nodeId")
        if node_id:
            self.call("DOM.setFileInputFiles", files=file_paths, nodeId=node_id)
            return True
        return False
