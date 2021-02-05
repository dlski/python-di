from typing import List

from tests.di.builder.mod_simple import Repo


class MockupRepo(Repo):
    def read(self) -> List[str]:
        return ["di", "test"]
