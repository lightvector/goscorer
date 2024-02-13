"""
An attempt at territory scoring in Go with seki detection.
See https://github.com/lightvector/goscorer
Original Author: lightvector
Released under MIT license (https://github.com/lightvector/goscorer/blob/main/LICENSE.txt)
"""

from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from collections import defaultdict

Color = int
EMPTY = 0
BLACK = 1
WHITE = 2

@dataclass
class LocScore:
    """Indicates how a given location on the board should be scored for territory, along with other metadata.
    The main field, "is_territory_for", indicates the territory on the board, including territory underneath dead stones,
    but not points for the dead stones themselves. If calculating the final score, points for marked dead stones,
    captured stones, and komi should be added - see also the implementation of the "final_score" function."""

    is_territory_for: Color
    """Indicates to score 1 point of territory for this color player.
    If EMPTY, nobody scores this point. It is possible that this is EMPTY under a stone marked dead, in which case
    the point under the dead stone should not be counted as territory even if the dead stone itself is counted for points.
    """

    belongs_to_seki_group: Color
    """If this is not EMPTY, then this location is believed to be part of a group of the given color or a space
    surrounded by that group that is not marked as dead, but that this algorithm does not see as independently alive
    with two eyes.
    Callers could display this for informational purposes.

    Additionally, this could be used to enforce the Japanese rule that that stones in seki situations cannot be
    treated as dead and counted but must actually be physically captured prior to game end, by not scoring stones
    marked dead on points that belong to a seki group according to this field. However, note that it may be simpler
    to just always count marked-dead stones as points. Behaving more strictly could require careful corresponding
    UI work, since if stones that users explicitly mark to be dead are sometimes not counted as points, it may be
    confusing for users, and it may not be easy to see or know when they are and are not.
    """

    is_false_eye: bool
    """True if this point is judged to be an eye that does not assist in life and death. Informational,
    can be used to introspect the algorithm's perception of false eyes and life and death."""

    is_unscorable_false_eye: bool
    """True if this point is judged to be a false eye that normally should not be scored as a territory point
    because it will eventually need to be filled. Informational, the primary output field is_territory_for
    should already take this into account depending on the score_false_eyes parameter."""

    is_dame: bool
    """True if this point is being treated as a "dame" point. This field especially should not be used by anything
    in a load-bearing way, it is purely informational. Note that the algorithm might NOT consider some loosely
    surrounded areas as dame, if they are surrounded *enough* that the algorithm is treating that area as an eye
    for life and death purposes."""

    eye_value: int
    """How many eyes (max 2) the algorithm is treating the eyespace containing this point to be worth.
    Should not be used by anything in a load-bearing way, and will NOT be tactically accurate outside of
    finished game positions. This is just an informational indicator."""


def final_territory_score(
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    black_points_from_captures: float,
    white_points_from_captures: float,
    komi: float,
    score_false_eyes: bool = False,
) -> Dict[Color,float]:
    """Perform territory scoring with seki detection assuming user or AI-supplied life and death markings,
    and return the final score.

    So long as markings are correct, this scoring can often handle dame being unfilled, and will
    automatically discount points for false eye shapes that require protection. Not all internal protections
    will be caught - players may still need to fill some dame to force such protections first.

    Seki detection might not be perfect, but generally players should be able to correct scoring by playing out
    additional dame and/or throw-ins and ataris, so long as stones are marked correctly. Failures in the
    scoring algorithm that can't be corrected by further play should be rare and exotic.

    Parameters:
    stones[y][x] - BLACK or WHITE or EMPTY indicating the stones on the board.
    marked_dead[y][x] - True if the location has a stone marked as dead, and False otherwise.
    black_points_from_captures - the number of points to add to black's score due to stones already captured
      and removed from the board.
    white_points_from_captures - the number of points to add to white's score due to stones already captured
      and removed from the board.
    komi - the number of points to add to white's score due to playing second.
    score_false_eyes - defaults to False, if set to True will score territory in false eyes even if
      is_unscorable_false_eye is True.

    Returns a dict { BLACK: final_black_score, WHITE: final_white_score }.
    """
    scoring: List[List[LocScore]] = territory_scoring(stones,marked_dead,score_false_eyes=score_false_eyes)

    ysize = len(stones)
    xsize = len(stones[0])
    final_black_score = 0
    final_white_score = 0
    for y in range(ysize):
        for x in range(xsize):
            if scoring[y][x].is_territory_for == BLACK:
                final_black_score += 1
            elif scoring[y][x].is_territory_for == WHITE:
                final_white_score += 1

            if stones[y][x] == BLACK and marked_dead[y][x]:
                final_white_score += 1
            elif stones[y][x] == WHITE and marked_dead[y][x]:
                final_black_score += 1

    final_black_score += black_points_from_captures
    final_white_score += white_points_from_captures
    final_white_score += komi
    return { BLACK: final_black_score, WHITE: final_white_score }

def final_area_score(
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    komi: float,
) -> Dict[Color,float]:
    """Perform area scoring assuming user or AI-supplied life and death markings,
    and return the final score.

    Parameters:
    stones[y][x] - BLACK or WHITE or EMPTY indicating the stones on the board.
    marked_dead[y][x] - True if the location has a stone marked as dead, and False otherwise.
    komi - the number of points to add to white's score due to playing second.

    Returns a dict { BLACK: final_black_score, WHITE: final_white_score }.
    """
    scoring: List[List[Color]] = area_scoring(stones,marked_dead)

    ysize = len(stones)
    xsize = len(stones[0])
    final_black_score = 0
    final_white_score = 0
    for y in range(ysize):
        for x in range(xsize):
            if scoring[y][x] == BLACK:
                final_black_score += 1
            elif scoring[y][x] == WHITE:
                final_white_score += 1
    final_white_score += komi
    return { BLACK: final_black_score, WHITE: final_white_score }

