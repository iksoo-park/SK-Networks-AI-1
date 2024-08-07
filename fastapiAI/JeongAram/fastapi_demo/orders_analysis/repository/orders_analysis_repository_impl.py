from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from orders_analysis.repository.orders_analysis_repository import OrdersAnalysisRepository

import tensorflow as tf

# 인공신경망(Artificial Nerual Network)는 사람의 뇌 신경망을 모방하여 만들어진 시스템입니다.
# 패턴 인식 및 데이터 분류와 같은 작업에서 사용되며 기계 학습과 딥러닝에 있어 중요합니다.

# 뉴런 <- 여러 신호를 입력 받음
# 우리가 작성한 코드에선 input_shape에 해당함
# 가중치 <- 각 입력에 가중치가 존재하여 학습하면서 이 값이 조정됨
# 활성함수 <- 입력의 총합을 처리하여 최종 결과를 얻는데 사용함
#            대표적인 녀석으로 sigmoid, ReLU, tanh, softmax 같은 것들이 있음

# Layer는 Input Layer, Hidden Layer, Output Layer로 구성됩니다.
# 입출력은 유일하지만 Hidden Layer는 더 다양하게 많이 구성될 수 있습니다.
# 위의 input_shape이 Input Layer에서 지정되어야 합니다.

# 시그모이드는 출력을 0~1 사이로 압축합니다.
# 즉 확률을 계산하기 위한 목적으로 사용합니다.
# ReLU는 입력 값이 0보다 작으면 0 , 크면 값을 그대로 유지합니다.
# tanh의 경우 값을 -1 ~ 1 사이로 압축합니다.
# 이와 같은 특성 때문에 데이터가 요동치는 경우에 적합합니다.

# 보편적으로 ANN을 구성하는 방법은 아래와 같습니다.
# 1. 먼저 학습한 데이터를 확보합니다.
# 2. 전처리를 진행합니다.(쓸데없는 데이터, 이상치들 제거)
# 3. 요상한 데이터가 없다면 신경망을 구성합니다.
# 4. 구성한 신경망으로 학습을 진행합니다.
# 5. 추론 시 빠르게 활용할 수 있도록 학습 정보를 저장합니다.(*.h5, *.keras)
# 6. 추론을 요청하면 앞서 저장한 *.h5 및 *.keras 에서 정보를 읽어서 빠르게 응답합니다.

# CNN: 컨볼루션 기반 신경망 -> 이미지 처리에 적합함
# RNN: 피드백이 포함된 구조로 시간 순서가 있는 경우에 적합함

# 4분위수 ?
# 전체 샘플 중에서 가운데가 어딘지 찾는 것(중앙값:Median) -> 이상치들이 있는 오류에서 사용

