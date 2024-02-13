import os
import re
import inspect

from goscorer import final_territory_score, final_area_score, territory_scoring, area_scoring, string2d, string2d2, EMPTY, BLACK, WHITE

def stones_and_marked_dead_of_str(stonestr: str):
    rows = stonestr.split("\n")
    rows = [row.strip() for row in rows if row.strip() != ""]

    ysize = len(rows)
    xsize = len(rows[0])

    stones = [[EMPTY for x in range(xsize)] for y in range(ysize)]
    marked_dead = [[False for x in range(xsize)] for y in range(ysize)]
    for y in range(ysize):
        for x in range(xsize):
            c = rows[y][x]
            if c == "x":
                stones[y][x] = BLACK
            if c == "o":
                stones[y][x] = WHITE
            if c == "b":
                stones[y][x] = BLACK
                marked_dead[y][x] = True
            if c == "w":
                stones[y][x] = WHITE
                marked_dead[y][x] = True
    return (stones,marked_dead)


def normalize_whitespace(s: str):
    return re.sub(r"\s+", " ", s)

def assert_matches_snapshot(name: str, output: str):
    expected_dir = "./expected_test_output"
    actual_dir = "./actual_test_output"

    expected_path = os.path.join(expected_dir, f"{name}.txt")
    actual_path = os.path.join(actual_dir, f"{name}.txt")

    if os.path.exists(expected_path):
        with open(expected_path) as f:
            expected = f.read()
    else:
        expected = ""

    if normalize_whitespace(expected) == normalize_whitespace(output):
        return

    os.makedirs(actual_dir, exist_ok=True)
    with open(actual_path, "w") as f:
        f.write(output)

    raise AssertionError(f"Failed test!\nExpected:\n{expected}\nActual:\n{output}")


def get_output(stonestr: str):
    rows = stonestr.split("\n")
    rows = [row.strip() for row in rows if row.strip() != ""]
    stones,marked_dead = stones_and_marked_dead_of_str(stonestr)
    scoring = territory_scoring(stones,marked_dead)
    output = ""

    output += "BOARD:" + "\n"
    output += "\n".join(rows) + "\n"
    output += "TERRITORY:" + "\n"
    output += string2d2(scoring, rows, lambda s,c: (
        "z" if s.is_territory_for == BLACK else "a" if s.is_territory_for == WHITE else c
    )) + "\n"
    output += "SEKI:" + "\n"
    output += string2d2(scoring, stones, lambda s,c: (
        "x" if s.belongs_to_seki_group == BLACK and c != EMPTY else
        "o" if s.belongs_to_seki_group == WHITE and c != EMPTY else
        "z" if s.belongs_to_seki_group == BLACK else
        "a" if s.belongs_to_seki_group == WHITE else
        "."
    )) + "\n"
    output += "FALSE EYES:" + "\n"
    output += string2d2(scoring, rows, lambda s,c: (
        "F" if s.is_false_eye else
        c
    )) + "\n"
    output += "UNSCORABLE FALSE EYES:" + "\n"
    output += string2d2(scoring, rows, lambda s,c: (
        "F" if s.is_unscorable_false_eye else
        c
    )) + "\n"
    output += "DAME:" + "\n"
    output += string2d2(scoring, rows, lambda s,c: (
        "1" if s.is_dame else
        c
    )) + "\n"
    output += "EYEVALUE:" + "\n"
    output += string2d2(scoring, rows, lambda s,c: (
        (c if s.eye_value == 0 else "0123456789"[s.eye_value])
    )) + "\n"
    return output

def run_snapshot_test(name: str, stonestr: str):
    output = get_output(stonestr)
    assert_matches_snapshot(name, output)

