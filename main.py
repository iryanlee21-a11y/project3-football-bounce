import pygame
import sys
import random
import math
from physics import PhysicsEngine
from football import Football

# 벡터 줄임말
Vector2 = pygame.math.Vector2

# 설정 상수
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# 색상 정의
BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
GREEN = (50, 200, 50)
RED = (255, 80, 80)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

def draw_arrow(screen, start, end, color, width=3):
    """
    화살표를 그리는 유틸리티 함수 (시각적 피드백용)
    """
    pygame.draw.line(screen, color, start, end, width)
    
    # 화살표 머리 그리기
    rotation = math.degrees(math.atan2(start.y - end.y, end.x - start.x)) + 90
    pygame.draw.polygon(screen, color, (
        (end.x + 10 * math.sin(math.radians(rotation)), end.y + 10 * math.cos(math.radians(rotation))),
        (end.x + 10 * math.sin(math.radians(rotation - 120)), end.y + 10 * math.cos(math.radians(rotation - 120))),
        (end.x + 10 * math.sin(math.radians(rotation + 120)), end.y + 10 * math.cos(math.radians(rotation + 120)))
    ))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Project #3: Slingshot Football Launch")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20)

    # 1. 물리 월드 생성
    engine = PhysicsEngine(gravity=(0, 1500), ground_y=650, world_width=WINDOW_WIDTH)

    # 2. 풋볼 객체 생성 (화면 왼쪽 바닥에 초기화)
    # 초기 위치를 바닥 근처(600)로 설정하여 티(Tee) 위에 있는 느낌
    ball = Football(x=200, y=600, width=90, height=45, mass=1.5)
    engine.add_body(ball)

    # === [입력 제어 변수] ===
    is_aiming = False           # 조준 중인지 여부
    drag_start_pos = Vector2()  # 마우스를 클릭한 시작 위치
    mouse_pos = Vector2()       # 현재 마우스 위치
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # --- 1. 입력 처리 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # A. 마우스 누름: 조준 시작
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # 왼쪽 클릭
                    is_aiming = True
                    drag_start_pos = Vector2(event.pos)
            
            # B. 마우스 움직임: 현재 위치 갱신 (화살표 그리기용)
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = Vector2(event.pos)

            # C. 마우스 뗌: 발사!
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and is_aiming:
                    is_aiming = False
                    
                    # 발사 벡터 계산: (클릭 위치 - 놓은 위치) => 당기는 반대 방향으로 나감
                    # 힘 조절 상수(5.0)를 곱해줍니다.
                    pull_vector = drag_start_pos - Vector2(event.pos)
                    launch_velocity = pull_vector * 6.0 
                    
                    # 너무 약하면 안 쏘기 (실수 방지)
                    if launch_velocity.length() > 50:
                        ball.vel = launch_velocity
                        # 스핀 추가: 공의 중심과 클릭 위치가 다르면 회전이 걸리는 느낌을 랜덤으로 줌
                        ball.angular_vel = random.uniform(-15, 15)

            # D. R키: 리셋 (공을 제자리로)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    ball.pos = Vector2(200, 600)
                    ball.vel = Vector2(0, 0)
                    ball.angular_vel = 0
                    ball.angle = 0
                    # 공을 멈춤 (운동 에너지 제거)
                    ball.force = Vector2(0, 0)
                    ball.torque = 0

        # --- 2. 물리 업데이트 ---
        # 조준 중일 때는 물리 시간을 멈출 수도 있고, 흐르게 할 수도 있습니다.
        # 여기서는 흐르게 두어 공이 움직이는 중에도 쏠 수 있게 합니다.
        engine.update(dt)

        # --- 3. 렌더링 ---
        screen.fill(BLACK)

        # 지면
        pygame.draw.line(screen, GREEN, (0, engine.ground_y), (WINDOW_WIDTH, engine.ground_y), 4)
        
        # 조준 UI (드래그 중일 때만 표시)
        if is_aiming:
            # 1) 고무줄 그리기 (클릭지점 <-> 마우스)
            pygame.draw.line(screen, GRAY, drag_start_pos, mouse_pos, 2)
            pygame.draw.circle(screen, WHITE, (int(drag_start_pos.x), int(drag_start_pos.y)), 5)

            # 2) 예상 발사 벡터 계산
            pull_vector = drag_start_pos - mouse_pos
            
            # 3) 공에서 나가는 화살표 그리기 (예상 방향)
            # 화살표 길이는 당긴 길이와 비례
            arrow_end = ball.pos + pull_vector
            draw_arrow(screen, ball.pos, arrow_end, YELLOW, 4)

        # 풋볼 그리기
        ball.draw(screen)

        # 안내 텍스트
        ui_texts = [
            f"FPS: {clock.get_fps():.1f}",
            f"Velocity: ({ball.vel.x:.0f}, {ball.vel.y:.0f})",
            "Mouse Drag: Aim & Shoot (Slingshot Style)",
            "R: Reset Ball"
        ]
        for i, t in enumerate(ui_texts):
            surf = font.render(t, True, WHITE)
            screen.blit(surf, (20, 20 + i * 25))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()