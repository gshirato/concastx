import cv2


class ROISquareSelector:
    def __init__(self):
        self.original = None
        self.image = None
        self.start_point = None
        self.end_point = None
        self.drawing = False

    def select_roi(self, img):
        self.original = img.copy()
        self.image = self.original.copy()
        cv2.namedWindow("ROI Selection")
        cv2.setMouseCallback("ROI Selection", self.mouse_callback)

        while True:
            cv2.imshow("ROI Selection", self.image)
            key = cv2.waitKey(1) & 0xFF
            if key == 13 or key == 27:  # Enter or ESC key
                break

        cv2.destroyWindow("ROI Selection")
        return (
            self.start_point[0],
            self.start_point[1],
            self.end_point[0] - self.start_point[0],
            self.end_point[1] - self.start_point[1],
        )

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.image = self.original.copy()
            self.start_point = (x, y)
            self.drawing = True
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.draw_square(x, y)
            self.end_point = (
                self.start_point[0] + self.length,
                self.start_point[1] + self.length,
            )
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.draw_square(x, y)

    def draw_square(self, x, y):
        self.image = self.original.copy()
        self.length = min(abs(x - self.start_point[0]), abs(y - self.start_point[1]))
        cv2.rectangle(
            self.image,
            self.start_point,
            (self.start_point[0] + self.length, self.start_point[1] + self.length),
            (255, 0, 0),
            4,
        )