def territory_scoring(
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    score_false_eyes: bool = False,
) -> List[List[LocScore]]:
    """Perform territory scoring with seki detection assuming user or AI-supplied life and death markings,
    and return the detailed territory map.

    So long as markings are correct, this scoring can often handle dame being unfilled, and will
    automatically discount points for false eye shapes that require protection. Not all internal protections
    will be caught - players may still need to fill some dame to force such protections first.

    Seki detection might not be perfect, but generally players should be able to correct scoring by playing out
    additional dame and/or throw-ins and ataris, so long as stones are marked correctly. Failures in the
    scoring algorithm that can't be corrected by further play should be rare and exotic.

    Parameters:
    stones[y][x] - BLACK or WHITE or EMPTY indicating the stones on the board.
    marked_dead[y][x] - True if the location has a stone marked as dead, and False otherwise.
    score_false_eyes - defaults to False, if set to True will score territory in false eyes even if
      is_unscorable_false_eye is True.

    Returns an array of PointScore objects that indicate how the points on the board should be scored."""

    ysize = len(stones)
    xsize = len(stones[0])
    for row in stones:
        if len(row) != xsize:
            raise ValueError(f"Not all rows in stones are the same length {xsize}")
        for value in row:
            if value != EMPTY and value != BLACK and value != WHITE:
                raise ValueError(f"Unexpected value in stones {value}")
    if len(marked_dead) != ysize:
        raise ValueError(f"marked_dead is not the same length as stones {ysize}")
    for row in marked_dead:
        if len(row) != xsize:
            raise ValueError(f"Not all rows in marked_dead are the same length as stones {xsize}")

    # Marks points where reachability should not be pathed through by the opponent.
    connection_blocks: List[List[Color]] = make_array(ysize,xsize,EMPTY)
    mark_connection_blocks(ysize,xsize,stones,marked_dead,connection_blocks)
    # print("CONNECTIONBLOCKS:")
    # print2d(connection_blocks, lambda c: ("." if c == -1 else color_to_str(c)))

    # Is there a path from this location to a living stone of the given color
    # that doesn't contain a living stone of the opponent?
    strict_reaches_black: List[List[bool]] = make_array(ysize,xsize,False)
    strict_reaches_white: List[List[bool]] = make_array(ysize,xsize,False)
    mark_reachability(ysize,xsize,stones,marked_dead,None,strict_reaches_black,strict_reaches_white)

    # Is there a path from this location to a living stone of the given color
    # that doesn't contain a living stone of the opponent and that doesn't pass through a connection block?
    reaches_black: List[List[bool]] = make_array(ysize,xsize,False)
    reaches_white: List[List[bool]] = make_array(ysize,xsize,False)
    mark_reachability(ysize,xsize,stones,marked_dead,connection_blocks,reaches_black,reaches_white)

    # Maximal contiguous areas that reach only one player, maximally unioned based on reachability.
    region_ids: List[List[RegionId]] = make_array(ysize,xsize,-1)
    region_infos_by_id: Dict[RegionId,RegionInfo] = {}
    mark_regions(ysize,xsize,stones,marked_dead,connection_blocks,reaches_black,reaches_white,region_ids,region_infos_by_id)
    # print("REGIONS:")
    # print2d(region_ids, lambda region_id: ".0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[region_id+1])
    # print("REGION COLOR:")
    # print2d(region_ids, lambda region_id: ("." if region_id == -1 else color_to_str(region_infos_by_id[region_id].color)))

    # Maximal contiguous areas of the same color and liveness
    chain_ids: List[List[ChainId]] = make_array(ysize,xsize,-1)
    chain_infos_by_id: Dict[ChainId,ChainInfo] = {}
    mark_chains(ysize,xsize,stones,marked_dead,region_ids,chain_ids,chain_infos_by_id)
    # print("CHAINS:")
    # print2d(chain_ids, lambda chain_id: ".0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[chain_id+1])

    # Maximal unions of non-empty chains based on reachability by the owner of that chain passing through
    # non-region space that is not connection-blocked.
    macrochain_ids: List[List[MacroChainId]] = make_array(ysize,xsize,-1)
    macrochain_infos_by_id: Dict[MacroChainId,MacroChainInfo] = {}
    mark_macrochains(ysize,xsize,stones,marked_dead,connection_blocks,region_ids,region_infos_by_id,chain_ids,chain_infos_by_id,macrochain_ids,macrochain_infos_by_id)
    # print("MACROCHAINS:")
    # print2d(macrochain_ids, lambda i: ".0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[i+1])

    # Eyes or potential eyes of regions
    # Does NOT fill in eye_value - all eyes are assumed to have eye value 0 for now.
    eye_ids: List[List[EyeId]] = make_array(ysize,xsize,-1)
    eye_infos_by_id: Dict[EyeId,EyeInfo] = {}
    mark_potential_eyes(ysize,xsize,stones,marked_dead,strict_reaches_black,strict_reaches_white,region_ids,region_infos_by_id,macrochain_ids,macrochain_infos_by_id,eye_ids,eye_infos_by_id)
    # print("EYES:")
    # print2d(eye_ids, lambda i: ".0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[i+1])

    # Detect points that should not be counted as part of eyes
    # Do this right now while eyes have value 0, to get the initial set of false eye points.
    is_false_eye_point: List[List[bool]] = make_array(ysize,xsize,False)
    mark_false_eye_points(ysize,xsize,region_ids,macrochain_ids,macrochain_infos_by_id,eye_infos_by_id,is_false_eye_point)
    # print("FALSE EYE POINTS:")
    # print2d(is_false_eye_point, lambda b: ("F" if b else "."))

    # Now fill in eye values
    mark_eye_values(ysize,xsize,stones,marked_dead,region_ids,region_infos_by_id,chain_ids,chain_infos_by_id,is_false_eye_point,eye_ids,eye_infos_by_id)
    # print("EYEVALUES:")
    # print2d(eye_ids, lambda eye_id: ("." if eye_id == -1 else "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[eye_infos_by_id[eye_id].eye_value]))

    # Now do the false eye detection again with proper eye values, to get the unscorable false eyes.
    is_unscorable_false_eye_point: List[List[bool]] = make_array(ysize,xsize,False)
    mark_false_eye_points(ysize,xsize,region_ids,macrochain_ids,macrochain_infos_by_id,eye_infos_by_id,is_unscorable_false_eye_point)
    # print("UNSCORABLE FALSE EYE POINTS:")
    # print2d(is_unscorable_false_eye_point, lambda b: ("F" if b else "."))

    # Final processing
    make_locscore = lambda: LocScore(is_territory_for=EMPTY,belongs_to_seki_group=EMPTY,is_false_eye=False,is_unscorable_false_eye=False,is_dame=False,eye_value=0)
    scoring: List[List[LocScore]] = make_array_from_callable(ysize,xsize,make_locscore)

    mark_scoring(ysize,xsize,stones,marked_dead,score_false_eyes,strict_reaches_black,strict_reaches_white,region_ids,region_infos_by_id,chain_ids,chain_infos_by_id,is_false_eye_point,eye_ids,eye_infos_by_id,is_unscorable_false_eye_point,scoring)

    return scoring


