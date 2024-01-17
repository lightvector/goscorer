from goscorer import territory_scoring, string2d, string2d2, EMPTY, BLACK, WHITE

def process(stonestr):
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
    scoring = territory_scoring(stones,marked_dead)

if __name__ == "__main__":
    for i in range(100):
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
        process(stonestr)
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
        process(stonestr)
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
        process(stonestr)
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
        process(stonestr)
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
        process(stonestr)
        stonestr = """
        .x.o.........x.x.
        ox.o..xwx..xx..oo
        ox.o.o.xx.x..ooo.
        ox.o..ooo..xxo.ox
        .x.o.b.......oxx.
        """
        process(stonestr)
        stonestr = """
        .x.........x.........x.........x
        .x.o..x....x.o..x....x.o.xx....x
        .x.o.o.xx..x.o.o.xx..x.ooo.xx..x
        .x.o..ooo..x.o..ooo..x.o..ooo..x
        .x.o.b.....x.o.......x.o.b..o..x
        """
        process(stonestr)
        stonestr = """
        .o.o.........o.o.
        xx.o.........o.xx
        .xxo.o.....o.oxx.
        xoxxo.......oxxwx
        o.oxo.......oxw.w
        """
        process(stonestr)
