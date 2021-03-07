from typing import List


class Repo:
    def read(self) -> List[str]:
        raise NotImplementedError


class DomainAction:
    def __init__(self, repo: Repo):
        self.repo = repo

    def present(self) -> str:
        joined = ", ".join(self.repo.read())
        return f"Data found: {joined}"
