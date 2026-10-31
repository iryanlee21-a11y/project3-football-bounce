import pygame
import math

# 벡터 연산을 위한 단축어
Vector2 = pygame.math.Vector2

# 감쇠율 (1/s): 1초마다 속도에 exp(-k)를 곱한다.
# 프레임 속도와 무관하게 같은 감쇠가 일어나도록 시간 기반으로 적용한다.
# 값은 기존 버전(60 FPS, 서브스텝 8회에서 매 스텝 0.999 / 0.99를 곱하던 방식)과
# 같은 1초 감쇠가 되도록 맞췄다: 0.999^480 ≈ exp(-0.48), 0.99^480 ≈ exp(-4.82)
LINEAR_DAMPING = 0.48
ANGULAR_DAMPING = 4.82
MAX_FRAME_DT = 1 / 30   # 창 이동 등으로 프레임이 크게 밀렸을 때 한 번에 계산할 최대 시간

class RigidBody2D:
    """
    [Rigid Body Dynamics] 수업 내용 기반
    모든 강체(Rigid Body)가 공통으로 가지는 물리 속성 정의
    """
    def __init__(self, x, y, mass, moment_of_inertia):
        # 1. 선형 물리량 (Linear Properties)
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.mass = mass
        # 역질량 (계산 최적화를 위해 미리 저장, 무한대 질량이면 0)
        self.inv_mass = 1.0 / mass if mass > 0 else 0.0

        # 2. 회전 물리량 (Angular Properties)
        self.angle = 0.0        # theta (radians)
        self.angular_vel = 0.0  # omega (rad/s)
        self.inertia = moment_of_inertia # I (Moment of Inertia)
        self.inv_inertia = 1.0 / moment_of_inertia if moment_of_inertia > 0 else 0.0

        # 3. 외력 (Forces)
        self.force = Vector2(0, 0)
        self.torque = 0.0

    def integrate(self, dt, gravity):
        """
        [Numerical Integration] Semi-Implicit Euler Method
        속도를 먼저 갱신하고, 그 속도로 위치를 갱신함
        """
        # 선형 가속도: a = F / m + g
        acceleration = self.force * self.inv_mass + gravity
        self.vel += acceleration * dt

        # 각가속도: alpha = Torque / I
        angular_acc = self.torque * self.inv_inertia
        self.angular_vel += angular_acc * dt

        # 감쇠(Damping): 공기 저항 시뮬레이션 (시간 기반, 프레임 속도와 무관)
        self.vel *= math.exp(-LINEAR_DAMPING * dt)
        self.angular_vel *= math.exp(-ANGULAR_DAMPING * dt)

        # 위치 및 각도 적분
        self.pos += self.vel * dt
        self.angle += self.angular_vel * dt

        # 힘 초기화
        self.force = Vector2(0, 0)
        self.torque = 0.0

class PhysicsEngine:
    """
    물리 시뮬레이션을 총괄하는 클래스
    """
    def __init__(self, gravity=(0, 1200), ground_y=650, world_width=1280):
        self.gravity = Vector2(gravity)
        self.ground_y = ground_y
        self.world_width = world_width
        self.bodies = []
        
        # [Collision Response] 파라미터
        self.restitution = 0.75  # 반발 계수 (e)
        self.friction = 0.4      # 마찰 계수
        
        # [Simulation] 서브 스테핑 횟수 (정밀도 향상)
        self.sub_steps = 8

    def add_body(self, body):
        self.bodies.append(body)

    def update(self, dt):
        """
        전체 물리 월드 업데이트 (서브 스테핑 적용)
        """
        dt = min(dt, MAX_FRAME_DT)
        sub_dt = dt / self.sub_steps
        for _ in range(self.sub_steps):
            self.step(sub_dt)

    def step(self, dt):
        for body in self.bodies:
            # 1. 적분 (Integration)
            body.integrate(dt, self.gravity)
            
            # 2. 지면 충돌 처리 (Collision Response)
            self.resolve_ground_collision(body)

            # 3. 화면 경계 처리 (반대편으로 이동)
            if body.pos.x < 0: body.pos.x = self.world_width
            if body.pos.x > self.world_width: body.pos.x = 0

    def resolve_ground_collision(self, body):
        """
        [Impulsive Collision Response]
        충격량(Impulse)을 계산하여 속도와 각속도를 즉시 변경
        """
        # 지면의 법선 벡터 (위쪽)
        normal = Vector2(0, -1) 
        
        # 해당 강체의 '가장 아래쪽 점'을 찾아옴 (Support Point)
        contact_point = body.get_support_point(Vector2(0, 1))
        
        # 침투 깊이 계산
        penetration = contact_point.y - self.ground_y
        
        # 충돌하지 않았으면 리턴
        if penetration <= 0:
            return

        # 1. 위치 보정 (Projection)
        body.pos.y -= penetration
        contact_point.y -= penetration 

        # 2. 충격량 계산 준비
        # r: 무게 중심에서 접촉점까지의 벡터 (Lever Arm)
        r = contact_point - body.pos
        
        # 접촉점의 속도 (회전 속도 포함)
        # v_point = v_cm + (omega x r)
        rot_vel = Vector2(-body.angular_vel * r.y, body.angular_vel * r.x)
        contact_vel = body.vel + rot_vel

        # 법선 방향 속도 성분
        vn = contact_vel.dot(normal)

        # 물체가 이미 위로 올라가고 있으면 무시
        if vn > 0: return

        # 3. 수직 충격량 (Normal Impulse) 계산 - 수업 Slide 53 참조
        rn_cross = r.x * normal.y - r.y * normal.x 
        inv_mass_sum = body.inv_mass + (rn_cross ** 2) * body.inv_inertia
        
        # 미세 떨림 방지 (Resting Contact)
        e = self.restitution
        if abs(vn) < 20.0: e = 0.0

        j = -(1 + e) * vn
        j /= inv_mass_sum

        impulse = normal * j

        # 4. 충격량 적용
        body.vel += impulse * body.inv_mass
        # 토크 = r x J
        torque_impulse = r.x * impulse.y - r.y * impulse.x
        body.angular_vel += torque_impulse * body.inv_inertia

        # 5. 마찰력 적용 (접선 방향 충격량)
        rot_vel_new = Vector2(-body.angular_vel * r.y, body.angular_vel * r.x)
        contact_vel_new = body.vel + rot_vel_new
        
        tangent = Vector2(1, 0) # 바닥 접선
        vt = contact_vel_new.dot(tangent)

        if abs(vt) > 0.1:
            rt_cross = r.x * tangent.y - r.y * tangent.x
            inv_mass_sum_t = body.inv_mass + (rt_cross ** 2) * body.inv_inertia
            
            jt = -vt / inv_mass_sum_t

            # 쿨롱 마찰 (최대 마찰력 제한)
            max_jt = abs(j) * self.friction
            jt = max(-max_jt, min(max_jt, jt))

            friction_impulse = tangent * jt

            body.vel += friction_impulse * body.inv_mass
            torque_friction = r.x * friction_impulse.y - r.y * friction_impulse.x
            body.angular_vel += torque_friction * body.inv_inertia