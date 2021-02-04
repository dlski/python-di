"""
Module containing config class
"""


class Config:
    """
    Simple application config
    """

    def __init__(self, num: int):
        """
        Config init
        :param num: number of elements in one combination group
        """
        self.num = num


# initialised config as present value example
config = Config(num=2)
