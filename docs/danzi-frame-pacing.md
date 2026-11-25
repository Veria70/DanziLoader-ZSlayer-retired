# First frame-pacing experiment

**Question.** Can the renderer spend less time preparing hash dispatches while
keeping the same 64 KiB pieces checked? Earlier work in upstream added
`VICTORY_CARD_REHASH_RUNS`. This fork tests that existing option separately
from a small change to how Rust stores the resulting list.

| Run | Group adjacent hash ranges | Storage for merged ranges |
| --- | --- | --- |
| A | Off | Upstream |
| B | On | Upstream, separate output vector |
| C | On | Compact the input vector in place |

B versus A measures the upstream option. C versus B measures our storage
change. The in-place operation keeps the previous sorted merge order. It does
not skip texture checks, change render scale or reduce shader work.

## Measurement

Use Series X on the same machine for each run. Copy the same starting save
and cache, use the same renderer settings, then leave the camera stationary
in the prison room. Enable diagnostic logging with
`VICTORY_LOG=info,victory_gpu::frame=debug`. Identify the room from frame
captures, select a window starting at a logged present token, and run:

```shell
python tools/present_window.py path/to/run.log FIRST_TOKEN --frames 240
```

The script rejects incomplete or duplicated token sequences. FPS is frame
count divided by elapsed time. The 95th percentile is the nearest-rank
percentile of individual frame intervals. The 40 ms count is the number of
intervals meeting the 25 FPS budget. Engine presents do not measure physical
display scanout. Window-title FPS and CPU microbenchmarks are separate measures.
