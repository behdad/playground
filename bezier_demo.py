from __future__ import division

import math
import Tkinter

import cu2qu


# curve render resolution (# points to draw)
RESOLUTION = 20

# max approximation error
MAX_ERR = 2


class BezierDemo(object):
    def __init__(self):
        self.ctrl_pts = []
        self.curve = []
        self.approx_curves= []
        self.active_pt = -1

    def dist(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def lerp(self, a, b, t):
        return a + (b - a) * t

    def lerp_pt(self, p0, p1, t):
        (x0, y0), (x1, y1) = p0, p1
        return self.lerp(x0, x1, t), self.lerp(y0, y1, t)

    def bezier_at(self, pts, t):
        if len(pts) == 1:
            return pts[0]
        return self.lerp_pt(
            self.bezier_at(pts[:-1], t), self.bezier_at(pts[1:], t), t)

    def calc_bez(self, ctrl_pts, rendered_pts):
        n = RESOLUTION
        for i in range(n + 1):
            rendered_pts.append(self.bezier_at(ctrl_pts, i / n))

    def calc_bez_spline(self, ctrl_pts, rendered_pts):
        num_segments = len(ctrl_pts) - 2
        for i in range(num_segments):
            p0 = ctrl_pts[i] if i == 0 else p2
            p1 = ctrl_pts[i + 1]
            if i == num_segments - 1:
                p2 = ctrl_pts[i + 2]
            else:
                p2 = self.lerp_pt(ctrl_pts[i + 1], ctrl_pts[i + 2], 0.5)
            curve = []
            self.calc_bez((p0, p1, p2), curve)
            rendered_pts.append(curve)

    def calc_approx(self):
        self.curve = []
        self.approx_curves = []
        self.calc_bez(self.ctrl_pts, self.curve)
        approx = cu2qu.curve_to_quadratic(self.ctrl_pts, MAX_ERR)
        self.calc_bez_spline(approx, self.approx_curves)

    def handle_mouse_down(self, x, y):
        if len(self.ctrl_pts) < 4:
            self.ctrl_pts.append((x, y))
            if len(self.ctrl_pts) == 4:
                self.calc_approx()
        else:
            self.active_pt = 0
            pt = self.ctrl_pts[0]
            cur_dist = self.dist(pt, (x, y))
            for i in range(1, len(self.ctrl_pts)):
                other_pt = self.ctrl_pts[i]
                other_dist = self.dist(other_pt, (x, y))
                if other_dist < cur_dist:
                    self.active_pt = i
                    pt = other_pt
                    cur_dist = other_dist

    def handle_mouse_move(self, x, y):
        if self.active_pt < 0:
            return
        self.ctrl_pts[self.active_pt] = (x, y)
        self.calc_approx()


class TkinterRenderer(object):
    def __init__(self, demo):
        self.demo = demo
        root = Tkinter.Tk()
        self.canvas = Tkinter.Canvas(root, width=750, height=750)
        self.canvas.pack()
        self.ctrl_pt_ids = [
            self.add_pt(6, 'black') for _ in range(4)]
        self.curve_pt_ids = self.add_curve(4, 'blue')
        self.approx_curve_pt_ids = [
            self.add_curve(2, 'green') for _ in range(10)]
        self.canvas.bind('<Button-1>', self.handle_mouse_down)
        self.canvas.bind('<B1-Motion>', self.handle_mouse_move)
        Tkinter.mainloop()

    def add_pt(self, radius, color):
        return self.canvas.create_oval(
            -radius * 2, -radius * 2, 0, 0, fill=color, outline=color)

    def add_curve(self, radius, color):
        return [
            self.add_pt(radius, color) for _ in range(RESOLUTION)]

    def center(self, pt_id):
        x0, y0, x1, y1 = self.canvas.bbox(pt_id)
        return (x0 + x1) * 0.5, (y0 + y1) * 0.5

    def move_pt(self, pt_id, x, y):
        old_x, old_y = self.center(pt_id)
        self.canvas.move(pt_id, x - old_x, y - old_y)

    def move_pts(self, pt_ids, pts):
        for pt_id, (x, y) in zip(pt_ids, pts):
            self.move_pt(pt_id, x, y)

    def draw(self):
        assert len(self.demo.approx_curves) <= len(self.approx_curve_pt_ids)
        self.move_pts(self.ctrl_pt_ids, self.demo.ctrl_pts)
        self.move_pts(self.curve_pt_ids, self.demo.curve)
        for pt_ids, pts in zip(
                self.approx_curve_pt_ids, self.demo.approx_curves):
            self.move_pts(pt_ids, pts)

    def handle_mouse_down(self, event):
        self.demo.handle_mouse_down(event.x, event.y)
        self.draw()

    def handle_mouse_move(self, event):
        self.demo.handle_mouse_move(event.x, event.y)
        self.draw()


def main():
    demo = BezierDemo()
    TkinterRenderer(demo)


if __name__ == '__main__':
    main()
