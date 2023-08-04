from manim import *
import numpy as np

order = 144 # <---设置展开阶数
num_arrow = order * 2 # <---设置箭头数量
arrow_angles = np.zeros(num_arrow)

# 通过Tex获得PI图形的矢量路径
def get_path():
    tex_mob =  Text(r"知")
    tex_mob.set_height(6)
    path = tex_mob.family_members_with_points()[0]
    path.set_fill(opacity=0)
    path.set_stroke(WHITE, 1)
    return path

path = get_path()
points_3d = path.points
points = points_3d[:,0:2]
points = np.concatenate((points, points[0:1, :]), axis=0)

# 辛普森积分法
def Simpson(fun,a,b,h):
    I = 0
    for i in range(int(abs(a-b)/h/2)):
        I += (h/3)*(fun(a+h*(2*i))+4*fun(a+h*(2*i+1))+fun(a+h*(2*i+2)))
    return I

def get_init_angle(A, B):
    tan_value = B/A
    arc_tan_value = np.arctan(tan_value)
    arc_tan_value[A<0] = arc_tan_value[A<0] + np.pi
    arc_tan_value[(A>0) & (B<0)] = arc_tan_value[(A>0) & (B<0)] + 2 * np.pi
    return arc_tan_value

def order_lists_by_arrow_lengths_descending(arrow_lengths, init_angle, arrow_speed):
    # Combine the three lists into a single list of tuples
    combined_lists = list(zip(arrow_lengths, init_angle, arrow_speed))

    # Sort the combined list based on the first element of each tuple (arrow_lengths)
    sorted_combined_lists = sorted(combined_lists, key=lambda x: x[0], reverse=True)

    # Unpack the sorted tuples back into separate lists
    sorted_arrow_lengths, sorted_init_angle, sorted_arrow_speed = zip(*sorted_combined_lists)

    return sorted_arrow_lengths, sorted_init_angle, sorted_arrow_speed

def numpy_array_to_str_list(arr, n=3):
    # Round the elements of the NumPy array to two decimal places
    rounded_arr = np.around(arr, decimals=n)

    # Convert the elements to strings with two significant digits
    str_list = [f"{x:.{n}f}" for x in rounded_arr]

    return str_list

# 根据参数方程设置图案形状
xt = points[:,0]
yt = points[:,1]
ts = np.linspace(0, 2 * np.pi, len(xt))

def x(t):
    x_interp = np.interp(t, ts, xt)
    return x_interp

def y(t):
    x_interp = np.interp(t, ts, yt)
    return x_interp

# 被积函数
def At(n, t):
    return 1 / np.pi / 2 * (x(t) * np.cos(n * t) + y(t) * np.sin(n * t))

def Bt(n, t):
    return 1 / np.pi / 2 * (-x(t) * np.sin(n * t) + y(t) * np.cos(n * t))


def calculate_AB(At, Bt, num_arrow):
    A = np.zeros(num_arrow+1)
    B = np.zeros(num_arrow+1)
    
    for i in range(num_arrow+1):
        n = i - num_arrow/2
        A[i] = Simpson(lambda t: At(n, t), 0, 2 * np.pi, 0.001)
        B[i] = Simpson(lambda t: Bt(n, t), 0, 2 * np.pi, 0.001)
    
    A = np.delete(A, order)
    B = np.delete(B, order)
    arrow_lengths = (A**2 + B**2)**(1/2)
    init_angle = get_init_angle(A,B)
    
    arrow_speed = np.delete(np.array(range(num_arrow+1)) - num_arrow/2, order)
    
    return arrow_lengths, init_angle, arrow_speed

arrow_lengths, init_angle, arrow_speed = calculate_AB(At, Bt, num_arrow)

print(f"arrow_lengths:\n {arrow_lengths}")
print(f"init_angle:\n {init_angle}")
print(f"arrow_speed:\n {arrow_speed}")


def get_end_relative_pos(length, angle):
    return np.array([length * np.cos(angle), length * np.sin(angle), 0])

class DrawFourierSoomth(Scene):
    def construct(self):
        
        O = [0,0,0]
        meta_speed = 0.05
        meta_length = 0.6
        
        pause_rotate = False
        pause_draw = True


        ## arrows
        arrows = VGroup(*[Arrow(start = O, end = (RIGHT * meta_length * arrow_lengths[i]), buff = 0
                                ) for i in range(num_arrow)]) # 创建若干个箭头，并放到一个VGroup中
        arrows.arrange_in_grid(12,24,buff=0.3) # 使用VGroup中的arrange_in_grid函数来控制他们的布局（12*24）

        tracks = VGroup(*[Circle(color = BLUE_A, stroke_width = 0.3, radius = meta_length * arrow_lengths[i]) for i in range(num_arrow)]) # 为箭头添加轨迹

        for i in range(num_arrow):
            arrows[i].rotate(init_angle[i], about_point=arrows[i].get_start()) # 让箭头旋转一个初项
            arrows[i].add_updater(lambda mobj, dt, i=i:(
                mobj.rotate(angle = meta_speed * arrow_speed[i] if not pause_rotate else 0, about_point = mobj.get_start()), 
            )) # 添加箭头自动按照速度旋转，并用pause_rotate来控制箭头的旋转与否，这个后面有用
            tracks[i].add_updater(lambda mobj, i=i:(
                mobj.move_to(arrows[i].get_start())
            )) # 设置轨迹自动追踪箭头的位置

        self.play(AnimationGroup(*[FadeIn(arrows), FadeIn(tracks)]))  # 箭头的轨迹的出场动画

        self.wait(5)

        pause_rotate = True # 首先先让箭头停止旋转

        # 计算每一个箭头移动的目标位置，并记录在target_pos中
        addition0 = 1/2 * get_end_relative_pos(meta_length * arrow_lengths[0], arrows[0].get_angle())
        target_pos = [addition0]
        end_pos = [addition0 * 2]
        for i in range(1, num_arrow):
            addition = 1/2 * get_end_relative_pos(meta_length * arrow_lengths[i], arrows[i].get_angle())
            target_pos.append(end_pos[i-1] + addition)
            end_pos.append(target_pos[i] + addition)

        self.play(AnimationGroup(*[(arrows[i].animate.move_to(target_pos[i])) for i in range(num_arrow)],lag_ratio=0.001), run_time = 10) #播放动画

        arrows[0].add_updater(lambda mobj, dt, i=i:(
            mobj.put_start_and_end_on(O, get_end_relative_pos(meta_length * arrow_lengths[0], mobj.get_angle()))  if not pause_draw else None,
        ))
        for i in range(1, num_arrow):
            arrows[i].add_updater(lambda mobj, dt, i=i:(
                mobj.put_start_and_end_on(arrows[i-1].get_end(), arrows[i-1].get_end() + get_end_relative_pos(meta_length * arrow_lengths[i], mobj.get_angle()))  if not pause_draw else None,
            )) # 添加updater，使得后一个的尾部，追踪上一个箭头的头部（就是得让他们连起来）

        self.wait(2)

        pause_rotate = False
        pause_draw = False

        # 画出路径
        path = TracedPath(arrows[-1].get_end, stroke_width = 1, stroke_color = RED_A) 
        self.add(path)
        self.wait(10)