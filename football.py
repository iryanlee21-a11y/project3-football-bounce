import pygame
import math
from physics import RigidBody2D

Vector2 = pygame.math.Vector2

class Football(RigidBody2D):
    """
    미식축구공 객체. 
    RigidBody2D를 상속받아 물리 속성을 가지며, 
    타원 형태의 기하학적 특성을 정의함.
    """
    def __init__(self, x, y, width, height, mass=1.0):
        self.width = width
        self.height = height
        
        # [Rigid Body Dynamics] 관성 모멘트 (Moment of Inertia)
        # 타원판의 관성 모멘트 공식: I = m * (a^2 + b^2) / 4
        # 이 값이 커질수록 회전시키기 어렵고, 회전이 오래 유지됨.
        a = width / 2
        b = height / 2
        inertia = mass * (a*a + b*b) / 4.0
        
        # 부모 클래스(RigidBody2D) 초기화
        super().__init__(x, y, mass, inertia)
        
        self.color = (255, 165, 0) # 오렌지색

    def get_support_point(self, direction):
        """
        [Collision Detection] Support Mapping
        특정 방향(direction)으로 가장 멀리 있는 타원 위의 점을 반환함.
        바닥 충돌을 위해 보통 (0, 1) 방향(아래쪽)을 넣음.
        """
        # 회전된 타원의 최하단을 찾기 위해 좌표계를 로컬로 변환하여 계산
        local_angle = -self.angle
        c = math.cos(local_angle)
        s = math.sin(local_angle)
        
        # 방향 벡터를 로컬 좌표계로 회전
        local_dir = Vector2(
            direction.x * c - direction.y * s,
            direction.x * s + direction.y * c
        )

        a = self.width / 2
        b = self.height / 2
        
        # 타원의 지지점 공식
        den = math.sqrt((a * local_dir.x)**2 + (b * local_dir.y)**2)
        if den == 0: return self.pos

        local_point = Vector2(
            (a**2 * local_dir.x) / den,
            (b**2 * local_dir.y) / den
        )

        # 구한 점을 다시 월드 좌표계로 변환 (회전 + 이동)
        world_angle = self.angle
        wc = math.cos(world_angle)
        ws = math.sin(world_angle)
        
        rotated_x = local_point.x * wc - local_point.y * ws
        rotated_y = local_point.x * ws + local_point.y * wc
        
        return self.pos + Vector2(rotated_x, rotated_y)

    def draw(self, screen):
        """
        화면에 풋볼 그리기
        """
        # 1. 투명 배경의 Surface 생성
        surf = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)
        
        # 2. 타원 그리기
        pygame.draw.ellipse(surf, self.color, (0, 0, int(self.width), int(self.height)))
        # 회전 상태를 확인하기 위한 흰색 줄무늬
        pygame.draw.line(surf, (255, 255, 255), (0, int(self.height/2)), (int(self.width), int(self.height/2)), 2)
        
        # 3. 회전 (Pygame의 transform.rotate 사용)
        # angle은 라디안이므로 도(degree)로 변환
        rotated_surf = pygame.transform.rotate(surf, -math.degrees(self.angle))
        
        # 4. 중심점 기준으로 위치 보정하여 그리기
        rect = rotated_surf.get_rect(center=(self.pos.x, self.pos.y))
        screen.blit(rotated_surf, rect.topleft)
        
        # (디버그용) 접촉 감지점 표시
        # sp = self.get_support_point(Vector2(0, 1))
        # pygame.draw.circle(screen, (255, 0, 0), (int(sp.x), int(sp.y)), 3)