def area_scoring(
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
) -> List[List[Color]]:
    """Perform area scoring assuming user or AI-supplied life and death markings,
    and return the detailed area map.

    Parameters:
    stones[y][x] - BLACK or WHITE or EMPTY indicating the stones on the board.
    marked_dead[y][x] - True if the location has a stone marked as dead, and False otherwise.

    Returns an array of Colors that indicate how the points on the board should be scored - which points are who's area."""

    ysize = len(stones)
    xsize = len(stones[0])
    for row in stones:
        if len(row) != xsize:
            raise ValueError(f"Not all rows in stones are the same length {xsize}")
        for value in row:
            if value != EMPTY and value != BLACK and value != WHITE:
                raise ValueError(f"Unexpected value in stones {value}")
    if len(marked_dead) != ysize:
        raise ValueError(f"marked_dead is not the same length as stones {ysize}")
    for row in marked_dead:
        if len(row) != xsize:
            raise ValueError(f"Not all rows in marked_dead are the same length as stones {xsize}")

    # Is there a path from this location to a living stone of the given color
    # that doesn't contain a living stone of the opponent?
    strict_reaches_black: List[List[bool]] = make_array(ysize,xsize,False)
    strict_reaches_white: List[List[bool]] = make_array(ysize,xsize,False)
    mark_reachability(ysize,xsize,stones,marked_dead,None,strict_reaches_black,strict_reaches_white)

    scoring: List[List[Color]] = make_array(ysize,xsize,EMPTY)
    for y in range(ysize):
        for x in range(xsize):
            if strict_reaches_white[y][x] and not strict_reaches_black[y][x]:
                scoring[y][x] = WHITE
            if strict_reaches_black[y][x] and not strict_reaches_white[y][x]:
                scoring[y][x] = BLACK
    return scoring


def get_opp(pla: Color) -> Color:
    return 3 - pla

RegionId = int
ChainId = int
MacroChainId = int
EyeId = int

def make_array(ysize, xsize, initial_value):
    rows = []
    for y in range(ysize):
        row = []
        for x in range(xsize):
            row.append(initial_value)
        rows.append(row)
    return rows

def make_array_from_callable(ysize, xsize, f):
    rows = []
    for y in range(ysize):
        row = []
        for x in range(xsize):
            row.append(f())
        rows.append(row)
    return rows

def is_on_board(y, x, ysize, xsize):
    return y >= 0 and x >= 0 and y < ysize and x < xsize

def is_on_border(y, x, ysize, xsize):
    return y == 0 or x == 0 or y == ysize-1 or x == xsize-1

def is_adjacent(y1, x1, y2, x2):
    return (y1 == y2 and (x1 == x2 + 1 or x1 == x2 - 1)) or (x1 == x2 and (y1 == y2 + 1 or y1 == y2 - 1))

def print2d(board, f):
    print(string2d(board,f))

def string2d(board, f):
    ysize = len(board)
    lines = []
    for y in range(ysize):
        pieces = []
        for item in board[y]:
            pieces.append(str(f(item)))
        lines.append("".join(pieces))
    return "\n".join(lines)

def string2d2(board1, board2, f):
    ysize = len(board1)
    lines = []
    for y in range(ysize):
        pieces = []
        for x in range(len(board1[y])):
            item1 = board1[y][x]
            item2 = board2[y][x]
            pieces.append(str(f(item1,item2)))
        lines.append("".join(pieces))
    return "\n".join(lines)

def color_to_str(color):
    if color == BLACK:
        return "x"
    elif color == WHITE:
        return "o"
    return "."


def mark_connection_blocks(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    connection_blocks: List[List[Color]],  # mutated by this function
):
    patterns = [
        [
            "pp",
            "@e",
            "pe",
        ],
        [
            "ep?",
            "e@e",
            "ep?",
        ],
        [
            "pee",
            "e@p",
            "pee",
        ],
        [
            "?e?",
            "p@p",
            "xxx",
        ],
        [
            "pp",
            "@e",
            "xx",
        ],
        [
            "ep?",
            "e@e",
            "xxx",
        ],
    ]

    for pla in [BLACK,WHITE]:
        opp = get_opp(pla)
        # Orient pattern 8 ways
        for pdydy, pdydx, pdxdy, pdxdx in [
            (1,0,0,1),
            (-1,0,0,1),
            (1,0,0,-1),
            (-1,0,0,-1),
            (0,1,1,0),
            (0,-1,1,0),
            (0,1,-1,0),
            (0,-1,-1,0),
        ]:
            for pattern in patterns:
                pylen = len(pattern)
                pxlen = len(pattern[0])
                is_edge_pattern = "x" in pattern[pylen-1]
                if is_edge_pattern:
                    pylen -= 1  # We check the edge specially

                y_range = list(range(ysize))
                x_range = list(range(xsize))

                if is_edge_pattern:
                    if pdydy == -1:
                        y_range = [ len(pattern)-2 ]
                    elif pdydy == 1:
                        y_range = [ ysize - (len(pattern)-1) ]
                    elif pdxdy == -1:
                        x_range = [ len(pattern)-2 ]
                    elif pdxdy == 1:
                        x_range = [ xsize - (len(pattern)-1) ]

                for y in y_range:
                    for x in x_range:
                        def get_target_yx(pdy,pdx):
                            return (y + pdydy * pdy + pdxdy * pdx, x + pdydx * pdy + pdxdx * pdx)

                        ty,tx = get_target_yx(pylen-1,pxlen-1)
                        if not is_on_board(ty,tx,ysize,xsize):
                            continue

                        atloc = None
                        mismatch = False
                        for pdy in range(pylen):
                            for pdx in range(pxlen):
                                c = pattern[pdy][pdx]
                                # Anything allowed
                                if c == "?":
                                    continue
                                ty,tx = get_target_yx(pdy,pdx)
                                # Living player
                                if c == "p":
                                    if not (stones[ty][tx] == pla and not marked_dead[ty][tx]):
                                        mismatch = True
                                        break
                                # Empty or living player or dead opponent
                                elif c == "e":
                                    if (
                                        stones[ty][tx] != EMPTY and
                                        not (stones[ty][tx] == pla and not marked_dead[ty][tx]) and
                                        not (stones[ty][tx] == opp and marked_dead[ty][tx])
                                    ):
                                        mismatch = True
                                        break
                                # Empty, and special point
                                elif c == "@":
                                    if stones[ty][tx] != EMPTY:
                                        mismatch = True
                                        break
                                    atloc = (ty,tx)
                                else:
                                    assert False, c

                            if mismatch:
                                break

                        if not mismatch:
                            assert atloc is not None
                            (ty,tx) = atloc
                            connection_blocks[ty][tx] = pla

