## goscorer

**Testing in progress, this code is new and might not be stable yet!**

Territory scoring in Go with automated seki detection is very challenging. The intent for this library is provide an open-source implementation that can correctly score almost any end-of-game position if the markings supplied are correct and enough of the eventually-necessary protective moves are made. It may not always be correct in sufficiently exotic positions, but some of those cases might still be correctable with additional neutral moves.

In practice, this implementation does NOT require players to fill all the dame. It will automatically exclude counting obvious false eye shapes that must eventually be filled. Of course, this will not catch all necessary internal protections - players still need to play enough of the dame to force internal protections that aren't simply false eye shapes.

There is both a Python implementation and a Javascript implementation that implement exactly the same algorithm and heuristics. The Python implementation is well-commented with verbose docstrings on the `LocScore` object and the primary `territory_scoring` function. The Javascript implementation is a port of the code - see the Python code for more detailed explanation of fields.

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

