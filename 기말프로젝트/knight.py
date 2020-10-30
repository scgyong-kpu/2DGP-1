from pico2d import *
import gfw
import gobj

def load_images_name(action):
    images = {}
    count = 0
    file_fmt = '%s/knight/%s/%s (%d).png'
    action_images = []
    n = 0
    while True:
        n += 1
        fn = file_fmt % (gobj.RES_DIR, action, action, n)
        if os.path.isfile(fn):
            action_images.append(gfw.image.load(fn))
        else:
            break
        count += 1
    images = action_images
    print('%d images loaded' % (count))
    return images

gravity = 0.4

class IdleState:
    @staticmethod
    def get(knight):
        if not hasattr(IdleState, 'singleton'):
            IdleState.singleton = IdleState()
            IdleState.singleton.knight = knight
        return IdleState.singleton

    def __init__(self):
        self.images = load_images_name('Idle')

    def enter(self):
        self.time = 0
        self.fidx = 0

    def exit(self):
        pass

    def draw(self):
        image = self.images[self.fidx]
        image.composite_draw(0, self.knight.flip, *self.knight.pos, image.w, image.h)

    def update(self):
        dx, dy = self.knight.delta
        self.time += gfw.delta_time
        gobj.move_obj(self.knight)
        frame = self.time * 15
        self.fidx = int(frame) % len(self.images)

        if dx != 0:
            self.knight.set_state(WalkState)

    def handle_event(self, e):
        pair = (e.type, e.key)
        if pair in Knight.KEY_MAP:
            self.knight.delta = gobj.point_add(self.knight.delta, Knight.KEY_MAP[pair])
        elif pair == Knight.KEYDOWN_SPACE:
            dx, dy = self.knight.delta
            dy = 15
            self.knight.delta = (dx, dy)
            self.knight.set_state(JumpState)

class WalkState:
    @staticmethod
    def get(knight):
        if not hasattr(WalkState, 'singleton'):
            WalkState.singleton = WalkState()
            WalkState.singleton.knight = knight
        return WalkState.singleton

    def __init__(self):
        self.images = load_images_name('Walk')

    def enter(self):
        self.time = 0
        self.fidx = 0

    def exit(self):
        pass

    def draw(self):
        image = self.images[self.fidx]
        image.composite_draw(0, self.knight.flip, *self.knight.pos, image.w, image.h)

    def update(self):
        self.time += gfw.delta_time
        gobj.move_obj(self.knight)
        frame = self.time * 15
        self.fidx = int(frame) % len(self.images)
        dx, dy = self.knight.delta
        if dx == 0:
            self.knight.set_state(IdleState)


    def handle_event(self, e):
        pair = (e.type, e.key)
        if pair in Knight.KEY_MAP:
            self.knight.delta = gobj.point_add(self.knight.delta, Knight.KEY_MAP[pair])
        elif pair == Knight.KEYDOWN_SPACE:
            dx, dy = self.knight.delta
            dy = 15
            self.knight.delta = (dx, dy)
            self.knight.set_state(JumpState)

class FallState:
    @staticmethod
    def get(knight):
        if not hasattr(FallState, 'singleton'):
            FallState.singleton = FallState()
            FallState.singleton.knight = knight
        return FallState.singleton

    def __init__(self):
        self.images = load_images_name('Fall')

    def enter(self):
        self.time = 0
        self.fidx = 0

    def exit(self):
        dx, dy = self.knight.delta
        self.knight.delta = (dx, 0)

    def draw(self):
        image = self.images[self.fidx]
        image.composite_draw(0, self.knight.flip, *self.knight.pos, image.w, image.h)

    def update(self):
        dx, dy = self.knight.delta
        dy -= gravity
        dy = clamp(-10, dy, 15)
        self.knight.delta = (dx, dy)
        self.time += gfw.delta_time
        gobj.move_obj(self.knight)
        frame = self.time * 15
        self.fidx = int(frame) % len(self.images)

        if self.knight.pos[1] <= 80:
            self.knight.set_state(IdleState)

    def handle_event(self, e):
        pair = (e.type, e.key)
        if pair in Knight.KEY_MAP:
            self.knight.delta = gobj.point_add(self.knight.delta, Knight.KEY_MAP[pair])

class JumpState:
    @staticmethod
    def get(knight):
        if not hasattr(JumpState, 'singleton'):
            JumpState.singleton = JumpState()
            JumpState.singleton.knight = knight
        return JumpState.singleton

    def __init__(self):
        self.images = load_images_name('Jump')

    def enter(self):
        self.time = 0
        self.fidx = 0

    def exit(self):
        dx, dy = self.knight.delta
        self.knight.delta = (dx, 0)

    def draw(self):
        image = self.images[self.fidx]
        image.composite_draw(0, self.knight.flip, *self.knight.pos, image.w, image.h)

    def update(self):
        dx, dy = self.knight.delta
        dy -= gravity
        self.knight.delta = (dx, dy)
        self.time += gfw.delta_time
        gobj.move_obj(self.knight)
        frame = self.time * 15
        self.fidx = int(frame) % len(self.images)

        if dy <= 0:
            self.knight.set_state(FallState)

    def handle_event(self, e):
        pair = (e.type, e.key)
        if pair in Knight.KEY_MAP:
            self.knight.delta = gobj.point_add(self.knight.delta, Knight.KEY_MAP[pair])
        elif pair == Knight.KEYUP_SPACE:
            self.knight.set_state(FallState)

class Knight:
    KEY_MAP = {
        (SDL_KEYDOWN, SDLK_LEFT):  (-3, 0),
        (SDL_KEYDOWN, SDLK_RIGHT): (3, 0),
        (SDL_KEYUP, SDLK_LEFT):    (3, 0),
        (SDL_KEYUP, SDLK_RIGHT):   (-3, 0)
    }
    KEYDOWN_SPACE = (SDL_KEYDOWN, SDLK_SPACE)
    KEYUP_SPACE = (SDL_KEYUP, SDLK_SPACE)
    ACTIONS = ['Idle', 'Walk', 'Jump', 'Fall']

    def __init__(self):
        self.pos = get_canvas_width() // 2, get_canvas_height() // 2
        self.delta = 0, 0
        self.time = 0
        self.fidx = 0
        self.flip = 'h'
        self.state = None
        self.set_state(FallState)

    def set_state(self, clazz):
        if self.state != None:
            self.state.exit()
        self.state = clazz.get(self)
        self.state.enter()

    def draw(self):
        self.state.draw()

    def update(self):
        self.state.update()

    def handle_event(self, e):
        self.state.handle_event(e)
        # flip 설정
        pair = (e.type, e.key)
        if pair == (SDL_KEYDOWN, SDLK_LEFT):
           self.flip = ''
        elif pair == (SDL_KEYDOWN, SDLK_RIGHT):
           self.flip = 'h'

    def get_bb(self):
        x,y = self.pos
        return x - 40, y - 50, x + 40, y + 40