def mark_reachability(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    connection_blocks: Optional[List[List[Color]]],
    reaches_black: List[List[bool]],  # mutated by this function
    reaches_white: List[List[bool]],  # mutated by this function
):
    # Recursively walk and fill non-pla areas, going through dead stones.
    def fill_reach(y: int, x: int, reaches_pla: List[List[bool]], pla: Color):
        if not is_on_board(y,x,ysize,xsize):
            return
        if reaches_pla[y][x]:
            return
        if stones[y][x] == get_opp(pla) and not marked_dead[y][x]:
            return
        reaches_pla[y][x] = True

        # Connection block spots might be reachable, but stop further propagation
        if connection_blocks is not None and connection_blocks[y][x] == get_opp(pla):
            return

        fill_reach(y-1,x,reaches_pla,pla)
        fill_reach(y+1,x,reaches_pla,pla)
        fill_reach(y,x-1,reaches_pla,pla)
        fill_reach(y,x+1,reaches_pla,pla)

    for y in range(ysize):
        for x in range(xsize):
            if stones[y][x] == BLACK and not marked_dead[y][x]:
                fill_reach(y,x,reaches_black,BLACK)
            if stones[y][x] == WHITE and not marked_dead[y][x]:
                fill_reach(y,x,reaches_white,WHITE)

@dataclass
class RegionInfo:
    region_id: RegionId
    color: Color
    region_and_dame: Set[Tuple[int,int]]
    eyes: Set[EyeId]

def mark_regions(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    connection_blocks: List[List[Color]],
    reaches_black: List[List[bool]],
    reaches_white: List[List[bool]],
    region_ids: List[List[RegionId]],  # mutated by this function
    region_infos_by_id: Dict[RegionId,RegionInfo],  # mutated by this function
):

    # Recursively walk and fill regions that reach only pla and not opp, but passing through anything
    # that's not an opponent living stone or a connection block
    def fill_region(y: int, x: int, with_id: RegionId, opp: Color, reaches_pla: List[List[bool]], reaches_opp: List[List[bool]], visited: List[List[bool]]):
        if not is_on_board(y,x,ysize,xsize):
            return
        if visited[y][x]:
            return
        if region_ids[y][x] != -1:
            return
        if stones[y][x] == opp and not marked_dead[y][x]:
            return

        visited[y][x] = True
        region_infos_by_id[with_id].region_and_dame.add((y,x))
        if reaches_pla[y][x] and not reaches_opp[y][x]:
            region_ids[y][x] = with_id

        # Connection block spots might be reachable, but stop further propagation
        if connection_blocks[y][x] == opp:
            return

        fill_region(y-1,x,with_id,opp,reaches_pla,reaches_opp,visited)
        fill_region(y+1,x,with_id,opp,reaches_pla,reaches_opp,visited)
        fill_region(y,x-1,with_id,opp,reaches_pla,reaches_opp,visited)
        fill_region(y,x+1,with_id,opp,reaches_pla,reaches_opp,visited)

    next_region_id = 0
    for y in range(ysize):
        for x in range(xsize):
            if reaches_black[y][x] and not reaches_white[y][x] and region_ids[y][x] == -1:
                region_id = next_region_id
                next_region_id += 1
                region_infos_by_id[region_id] = RegionInfo(region_id=region_id, color=BLACK, region_and_dame=set(), eyes=set())
                visited = make_array(ysize,xsize,False)
                fill_region(y,x,region_id,WHITE,reaches_black,reaches_white,visited)
            if reaches_white[y][x] and not reaches_black[y][x] and region_ids[y][x] == -1:
                region_id = next_region_id
                next_region_id += 1
                region_infos_by_id[region_id] = RegionInfo(region_id=region_id, color=WHITE, region_and_dame=set(), eyes=set())
                visited = make_array(ysize,xsize,False)
                fill_region(y,x,region_id,BLACK,reaches_white,reaches_black,visited)

@dataclass
class ChainInfo:
    chain_id: ChainId
    region_id: RegionId  # -1 unless a chain ENTIRELY belongs to a region (empty chain may cross regions due to connection blockers)
    color: Color
    points: List[Tuple[int,int]]
    neighbors: Set[ChainId]
    adjacents: Set[Tuple[int,int]]
    liberties: Set[Tuple[int,int]]
    is_marked_dead: bool

def mark_chains(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    region_ids: List[List[RegionId]],
    chain_ids: List[List[ChainId]],  # mutated by this function
    chain_infos_by_id: Dict[ChainId,ChainInfo],  # mutated by this function
):
    # Recursively walk and fill contiguous areas of the same color and liveness
    # while accumulating the various properties
    def fill_chain(y: int, x: int, with_id: ChainId, color: Color, is_marked_dead: bool):
        if not is_on_board(y,x,ysize,xsize):
            return
        if chain_ids[y][x] == with_id:
            return
        if chain_ids[y][x] != -1:
            other_id = chain_ids[y][x]
            chain_infos_by_id[other_id].neighbors.add(with_id)
            chain_infos_by_id[with_id].neighbors.add(other_id)
            chain_infos_by_id[with_id].adjacents.add((y,x))
            if stones[y][x] == EMPTY:
                chain_infos_by_id[with_id].liberties.add((y,x))
            return
        if stones[y][x] != color or marked_dead[y][x] != is_marked_dead:
            chain_infos_by_id[with_id].adjacents.add((y,x))
            if stones[y][x] == EMPTY:
                chain_infos_by_id[with_id].liberties.add((y,x))
            return
        chain_ids[y][x] = with_id
        chain_infos_by_id[with_id].points.append((y,x))
        # If chain would seem to belong to more than one region then set its region to -1.
        if chain_infos_by_id[with_id].region_id != region_ids[y][x]:
            chain_infos_by_id[with_id].region_id = -1

        # Any contiguous chain of the same liveness and color if it's nonempty should always belong to the
        # same region, or -1 if they don't belong to any region.
        assert color == EMPTY or region_ids[y][x] == chain_infos_by_id[with_id].region_id

        fill_chain(y-1,x,with_id,color,is_marked_dead)
        fill_chain(y+1,x,with_id,color,is_marked_dead)
        fill_chain(y,x-1,with_id,color,is_marked_dead)
        fill_chain(y,x+1,with_id,color,is_marked_dead)

    next_chain_id = 0
    for y in range(ysize):
        for x in range(xsize):
            if chain_ids[y][x] == -1:
                chain_id = next_chain_id
                next_chain_id += 1
                color = stones[y][x]
                is_marked_dead = marked_dead[y][x]
                chain_infos_by_id[chain_id] = ChainInfo(
                    chain_id=chain_id,
                    region_id=region_ids[y][x],
                    color=color,
                    points=[],
                    neighbors=set(),
                    adjacents=set(),
                    liberties=set(),
                    is_marked_dead=is_marked_dead,
                )
                assert is_marked_dead or color == EMPTY or region_ids[y][x] != -1
                fill_chain(y,x,chain_id,color,is_marked_dead)