def test_final_scoring():
    stonestr = """
    .xo.oxxo.
    x.o.oxo.o
    ooooxxo..
    xxxxxxooo
    ....x.x.o
    """
    stones,marked_dead = stones_and_marked_dead_of_str(stonestr)
    assert final_territory_score(stones,marked_dead,black_points_from_captures=0,white_points_from_captures=0,komi=0) == { BLACK: 4, WHITE: 4 }
    assert final_territory_score(stones,marked_dead,black_points_from_captures=0,white_points_from_captures=0,komi=0,score_false_eyes=True) == { BLACK: 5, WHITE: 4 }
    assert final_territory_score(stones,marked_dead,black_points_from_captures=0,white_points_from_captures=0,komi=3.5,score_false_eyes=True) == { BLACK: 5, WHITE: 7.5 }
    assert final_territory_score(stones,marked_dead,black_points_from_captures=8,white_points_from_captures=6,komi=3.5,score_false_eyes=True) == { BLACK: 13, WHITE: 13.5 }
    assert final_area_score(stones,marked_dead,komi=3.5) == { BLACK: 21, WHITE: 25.5 }

    stonestr = """
    .xo.oxxo.
    x.o.oxo.o
    ooooxxob.
    xxxxxxooo
    w..wx.x.o
    """
    stones,marked_dead = stones_and_marked_dead_of_str(stonestr)
    assert final_territory_score(stones,marked_dead,black_points_from_captures=0,white_points_from_captures=0,komi=0) == { BLACK: 6, WHITE: 5 }
    assert final_territory_score(stones,marked_dead,black_points_from_captures=0,white_points_from_captures=0,komi=0,score_false_eyes=True) == { BLACK: 7, WHITE: 5 }
    assert final_territory_score(stones,marked_dead,black_points_from_captures=0,white_points_from_captures=0,komi=3.5,score_false_eyes=True) == { BLACK: 7, WHITE: 8.5 }
    assert final_territory_score(stones,marked_dead,black_points_from_captures=8,white_points_from_captures=6,komi=3.5,score_false_eyes=True) == { BLACK: 15, WHITE: 14.5 }
    assert final_area_score(stones,marked_dead,komi=0) == { BLACK: 21, WHITE: 22 }

    stonestr = """
    .xo.oxxo.
    x.o.oxo.o
    ooooxxo..
    xxxxxxo.w
    ....x.o..
    """
    stones,marked_dead = stones_and_marked_dead_of_str(stonestr)
    assert final_territory_score(stones,marked_dead,black_points_from_captures=0,white_points_from_captures=0,komi=0) == { BLACK: 5, WHITE: 8 }
    assert final_area_score(stones,marked_dead,komi=0) == { BLACK: 19, WHITE: 24 }

