import redis
from django.conf import settings

from oauth.service.redis_service import RedisService


class RedisServiceImpl(RedisService):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.redis_client = redis.StrictRedis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )

        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def store_access_token(self, account_id, userToken):
        try:
            self.redis_client.set(userToken, account_id)
        except Exception as e:
            print('Error storing access token in Redis:', e)
            raise e

    # userToken 받으면 나는 Account 누구다
    # 즉 기존 게시판의 작성자를 직접 write 하지 않고
    # 이제 userToken으로 자동화하여 기입할 수 있음
    # 장바구니, 상품 구매 등등 또한 모두 같은 맥락임
    # 누가(Account id)가 뭐 했다
    def getValueByKey(self, key):
        try:
            return self.redis_client.get(key)
        except Exception as e:
            print("redis key로 value 찾는 중 에러 발생:", e)
            raise e

    def deleteKey(self, key):
        try:
            result = self.redis_client.delete(key)
            if result == 1:
                print(f"유저 토큰 삭제 성공: {key}")    #디버깅을 위해 print를 찍었지만 실제 서비스에선 print를 빼는게 좋다.
                return True                          #왜? 일단 print가 I/O이니까 성능에 영향을 주기도 하고
                                                     # key값은 예민한 정보이니 출력을 안 찍는게 좋다.

            return False
        except Exception as e:
            print("redis key 삭제 중 에러 발생:", e)
            raise e