class OrdersAnalysisRepositoryImpl(OrdersAnalysisRepository):
    # viewCount와 quantity 열을 추출하여 독립 변수 X와 종속 변수 y로 사용
    #
    async def prepareViewCountVsQuantity(self, dataFrame):
        X = dataFrame['viewCount'].values.reshape(-1, 1) # ['컬럼명'] 열벡터로 들어오는 데이터프레임을 reshape으로 행으로 바꿈
        y = dataFrame['quantity'].values

        scaler = StandardScaler()  # 표준화 : 정해진 식에 따라 작동 -> 정규 분포의 형태
        X_scaled = scaler.fit_transform(X)

        return X_scaled, y, scaler

    # 데이터 전체 중 훈련 집합으로 80%, 테스트 목적으로 20%를 구성함
    # train, test 의 순서로 작성해야함 -> 순서가 바뀌면 결과가 완전 바뀌게 됨
    async def splitTrainTestData(self, X_scaled, y):
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )

        return X_train, X_test, y_train, y_test

    # Keras Sequential 모델 생성
    # 입력 크기가 1인 입력층을 구성하고 Dropout을 사용하여 일정 데이터를 버렸음
    # 현재 상황이 데이터 특정이 안되기 때문에 Dropout을 버리는 것은 사실 다소 위험할 수 있음
    # Sequential 은 형태가 늘어져 있게(유지?될 수 있게)해주는 포장지 같은 역할
    # 입력하는 값보다 중간 레이어가 많아야하고(예상하지 못하는 값으로 흐트려놓기 위해서)
    # layer를 줄여가면서 마지막에 Dense(1)이 원하는 결과값
    # activation(활성함수): 비선형성을 더해주기 위함
    # relu는 음수를 0으로 처리하기 때문에 tanh을 섞어서 조금 남겨두겠다
    #
    async def createModel(self):
        model = tf.keras.models.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(1,)), # 조회수 1개, 입력레이어
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(64, activation='relu'), # 히든레이어
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation='tanh'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='tanh'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='tanh'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(8, activation='relu'),
            tf.keras.layers.Dense(8, activation='tanh'),
            tf.keras.layers.Dense(4, activation='relu'),
            tf.keras.layers.Dense(4, activation='tanh'),
            tf.keras.layers.Dense(2, activation='relu'),
            tf.keras.layers.Dense(2, activation='tanh'),
            tf.keras.layers.Dense(1)
        ]) # 과적합 방지 위해서 20% 버리는 것을 선택 (dropout)

        # 학습하기 전에 미리 지정해주는 부분
        model.compile(
            # learning_rate: 어떤 값으로 수렴하는 속도
            # 너무 작으면 학습 속도가 너무 오래 걸림
            # 너무 크면 도달하고자 하는 점을 넘어가서 발산될 수 있음
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mean_squared_error',
            metrics=['mae']  # 측정 기준: 실제값과 예측값이 유사하게 흘러갈 수 있도록 페널티를 줌
            # 예측값과 실제값의 차이가 클수록 metric이 커짐 -> 절댓값 사용
        )

        return model

    # 실제 모델에 대한 fit을 할 때 학습하는 과정 자체
    # 이 과정 자체를 보여주고자 한다면 verbose를 1로 설정하면 됨
    # model.fit을 해야 학습을 하게 됨 (모의고사라도 풀어본 애가 됨)
    # validation이 없어도 돌아가지만 있어야 좀 더 정확한 방향(loss와 optimizer)으로 할 수 있음
    # 20%를 빼놓음 -> 훈련이 끝나면 끝난 상태에서 20%를 넣어 한 번 더 검증시켜 예측함
    # batch_size : 학습시킬 때 얼만큼씩 붙여서 학습시킬지(보통 짝수) -> 정확도는 어느정도 감수해야 하지만 속도는 빨라짐
    # verbose: 0이면 중간과정 생략(epoch 안에 있는 일) -> 큰 틀만 나옴
    async def fitModel(self, model, X_train, y_train):
        model.fit(X_train, y_train, epochs=100, validation_split=0.2, batch_size=32, verbose=0)

    # 입력 데이터를 스케일링함
    # StandardScaler로 만들어진 것을 joblib을 이용해서 저장했었음
    # 이를 사용하여 0 ~ 1 사이의 정규 분포 구성으로 설정함
    # 즉 반환 값은 x_pred 라는 녀석을 0~ 1 사이로 정규화한 데이터 리스트
    # transform을 해주기 위해 2차원으로 [[]] 해줌 -> 1차원 배열에서는 돌아가지 않음
    async def transformFromScaler(self, scaler, X_pred):
        return scaler.transform(X_pred)

    # 훈련된 Keras Model을 사용하여 실질적인 예측을 진행함
    # 실제로 predict()는 2D 배열을 반환하는데
    # flatten()을 사용하여 1D 배열로 변경하여 첫 번째 요소를 반환
    #
    async def predictFromModel(self, ordersModel, X_pred_scaled):
        return ordersModel.predict(X_pred_scaled).flatten()[0]