def test_empty():
    stonestr = """
    .........
    .........
    .........
    .........
    .........
    .........
    .........
    .........
    .........
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_basic():
    stonestr = """
    ......x..
    .xx.x.x..
    ......x..
    ......x..
    oooooox..
    .....oxxx
    .....o.o.
    ...o.o..o
    .....o...
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_dead_stone_marking():
    stonestr = """
    ..w...xw.
    .xx.x.x.w
    ......xxx
    ......x.o
    oooooox..
    o.o.xoxxx
    oboxxo.o.
    ob.o.o..o
    .ooooo.b.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_false_eyes():
    stonestr = """
    .........
    xxxx.xx..
    .oxoxox..
    o.oo.ox..
    ..oooox.x
    ...o.x.x.
    ....ooxox
    ...o.o.ox
    .....ooo.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_2():
    stonestr = """
    ...xx.x..
    wxxx.x...
    xoxxoxx..
    x.ooxox..
    x.o.xox.x
    oo.o.o.x.
    ....oooxo
    bbbbb..o.
    ....b...b
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_chain():
    stonestr = """
    ......xx.
    ......oox
    ....oo.xx
    ooooo.ox.
    ..o.oooox
    ooo...ox.
    ......oxx
    .......x.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_chain_bamboo():
    stonestr = """
    ......xx.
    ......oox
    ....oo.xx
    ooo.o.ox.
    ..o.oooox
    ooo...ox.
    ......oxx
    .......x.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_chain_no_bamboo():
    stonestr = """
    ......xx.
    ......oox
    ....oo.xx
    oo..o.ox.
    .o..oooox
    oo....ox.
    ......oxx
    .......x.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_chain_loose_eye():
    stonestr = """
    .......x.
    .........
    ..o.oo.xx
    oo.oo.ox.
    .oo.oooox
    oo....ox.
    ......oxx
    .......x.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_chain_loose_eye_2():
    stonestr = """
    .........
    ......oo.
    ..o.oo.x.
    oo.oo.ox.
    .oo.oooox
    oo....ox.
    ......oxx
    .......x.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_chain_loose_eye_3():
    stonestr = """
    .........
    .....xxx.
    ..o.oo.x.
    oo.oo.ox.
    .oo.oooox
    oo....ox.
    ......oxx
    .......x.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_chain_loose_eye_4():
    stonestr = """
    .......x.
    .......x.
    ..o.oo.x.
    oo.oo.ox.
    .oo.oooox
    oo....ox.
    ......oxx
    .......x.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_chain_big_false_eye():
    stonestr = """
    xxx..xxx.
    xooxxooox
    .xo....x.
    .xooooox.
    .xo...ox.
    xoo...oox
    x.o...oxx
    ..o...ox.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_chain_big_false_eye_aliveend():
    stonestr = """
    xxx..xxx.
    xooxxooox
    .xo....x.
    .xooooox.
    .xo...ox.
    xoo..ooox
    x.o.oxxxx
    ..o.ox.x.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eyes_chain_big_false_eye_aliveends():
    stonestr = """
    xxx..xxx.
    xooxxooox
    .xo....x.
    .xooooox.
    .xo...ox.
    xoo..ooox
    x.o.oxxxx
    .xo.ox.w.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_basic_sekis():
    stonestr = """
    .x.o.........x.x.
    ox.o..xwx..xx..oo
    ox.o.o.xx.x..ooo.
    ox.o..ooo..xxo.ox
    .x.o.b.......oxx.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_basic_sekis_marked_dead():
    stonestr = """
    .x.o.........x.x.
    wx.o..xox..xx..oo
    wx.o.o.xx.x..ooo.
    wx.o..ooo..xxo.ob
    .x.o.x.......obb.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_more_fancy_sekis():
    stonestr = """
    .ox.xoo....ox.xo.
    o.xwwxo.o..ox.x.o
    xxxxxxo..o.ooxxxx
    ooooooo.o...ooooo
    xxx..............
    oox..........xxxx
    .ox.....x...xxooo
    ooxxxxx..x..xo.o.
    .xoooox.x.x.xooxx
    x.o.box.....xo.o.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_double_ko_death():
    stonestr = """
    .o.o.........o.o.
    xx.o.........o.xx
    .xxo.o.....o.oxx.
    xoxxo.......oxxwx
    o.oxo.......oxw.w
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_double_ko_death2():
    stonestr = """
    .o.o.........o.o.
    xx.o.........o.xx
    .xxo.o.....o.oxx.
    boxxo.......oxxwb
    o.oxo.......oxw.w
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_double_ko():
    stonestr = """
    .xooox.....xooox.
    xxxxoxx...xxoxxxx
    .xoxoox...xoox.x.
    xo.o.ox...xo.oxox
    oooooox...xo.oooo
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_double_ko2():
    stonestr = """
    .xooox.....xooox.
    xxxxoxx...xxoxxxx
    .xoxoox...xoox.x.
    bo.o.ox...xo.obob
    oooooox...xo.oooo
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_loose_nakade():
    stonestr = """
    .x.........x.........x.........x
    .x.o..x....x.o..x....x.o.xx....x
    .x.o.o.xx..x.o.o.xx..x.ooo.xx..x
    .x.o..ooo..x.o..ooo..x.o..ooo..x
    .x.o.b.....x.o.......x.o.b..o..x
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_cycle():
    stonestr = """
    ...ooooo.x..
    xxoxxxxo.x..
    .xox.xxo.x..
    .xoxx.xo.x..
    .xo.xxooox..
    xxo.ooooox..
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_cycle_false_eye():
    stonestr = """
    .o.ooooo.x..
    xxoxxxxo.x..
    .xox.xxo.x..
    .xoxx.xo.x..
    .xo.xxooox..
    xxo.ooooox..
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_cycle_real_eye():
    stonestr = """
    .o.oooo.ox..
    xxoxxxxoox..
    .xox.xxo.x..
    .xoxx.xo.x..
    .xo.xxooox..
    xxo.ooooox..
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_cycle_real_2eye():
    stonestr = """
    .o.oooo.ox..
    xxoxxxxoox..
    .xox.xxo.x..
    .xoxx.xoxx..
    .xo.xxo.ox..
    xxo.ooooox..
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_cycle_real_3spaceeye():
    stonestr = """
    .o.oooo.x...
    xxoxxxxoox..
    .xox.xxoox..
    .xoxx.xxox..
    .xoxoooxox..
    xxoo...oox..
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_bamboo_interleave_seki():
    stonestr = """
    .xxxxxx.ox..
    xo..x.x.ox..
    xooooxooox..
    xx..xx.o.x..
    x.oo..oo.x..
    xxooxxoo.x..
    x.o.oo.o.x..
    ooooxxoo.x..
    xxxxxxxxx...
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_no_bamboo_interleave_seki_broken():
    stonestr = """
    .xxxxxx.ox..
    xo..xxx.ox..
    xooo...oox..
    xx.....o.x..
    x.ooxx.o.x..
    xxooxxoo.x..
    x.o.oo.o.x..
    ooooxxoo.x..
    xxxxxxxxx...
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_double_throwin_seki4():
    stonestr = """
    .x............
    .x............
    .x............
    .xxx.x.x.x.xx.
    oo.x........x.
    .oxx........o.
    ooxooooooo.oo.
    .oox.....o....
    x.oxxxxx.o....
    xxxww..x.o....
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_double_throwin_seki3():
    stonestr = """
    .x............
    .x............
    .x............
    .xxx.x.x.x.xx.
    oo.x........x.
    .oxx........o.
    ooxooooooo.oo.
    .oox.....o....
    x.oxxxxx.o....
    xxxww.xx.o....
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_side_bamboo_cut():
    stonestr = """
    ..o.o..o.o....
    .xo.oxxo.o.x..
    .xooo..ooox...
    .x...xx...x...
    ..x.x..x.x....
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_cross_noseal():
    stonestr = """
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox......o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_cross_nothrowin():
    stonestr = """
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox...xx.o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_cross_nopoke():
    stonestr = """
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox..wxx.o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_cross_poke():
    stonestr = """
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox.wwxx.o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_cross_poke_deeper():
    stonestr = """
    .o.x.x..o.....
    .o.xxx.o.o....
    oxxx.xo.o.....
    ox..wwxx.o....
    oxxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_three_point_false_eye():
    stonestr = """
    ........o....
    xoooox..o....
    xo.oox..o....
    xoo.oxoo.....
    .xoox.x.o....
    ..xx..x.o....
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_three_point_false_eye_cycle():
    stonestr = """
    ........o....
    x....x..o....
    xo.oox..o....
    xoo.oxoo.....
    .xoox.x.o....
    ..xx..x.o....
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_three_way_pokes():
    stonestr = """
    .xxwwwxx.o...xxwwwxx.o........
    ..ox.xo.o.....oxwxo.o..ooo....
    .o.xxx.o.....o.x.x.o..o...o...
    .o.x.x.o.....o.xxx.o..oxxxo...
    .o.xxx.o.....o.x.x.o..ox.xo...
    ..ooooo.......oxxxo..xxw.wxx..
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_belly_eye():
    stonestr = """
    .b.o.x..
    b..o.x..
    .b.o.x..
    oooo.x..
    xxxxxx..
    ........
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_belly_eye2():
    stonestr = """
    .b.o.x..
    bb.o.x..
    .b.o.x..
    oooo.x..
    xxxxxx..
    ........
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_solid_eyeshapes():
    stonestr = """
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    x.xx..xx.xxx..xxxxx..xxxx..xxxxx
    xxxxxxxx..xx..xxxxxx..xx....xxxx
    x...xxxxx.xxxxxxxxxx.xxxxxxxx...
    xxxxx..xxxxx..xxx.xxxx.xxxxxxx..
    x..xx.xxxxxx..xx...xx...xxxxxxx.
    xx.xx.xx.xxx.xxxx.xxx..xxx...xxx
    xxxxxxx...xxxxxxxxxxxxxxxx...xxx
    x....xxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_solid_eyeshapes_nakade():
    stonestr = """
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    x.xx..xx.xxx..xxxxx..xxxx..xxxxx
    xxxxxxxxw.xxw.xxxxxxw.xx.w..xxxx
    x.w.xxxxx.xxxxxxxxxx.xxxxxxxx.w.
    xxxxxw.xxxxx..xxx.xxxx.xxxxxxx..
    x.wxx.xxxxxxw.xx.w.xx.w.xxxxxxx.
    xx.xx.xx.xxx.xxxx.xxx..xxx.w.xxx
    xxxxxxx.w.xxxxxxxxxxxxxxxx...xxx
    x..w.xxxxxxxxxxxxxxxxxxxxxxxxxxx
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_solid_eyeshapes_nakade2():
    stonestr = """
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    x.xx.wxxwxxx.wxxxxx.wxxxx..xxxxx
    xxxxxxxxw.xxwwxxxxxxw.xx.ww.xxxx
    x.wwxxxxx.xxxxxxxxxx.xxxxxxxx.w.
    xxxxxw.xxxxx.wxxx.xxxxwxxxxxxx.w
    x.wxxwxxxxxxwwxx.w.xxww.xxxxxxx.
    xxwxx.xx.xxx.xxxx.xxxwwxxx.w.xxx
    xxxxxxxww.xxx...xxxxxxxxxx.w.xxx
    x.ww.xxxxxxxx.wwxxxxxxxxxxxxxxxx
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_bamboo_reachable_seki():
    stonestr = """
    ...xxxxxoooooo...
    xxx..x.xo..o..ooo
    oooxxoooxxxxooxxx
    o.o..o.o.x.x..x.x
    .ooxxoooxxxxooxx.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_hanezeki():
    stonestr = """
    oxox.oxw.boxo
    oxoxoxxxoboxo
    oxoxox.xoboxo
    .xooox.xooox.
    xxoxxx.xxxoxx
    ooox.....xooo
    xxxx.....xxxx
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_hanezeki2():
    stonestr = """
    wxox.oxw.boxw
    wxoxoxxxoboxw
    wxoxox.xoboxw
    .xooox.xooox.
    xxoxxx.xxxoxx
    ooox.....xooo
    xxxx.....xxxx
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_big_eye_seki():
    stonestr = """
    .xoxxx
    xxoox.
    .xxooo
    ooxxx.
    .oooxx
    xxxo.x
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_lgroups_and_rectanglelikes():
    stonestr = """
    ....x.o...o.x...x.o..ox...
    ...xooo...o.x...x.o..ox...
    .xxxo.....o.xx.xx.o..oxxx.
    xoooo.....ooooxoooo..oooox
    .o...........o.o........o.
    o..........o..o.........oo
    .o........o.o............o
    xoooo.....oxoooo.....oooo.
    .xxxoo...ox.xxxo.....oxxxx
    ...xxo...ox...xxooooooxw.w
    ....xo...ox.....x.o.o.xw.w
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_lgroups_and_rectanglelikes2():
    stonestr = """
    ...wx.o...o.x.w.x.o..oxw..
    ...xooo...o.x...x.o..oxw..
    xxxxo.....o.xx.xx.o..oxxx.
    xoooo.....ooooxoooo..oooox
    .o...........o.o........o.
    o..........o..o.........oo
    .o........o.o............o
    xoooo.....oxoooo.....oooo.
    .xxxoo...ox.xxxo.....oxxxx
    ..wxxo...ox...xooooooox...
    ...wxo...ox....x.oo.o.x.w.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_lgroups_and_rectanglelikes3():
    stonestr = """
    .....x.o..o.x.ww.xo..ox.w.
    ....xooo..o.x.w.xxo..ox...
    .xxxxo....o.x.xxx.o..oxxx.
    xooooo....oooxooooo..oooox
    .o..........o.o.........o.
    o..........o.o..........oo
    .o........o.o............o
    xoooo.....oxoooo.....ooooo
    .xxxoo...ox.xxxo....ooxxxx
    ...xxo...ox.w.xxoo..oxx...
    ..w.xo...ox.w..x.o..ox.w..
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_lgroups_and_rectanglelikes4():
    stonestr = """
    .w...x.o..ox.www.xo.ox.w..
    .w..xooo..oxx...xxo.oxx...
    xxxxxo....o.xxxxx.o..oxxxw
    xooooo....oooxooooo..oooox
    .o..........o.o.........o.
    o..........o.o..........oo
    .o........o.o............o
    xoooo.....oxoooo.....ooooo
    xxxxoo...oxxxxxo....ooxxxx
    ...xxo...ox...xxoo..oxx...
    ..w.xo...ox..wwx.o..oxxwww
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_lgroups_and_rectanglelikes5():
    stonestr = """
    .w..xx.o..ox.w.w.xo.ox.w..
    .w..xooo..oxx...xxo.ox....
    xxxxxo....o.xxxxx.o.oxxxxw
    xooooo....oooxooooo..oooox
    .o..........o.o.........o.
    o..........o.o..........oo
    .o........o.o............o
    xoooo...oooxoooo.....ooooo
    xxxxoo.ooxxxxxxo....ooxxxx
    w..xxo.oxx....xxoo..oxx.ww
    ..w.xo.ox.wwww.x.o..oxxwww
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_lgroups_and_rectanglelikes6():
    stonestr = """
    xoooo...ooxxxxoo.....ooooo
    xxxxoo.oox.w.xxo....ooxxxx
    .w.xxo.oxx..w.xxoo..oxx.w.
    ..w.xo.oxxxxxxx..o..oxx...
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_two_point_eye_falsity():
    stonestr = """
    .xx..x.oooooooo.ooooooo.
    xxoxxoooxxxoxxoooxxxoxxx
    oooooo.ox.xx..x.ox.xx..x
    xxoxxxooxxxoxxoooxxxoxxx
    .xx..xooooooooo.ooooooo.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


def test_false_eye_multicycles1():
    stonestr = """
    xxxxx.xo............
    xooooxoo............
    .xo.ox.o............
    xo.ooxooooooo.......
    xooooxoxxxxxo.......
    xxxxx.xx.w.xo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_false_eye_multicycles2():
    stonestr = """
    xxxxx.xo............
    xooooxoo............
    .xo.ox.o............
    xo.ooxooooooo.......
    xoooxxoxxxxxo.......
    xxxxx.xx.w.xo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_false_eye_multicycles3():
    stonestr = """
    xxxxx.xo............
    xooooxoo............
    .xo.ox.o............
    xo.ooxooooooo.......
    xooooxxxxxxxo.......
    xxxxx.xx.w.xo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_false_eye_multicycles4():
    stonestr = """
    xxxxx.xo............
    xooooxoooooo........
    .xo.oxxoxxx.o.......
    xo.oox.xx.x.o.......
    xoooxxxoxxxxo.......
    xxxxxoooooooo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_false_eye_multicycles5():
    stonestr = """
    xxxxx.xo............
    xooooxoooooo........
    .xo.oxxoxxx.o.......
    xo.oxx.xx.x.o.......
    xoooxoxxxxxxo.......
    xxxxxoooooooo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_false_eye_multicycles6():
    stonestr = """
    .xxxx.xo............
    xooooxoooooo........
    .xo.oxxoxxx.o.......
    xo.oxx.xx.x.o.......
    xoooxoxxxxxxo.......
    xxxxxoooooooo.......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_live_in_a_row():
    stonestr = """
    ......o.......o........o.........o..........o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    .......o............o...........o...o........
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_live_in_a_row_with_hane():
    stonestr = """
    ....x.o.x...x.o.x....x.o.x.....x.o.x......x.o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    .....x.o.x........x.o.x.......x.o...o.x......
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_live_in_a_row_with_hane_throwin():
    stonestr = """
    ...wx.o.xw..x.o.xw...x.o.xw....x.o.xw.....x.o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    ....wx.o.xw.......x.o.xw......x.o...o.xw.....
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_live_in_a_row_with_hane_throwin_poke():
    stonestr = """
    ..wwx.o.xww.x.o.xww..x.o.xww...x.o.xww....x.o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    ...wwx.o.xww......x.o.xww.....x.o...o.xww....
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_throwin_false_eye_chains():
    stonestr = """
    .wxx.x.xx.x.x.xx..
    xxoxxoxx.xxxoxxoxx
    ..o..o.xxxx.o..o..
    oooooooooooooooooo
    ooo.oo.o...o..o...
    ...o..o.xxxo..oxxx
    xxxoxxoxx.xoxxox.x
    .wwxx.xx.xxx.xxww.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_various_eyefillings():
    stonestr = """
    .box...x...ox.www.
    bboxx.x.x..oxxxxxx
    ooooxx.x...ooooooo
    ...xo.............
    xxxxo.............
    .w.xo.....oooooooo
    xxxxo.....oxxxxxxx
    ooooo.....ox.wwww.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_various_eyefillings2():
    stonestr = """
    ..xxox.xobbb.oxxw.
    wwwxox.xobboooxw.w
    ww.xox.xooooo.xwwx
    xxxxox.xxo...xx.xx
    ooooooxxxoxxxxxxxo
    xxxxxo..xxoooooooo
    xww.xooooooxxxxxxx
    wwxxx.o.o.ox.wwww.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_various_eyefillings3():
    stonestr = """
    wwxxox.xobbb.oxxw.
    wwwxox.xobbbooxwww
    ww.xox.xooooo.xwwx
    xxxxox.xxo...xx.xx
    ooooooxxxoxxxxxxxo
    xxxxxo..xxoooooooo
    xww.xooooooxxxxxxx
    .wxxx.o.o.ox.w.ww.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_various_eyefillings4():
    stonestr = """
    bbbboooo.x.oooobbbb
    bbbox...x.x...xobbb
    ..oo.xxxx..xxx.oob.
    ooo.xx.......xx.ooo
    ....x.........x....
    xxxxx.........xxxxx
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_various_eyefillings5():
    stonestr = """
    .b.oxxo.bbb.oxxo.bb
    boooxxoooboooxxooob
    .o.xxxx.o.o.xxxx.o.
    oox....xooox....xoo
    xxx....xxxxx....xxx
    oox....xxxxx....xxx
    .o.x...xooox....xoo
    bo..xxx.o.o.xxxx.o.
    booooxoooboooxxooob
    bbb.oxo.b.b.oxxoob.
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)

def test_various_corner_eyes():
    stonestr = """
    ...xo.......xox..x
    ...xo.......xox...
    ...xo.......xox...
    xxxxo.......xoxxxx
    oooox.......xooooo
    ..oox.......xo....
    ...ox.......xo....
    ...ox.......xo....
    """
    run_snapshot_test(inspect.currentframe().f_code.co_name, stonestr)


