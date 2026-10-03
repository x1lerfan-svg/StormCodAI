from stormcodai.agent import CodingAgent
from stormcodai.workspace import Workspace

class FakeClient:
    def __init__(self): self.calls=[]
    def chat(self, system, user): self.calls.append((system,user)); return "ok"

def test_agent_uses_bounded_context(tmp_path):
    ws=Workspace(str(tmp_path))
    (tmp_path/"src.py").write_text("print('ok')",encoding="utf-8")
    (tmp_path/".env").write_text("api_key=secret",encoding="utf-8")
    client=FakeClient()
    assert CodingAgent(client,ws).ask("inspect src.py")=="ok"
    assert "src.py" in client.calls[0][1]
    assert "secret" not in client.calls[0][1]
    assert "untrusted data" in client.calls[0][0]
