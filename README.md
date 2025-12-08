# 🏈 FootBall Physics Simulation

**SWCON211 Game Programming Project #3**  
외부 물리 라이브러리 없이 직접 구현한 **2D 강체 물리 엔진**입니다.  
미식축구공(럭비공)이 지면에 닿을 때 발생하는 **회전과 마찰에 의한 불규칙한 바운드**를 시뮬레이션합니다.

## 🚀 실행 방법 (How to Run)

### 필수 라이브러리 설치
터미널에 아래 명령어를 입력하세요.
```bash
pip install pygame
```
### 게임 실행
터미널에 아래 명령어를 입력하여 실행합니다.
```bash
python main.py
```

## 🎮 조작 방법 (Controls)

마우스 왼쪽 드래그: 공을 당겨서 조준 및 발사 (Slingshot)  
R 키: 공 위치 및 물리 상태 초기화 (Reset)  

## ✨ 주요 구현 내용 (Features)
Custom Physics Engine: 질점(Particle)이 아닌 강체(Rigid Body) 기반 물리 엔진 구현  
Rigid Body Dynamics: 타원형 물체의 **관성 모멘트(Moment of Inertia)**와 회전 운동 적용  
Advanced Collision: **충격량(Impulse)**과 마찰력(Friction) 공식을 직접 구현하여 리얼한 바운드 표현  
Optimization: Sub-stepping 기법을 적용하여 고속 충돌 시의 시뮬레이션 안정성 확보  

## 📂 파일 구조
main.py: 게임 실행, 입력 처리, 렌더링  
physics.py: 물리 엔진 코어 (적분, 충돌 처리)  
football.py: 풋볼 객체 정의 (모양, 관성 모멘트)  
