
import { EMPTY, BLACK, WHITE, string2d2, finalTerritoryScore, finalAreaScore, territoryScoring } from "./goscorer.js";

function stonesAndMarkedDeadOfStr(stonestr) {
    const rows = stonestr.split("\n").map(row => row.trim()).filter(row => row !== "");

    const ysize = rows.length;
    const xsize = rows[0].length;

    const stones = Array.from({length: ysize}, () => Array.from({length: xsize}, () => EMPTY));
    const markedDead = Array.from({length: ysize}, () => Array.from({length: xsize}, () => false));

    for(let y = 0; y < ysize; y++) {
        for(let x = 0; x < xsize; x++) {
            let c = rows[y][x];
            if(c === "x")
                stones[y][x] = BLACK;
            else if(c === "o")
                stones[y][x] = WHITE;
            else if(c === "b") {
                stones[y][x] = BLACK;
                markedDead[y][x] = true;
            }
            else if(c === "w") {
                stones[y][x] = WHITE;
                markedDead[y][x] = true;
            }
        }
    }
    return { stones, markedDead };

}

function testFinalScoring() {
    {
        let stonestr = `
    .xo.oxxo.
    x.o.oxo.o
    ooooxxo..
    xxxxxxooo
    ....x.x.o
    `;
        let { stones,markedDead } = stonesAndMarkedDeadOfStr(stonestr);
        console.assert(finalTerritoryScore(stones,markedDead,0,0,0).toString() == { black: 4, white: 4 }.toString());
        console.assert(finalTerritoryScore(stones,markedDead,0,0,0).toString() == { black: 4, white: 4 }.toString());
        console.assert(finalTerritoryScore(stones,markedDead,0,0,0,true).toString() == { black: 5, white: 4 }.toString());
        console.assert(finalTerritoryScore(stones,markedDead,0,0,3.5,true).toString() == { black: 5, white: 7.5 }.toString());
        console.assert(finalTerritoryScore(stones,markedDead,8,6,3.5,true).toString() == { black: 13, white: 13.5 }.toString());
        console.assert(finalAreaScore(stones,markedDead,3.5).toString() == { black: 21, white: 25.5 }.toString());
    }
    {
        let stonestr = `
    .xo.oxxo.
    x.o.oxo.o
    ooooxxob.
    xxxxxxooo
    w..wx.x.o
    `;
        let { stones,markedDead } = stonesAndMarkedDeadOfStr(stonestr);
        console.assert(finalTerritoryScore(stones,markedDead,0,0,0).toString() == { black: 6, white: 5 }.toString());
        console.assert(finalTerritoryScore(stones,markedDead,0,0,0,true).toString() == { black: 7, white: 5 }.toString());
        console.assert(finalTerritoryScore(stones,markedDead,0,0,3.5,true).toString() == { black: 7, white: 8.5 }.toString());
        console.assert(finalTerritoryScore(stones,markedDead,8,6,3.5,true).toString() == { black: 15, white: 14.5 }.toString());
        console.assert(finalAreaScore(stones,markedDead,0).toString() == { black: 21, white: 22.5 }.toString());
    }
    {
        let stonestr = `
    .xo.oxxo.
    x.o.oxo.o
    ooooxxo..
    xxxxxxo.w
    ....x.o..
    `;
        let { stones,markedDead } = stonesAndMarkedDeadOfStr(stonestr);
        console.assert(finalTerritoryScore(stones,markedDead,0,0,0).toString() == { black: 5, white: 8 }.toString());
        console.assert(finalAreaScore(stones,markedDead,0).toString() == { black: 19, white: 24 }.toString());
    }
}

