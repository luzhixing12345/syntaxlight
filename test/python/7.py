def run_code(
    self,
    code: str,
) -> Execution:
    """
    POST /execute - Execute code inside the sandbox.
    """
    if self._client is None:
        self._client = self._build_data_client() # 创建了一个 httpx.Client 对象用于后续请求发送，和 CubeProxy 有关

    url = f"http://{self.get_host(JUPYTER_PORT)}/execute"
    payload = {
        "code": code,
        "language": language,
        "env_vars": envs,
    }
    execution = Execution()

    return execution