from fastapi import HTTPException, status
class Auth:
    def __init__(self, cfg):
        self.admin = cfg["tokens"]["admin"]
        self.agents = set(cfg["tokens"]["agents"])
    def require_admin(self, token):
        if token != self.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    def require_agent_or_admin(self, token):
        if token == self.admin:
            return
        if token not in self.agents:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
