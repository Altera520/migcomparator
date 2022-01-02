from datetime import datetime


class elapsed_time:
    """
    경과시간 출력 데코레이터
    """
    def __init__(self, text=None):
        self._text = f', text: {text})' if text else ')'

    def __call__(self, func):
        def wrap(instance, *args, **kwargs):
            start_time = datetime.now()
            result = func(instance, *args, **kwargs)
            end_time = datetime.now()
            print(f"[TIME ELAPSED] - (time: {end_time - start_time}{self._text}")
            return result
        return wrap
