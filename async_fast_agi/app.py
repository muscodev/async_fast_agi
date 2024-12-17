
from typing import get_type_hints, Type
from panoramisk.fast_agi import Application, Request as PanoramiskRequest
import logging
import inspect

from .request import Request

logger = logging.getLogger(__name__)


class FastAGIApp(Application):

    def __init__(self, default_encoding='utf-8',request_class: Type[Request] = None, loop=None):
        super().__init__(default_encoding, loop)
        if request_class and not issubclass(request_class, Request):
            raise TypeError(f"{request_class.__name__} must inherit from {Request}")
        
        self.Request:Request = request_class or Request

    def route(self, route: str):

        def decorator(callbk):
            
            async def wrapper(prequest: PanoramiskRequest):
                

                request = self.Request(
                    prequest.app,
                    prequest.headers,
                    prequest.reader,
                    prequest.writer,
                    prequest.encoding,
                )


                kwargs = {}

                if request.parsed_url:
                    for name, param in inspect.signature(callbk).parameters.items():
                        if(name=='request'): 
                            kwargs['request'] = request
                            continue
                        value = request.query_params.get(name,param.default)

                        if(isinstance(value, list)):
                            name_type = get_type_hints(callbk).get(name,list)
                            kwargs[name] = value if name_type == list and value else value[0]
                try:                    
                    return await callbk(**kwargs)                    
                except TypeError:
                    raise



            self.add_route(route, wrapper)

            return callbk

        return decorator
