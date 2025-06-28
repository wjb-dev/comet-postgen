import abc


class Service(abc.ABC):
    name: str

    @abc.abstractmethod
    async def startup(self): ...

    @abc.abstractmethod
    async def shutdown(self): ...