@dataclass
class MacroChainInfo:
    macrochain_id: ChainId
    region_id: RegionId
    color: Color
    points: List[Tuple[int,int]]
    chains: Set[ChainId]
    eye_neighbors_from: Dict[EyeId,Set[Tuple[int,int]]]  # For each eye, which points of this macrochain touch it

def mark_macrochains(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    connection_blocks: List[List[Color]],
    region_ids: List[List[RegionId]],
    region_infos_by_id: Dict[RegionId,RegionInfo],
    chain_ids: List[List[ChainId]],
    chain_infos_by_id: Dict[ChainId,ChainInfo],
    macrochain_ids: List[List[MacroChainId]],
    macrochain_infos_by_id: Dict[MacroChainId,MacroChainInfo],
):
    next_macrochain_id = 0

    for pla in [BLACK,WHITE]:
        opp = get_opp(pla)

        chains_handled: Set[ChainId] = set()
        visited = make_array(ysize,xsize,False)

        for chain_id, chain_info in chain_infos_by_id.items():
            # Already done
            if chain_id in chains_handled:
                continue
            if not (chain_info.color == pla and not chain_info.is_marked_dead):
                continue
            region_id = chain_info.region_id
            assert region_id != -1

            macrochain_id = next_macrochain_id
            next_macrochain_id += 1

            points = []
            chains = set()

            def walk_and_accumulate(y: int, x: int):
                if not is_on_board(y,x,ysize,xsize):
                    return
                if visited[y][x]:
                    return
                visited[y][x] = True

                chain_id = chain_ids[y][x]
                chain_info = chain_infos_by_id[chain_id]
                should_recurse = False
                if stones[y][x] == pla and not marked_dead[y][x]:
                    macrochain_ids[y][x] = macrochain_id
                    points.append((y,x))
                    if chain_id not in chains:
                        chains.add(chain_id)
                        chains_handled.add(chain_id)
                    # Walk through player chains
                    should_recurse = True
                elif region_ids[y][x] == -1 and connection_blocks[y][x] != opp:
                    # Walk through regionless unblocked space
                    should_recurse = True

                if should_recurse:
                    walk_and_accumulate(y-1,x)
                    walk_and_accumulate(y+1,x)
                    walk_and_accumulate(y,x-1)
                    walk_and_accumulate(y,x+1)

            (y,x) = chain_info.points[0]
            walk_and_accumulate(y,x)

            macrochain_infos_by_id[macrochain_id] = MacroChainInfo(
                macrochain_id=macrochain_id,
                region_id=region_id,
                color=pla,
                points=points,
                chains=chains,
                eye_neighbors_from={}, # filled in later
            )

@dataclass
class EyeInfo:
    pla: Color
    region_id: RegionId
    eye_id: EyeId
    potential_points: Set[Tuple[int,int]]
    real_points: Set[Tuple[int,int]]
    macrochain_neighbors_from: Dict[MacroChainId,Set[Tuple[int,int]]]  # For each macrochain, which potential eye points touch it
    is_loose: bool  # Loosely surrounded eye, strictly reachable by the opponent
    eye_value: int

def mark_potential_eyes(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    strict_reaches_black: List[List[bool]],
    strict_reaches_white: List[List[bool]],
    region_ids: List[List[RegionId]],
    region_infos_by_id: Dict[RegionId,RegionInfo],  # mutated by this function to fill in eyes
    macrochain_ids: List[List[MacroChainId]],
    macrochain_infos_by_id: Dict[MacroChainId,MacroChainInfo],  # mutated by this function to add eye adjacencies
    eye_ids: List[List[EyeId]],  # mutated by this function
    eye_infos_by_id: Dict[EyeId,EyeInfo],  # mutated by this function
):
    next_eye_id = 0

    # Also heuristically count eyes for connection-blocked area that isn't strictly blocked.
    visited = make_array(ysize,xsize,False)
    for y in range(ysize):
        for x in range(xsize):
            if visited[y][x]:
                continue
            if eye_ids[y][x] != -1:
                continue
            if stones[y][x] != EMPTY and not marked_dead[y][x]:
                continue
            region_id = region_ids[y][x]
            if region_id == -1:
                continue
            region_info = region_infos_by_id[region_id]
            pla = region_info.color
            is_loose = strict_reaches_white[y][x] and strict_reaches_black[y][x]

            # Allocate the new eye id and populate the arrays!
            eye_id = next_eye_id
            next_eye_id += 1

            # Recursively accumulate the empty or marked-dead points within the region.
            potential_points = set()
            macrochain_neighbors_from = {}
            def acc_region(y: int, x: int, prevy: int, prevx: int):
                if not is_on_board(y,x,ysize,xsize):
                    return
                if visited[y][x]:
                    return
                if region_ids[y][x] != region_id:
                    return
                if macrochain_ids[y][x] != -1:
                    macrochain_id = macrochain_ids[y][x]
                    if macrochain_id not in macrochain_neighbors_from:
                        macrochain_neighbors_from[macrochain_id] = set()
                    macrochain_neighbors_from[macrochain_id].add((prevy,prevx))
                    if eye_id not in macrochain_infos_by_id[macrochain_id].eye_neighbors_from:
                        macrochain_infos_by_id[macrochain_id].eye_neighbors_from[eye_id] = set()
                    macrochain_infos_by_id[macrochain_id].eye_neighbors_from[eye_id].add((y,x))
                if stones[y][x] != EMPTY and not marked_dead[y][x]:
                    return
                visited[y][x] = True
                eye_ids[y][x] = eye_id
                potential_points.add((y,x))
                acc_region(y-1,x,y,x)
                acc_region(y+1,x,y,x)
                acc_region(y,x-1,y,x)
                acc_region(y,x+1,y,x)

            assert macrochain_ids[y][x] == -1
            acc_region(y,x,10000,10000)

            eye_infos_by_id[eye_id] = EyeInfo(
                pla=pla,
                region_id=region_id,
                eye_id=eye_id,
                potential_points=potential_points,
                real_points=set(),  # filled in later
                macrochain_neighbors_from=macrochain_neighbors_from,
                is_loose=is_loose,
                eye_value=0, # estimated later
            )
            # Update the region info with this eye too
            region_infos_by_id[region_id].eyes.add(eye_id)