function printTest(stonestr) {
    const { stones, markedDead } = stonesAndMarkedDeadOfStr(stonestr);
    const rows = stonestr.split("\n").map(row => row.trim()).filter(row => row !== "");
    const scoring = territoryScoring(stones, markedDead);

    let output = "";

    output += "BOARD:\n";
    output += rows.join("\n") + "\n";

    output += "TERRITORY:\n";
    output += string2d2(scoring, rows, (s, c) =>
                        s.isTerritoryFor === BLACK ? "z" :
                        s.isTerritoryFor === WHITE ? "a" :
                        c
                       ) + "\n";

    output += "SEKI:\n";
    output += string2d2(scoring, stones, (s, c) =>
                        s.belongsToSekiGroup === BLACK && c !== EMPTY ? "x" :
                        s.belongsToSekiGroup === WHITE && c !== EMPTY ? "o" :
                        s.belongsToSekiGroup === BLACK ? "z" :
                        s.belongsToSekiGroup === WHITE ? "a" :
                        "."
                       ) + "\n";

    output += "FALSE EYES:\n";
    output += string2d2(scoring, rows, (s, c) =>
                        s.isFalseEye ? "F" : c
                       ) + "\n";

    output += "UNSCORABLE FALSE EYES:\n";
    output += string2d2(scoring, rows, (s, c) =>
                        s.isUnscorableFalseEye ? "F" : c
                       ) + "\n";

    output += "DAME:\n";
    output += string2d2(scoring, rows, (s, c) =>
                        s.isDame ? "1" : c
                       ) + "\n";

    output += "EYEVALUE:\n";
    output += string2d2(scoring, rows, (s, c) =>
                        s.eyeValue === 0 ? c : "0123456789"[s.eyeValue]
                       ) + "\n";

    console.log(output);
}

