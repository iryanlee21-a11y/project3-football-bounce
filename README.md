FootBall Physics Simulation

SWCON211 Game Programming Project #3
외부 물리 라이브러리 없이 직접 구현한 2D 강체 물리 엔진입니다.
미식축구공(럭비공)이 지면에 닿을 때 발생하는 회전과 마찰에 의한 불규칙한 바운스를 시뮬레이션합니다.

실행 방법 (How to Run)

필수 라이브러리 설치

Python 3.10 이상

pygame 설치

명령어:
pip install pygame

게임 실행

프로젝트 폴더에서 아래 명령어 실행:
python main.py

조작 방법 (Controls)

마우스 왼쪽 드래그: 공을 당겨서 조준 및 발사 (Slingshot)

마우스 오른쪽 클릭: 공 위치 및 물리 상태 초기화 (Reset)

주요 구현 내용 (Features)

Custom Physics Engine: 질점(Particle)이 아닌 강체(Rigid Body) 기반 물리 엔진 구현 (physics.py)

Rigid Body Dynamics: 타원형 풋볼에 관성 모멘트(Moment of Inertia)와 회전 운동 적용

Advanced Collision: 충격량(Impulse)과 마찰력(Friction)을 사용한 바닥 충돌 응답

Optimization: Sub-stepping을 이용하여 고속 충돌 시 시뮬레이션 안정성 확보

파일 구성 (Files)

main.py : 게임 실행, 입력 처리, 렌더링

physics.py : 물리 엔진 코어 (중력, 충돌 처리)

football.py : 풋볼 객체 정의 (모양, 관성 모멘트)