def mark_false_eye_points(
    ysize: int,
    xsize: int,
    region_ids: List[List[RegionId]],
    macrochain_ids: List[List[MacroChainId]],
    macrochain_infos_by_id: Dict[MacroChainId,MacroChainInfo],
    eye_infos_by_id: Dict[EyeId,EyeInfo],
    is_false_eye_point: List[List[bool]],  # mutated by this function
):
    # Check each eye for false eye points
    # A point within a potential eye is a false eye point for life and death if there is some macrochain border of that
    # point that doesn't have any path to reach some other macrochain border of that eye other than connecting through
    # that point itself. It is allowed to go through other eyes or macrochains, following normal adjacency, as well as
    # going through other points *within* the same eye.
    # A point is additionally an unscorable false eye point if that macrochain doesn't reach any real point of any eye
    # with eyevalue >= 1, including real points of the eye itself.
    # This method checks for unscorable false eye points, but it will check for life and death false eye points if you
    # call it while eyevalues are all 0 (which is good, since eye value computation uses the false eye determination).
    for orig_eye_id, orig_eye_info in eye_infos_by_id.items():
        for orig_macrochain_id, neighbors_from_eye_points in orig_eye_info.macrochain_neighbors_from.items():
            # Check each point to see if it's going to be false
            for ey,ex in neighbors_from_eye_points:
                # Cannot be a false eye point if it is adjacent to more than one other point within the eye.
                same_eye_adj_count = sum(1 for point in [(ey-1,ex),(ey+1,ex),(ey,ex-1),(ey,ex+1)] if point in orig_eye_info.potential_points)
                if same_eye_adj_count > 1:
                    continue

                # See if the macrochain connects recursively to anything that reaches the eye again from *all* possible sides.
                # Or if it reaches an eye with positive eye value.
                reaching_sides = set()
                visited_macro = set()
                visited_other_eyes = set()
                visited_orig_eye_points = set()
                # Add to visited orig eye points so we can exclude any visits to it
                visited_orig_eye_points.add((ey,ex))

                # How many sides we need to reach for it NOT to be false.
                target_side_count = 0
                for (y,x) in [(ey-1,ex),(ey+1,ex),(ey,ex-1),(ey,ex+1)]:
                    # Obviously we don't need to reach an eye from off the board
                    # More subtly, we don't need to reach from directions that are out of the region entirely
                    # This applies to "eyes" that are surrounded loosely.
                    if is_on_board(y,x,ysize,xsize) and region_ids[y][x] == orig_eye_info.region_id:
                        target_side_count += 1

                # print(f"TESTING MACRO {orig_macrochain_id} for eye {orig_eye_id} at {ey} {ex}")
                def search(macrochain_id: MacroChainId):
                    if macrochain_id in visited_macro:
                        return False
                    visited_macro.add(macrochain_id)
                    # print(f"SEARCH {macrochain_id}")

                    macrochain_info = macrochain_infos_by_id[macrochain_id]
                    for eye_id, neighbors_from_macro_points in macrochain_info.eye_neighbors_from.items():
                        if eye_id in visited_other_eyes:
                            continue
                        # print(f"SEARCH EYE {eye_id}")
                        if eye_id == orig_eye_id:
                            eye_info = eye_infos_by_id[eye_id]
                            # print(f"REACHED ORIG")
                            for (y,x) in neighbors_from_macro_points:
                                if is_adjacent(y,x,ey,ex):
                                    reaching_sides.add((y,x))
                                    # print(f"REACHED SIDES {reaching_sides} {target_side_count}")
                            if len(reaching_sides) >= target_side_count:
                                return True

                            # If we reached the original eye at other points besides the point being tested for falseness,
                            # we specially handle propagation through them. Find all points reachable excluding the point being tested.
                            points_reached = find_recursively_adjacent_points(
                                within_set=eye_info.potential_points,
                                from_points=eye_info.macrochain_neighbors_from[macrochain_id],
                                excluding_points=visited_orig_eye_points,
                            )
                            if len(points_reached) == 0:
                                continue
                            visited_orig_eye_points.update(points_reached)

                            # Reaches real point of the same eye with positive eye value?
                            if eye_info.eye_value > 0:
                                for point in points_reached:
                                    if point in eye_info.real_points:
                                        return True

                            # Continue to count sides reached of the possible false eye point
                            for point in points_reached:
                                (y,x) = point
                                if is_adjacent(y,x,ey,ex):
                                    reaching_sides.add(point)
                                    # print(f"REACHED SIDES {reaching_sides} {target_side_count}")
                            if len(reaching_sides) >= target_side_count:
                                return True

                            # Then find all macrochains adjacent to one of those points and recurse propagation through them
                            for next_macrochain_id, from_eye_points in eye_info.macrochain_neighbors_from.items():
                                if any(point in points_reached for point in from_eye_points):
                                    if search(next_macrochain_id):
                                        return True
                        else:
                            visited_other_eyes.add(eye_id)
                            eye_info = eye_infos_by_id[eye_id]
                            if eye_info.eye_value > 0:
                                return True
                            for next_macrochain_id in eye_info.macrochain_neighbors_from:
                                if search(next_macrochain_id):
                                    return True
                    return False

                # Found a connection to a second point or reaching from all sides or found a different eye with positive eye value?
                if search(orig_macrochain_id):
                    # Not a false eye
                    # print(f"TESTING MACRO {orig_macrochain_id} for eye {orig_eye_id} TRUE")
                    pass
                else:
                    # print(f"TESTING MACRO {orig_macrochain_id} for eye {orig_eye_id} FALSE")
                    is_false_eye_point[ey][ex] = True


def find_recursively_adjacent_points(
    within_set: Set[Tuple[int,int]],
    from_points: Set[Tuple[int,int]],
    excluding_points: Set[Tuple[int,int]]
) -> Set[Tuple[int,int]]:
    expanded = set()
    from_points = list(from_points)
    i = 0
    while i < len(from_points):
        point = from_points[i]
        i += 1
        if point in excluding_points or point in expanded or point not in within_set:
            continue
        expanded.add(point)
        (y,x) = point
        from_points.append((y-1,x))
        from_points.append((y+1,x))
        from_points.append((y,x-1))
        from_points.append((y,x+1))
    return expanded


def get_pieces(ysize: int, xsize: int, points: Set[Tuple[int,int]], points_to_delete: Set[Tuple[int,int]]) -> List[Set[Tuple[int,int]]]:
    """Get the connected pieces resulting from deleting the given point"""
    used_points = set()

    def floodfill(point, piece: Set[Tuple[int,int]]):
        if point in used_points or point in points_to_delete:
            return
        used_points.add(point)
        piece.add(point)

        (y,x) = point
        adjacents = [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]
        for point in adjacents:
            if point in points:
                floodfill(point,piece)

    pieces = []
    for point in points:
        if point not in used_points:
            piece = set()
            floodfill(point,piece)
            if len(piece) > 0:
                pieces.append(piece)
    return pieces

