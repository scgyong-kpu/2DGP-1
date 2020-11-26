import os.path
import gfw
from pico2d import *
import gobj
from knight import Knight, RecoilState, DeathState
from crawlid import Crawlid
from hornet import Hornet
from HUD import Frame
import game_end_state
from background import FixedBackground

canvas_width = 1280
canvas_height = 720

def enter():
    gfw.world.init(['bg', 'platform', 'enemy', 'hornet', 'needle', 'knight', 'slash', 'ui'])

    bg = FixedBackground('res/KingsPass_cut.png')
    gfw.world.add(gfw.layer.bg, bg)

    crawlid = Crawlid()
    crawlid.bg = bg
    gfw.world.add(gfw.layer.enemy, crawlid)

    global knight
    knight = Knight()
    knight.bg = bg
    bg.target = knight
    gfw.world.add(gfw.layer.knight, knight)

    global frame
    frame = Frame(knight)
    gfw.world.add(gfw.layer.ui, frame)

    global hornet
    hornet = Hornet()
    hornet.bg = bg
    hornet.target = knight
    gfw.world.add(gfw.layer.hornet, hornet)

    global bgm, opening_sting, enemy_damaged
    bgm = gfw.sound.load_m('res/Sound/cave_wind_loop.mp3')
    opening_sting = gfw.sound.load_w('res/Sound/S75 Opening Sting-08.wav')
    enemy_damaged = gfw.sound.load_w('res/Sound/enemy_damage.wav')

    opening_sting.set_volume(50)
    bgm.repeat_play()
    opening_sting.play()

def knight_damaged_by(e):
    if knight.time > Knight.Unbeatable_Time:
        knight.time = 0.0
        if knight.mask > 1:
            knight.mask -= 1
            frame.mask_stack[knight.mask].set_action('Break')
            knight.set_state(RecoilState)
            if knight.pos[0] <= e.pos[0]:
                knight.flip = 'h'
                knight.delta = (-2, 1)
            else:
                knight.flip = ''
                knight.delta = (2, 1)
        elif knight.mask == 1:
            frame.mask_stack[0].set_action('Break')
            knight.set_state(DeathState)

def check_collide(e):
    global knight, frame
    if gobj.collides_box(knight, e):
        if e.action != 'Death':
            knight_damaged_by(e)

    for s in gfw.world.objects_at(gfw.layer.slash):
        if gobj.collides_box(s, e):
            if e.action != 'Death' and e.slashed != s:
                enemy_damaged.play()
                e.slashed = s
                e.health -= 5
                if knight.flip == 'h':
                    e.pos = gobj.point_add(e.pos, (100, 0))
                elif knight.flip == '':
                    e.pos = gobj.point_add(e.pos, (-100, 0))

def check_collides_needle():
    global knight, hornet
    if hornet.ball is not None:
        if gobj.collides_distance(knight, hornet.ball):
            knight_damaged_by(hornet.ball)
    elif hornet.th_needle is not None:
        if gobj.collides_box(knight, hornet.th_needle):
            knight_damaged_by(hornet.th_needle)


def update():
    gfw.world.update()
    for e in gfw.world.objects_at(gfw.layer.enemy):
        check_collide(e)

    global hornet
    check_collide(hornet)
    check_collides_needle()

    global frame
    if frame.cracked_time >= 1.5:
        gfw.change(game_end_state)

def draw():
    gfw.world.draw()
    gobj.draw_collision_box()

def handle_event(e):
    global knight
    if e.type == SDL_QUIT:
        gfw.quit()
    elif e.type == SDL_KEYDOWN:
        if e.key == SDLK_ESCAPE:
            gfw.pop()

    knight.handle_event(e)

def exit():
    global bgm, opening_sting
    bgm.stop()
    gfw.sound.unload_m('res/Sound/cave_wind_loop.mp3')
    gfw.sound.unload_w('res/Sound/S75 Opening Sting-08.wav')

    for e in gfw.world.objects_at(gfw.layer.enemy):
        for w in e.sounds:
            e.sounds[w].set_volume(0)

    gfw.world.clear()

def pause():
    pass
def resume():
    pass

if __name__ == '__main__':
    gfw.run_main()
