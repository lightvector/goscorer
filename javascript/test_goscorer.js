
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

function getOutput(stonestr) {
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
    return output;
}

function printTest(stonestr) {
    console.log(getOutput(stonestr));
}

function runTest(stonestr, expectedPath) {
    fetch(expectedPath)
        .then((res) => res.text())
        .then((text) => {console.assert(text === getOutput(stonestr), getOutput(stonestr), expectedPath);})
        .catch((e) => console.error(e));
}

function runAllTests() {
    let stonestr;

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
    runTest(stonestr,"/python/expected_test_output/test_empty.txt");

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
    runTest(stonestr,"/python/expected_test_output/test_basic.txt");

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
    runTest(stonestr,"/python/expected_test_output/test_dead_stone_marking.txt");


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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes.txt");


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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_2.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_chain.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_chain_bamboo.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_chain_no_bamboo.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_chain_loose_eye.txt");




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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_chain_loose_eye_2.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_chain_loose_eye_3.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_chain_loose_eye_4.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_chain_big_false_eye.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_chain_big_false_eye_aliveend.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_false_eyes_chain_big_false_eye_aliveends.txt");



    stonestr = `
    .x.o.........x.x.
    ox.o..xwx..xx..oo
    ox.o.o.xx.x..ooo.
    ox.o..ooo..xxo.ox
    .x.o.b.......oxx.
    `;
    runTest(stonestr,"/python/expected_test_output/test_basic_sekis.txt");



    stonestr = `
    .x.o.........x.x.
    wx.o..xox..xx..oo
    wx.o.o.xx.x..ooo.
    wx.o..ooo..xxo.ob
    .x.o.x.......obb.
    `;
    runTest(stonestr,"/python/expected_test_output/test_basic_sekis_marked_dead.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_more_fancy_sekis.txt");



    stonestr = `
    .o.o.........o.o.
    xx.o.........o.xx
    .xxo.o.....o.oxx.
    xoxxo.......oxxwx
    o.oxo.......oxw.w
    `;
    runTest(stonestr,"/python/expected_test_output/test_double_ko_death.txt");



    stonestr = `
    .o.o.........o.o.
    xx.o.........o.xx
    .xxo.o.....o.oxx.
    boxxo.......oxxwb
    o.oxo.......oxw.w
    `;
    runTest(stonestr,"/python/expected_test_output/test_double_ko_death2.txt");


    stonestr = `
    .xooox.....xooox.
    xxxxoxx...xxoxxxx
    .xoxoox...xoox.x.
    xo.o.ox...xo.oxox
    oooooox...xo.oooo
    `;
    runTest(stonestr,"/python/expected_test_output/test_double_ko.txt");


    stonestr = `
    .xooox.....xooox.
    xxxxoxx...xxoxxxx
    .xoxoox...xoox.x.
    bo.o.ox...xo.obob
    oooooox...xo.oooo
    `;
    runTest(stonestr,"/python/expected_test_output/test_double_ko2.txt");



    stonestr = `
    .x.........x.........x.........x
    .x.o..x....x.o..x....x.o.xx....x
    .x.o.o.xx..x.o.o.xx..x.ooo.xx..x
    .x.o..ooo..x.o..ooo..x.o..ooo..x
    .x.o.b.....x.o.......x.o.b..o..x
    `;
    runTest(stonestr,"/python/expected_test_output/test_loose_nakade.txt");



    stonestr = `
    ...ooooo.x..
    xxoxxxxo.x..
    .xox.xxo.x..
    .xoxx.xo.x..
    .xo.xxooox..
    xxo.ooooox..
    `;
    runTest(stonestr,"/python/expected_test_output/test_cycle.txt");


    stonestr = `
    .o.ooooo.x..
    xxoxxxxo.x..
    .xox.xxo.x..
    .xoxx.xo.x..
    .xo.xxooox..
    xxo.ooooox..
    `;
    runTest(stonestr,"/python/expected_test_output/test_cycle_false_eye.txt");


    stonestr = `
    .o.oooo.ox..
    xxoxxxxoox..
    .xox.xxo.x..
    .xoxx.xo.x..
    .xo.xxooox..
    xxo.ooooox..
    `;
    runTest(stonestr,"/python/expected_test_output/test_cycle_real_eye.txt");


    stonestr = `
    .o.oooo.ox..
    xxoxxxxoox..
    .xox.xxo.x..
    .xoxx.xoxx..
    .xo.xxo.ox..
    xxo.ooooox..
    `;
    runTest(stonestr,"/python/expected_test_output/test_cycle_real_2eye.txt");



    stonestr = `
    .o.oooo.x...
    xxoxxxxoox..
    .xox.xxoox..
    .xoxx.xxox..
    .xoxoooxox..
    xxoo...oox..
    `;
    runTest(stonestr,"/python/expected_test_output/test_cycle_real_3spaceeye.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_bamboo_interleave_seki.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_no_bamboo_interleave_seki_broken.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_double_throwin_seki4.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_double_throwin_seki3.txt");


    stonestr = `
    ..o.o..o.o....
    .xo.oxxo.o.x..
    .xooo..ooox...
    .x...xx...x...
    ..x.x..x.x....
    `;
    runTest(stonestr,"/python/expected_test_output/test_side_bamboo_cut.txt");


    stonestr = `
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox......o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_cross_noseal.txt");


    stonestr = `
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox...xx.o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_cross_nothrowin.txt");


    stonestr = `
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox..wxx.o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_cross_nopoke.txt");


    stonestr = `
    .o.x.x..o.....
    .o.xxx.o.o....
    .oxx.xo.o.....
    .ox.wwxx.o....
    .oxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_cross_poke.txt");


    stonestr = `
    .o.x.x..o.....
    .o.xxx.o.o....
    oxxx.xo.o.....
    ox..wwxx.o....
    oxxx.xo.o.....
    .o.xxx.o.o....
    .o...oo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_cross_poke_deeper.txt");


    stonestr = `
    ........o....
    xoooox..o....
    xo.oox..o....
    xoo.oxoo.....
    .xoox.x.o....
    ..xx..x.o....
    `;
    runTest(stonestr,"/python/expected_test_output/test_three_point_false_eye.txt");


    stonestr = `
    ........o....
    x....x..o....
    xo.oox..o....
    xoo.oxoo.....
    .xoox.x.o....
    ..xx..x.o....
    `;
    runTest(stonestr,"/python/expected_test_output/test_three_point_false_eye_cycle.txt");



    stonestr = `
    .xxwwwxx.o...xxwwwxx.o........
    ..ox.xo.o.....oxwxo.o..ooo....
    .o.xxx.o.....o.x.x.o..o...o...
    .o.x.x.o.....o.xxx.o..oxxxo...
    .o.xxx.o.....o.x.x.o..ox.xo...
    ..ooooo.......oxxxo..xxw.wxx..
    `;
    runTest(stonestr,"/python/expected_test_output/test_three_way_pokes.txt");


    stonestr = `
    .b.o.x..
    b..o.x..
    .b.o.x..
    oooo.x..
    xxxxxx..
    ........
    `;
    runTest(stonestr,"/python/expected_test_output/test_belly_eye.txt");



    stonestr = `
    .b.o.x..
    bb.o.x..
    .b.o.x..
    oooo.x..
    xxxxxx..
    ........
    `;
    runTest(stonestr,"/python/expected_test_output/test_belly_eye2.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_solid_eyeshapes.txt");


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
    runTest(stonestr,"/python/expected_test_output/test_solid_eyeshapes_nakade.txt");



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
    runTest(stonestr,"/python/expected_test_output/test_solid_eyeshapes_nakade2.txt");


    stonestr = `
    ...xxxxxoooooo...
    xxx..x.xo..o..ooo
    oooxxoooxxxxooxxx
    o.o..o.o.x.x..x.x
    .ooxxoooxxxxooxx.
    `;
    runTest(stonestr,"/python/expected_test_output/test_bamboo_reachable_seki.txt");


    stonestr = `
    ..xx.o.............o.xx..
    ...x.o.............o.x.w.
    x..x.o.............o.x..x
    xxxx.o.............o.xxxx
    oooooo.............oooooo
    xxxx.o.............o.xxxx
    x.wx.o.............o.x..x
    .w.x.o.............o.x.ww
    ..xx.o.............o.xx..
    `;
    runTest(stonestr,"/python/expected_test_output/test_7pteyes.txt");

    stonestr = `
    ...x.o.............o.x...
    ...x.o.............o.x.w.
    x.xx.o.............o.xx.x
    xxxx.o.............o.xxxx
    oooooo.............oooooo
    xxxx.o.............o.xxxx
    x.xx.o.............o.xx.x
    ...x.o.............o.x.w.
    .wwx.o.............o.x.w.
    `;
    runTest(stonestr,"/python/expected_test_output/test_7pteyes_2.txt");

    stonestr = `
    ...x.o.............o.x.w.
    ww.x.o.............o.x.ww
    ..xx.o.............o.xx..
    xxxx.o.............o.xxxx
    oooooo.............oooooo
    xxxx.o.............o.xxxx
    ..xx.o.............o.xx..
    .w.x.o.............o.x.w.
    ww.x.o.............o.x..w
    `;
    runTest(stonestr,"/python/expected_test_output/test_8pteyes.txt");

    stonestr = `
    oxox.oxw.boxo
    oxoxoxxxoboxo
    oxoxox.xoboxo
    .xooox.xooox.
    xxoxxx.xxxoxx
    ooox.....xooo
    xxxx.....xxxx
    `;
    runTest(stonestr,"/python/expected_test_output/test_hanezeki.txt");


    stonestr = `
    wxox.oxw.boxw
    wxoxoxxxoboxw
    wxoxox.xoboxw
    .xooox.xooox.
    xxoxxx.xxxoxx
    ooox.....xooo
    xxxx.....xxxx
    `;
    runTest(stonestr,"/python/expected_test_output/test_hanezeki2.txt");


    stonestr = `
    .xoxxx
    xxoox.
    .xxooo
    ooxxx.
    .oooxx
    xxxo.x
    `;
    runTest(stonestr,"/python/expected_test_output/test_big_eye_seki.txt");


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
    runTest(stonestr,"/python/expected_test_output/test_lgroups_and_rectanglelikes.txt");


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
    runTest(stonestr,"/python/expected_test_output/test_lgroups_and_rectanglelikes2.txt");


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
    runTest(stonestr,"/python/expected_test_output/test_lgroups_and_rectanglelikes3.txt");


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
    runTest(stonestr,"/python/expected_test_output/test_lgroups_and_rectanglelikes4.txt");


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
    runTest(stonestr,"/python/expected_test_output/test_lgroups_and_rectanglelikes5.txt");


    stonestr = `
    xoooo...ooxxxxoo.....ooooo
    xxxxoo.oox.w.xxo....ooxxxx
    .w.xxo.oxx..w.xxoo..oxx.w.
    ..w.xo.oxxxxxxx..o..oxx...
    `;
    runTest(stonestr,"/python/expected_test_output/test_lgroups_and_rectanglelikes6.txt");



    stonestr = `
    .xx..x.oooooooo.ooooooo.
    xxoxxoooxxxoxxoooxxxoxxx
    oooooo.ox.xx..x.ox.xx..x
    xxoxxxooxxxoxxoooxxxoxxx
    .xx..xooooooooo.ooooooo.
    `;
    runTest(stonestr,"/python/expected_test_output/test_two_point_eye_falsity.txt");


    stonestr = `
    xxxxx.xo............
    xooooxoo............
    .xo.ox.o............
    xo.ooxooooooo.......
    xooooxoxxxxxo.......
    xxxxx.xx.w.xo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_false_eye_multicycles1.txt");


    stonestr = `
    xxxxx.xo............
    xooooxoo............
    .xo.ox.o............
    xo.ooxooooooo.......
    xoooxxoxxxxxo.......
    xxxxx.xx.w.xo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_false_eye_multicycles2.txt");


    stonestr = `
    xxxxx.xo............
    xooooxoo............
    .xo.ox.o............
    xo.ooxooooooo.......
    xooooxxxxxxxo.......
    xxxxx.xx.w.xo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_false_eye_multicycles3.txt");


    stonestr = `
    xxxxx.xo............
    xooooxoooooo........
    .xo.oxxoxxx.o.......
    xo.oox.xx.x.o.......
    xoooxxxoxxxxo.......
    xxxxxoooooooo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_false_eye_multicycles4.txt");


    stonestr = `
    xxxxx.xo............
    xooooxoooooo........
    .xo.oxxoxxx.o.......
    xo.oxx.xx.x.o.......
    xoooxoxxxxxxo.......
    xxxxxoooooooo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_false_eye_multicycles5.txt");


    stonestr = `
    .xxxx.xo............
    xooooxoooooo........
    .xo.oxxoxxx.o.......
    xo.oxx.xx.x.o.......
    xoooxoxxxxxxo.......
    xxxxxoooooooo.......
    `;
    runTest(stonestr,"/python/expected_test_output/test_false_eye_multicycles6.txt");


    stonestr = `
    ......o.......o........o.........o..........o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    .......o............o...........o...o........
    `;
    runTest(stonestr,"/python/expected_test_output/test_live_in_a_row.txt");


    stonestr = `
    ....x.o.x...x.o.x....x.o.x.....x.o.x......x.o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    .....x.o.x........x.o.x.......x.o...o.x......
    `;
    runTest(stonestr,"/python/expected_test_output/test_live_in_a_row_with_hane.txt");


    stonestr = `
    ...wx.o.xw..x.o.xw...x.o.xw....x.o.xw.....x.o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    ....wx.o.xw.......x.o.xw......x.o...o.xw.....
    `;
    runTest(stonestr,"/python/expected_test_output/test_live_in_a_row_with_hane_throwin.txt");


    stonestr = `
    ..wwx.o.xww.x.o.xww..x.o.xww...x.o.xww....x.o
    xxxxoooooxxxoooooxxxxoooooxxxxxoooooxxxxxxooo
    ....o...o...o...o....o...o.....o...o......o..
    oooooo..ooooooooooo..oo..ooooooo...oooooooo..
    .....o...o........o...o.......o.......o......
    xxxxxoooooxxxxxxxxoooooxxxxxxxooo...oooxxxxxx
    ...wwx.o.xww......x.o.xww.....x.o...o.xww....
    `;
    runTest(stonestr,"/python/expected_test_output/test_live_in_a_row_with_hane_throwin_poke.txt");

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
    runTest(stonestr,"/python/expected_test_output/test_throwin_false_eye_chains.txt");

    stonestr = `
    .box...x...ox.www.
    bboxx.x.x..oxxxxxx
    ooooxx.x...ooooooo
    ...xo.............
    xxxxo.............
    .w.xo.....oooooooo
    xxxxo.....oxxxxxxx
    ooooo.....ox.wwww.
    `;
    runTest(stonestr,"/python/expected_test_output/test_various_eyefillings.txt");

    stonestr = `
    ..xx.o.xobbb.oxxw.
    wwwxooxxobboooxw.w
    ww.xox.xooooo.xwwx
    xxxxoxx.xo...xx.xx
    ooooooxxxoxxxxxxxo
    xxxxxo..xxoooooooo
    xww.xooooooxxxxxxx
    wwxxx.o.o.ox.wwww.
    `;
    runTest(stonestr,"/python/expected_test_output/test_various_eyefillings2.txt");

    stonestr = `
    .wxx.o.xob.b.oxxw.
    w.wxooxxobboooxw.w
    ww.xox.xooooo.xwwx
    xxxxoxx.xo..xxxxxx
    ooooooxxxoxxxooooo
    xxxxxo..xxooooxxxx
    xwxxxooooooxxxxxww
    w.wxx..o.o.oo.xwww
    .wwxx.........xxw.
    `;
    runTest(stonestr,"/python/expected_test_output/test_various_eyefillings2b.txt");

    stonestr = `
    .wxx.o.xob.b.oxxww
    w.wxooxxo.boooxwww
    ...xox.xooooo.xww.
    xxxxoxx.xo..xxxxxx
    ooooooxxxoxxxooooo
    xxxxxo..xxooooxxxx
    .wxxxooooooxxxx.ww
    w.wxx..o.o.oo.xwww
    .w.xx.........xxw.
    `;
    runTest(stonestr,"/python/expected_test_output/test_various_eyefillings2c.txt");

    stonestr = `
    wwxx.o.xobbb.oxxw.
    wwwxooxxobbbooxwww
    ww.xox.xooooo.xwwx
    xxxxoxx.xo...xx.xx
    ooooooxxxoxxxxxxxo
    xxxxxo..xxoooooooo
    xww.xooooooxxxxxxx
    .wxxx.o.o.ox.w.ww.
    `;
    runTest(stonestr,"/python/expected_test_output/test_various_eyefillings3.txt");

    stonestr = `
    bbbboooo.x.oooobbbb
    bbbox...x.x...xobbb
    ..oo.xxxx..xxx.oob.
    ooo.xx.......xx.ooo
    ....x.........x....
    xxxxx.........xxxxx
    `;
    runTest(stonestr,"/python/expected_test_output/test_various_eyefillings4.txt");

    stonestr = `
    .b.oxxo.bbb.oxxo.bb
    boooxxoooboooxxooob
    .o.xxxx.o.o.xxxx.o.
    oox....xooox....xoo
    xxx....xxxxx....xxx
    oox....xxxxx....xxx
    .o.x...xooox....xoo
    bo..xxx.o.o.xxxx.o.
    booooxoooboooxxooob
    .bb.oxo.b.b.oxxoob.
    `;
    runTest(stonestr,"/python/expected_test_output/test_various_eyefillings5.txt");

    stonestr = `
    ...xo.......xox..x
    ...xo.......xox...
    ...xo.......xox...
    xxxxo.......xoxxxx
    oooox.......xooooo
    ..oox.......xo....
    ...ox.......xo....
    ...ox.......xo....
    `;
    runTest(stonestr,"/python/expected_test_output/test_various_corner_eyes.txt");

    stonestr = `
    .x.x.o.
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board1.txt");

    stonestr = `
    .x.o.b
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board2.txt");

    stonestr = `
    .x.
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board3.txt");

    stonestr = `
    .x.x.xx.x.o.o.
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board4.txt");

    stonestr = `
    .x.o
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board5.txt");

    stonestr = `
    .x.w
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board6.txt");

    stonestr = `
    x.w.
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board7.txt");

    stonestr = `
    .
    o
    .
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board8.txt");

    stonestr = `
    x
    .
    o
    .
    b
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board9.txt");

    stonestr = `
    b
    .
    o
    .
    b
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board10.txt");

    stonestr = `
    .o
    o.
    xo
    x.
    .x
    ox
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board11.txt");

    stonestr = `
    .o
    o.
    xo
    x.
    .x
    wx
    `;
    runTest(stonestr,"/python/expected_test_output/test_narrow_board12.txt");

}

export {
    stonesAndMarkedDeadOfStr,
    testFinalScoring,
    getOutput,
    printTest,
    runTest,
    runAllTests,
};