def is_pseudolegal(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    chain_ids: List[List[ChainId]],
    chain_infos_by_id: Dict[ChainId,ChainInfo],
    y: int,
    x: int,
    pla: Color,
) -> bool:
    if stones[y][x] != EMPTY:
        return False
    adjacents = [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]
    opp = get_opp(pla)
    for (ay,ax) in adjacents:
        if is_on_board(ay,ax,ysize,xsize):
            if stones[ay][ax] != opp:
                return True
            if len(chain_infos_by_id[chain_ids[ay][ax]].liberties) <= 1:
                return True
    return False

@dataclass
class EyePointInfo:
    adj_points: List[Tuple[int,int]]
    adj_eye_points: List[Tuple[int,int]]
    num_empty_adj_points: int = 0
    num_empty_adj_false_points: int = 0
    num_empty_adj_eye_points: int = 0
    num_opp_adj_false_points: int = 0

    # True on an opp stone that is connected and adjacent to opp stone thrown in on a false eye point.
    # Indicates basically that this spot cannot ever be used by the player to block of an eye.
    is_false_eye_poke: bool = False

    # Num moves assumed to turn this spot into an eye. Counts +1 for adjacent empty spots not part of the eye,
    # And +1 for adjacent spots in the eye that are adjacent to opponent stones not part of the eye. (opponent has thrown in)
    # And +1000 for adjacent spots that are false eye pokes (impossible to block off now)
    num_moves_to_block: int = 0

    # Number of spots that can be blocked in 1 move that are depending on here being the spot to block.
    num_blockables_depending_on_this_spot: int = 0

def count(points,predicate):
    c = 0
    for (y,x) in points:
        if predicate(y,x):
            c += 1
    return c

def mark_eye_values(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    region_ids: List[List[RegionId]],
    region_infos_by_id: Dict[RegionId,RegionInfo],
    chain_ids: List[List[ChainId]],
    chain_infos_by_id: Dict[ChainId,ChainInfo],
    is_false_eye_point: List[List[bool]],
    eye_ids: List[List[EyeId]],
    eye_infos_by_id: Dict[EyeId,EyeInfo],  # mutated by this function to fill in eye value
):
    for eye_id, eye_info in eye_infos_by_id.items():
        pla = eye_info.pla
        opp = get_opp(pla)

        # Fill in real points of eye
        # And let's accumulate various stats about the points in the eye
        info_by_point = {}
        assert len(eye_info.real_points) == 0  # shouldn't be filled in yet
        for (y,x) in eye_info.potential_points:
            if not is_false_eye_point[y][x]:
                eye_info.real_points.add((y,x))
                info = EyePointInfo(adj_points=[],adj_eye_points=[])
                info_by_point[(y,x)] = info

        for (y,x) in eye_info.real_points:
            info = info_by_point[(y,x)]
            adjacents = [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]
            for (ay,ax) in adjacents:
                if not is_on_board(ay,ax,ysize,xsize):
                    continue
                info.adj_points.append((ay,ax))
                if (ay,ax) in eye_info.real_points:
                    info.adj_eye_points.append((ay,ax))

        for (y,x) in eye_info.real_points:
            info = info_by_point[(y,x)]
            for (ay,ax) in info.adj_points:
                if stones[ay][ax] == EMPTY:
                    info.num_empty_adj_points += 1
                if stones[ay][ax] == EMPTY and (ay,ax) in eye_info.real_points:
                    info.num_empty_adj_eye_points += 1
                if stones[ay][ax] == EMPTY and is_false_eye_point[ay][ax]:
                    info.num_empty_adj_false_points += 1
                if stones[ay][ax] == opp and is_false_eye_point[ay][ax]:
                    info.num_opp_adj_false_points += 1

            if info.num_opp_adj_false_points > 0 and stones[y][x] == opp:
                info.is_false_eye_poke = True
            if info.num_empty_adj_false_points >= 2 and stones[y][x] == opp:
                info.is_false_eye_poke = True  # miai to make the poke

        for (y,x) in eye_info.real_points:
            info = info_by_point[(y,x)]
            info.num_moves_to_block = 0
            info.num_moves_to_block_no_opps = 0
            for (ay,ax) in info.adj_points:
                block = 0
                if stones[ay][ax] == EMPTY and (ay,ax) not in eye_info.real_points:
                    block = 1
                if stones[ay][ax] == EMPTY and (ay,ax) in info_by_point and info_by_point[(ay,ax)].num_opp_adj_false_points >= 1:
                    block = 1
                if stones[ay][ax] == opp and (ay,ax) in info_by_point and info_by_point[(ay,ax)].num_empty_adj_false_points >= 1:
                    block = 1
                if stones[ay][ax] == opp and is_false_eye_point[ay][ax]:
                    block = 1000
                if stones[ay][ax] == opp and (ay,ax) in info_by_point and info_by_point[(ay,ax)].is_false_eye_poke:
                    block = 1000
                info.num_moves_to_block += block

        # Try to compute the eye value of this eye
        # A lot of the cases are just heuristic and are not entirely correct, but
        # it should be very rare for them to not be fixable by playing more dame and connecting more false eye shapes and such.
        eye_value = 0
        # General for all eyes - if the eye contains a point that can be blocked off in one move or less,
        # we treat it at as at least one eye (favoring the defender for unsettled)
        if count(eye_info.real_points, lambda y,x: info_by_point[(y,x)].num_moves_to_block <= 1) >= 1:
            eye_value = 1

        # General for all eyes - if the eye contains a topologically interior bottleneck with respect
        # to the graph of points contained only within the eye itself and it can be played
        # and there are at least N pieces that have a point with <= 0 moves to block off, count N eye value
        for point_to_delete in eye_info.real_points:
            (dy,dx) = point_to_delete
            if not is_pseudolegal(ysize,xsize,stones,chain_ids,chain_infos_by_id,dy,dx,pla):
                continue

            pieces = get_pieces(ysize,xsize,eye_info.real_points,set([point_to_delete]))
            if len(pieces) < 2:
                continue

            # Also, pieces should accrue -1 moves to block if the bottleneck itself was the only reason.
            # Since playing the bottleneck move will actually perform that block
            should_bonus = info_by_point[(dy,dx)].num_opp_adj_false_points == 1

            num_definite_eye_pieces = 0
            for piece in pieces:
                zero_moves_to_block = False
                for point in piece:
                    if info_by_point[point].num_moves_to_block <= 0:
                        zero_moves_to_block = True
                        break
                    if should_bonus and info_by_point[point].num_moves_to_block <= 1:
                        zero_moves_to_block = True
                        break
                if zero_moves_to_block:
                    num_definite_eye_pieces += 1
            eye_value = max(eye_value, num_definite_eye_pieces)

        # General for all eyes - assume 1 eye value if there are at least 5 stones marked as dead in the eye
        # General for all eyes - assume 2 eye value if there are at least 8 stones marked as dead in the eye
        marked_dead_count = count(eye_info.real_points, lambda y,x: stones[y][x] == opp and marked_dead[y][x])
        if marked_dead_count >= 5:
            eye_value = max(eye_value, 1)
        if marked_dead_count >= 8:
            eye_value = max(eye_value, 2)

        # General for all eyes - assume 2 eye value if the size of the eye minus the number of weaknesses (counting severe weaknesses 2x)
        # minus the number of opponent stones inside on degree >= 2 points is at least 6.
        if eye_value < 2 and (
            len(eye_info.real_points)
            - count(eye_info.real_points, lambda y,x: info_by_point[(y,x)].num_moves_to_block >= 1)
            - count(eye_info.real_points, lambda y,x: info_by_point[(y,x)].num_moves_to_block >= 2)
            - count(eye_info.real_points, lambda y,x: stones[y][x] == opp and len(info_by_point[(y,x)].adj_eye_points) >= 2)
            >= 6
        ):
            eye_value = max(eye_value, 2)

        # General for all eyes - assume 2 eye value if there are many empty degree 3 or 4 points inside.
        if eye_value < 2 and (
            count(eye_info.real_points, lambda y,x: stones[y][x] == EMPTY and len(info_by_point[(y,x)].adj_eye_points) >= 4) +
            count(eye_info.real_points, lambda y,x: stones[y][x] == EMPTY and len(info_by_point[(y,x)].adj_eye_points) >= 3)
            >= 6
        ):
            eye_value = max(eye_value, 2)


        # General for all eyes - assume 2 eye value if there are two adjacent degree >= 3 points at least one of which is empty
        # and not on the border and the other is empty or has an empty eye neighbor besides the first.
        # And it splits the space into at least two pieces for which each piece has a point with num_moves_to_block == 0 and
        # at least one piece has two such points and at least two such pieces if the other point was not also empty.
        if eye_value < 2:
            for point_to_delete in eye_info.real_points:
                (dy,dx) = point_to_delete
                if stones[dy][dx] != EMPTY:
                    continue
                if is_on_border(dy,dx,ysize,xsize):
                    continue

                info1 = info_by_point[point_to_delete]
                if info1.num_moves_to_block > 1 or len(info1.adj_eye_points) < 3:
                    continue

                for adjacent in info1.adj_eye_points:
                    info2 = info_by_point[adjacent]
                    if len(info2.adj_eye_points) < 3:
                        continue
                    if info2.num_moves_to_block > 1:
                        continue
                    dy2,dx2 = adjacent
                    if stones[dy2][dx2] != EMPTY and info2.num_empty_adj_eye_points <= 1:
                        continue


                    pieces = get_pieces(ysize,xsize,eye_info.real_points,set([point_to_delete,adjacent]))
                    if len(pieces) < 2:
                        continue

                    num_definite_eye_pieces = 0
                    num_double_definite_eye_pieces = 0
                    for piece in pieces:
                        num_zero_moves_to_block = 0
                        for point in piece:
                            if info_by_point[point].num_moves_to_block <= 0:
                                num_zero_moves_to_block += 1
                                if num_zero_moves_to_block >= 2:
                                    break
                        if num_zero_moves_to_block >= 1:
                            num_definite_eye_pieces += 1
                        if num_zero_moves_to_block >= 2:
                            num_double_definite_eye_pieces += 1

                    if (
                        num_definite_eye_pieces >= 2 and
                        num_double_definite_eye_pieces >= 1 and
                        (stones[dy2][dx2] == EMPTY or num_double_definite_eye_pieces >= 2)
                    ):
                        eye_value = max(eye_value, 2)
                        break

                if eye_value >= 2:
                    break

        eye_value = min(eye_value, 2)
        eye_info.eye_value = eye_value


