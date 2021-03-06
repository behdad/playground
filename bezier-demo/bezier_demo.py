from __future__ import division

import math
import Tkinter

import cu2qu


# curve render resolution (# points to draw)
RESOLUTION = 20

# max approximation error
MAX_ERR = 2


class BezierDemo(object):
    def __init__(self, renderer_class):
        self.ctrl_pts = []
        self.curve = []
        self.approx_curves= []
        self.active_pt = -1
        self.renderer = renderer_class(
            self._handle_mouse_down, self._handle_mouse_move)

    def run(self):
        self.renderer.run()

    def _handle_mouse_down(self, renderer, x, y):
        if len(self.ctrl_pts) < 4:
            self.ctrl_pts.append((x, y))
            if len(self.ctrl_pts) == 4:
                self._calc_approx()
        else:
            self.active_pt = 0
            pt = self.ctrl_pts[0]
            cur_dist = self._dist(pt, (x, y))
            for i in range(1, len(self.ctrl_pts)):
                other_pt = self.ctrl_pts[i]
                other_dist = self._dist(other_pt, (x, y))
                if other_dist < cur_dist:
                    self.active_pt = i
                    pt = other_pt
                    cur_dist = other_dist
        self._draw(renderer)

    def _handle_mouse_move(self, renderer, x, y):
        if self.active_pt < 0:
            return
        self.ctrl_pts[self.active_pt] = (x, y)
        self._calc_approx()
        self._draw(renderer)

    def _draw(self, renderer):
        renderer.draw(self.ctrl_pts, self.curve, self.approx_curves)

    def _dist(self, p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def _lerp(self, a, b, t):
        return a + (b - a) * t

    def _lerp_pt(self, p0, p1, t):
        (x0, y0), (x1, y1) = p0, p1
        return self._lerp(x0, x1, t), self._lerp(y0, y1, t)

    def _bezier_at(self, pts, t):
        if len(pts) == 1:
            return pts[0]
        return self._lerp_pt(
            self._bezier_at(pts[:-1], t), self._bezier_at(pts[1:], t), t)

    def _calc_bez(self, ctrl_pts, rendered_pts):
        n = RESOLUTION
        for i in range(n + 1):
            rendered_pts.append(self._bezier_at(ctrl_pts, i / n))

    def _calc_bez_spline(self, ctrl_pts, rendered_pts):
        num_segments = len(ctrl_pts) - 2
        for i in range(num_segments):
            p0 = ctrl_pts[i] if i == 0 else p2
            p1 = ctrl_pts[i + 1]
            if i == num_segments - 1:
                p2 = ctrl_pts[i + 2]
            else:
                p2 = self._lerp_pt(ctrl_pts[i + 1], ctrl_pts[i + 2], 0.5)
            curve = []
            self._calc_bez((p0, p1, p2), curve)
            rendered_pts.append(curve)

    def _calc_approx(self):
        self.curve = []
        self.approx_curves = []
        self._calc_bez(self.ctrl_pts, self.curve)
        approx = cu2qu.curve_to_quadratic(self.ctrl_pts, MAX_ERR)
        self._calc_bez_spline(approx, self.approx_curves)


class TkinterRenderer(object):
    def __init__(self, mouse_down_callback, mouse_move_callback):
        self.mouse_down_callback = mouse_down_callback
        self.mouse_move_callback = mouse_move_callback

    def run(self):
        root = Tkinter.Tk()
        self.canvas = Tkinter.Canvas(root, width=750, height=750)
        self.canvas.pack()
        self.ctrl_pt_ids = [
            self._add_pt(6, 'black') for _ in range(4)]
        self.curve_pt_ids = self._add_curve(4, 'blue')
        self.approx_curve_pt_ids = [
            self._add_curve(2, 'green') for _ in range(10)]
        self.canvas.bind('<Button-1>', self._handle_mouse_down)
        self.canvas.bind('<B1-Motion>', self._handle_mouse_move)
        Tkinter.mainloop()

    def draw(self, ctrl_pts, curve, approx_curves):
        assert len(approx_curves) <= len(self.approx_curve_pt_ids)
        self._move_pts(self.ctrl_pt_ids, ctrl_pts)
        self._move_pts(self.curve_pt_ids, curve)
        for pt_ids, pts in zip(
                self.approx_curve_pt_ids, approx_curves):
            self._move_pts(pt_ids, pts)

    def _add_pt(self, radius, color):
        return self.canvas.create_oval(
            -radius * 2, -radius * 2, 0, 0, fill=color, outline=color)

    def _add_curve(self, radius, color):
        return [
            self._add_pt(radius, color) for _ in range(RESOLUTION)]

    def _center(self, pt_id):
        x0, y0, x1, y1 = self.canvas.bbox(pt_id)
        return (x0 + x1) * 0.5, (y0 + y1) * 0.5

    def _move_pt(self, pt_id, x, y):
        old_x, old_y = self._center(pt_id)
        self.canvas.move(pt_id, x - old_x, y - old_y)

    def _move_pts(self, pt_ids, pts):
        for pt_id, (x, y) in zip(pt_ids, pts):
            self._move_pt(pt_id, x, y)

    def _handle_mouse_down(self, event):
        self.mouse_down_callback(self, event.x, event.y)

    def _handle_mouse_move(self, event):
        self.mouse_move_callback(self, event.x, event.y)


def main():
    demo = BezierDemo(TkinterRenderer)
    demo.run()


if __name__ == '__main__':
    main()