function printAllTests(stonestr) {

    stonestr = `
    .........
    .........
    .........
    .........
    .........
    .........
    .........
    .........
    .........
    `;
    printTest(stonestr);


    stonestr = `
    ......x..
    .xx.x.x..
    ......x..
    ......x..
    oooooox..
    .....oxxx
    .....o.o.
    ...o.o..o
    .....o...
    `;
    printTest(stonestr);


    stonestr = `
    ..w...xw.
    .xx.x.x.w
    ......xxx
    ......x.o
    oooooox..
    o.o.xoxxx
    oboxxo.o.
    ob.o.o..o
    .ooooo.b.
    `;
    printTest(stonestr);


    stonestr = `
    .........
    xxxx.xx..
    .oxoxox..
    o.oo.ox..
    ..oooox.x
    ...o.x.x.
    ....ooxox
    ...o.o.ox
    .....ooo.
    `;
    printTest(stonestr);



    stonestr = `
    ...xx.x..
    wxxx.x...
    xoxxoxx..
    x.ooxox..
    x.o.xox.x
    oo.o.o.x.
    ....oooxo
    bbbbb..o.
    ....b...b
    `;
    printTest(stonestr);



    stonestr = `
    ......xx.
    ......oox
    ....oo.xx
    ooooo.ox.
    ..o.oooox
    ooo...ox.
    ......oxx
    .......x.
    `;
    printTest(stonestr);



    stonestr = `
    ......xx.
    ......oox
    ....oo.xx
    ooo.o.ox.
    ..o.oooox
    ooo...ox.
    ......oxx
    .......x.
    `;
    printTest(stonestr);



    stonestr = `
    ......xx.
    ......oox
    ....oo.xx
    oo..o.ox.
    .o..oooox
    oo....ox.
    ......oxx
    .......x.
    `;
    printTest(stonestr);



    stonestr = `
    .......x.
    .........
    ..o.oo.xx
    oo.oo.ox.
    .oo.oooox
    oo....ox.
    ......oxx
    .......x.
    `;
    printTest(stonestr);



    stonestr = `
    .........
    ......oo.
    ..o.oo.x.
    oo.oo.ox.
    .oo.oooox
    oo....ox.
    ......oxx
    .......x.
    `;
    printTest(stonestr);



    stonestr = `
    .........
    .....xxx.
    ..o.oo.x.
    oo.oo.ox.
    .oo.oooox
    oo....ox.
    ......oxx
    .......x.
    `;
    printTest(stonestr);



    stonestr = `
    .......x.
    .......x.
    ..o.oo.x.
    oo.oo.ox.
    .oo.oooox
    oo....ox.
    ......oxx
    .......x.
    `;
    printTest(stonestr);



    stonestr = `
    xxx..xxx.
    xooxxooox
    .xo....x.
    .xooooox.
    .xo...ox.
    xoo...oox
    x.o...oxx
    ..o...ox.
    `;
    printTest(stonestr);



    stonestr = `
    xxx..xxx.
    xooxxooox
    .xo....x.
    .xooooox.
    .xo...ox.
    xoo..ooox
    x.o.oxxxx
    ..o.ox.x.
    `;
    printTest(stonestr);



    stonestr = `
    xxx..xxx.
    xooxxooox
    .xo....x.
    .xooooox.
    .xo...ox.
    xoo..ooox
    x.o.oxxxx
    .xo.ox.w.
    `;
    printTest(stonestr);



    stonestr = `
    .x.o.........x.x.
    ox.o..xwx..xx..oo
    ox.o.o.xx.x..ooo.
    ox.o..ooo..xxo.ox
    .x.o.b.......oxx.
    `;
    printTest(stonestr);



    stonestr = `
    .x.o.........x.x.
    wx.o..xox..xx..oo
    wx.o.o.xx.x..ooo.
    wx.o..ooo..xxo.ob
    .x.o.x.......obb.
    `;
    printTest(stonestr);



    stonestr = `
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
    `;
    printTest(stonestr);



    stonestr = `
    .o.o.........o.o.
    xx.o.........o.xx
    .xxo.o.....o.oxx.
    xoxxo.......oxxwx
    o.oxo.......oxw.w
    `;
    printTest(stonestr);



    stonestr = `
    .o.o.........o.o.
    xx.o.........o.xx
    .xxo.o.....o.oxx.
    boxxo.......oxxwb
    o.oxo.......oxw.w
    `;
    printTest(stonestr);


    stonestr = `
    .xooox.....xooox.
    xxxxoxx...xxoxxxx
    .xoxoox...xoox.x.
    xo.o.ox...xo.oxox
    oooooox...xo.oooo
    `;
    printTest(stonestr);


    stonestr = `
    .xooox.....xooox.
    xxxxoxx...xxoxxxx
    .xoxoox...xoox.x.
    bo.o.ox...xo.obob
    oooooox...xo.oooo
    `;
    printTest(stonestr);



    stonestr = `
    .x.........x.........x.........x
    .x.o..x....x.o..x....x.o.xx....x
    .x.o.o.xx..x.o.o.xx..x.ooo.xx..x
    .x.o..ooo..x.o..ooo..x.o..ooo..x
    .x.o.b.....x.o.......x.o.b..o..x
    `;
    printTest(stonestr);



    stonestr = `
    ...ooooo.x..
    xxoxxxxo.x..
    .xox.xxo.x..
    .xoxx.xo.x..
    .xo.xxooox..
    xxo.ooooox..
    `;
    printTest(stonestr);


    stonestr = `
    .o.ooooo.x..
    xxoxxxxo.x..
    .xox.xxo.x..
    .xoxx.xo.x..
    .xo.xxooox..
    xxo.ooooox..
    `;
    printTest(stonestr);


    stonestr = `
    .o.oooo.ox..
    xxoxxxxoox..
    .xox.xxo.x..
    .xoxx.xo.x..
    .xo.xxooox..
    xxo.ooooox..
    `;
    printTest(stonestr);


    stonestr = `
    .o.oooo.ox..
    xxoxxxxoox..
    .xox.xxo.x..
    .xoxx.xoxx..
    .xo.xxo.ox..
    xxo.ooooox..
    `;
    printTest(stonestr);



    stonestr = `
    .o.oooo.x...
    xxoxxxxoox..
    .xox.xxoox..
    .xoxx.xxox..
    .xoxoooxox..
    xxoo...oox..
    `;
    printTest(stonestr);



    stonestr = `
    .xxxxxx.ox..
    xo..x.x.ox..
    xooooxooox..
    xx..xx.o.x..
    x.oo..oo.x..
    xxooxxoo.x..
    x.o.oo.o.x..
    ooooxxoo.x..
    xxxxxxxxx...
    `;
    printTest(stonestr);



    stonestr = `
    .xxxxxx.ox..
    xo..xxx.ox..
    xooo...oox..
    xx.....o.x..
    x.ooxx.o.x..
    xxooxxoo.x..
    x.o.oo.o.x..
    ooooxxoo.x..
    xxxxxxxxx...
    `;
    printTest(stonestr);



    stonestr = `
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
    `;
    printTest(stonestr);



    stonestr = `
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
    `;
    printTest(stonestr);


    stonestr = `
    ..o.o..o.o....
    .xo.oxxo.o.x..
    .xooo..ooox...
    .x...xx...x...
    ..x.x..x.x....
    `;
    printTest(stonestr);


    stonestr = `
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox......o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    `;
    printTest(stonestr);


    stonestr = `
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox...xx.o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    `;
    printTest(stonestr);


    stonestr = `
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox..wxx.o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    `;
    printTest(stonestr);


    stonestr = `
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox.wwxx.o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    `;
    printTest(stonestr);


    stonestr = `
    .o.x.x..o.....
    .o.xxx.o.o....
    oxxx.xo.o.....
    ox..wwxx.o....
    oxxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    `;
    printTest(stonestr);


    stonestr = `
    ........o....
    xoooox..o....
    xo.oox..o....
    xoo.oxoo.....
    .xoox.x.o....
    ..xx..x.o....
    `;
    printTest(stonestr);


    stonestr = `
    ........o....
    x....x..o....
    xo.oox..o....
    xoo.oxoo.....
    .xoox.x.o....
    ..xx..x.o....
    `;
    printTest(stonestr);



    stonestr = `
    .xxwwwxx.o...xxwwwxx.o........
    ..ox.xo.o.....oxwxo.o..ooo....
    .o.xxx.o.....o.x.x.o..o...o...
    .o.x.x.o.....o.xxx.o..oxxxo...
    .o.xxx.o.....o.x.x.o..ox.xo...
    ..ooooo.......oxxxo..xxw.wxx..
    `;
    printTest(stonestr);


    stonestr = `
    .b.o.x..
    b..o.x..
    .b.o.x..
    oooo.x..
    xxxxxx..
    ........
    `;
    printTest(stonestr);



    stonestr = `
    .b.o.x..
    bb.o.x..
    .b.o.x..
    oooo.x..
    xxxxxx..
    ........
    `;
    printTest(stonestr);



    stonestr = `
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    x.xx..xx.xxx..xxxxx..xxxx..xxxxx
    xxxxxxxx..xx..xxxxxx..xx....xxxx
    x...xxxxx.xxxxxxxxxx.xxxxxxxx...
    xxxxx..xxxxx..xxx.xxxx.xxxxxxx..
    x..xx.xxxxxx..xx...xx...xxxxxxx.
    xx.xx.xx.xxx.xxxx.xxx..xxx...xxx
    xxxxxxx...xxxxxxxxxxxxxxxx...xxx
    x....xxxxxxxxxxxxxxxxxxxxxxxxxxx
    `;
    printTest(stonestr);


    stonestr = `
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    x.xx..xx.xxx..xxxxx..xxxx..xxxxx
    xxxxxxxxw.xxw.xxxxxxw.xx.w..xxxx
    x.w.xxxxx.xxxxxxxxxx.xxxxxxxx.w.
    xxxxxw.xxxxx..xxx.xxxx.xxxxxxx..
    x.wxx.xxxxxxw.xx.w.xx.w.xxxxxxx.
    xx.xx.xx.xxx.xxxx.xxx..xxx.w.xxx
    xxxxxxx.w.xxxxxxxxxxxxxxxx...xxx
    x..w.xxxxxxxxxxxxxxxxxxxxxxxxxxx
    `;
    printTest(stonestr);



    stonestr = `
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    x.xx.wxxwxxx.wxxxxx.wxxxx..xxxxx
    xxxxxxxxw.xxwwxxxxxxw.xx.ww.xxxx
    x.wwxxxxx.xxxxxxxxxx.xxxxxxxx.w.
    xxxxxw.xxxxx.wxxx.xxxxwxxxxxxx.w
    x.wxxwxxxxxxwwxx.w.xxww.xxxxxxx.
    xxwxx.xx.xxx.xxxx.xxxwwxxx.w.xxx
    xxxxxxxww.xxx...xxxxxxxxxx.w.xxx
    x.ww.xxxxxxxx.wwxxxxxxxxxxxxxxxx
    `;
    printTest(stonestr);


    stonestr = `
    ...xxxxxoooooo...
    xxx..x.xo..o..ooo
    oooxxoooxxxxooxxx
    o.o..o.o.x.x..x.x
    .ooxxoooxxxxooxx.
    `;
    printTest(stonestr);



    stonestr = `
    oxox.oxw.boxo
    oxoxoxxxoboxo
    oxoxox.xoboxo
    .xooox.xooox.
    xxoxxx.xxxoxx
    ooox.....xooo
    xxxx.....xxxx
    `;
    printTest(stonestr);


    stonestr = `
    wxox.oxw.boxw
    wxoxoxxxoboxw
    wxoxox.xoboxw
    .xooox.xooox.
    xxoxxx.xxxoxx
    ooox.....xooo
    xxxx.....xxxx
    `;
    printTest(stonestr);


    stonestr = `
    .xoxxx
    xxoox.
    .xxooo
    ooxxx.
    .oooxx
    xxxo.x
    `;
    printTest(stonestr);


    stonestr = `
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
    `;
    printTest(stonestr);


    stonestr = `
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
    `;
    printTest(stonestr);


    stonestr = `
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
    `;
    printTest(stonestr);


    stonestr = `
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
    `;
    printTest(stonestr);


    stonestr = `
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
    `;
    printTest(stonestr);


    stonestr = `
    xoooo...ooxxxxoo.....ooooo
    xxxxoo.oox.w.xxo....ooxxxx
    .w.xxo.oxx..w.xxoo..oxx.w.
    ..w.xo.oxxxxxxx..o..oxx...
    `;
    printTest(stonestr);



    stonestr = `
    .xx..x.oooooooo.ooooooo.
    xxoxxoooxxxoxxoooxxxoxxx
    oooooo.ox.xx..x.ox.xx..x
    xxoxxxooxxxoxxoooxxxoxxx
    .xx..xooooooooo.ooooooo.
    `;
    printTest(stonestr);



    stonestr = `
    xxxxx.xo............
    xooooxoo............
    .xo.ox.o............
    xo.ooxooooooo.......
    xooooxoxxxxxo.......
    xxxxx.xx.w.xo.......
    `;
    printTest(stonestr);


    stonestr = `
    xxxxx.xo............
    xooooxoo............
    .xo.ox.o............
    xo.ooxooooooo.......
    xoooxxoxxxxxo.......
    xxxxx.xx.w.xo.......
    `;
    printTest(stonestr);


    stonestr = `
    xxxxx.xo............
    xooooxoo............
    .xo.ox.o............
    xo.ooxooooooo.......
    xooooxxxxxxxo.......
    xxxxx.xx.w.xo.......
    `;
    printTest(stonestr);


    stonestr = `
    xxxxx.xo............
    xooooxoooooo........
    .xo.oxxoxxx.o.......
    xo.oox.xx.x.o.......
    xoooxxxoxxxxo.......
    xxxxxoooooooo.......
    `;
    printTest(stonestr);


    stonestr = `
    xxxxx.xo............
    xooooxoooooo........
    .xo.oxxoxxx.o.......
    xo.oxx.xx.x.o.......
    xoooxoxxxxxxo.......
    xxxxxoooooooo.......
    `;
    printTest(stonestr);


    stonestr = `
    .xxxx.xo............
    xooooxoooooo........
    .xo.oxxoxxx.o.......
    xo.oxx.xx.x.o.......
    xoooxoxxxxxxo.......
    xxxxxoooooooo.......
    `;
    printTest(stonestr);


    stonestr = `
    ......o.......o........o.........o..........o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    .......o............o...........o...o........
    `;
    printTest(stonestr);


    stonestr = `
    ....x.o.x...x.o.x....x.o.x.....x.o.x......x.o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    .....x.o.x........x.o.x.......x.o...o.x......
    `;
    printTest(stonestr);


    stonestr = `
    ...wx.o.xw..x.o.xw...x.o.xw....x.o.xw.....x.o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    ....wx.o.xw.......x.o.xw......x.o...o.xw.....
    `;
    printTest(stonestr);


    stonestr = `
    ..wwx.o.xww.x.o.xww..x.o.xww...x.o.xww....x.o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    ...wwx.o.xww......x.o.xww.....x.o...o.xww....
    `;
    printTest(stonestr);

    stonestr = `
    .wxx.x.xx.x.x.xx..
    xxoxxoxx.xxxoxxoxx
    ..o..o.xxxx.o..o..
    oooooooooooooooooo
    ooo.oo.o...o..o...
    ...o..o.xxxo..oxxx
    xxxoxxoxx.xoxxox.x
    .wwxx.xx.xxx.xxww.
    `;
    printTest(stonestr);
}

export {
    stonesAndMarkedDeadOfStr,
    testFinalScoring,
    printTest,
    printAllTests,
};