def mark_scoring(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    score_false_eyes: bool,
    strict_reaches_black: List[List[bool]],
    strict_reaches_white: List[List[bool]],
    region_ids: List[List[RegionId]],
    region_infos_by_id: Dict[RegionId,RegionInfo],
    chain_ids: List[List[ChainId]],
    chain_infos_by_id: Dict[ChainId,ChainInfo],
    is_false_eye_point: List[List[bool]],
    eye_ids: List[List[EyeId]],
    eye_infos_by_id: Dict[EyeId,EyeInfo],
    is_unscorable_false_eye_point: List[List[bool]],
    scoring: List[List[LocScore]],  # mutated by this function
):
    # Also avoid scoring points immediately adjacent to false eye points occupied by single dead opponent throwins.
    extra_black_unscoreable_points = set()
    extra_white_unscoreable_points = set()
    for y in range(ysize):
        for x in range(xsize):
            if is_unscorable_false_eye_point[y][x] and stones[y][x] != EMPTY and marked_dead[y][x]:
                adjacents = [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]
                if stones[y][x] == WHITE:
                    for point in adjacents:
                        extra_black_unscoreable_points.add(point);
                else:
                    for point in adjacents:
                        extra_white_unscoreable_points.add(point);

    for y in range(ysize):
        for x in range(xsize):
            s = scoring[y][x]
            region_id = region_ids[y][x]
            if region_id == -1:
                s.is_dame = True
            else:
                region_info = region_infos_by_id[region_id]
                color = region_info.color
                total_eyes = sum(eye_infos_by_id[eye_id].eye_value for eye_id in region_info.eyes)
                if total_eyes <= 1:
                    s.belongs_to_seki_group = region_info.color

                if is_false_eye_point[y][x]:
                    s.is_false_eye = True

                if is_unscorable_false_eye_point[y][x]:
                    s.is_unscorable_false_eye = True
                if (stones[y][x] == EMPTY or marked_dead[y][x]) and (
                    (color == BLACK and (y,x) in extra_black_unscoreable_points) or
                    (color == WHITE and (y,x) in extra_white_unscoreable_points)
                ):
                    s.is_unscorable_false_eye = True

                s.eye_value = 0
                if eye_ids[y][x] != -1:
                    s.eye_value = eye_infos_by_id[eye_ids[y][x]].eye_value

                if (
                    (stones[y][x] != color or marked_dead[y][x]) and
                    s.belongs_to_seki_group == EMPTY and
                    (score_false_eyes or not s.is_unscorable_false_eye) and
                    chain_infos_by_id[chain_ids[y][x]].region_id == region_id and
                    not (color == WHITE and strict_reaches_black[y][x]) and
                    not (color == BLACK and strict_reaches_white[y][x])
                ):
                    s.is_territory_for = color



