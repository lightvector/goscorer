
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict

Color = int
EMPTY = 0
BLACK = 1
WHITE = 2

@dataclass
class LocScore:
    """Indicates how a given location on the board should be scored for territory.
    Only indicates the territory on the board (including territory, if any, underneath dead stones), but not the dead
    stones themselves."""

    is_territory_for: Color
    """Score 1 point of territory for this color player. If EMPTY, nobody scores this point.
    It is possible that this is EMPTY under a stone marked dead, in which case the point under the dead stone should
    not be counted as territory, even if the dead stone itself is counted for points.
    """

    belongs_to_seki_group: bool
    """If this is true, then this location is believed to be part of a group or surrounded space involved in a seki.
    Callers can display this for informational purposes. Additionally, if a caller wants to try to enforce more
    strictly the Japanese rule that that stones cannot just be treated as dead and counted in seki situations but
    must actually be physically captured prior to game end, they can consider also not scoring stones marked dead
    in locations marked as seki groups.
    """

    is_dame: bool
    """Callers can display this for informational purposes."""


def score(stones: List[List[Color]], marked_dead:List[List[bool]]) -> List[List[LocScore]]:
    """Perform territory scoring with seki detection assuming user or AI-supplied life and death markings,
    and also discounting false eye points without requiring dame filling.

    Seki detection might not be perfect, but generally players should be able to correct scoring by playing out
    additional dame and/or throw-ins and ataris, so long as stones are marked correctly. If this is genuniely
    a terminal position, failures that can't be corrected by further play should be rare and exotic.

    Parameters:
    stones[y][x] should indicate the color of the stone at that location or EMPTY if it empty.
    marked_dead[y][x] should be true if the location has a stone marked as dead, and false otherwise.

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
        raise ValueError(f"Marked_dead is not the same length as stones {ysize}")
    for row in marked_dead:
        if len(row) != xsize:
            raise ValueError(f"Not all rows in marked_dead are the same length as stones {xsize}")

    # Is there a path from this location to a living stone of the given color
    # that doesn't contain a living stone of the opponent?
    reaches_black: List[List[bool]] = [[False for x in range(xsize)] for y in range(ysize)]
    reaches_white: List[List[bool]] = [[False for x in range(xsize)] for y in range(ysize)]

    # Maximal contiuguous areas that reach only one player, maximally unioned based on reachability through empty space.
    region_ids: List[List[RegionId]] = [[-1 for x in range(xsize)] for y in range(ysize)]
    region_infos_by_id: Dict[RegionId,RegionInfo] = {}

    mark_regions(ysize,xsize,stones,marked_dead,reaches_black,reaches_white,region_ids,region_infos_by_id)

    # Maximal contiguous areas of the same color and liveness
    chain_ids: List[List[ChainId]] = [[-1 for x in range(xsize)] for y in range(ysize)]
    chain_infos_by_id: Dict[ChainId,ChainInfo] = {}

    mark_chains(ysize,xsize,stones,marked_dead,region_ids,chain_ids,chain_infos_by_id)

    # Points that should not be counted as part of eyes or scored
    is_false_eye_point: List[List[bool]] = [[False for x in range(xsize)] for y in range(ysize)]

    mark_false_eye_points(ysize,xsize,stones,marked_dead,region_ids,region_infos_by_id,chain_ids,chain_infos_by_id,is_false_eye_point)

    # Eyes of regions
    eye_ids: List[List[EyeId]] = [[-1 for x in range(xsize)] for y in range(ysize)]
    eye_infos_by_id: Dict[EyeId,EyeInfo] = {}

    mark_eyes(ysize,xsize,stones,marked_dead,region_ids,region_infos_by_id,chain_ids,chain_infos_by_id,is_false_eye_point,eye_ids,eye_infos_by_id)

    # Final processing
    make_locscore = lambda: LocScore(is_territory_for=EMPTY,belongs_to_seki_group=False,is_dame=False)
    scoring: List[List[LocScore]] = [[make_locscore() for x in range(xsize)] for y in range(ysize)]

    mark_scoring(ysize,xsize,stones,marked_dead,region_ids,region_infos_by_id,is_false_eye_point,eye_infos_by_id,scoring)

    return scoring

def get_opp(pla: Color) -> Color:
    return 3 - pla

RegionId = int
ChainId = int
EyeId = int

def is_on_board(y, x, ysize, xsize):
    return y >= 0 and x >= 0 and y < ysize and x < xsize

def print2d(board, f):
    for y in range(ysize):
        print("".join([str(f(item)) for item in board[y]]))

def color_to_str(color):
    if color == BLACK:
        return "x"
    elif color == WHITE:
        return "o"
    return "."

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
    reaches_black: List[List[bool]],  # mutated by this function
    reaches_white: List[List[bool]],  # mutated by this function
    region_ids: List[List[RegionId]],  # mutated by this function
    region_infos_by_id: Dict[RegionId,RegionInfo],  # mutated by this function
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

    # Recursively walk and fill regions that reach only pla and not opp, but passing through anything that's not an opponent living stone.
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
                visited = [[False for x in range(xsize)] for y in range(ysize)]
                fill_region(y,x,region_id,WHITE,reaches_black,reaches_white,visited)
            if reaches_white[y][x] and not reaches_black[y][x] and region_ids[y][x] == -1:
                region_id = next_region_id
                next_region_id += 1
                region_infos_by_id[region_id] = RegionInfo(region_id=region_id, color=WHITE, region_and_dame=set(), eyes=set())
                visited = [[False for x in range(xsize)] for y in range(ysize)]
                fill_region(y,x,region_id,BLACK,reaches_white,reaches_black,visited)

@dataclass
class ChainInfo:
    chain_id: ChainId
    region_id: RegionId
    color: Color
    points: List[Tuple[int,int]]
    neighbors: Set[ChainId]
    adjacents: Set[Tuple[int,int]]
    is_marked_dead: bool
    touches_same_color_different_mark: bool

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
            return
        if stones[y][x] != color or marked_dead[y][x] != is_marked_dead:
            chain_infos_by_id[with_id].adjacents.add((y,x))
            return
        chain_ids[y][x] = with_id
        chain_infos_by_id[with_id].points.append((y,x))

        # Any contiguous chain of the same liveness and color should always belong to the
        # same region, or -1 if they don't belong to any region.
        assert region_ids[y][x] == chain_infos_by_id[with_id].region_id

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
                    is_marked_dead=is_marked_dead,
                    touches_same_color_different_mark=False,
                )
                assert is_marked_dead or color == EMPTY or region_ids[y][x] != -1
                fill_chain(y,x,chain_id,color,is_marked_dead)

                for (ay,ax) in chain_infos_by_id[chain_id].adjacents:
                    if stones[ay][ax] == color and marked_dead[ay][ax] != is_marked_dead:
                        chain_infos_by_id[with_id].touches_same_color_different_mark = True
                        break


def mark_false_eye_points(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    region_ids: List[List[RegionId]],
    region_infos_by_id: Dict[RegionId,RegionInfo],
    chain_ids: List[List[ChainId]],
    chain_infos_by_id: Dict[ChainId,ChainInfo],
    is_false_eye_point: List[List[bool]],  # mutated by this function
):
    MacroChainId = int

    for pla in [BLACK,WHITE]:
        opp = get_opp(pla)

        # Maximally union alive chains for the player with chains of empty space that are not part of a region
        # so that for false eye detection we consider loose connections to chains that may have more eyes.
        next_macrochain_id = 0
        chains_of_macrochain: Dict[MacroChainId,List[ChainId]] = defaultdict(list)
        macrochain_of_chain: Dict[ChainId,MacroChainId] = {}

        def should_merge(chain_info: ChainInfo):
            return (
                (chain_info.region_id != -1 and region_infos_by_id[chain_info.region_id].color == pla and chain_info.color == pla and not chain_info.is_marked_dead) or
                (chain_info.region_id == -1)
            )
        for chain_id, chain_info in chain_infos_by_id.items():
            # Already done
            if chain_id in macrochain_of_chain:
                continue

            if not should_merge(chain_info):
                macrochain_id = next_macrochain_id
                next_macrochain_id += 1
                chains_of_macrochain[macrochain_id].append(chain_id)
                macrochain_of_chain[chain_id] = macrochain_id
            else:
                macrochain_id = next_macrochain_id
                next_macrochain_id += 1

                def merge(chain_info):
                    if chain_info.chain_id in macrochain_of_chain:
                        return
                    chains_of_macrochain[macrochain_id].append(chain_info.chain_id)
                    macrochain_of_chain[chain_info.chain_id] = macrochain_id
                    for c in chain_info.neighbors:
                        neighbor_info = chain_infos_by_id[c]
                        if should_merge(neighbor_info):
                            merge(neighbor_info)

                merge(chain_info)

        while True:
            anything_changed = False
            # Test each macro chain of a player's regions to see if it is disconnected tail leading to a false eye
            for macrochain_id, chains in chains_of_macrochain.items():
                has_alive_player_region_chain = False
                region_ids_in_macrochain = set()
                for chain_id in chains:
                    chain_info = chain_infos_by_id[chain_id]
                    if (chain_info.region_id != -1 and region_infos_by_id[chain_info.region_id].color == pla and chain_info.color == pla and not chain_info.is_marked_dead):
                        has_alive_player_region_chain = True
                        region_ids_in_macrochain.add(chain_info.region_id)

                if not has_alive_player_region_chain:
                    continue

                # All macrochains of the player should overlap only one region id, else something is a bug
                assert len(region_ids_in_macrochain) == 1
                region_id = list(region_ids_in_macrochain)[0]

                # See if the macro chain has exactly one adjacent point that is not a living player that is also part of the same region
                # and that is not itself already marked as a false eye point.
                candidate_false_eye_point = None
                too_many_candidates = False
                for chain_id in chains:
                    if too_many_candidates:
                        break
                    chain_info = chain_infos_by_id[chain_id]
                    for (y,x) in chain_info.adjacents:
                        if region_ids[y][x] == chain_info.region_id and not is_false_eye_point[y][x] and not (stones[y][x] == pla and not marked_dead[y][x]):
                            # It was a second point? Aaah bad.
                            if candidate_false_eye_point is not None:
                                too_many_candidates = True
                                break
                            candidate_false_eye_point = (y,x)

                if candidate_false_eye_point is None or too_many_candidates:
                    continue

                # Check each adjacent location to the false eye point that is not the original macrochain and see
                # if it can reach the original macrochain via a path that does not go through living opponent stones
                # or the candidate false eye.

                pla = chain_info.color
                opp = get_opp(pla)

                cy, cx = candidate_false_eye_point
                def can_reach_chain(y,x,visited):
                    if not is_on_board(y,x,ysize,xsize):
                        return False
                    if visited[y][x]:
                        return False
                    if macrochain_of_chain[chain_ids[y][x]] == macrochain_id:
                        return True
                    if y == cy and x == cx:
                        return False
                    if stones[y][x] == opp and not marked_dead[y][x]:
                        return False
                    visited[y][x] = True
                    return (
                        can_reach_chain(y-1,x,visited) or
                        can_reach_chain(y+1,x,visited) or
                        can_reach_chain(y,x-1,visited) or
                        can_reach_chain(y,x+1,visited)
                    )

                adjacents = [(cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)]
                found_can_reach = False
                found_different_macrochain = False
                for (ay,ax) in adjacents:
                    if not is_on_board(ay,ax,ysize,xsize):
                        continue
                    # Original macrochain
                    if macrochain_of_chain[chain_ids[ay][ax]] == macrochain_id:
                        continue
                    found_different_macrochain = True
                    visited = [[False for x in range(xsize)] for y in range(ysize)]
                    if can_reach_chain(ay,ax,visited):
                        found_can_reach = True
                        break
                # It's a false eye if there is at least one different chain but none of them can reach
                if found_different_macrochain and not found_can_reach:
                    is_false_eye_point[cy][cx] = True
                    anything_changed = True

            if not anything_changed:
                break

def get_pieces(ysize: int, xsize: int, points: Set[Tuple[int,int]], point_to_delete: Tuple[int,int]) -> List[Set[Tuple[int,int]]]:
    """Get the connected pieces resulting from deleting the given point"""
    used_points = set()

    def floodfill(point, piece: Set[Tuple[int,int]]):
        if point in used_points:
            return
        used_points.add(point)
        piece.add(point)

        (y,x) = point
        adjacents = [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]
        for (ay,ax) in adjacents:
            if not is_on_board(ay,ax,ysize,xsize):
                continue
            floodfill((ay,ax),piece)

    pieces = []
    for point in points:
        if point not in used_points:
            piece = set()
            floodfill(point,piece)
            pieces.append(piece)
    return pieces

@dataclass
class EyeInfo:
    pla: Color
    region_id: RegionId
    eye_id: EyeId
    size: int
    points: Set[Tuple[int,int]]
    eye_value: int

@dataclass
class EyePointInfo:
    adj_points: List[Tuple[int,int]]
    adj_eye_points: List[Tuple[int,int]]
    num_empty_adj_points: int = 0
    num_empty_adj_false_points: int = 0
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

def mark_eyes(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    region_ids: List[List[RegionId]],
    region_infos_by_id: Dict[RegionId,RegionInfo],
    chain_ids: List[List[ChainId]],
    chain_infos_by_id: Dict[ChainId,ChainInfo],
    is_false_eye_point: List[List[bool]],
    eye_ids: List[List[EyeId]],  # mutated by this function
    eye_infos_by_id: Dict[EyeId,EyeInfo],  # mutated by this function
):
    next_eye_id = 0
    chains_tested = set()

    # Iterate over empty chains that belong to a region
    for base_chain_id, base_chain_info in chain_infos_by_id.items():
        if base_chain_info.color != EMPTY:
            continue
        if base_chain_info.region_id == -1:
            continue
        # If this chain is tested for eyeness already, we're done.
        if base_chain_id in chains_tested:
            continue

        region_id = base_chain_info.region_id
        pla = region_infos_by_id[region_id].color
        opp = get_opp(pla)

        # Do a recursive search walking through adjacent chains of either color marked dead
        # and through other empty spaces, stopping at opponent or player stones marked alive.
        # It must be the case that we only run into player stones marked alive, no opponent
        # stones marked alive, for this to be an eye.
        chains_included = set()
        new_chains_to_iterate = [base_chain_id]
        found_living_pla_border = False
        found_living_opp_border = False
        while len(new_chains_to_iterate) > 0:
            chain_id = new_chains_to_iterate.pop()
            if chain_id in chains_included:
                continue

            chain_info = chain_infos_by_id[chain_id]
            assert chain_info.region_id == region_id

            if chain_info.color != EMPTY and not chain_info.is_marked_dead:
                if chain_info.color == pla:
                    found_living_pla_border = True
                elif chain_info.color == opp:
                    found_living_opp_border = True
                continue

            # For player chains marked dead that touch alive player stones,
            # we treat them as also alive and it interrupts the eye propagation
            if chain_info.color == pla and chain_info.touches_same_color_different_mark:
                found_living_pla_border = True
                continue

            chains_included.add(chain_id)
            new_chains_to_iterate.extend(chain_info.neighbors)

        # We've found the maximal potential eye, mark them all as tested
        for chain_id in chains_included:
            chains_tested.add(chain_id)

        # Not an eye
        if not found_living_pla_border:
            continue
        if found_living_opp_border:
            continue

        # Okay, so at this point we have an eye!
        # Let's accumulate various stats about the points in the eye
        points = set()
        info_by_point = {}
        for chain_id in chains_included:
            for (y,x) in chain_infos_by_id[chain_id].points:
                if is_false_eye_point[y][x]:
                    continue
                points.add((y,x))
                info = EyePointInfo(adj_points=[],adj_eye_points=[])
                info_by_point[(y,x)] = info

        for (y,x) in points:
            info = info_by_point[(y,x)]
            adjacents = [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]
            for (ay,ax) in adjacents:
                if not is_on_board(ay,ax,ysize,xsize):
                    continue
                info.adj_points.append((ay,ax))
                if (ay,ax) in points:
                    info.adj_eye_points.append((ay,ax))

        for (y,x) in points:
            info = info_by_point[(y,x)]
            for (ay,ax) in info.adj_points:
                if stones[ay][ax] == EMPTY:
                    info.num_empty_adj_points += 1
                if stones[ay][ax] == EMPTY and is_false_eye_point[ay][ax]:
                    info.num_empty_adj_false_points += 1
                if stones[ay][ax] == EMPTY and is_false_eye_point[ay][ax]:
                    info.num_opp_adj_false_points += 1

            if info.num_opp_adj_false_points > 0 and stones[y][x] == opp:
                info.is_false_eye_poke = True
            if info.num_empty_adj_false_points >= 2 and stones[y][x] == opp:
                info.is_false_eye_poke = True  # miai to make the poke

        for (y,x) in points:
            info = info_by_point[(y,x)]
            info.num_moves_to_block = 0
            info.num_moves_to_block_no_opps = 0
            for (ay,ax) in info.adj_points:
                block = 0
                if stones[ay][ax] == EMPTY and (ay,ax) not in points:
                    block = 1
                if stones[ay][ax] == EMPTY and (ay,ax) in info_by_point and info_by_point[(ay,ax)].num_opp_adj_false_points >= 1:
                    block = 1
                if stones[ay][ax] == opp and (ay,ax) in info_by_point and info_by_point[(ay,ax)].num_empty_adj_false_points >= 1:
                    block = 1
                if stones[ay][ax] == opp and (ay,ax) in is_false_eye_point[ay][ax]:
                    block = 1000
                if stones[ay][ax] == opp and (ay,ax) in info_by_point and info_by_point[(ay,ax)].is_false_eye_poke:
                    block = 1000
                info.num_moves_to_block += block

        def count(points,predicate):
            c = 0
            for (y,x) in points:
                if predicate(y,x):
                    c += 1
            return c

        # Try to compute the eye value of this eye
        # A lot of the cases are just heuristic and are not entirely correct, but
        # it should be very rare for them to not be fixable by playing more dame and connecting more false eye shapes and such.
        eye_value = 0
        # General for all eyes - if the eye contains a point that can be blocked off in one move or less,
        # we treat it at as at least one eye (favoring the defender for unsettled)
        if count(points, lambda y,x: info_by_point[(y,x)].num_moves_to_block <= 1) >= 1:
            eye_value = 1

        # General for all eyes - if the eye contains a topologically interior bottleneck with respect
        # to the graph of points contained only within the eye itself and it is empty so it can be played
        # and there are at least N pieces that have a point with <= 0 moves to block off, count N eye value
        for point_to_delete in points:
            (dy,dx) = point_to_delete
            if stones[dy][dx] != EMPTY:
                continue
            pieces = get_pieces(ysize,xsize,points,point_to_delete)
            if len(pieces) < 2:
                continue
            num_definite_eye_pieces = 0
            for piece in pieces:
                zero_moves_to_block = False
                for point in piece:
                    if info_by_point[point].num_moves_to_block <= 0:
                        zero_moves_to_block = True
                        break
                if zero_moves_to_block:
                    num_definite_eye_pieces += 1
            eye_value = max(eye_value, num_definite_eye_pieces)

        # General for all eyes - assume 1 eye value if there are at least 6 stones marked as dead in the eye
        # General for all eyes - assume 2 eye value if there are at least 9 stones marked as dead in the eye
        marked_dead_count = count(points, lambda y,x: stones[y][x] == opp and marked_dead[y][x])
        if marked_dead_count >= 6:
            eye_value = max(eye_value, 1)
        if marked_dead_count >= 9:
            eye_value = max(eye_value, 2)

        # General for all eyes - assume 1 eye value if there are at least 6 stones marked as dead in the eye
        # General for all eyes - assume 2 eye value if there are at least 8 stones marked as dead in the eye
        marked_dead_count = count(points, lambda y,x: stones[y][x] == opp and marked_dead[y][x])
        if marked_dead_count >= 5:
            eye_value = max(eye_value, 1)
        if marked_dead_count >= 8:
            eye_value = max(eye_value, 2)

        # General for all eyes - assume 2 eye value if the size of the eye minus the number of weaknesses (counting severe weaknesses 2x)
        # minus the number of opponent stones inside is at least 6.
        if (
            len(points)
            - count(points, lambda y,x: info_by_point[(y,x)].num_moves_to_block >= 1)
            - count(points, lambda y,x: info_by_point[(y,x)].num_moves_to_block >= 2)
            - count(points, lambda y,x: stones[y][x] == opp)
            >= 6
        ):
            eye_value = max(eye_value, 2)

        if len(points) <= 5:
            # All cases handled by general cases
            pass
        elif len(points) == 6:
            # Rectangle 6 (2 points of degree 3, 4 points of degree 2)
            if (
                count(points, lambda y,x: len(info_by_point[(y,x)].adj_eye_points) == 3) == 2 and
                count(points, lambda y,x: len(info_by_point[(y,x)].adj_eye_points) == 2) == 4
            ):
                # Treat as alive if there are zero weaknesses on degree 2 and at least one degree 3 point is empty
                if (
                    count(points, lambda y,x: len(info_by_point[(y,x)].adj_eye_points) == 3 and stones[y][x] == EMPTY) >= 1 and
                    count(points, lambda y,x: len(info_by_point[(y,x)].adj_eye_points) == 2 and info_by_point[(y,x)].num_moves_to_block == 0) == 4
                ):
                    eye_value = max(eye_value, 2)
                # Treat as alive if both degree 3 points are empty, at most one non-severe weakness on degree 2, and at most one weakness on degree 3.
                if (
                    count(points, lambda y,x: len(info_by_point[(y,x)].adj_eye_points) == 3 and stones[y][x] == EMPTY) >= 2 and
                    count(points, lambda y,x: len(info_by_point[(y,x)].adj_eye_points) == 3 and info_by_point[(y,x)].num_moves_to_block == 0) >= 1 and
                    count(points, lambda y,x: len(info_by_point[(y,x)].adj_eye_points) == 2 and info_by_point[(y,x)].num_moves_to_block == 0) >= 3 and
                    count(points, lambda y,x: len(info_by_point[(y,x)].adj_eye_points) == 2 and info_by_point[(y,x)].num_moves_to_block <= 1) >= 4
                ):
                    eye_value = max(eye_value, 2)


        # Allocate the new eye id and populate the arrays!
        eye_id = next_eye_id
        next_eye_id += 1

        for (y,x) in points:
            eye_ids[y][x] = eye_id

        eye_infos_by_id[eye_id] = EyeInfo(
            pla=pla,
            region_id=region_id,
            eye_id=eye_id,
            size=len(points),
            points=points,
            eye_value=eye_value,
        )

        # Update the region info with this eye too
        region_infos_by_id[region_id].eyes.add(eye_id)

def mark_scoring(
    ysize: int,
    xsize: int,
    stones: List[List[Color]],
    marked_dead: List[List[bool]],
    region_ids: List[List[RegionId]],
    region_infos_by_id: Dict[RegionId,RegionInfo],
    is_false_eye_point: List[List[bool]],
    eye_infos_by_id: Dict[EyeId,EyeInfo],
    scoring: List[List[LocScore]],  # mutated by this function
):
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
                    s.belongs_to_seki_group = True

                if (stones[y][x] != color or marked_dead[y][x]) and not s.belongs_to_seki_group and not is_false_eye_point[y][x]:
                    s.is_territory_for = color




if __name__ == "__main__":
    stonestrs = [
        ".........",
        ".........",
        ".........",
        ".........",
        ".........",
        ".........",
        ".........",
        ".........",
    ]
    ysize = len(stonestrs)
    xsize = len(stonestrs[0])
    stones = [[EMPTY for x in range(xsize)] for y in range(ysize)]
    marked_dead = [[False for x in range(xsize)] for y in range(ysize)]
    for y in range(ysize):
        for x in range(xsize):
            c = stonestrs[y][x]
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

    scoring = score(stones,marked_dead)
    print("TERRITORY:")
    print2d(scoring, lambda s: ("x" if s.is_territory_for == BLACK else "o" if s.is_territory_for == WHITE else "."))
    print("SEKI:")
    print2d(scoring, lambda s: "1" if s.belongs_to_seki_group else ".")
    print("DAME:")
    print2d(scoring, lambda s: "1" if s.is_dame else ".")



