## goscorer
**Testing in progress, this code is new and might not be stable yet!**

Territory scoring in Go with automated seki detection is very challenging. The intent for this library is provide an open-source implementation that can correctly score almost any end-of-game position under Japanese-like rules that territory is not counted for groups alive in seki, if dead stones are correctly marked and enough of the eventually-necessary protective moves are made. It may not always be correct in sufficiently exotic positions, but positions not correctable with further play should be rare.

In practice, this implementation does NOT require players to fill all the dame. By default it will automatically exclude counting obvious false eye shapes that must eventually be filled, although this can be configured. Of course, this will not catch all necessary internal protections. Players still need to play enough of the dame to force internal protections that aren't simply false eye shapes.

<table class="image">
<tr><td><img src="https://raw.githubusercontent.com/lightvector/goscorer/master/images/example.png" height="350"/></td></tr>
<tr><td><sub>Top groups are correctly detected as alive in seki and no territory is counted. Bottom groups are alive with territory, but territory is still not counted for some of the false eyes.</sub></tr></td>
</table>

There is both a Python implementation and a Javascript implementation that implement exactly the same algorithm and heuristics. The Python implementation is well-commented with verbose docstrings on the `LocScore` object and the primary `territory_scoring` function. The Javascript implementation is a port of the Python implementation, so for more detailed documentation, see the Python code rather than the Javascript code. For completeness, an area scoring implementation is also provided alongside the territory scoring implementation.


The relevant code in this repo is released under a MIT license, see LICENSE.txt for details.

Example in Python:
```
from goscorer import EMPTY, BLACK, WHITE, final_territory_score, territory_scoring
stones = [
  [BLACK, EMPTY, BLACK, EMPTY, WHITE],
  [BLACK, BLACK, BLACK, WHITE, EMPTY],
  [WHITE, WHITE, WHITE, BLACK, BLACK],
  [WHITE, EMPTY, WHITE, BLACK, EMPTY],
  [EMPTY, WHITE, WHITE, BLACK, BLACK],
]
marked_dead = [ [ False for _ in range(5) ] for _ in range(5) ]

# just the score
final_score = final_territory_score(
    stones,
    marked_dead,
    black_points_from_captures=0,
    white_points_from_captures=0,
    komi=6.5,
)
# detailed territory map
scoring = territory_scoring(stones,marked_dead)
```

Example in Javascript:
```
import { EMPTY, BLACK, WHITE, finalTerritoryScore, territoryScoring } from "./goscorer.js";

stones = [
  [BLACK, EMPTY, BLACK, EMPTY, WHITE],
  [BLACK, BLACK, BLACK, WHITE, EMPTY],
  [WHITE, WHITE, WHITE, BLACK, BLACK],
  [WHITE, EMPTY, WHITE, BLACK, EMPTY],
  [EMPTY, WHITE, WHITE, BLACK, BLACK],
];
markedDead = Array.from({length: 5}, () => Array.from({length: 5}, () => false));

// just the score
finalScore = finalTerritoryScore(
    stones,
    markedDead,
    0,
    0,
    6.5,
)
// detailed territory map
scoring = territoryScoring(stones,markedDead)
```

