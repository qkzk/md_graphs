---
title: exemple avec graphe

---

# Un titre


## Un sous titre

```python
def bonjour():
  return "Bonjour"
```

* 1 

    ```graph
    graph G {



    0 -- 1 [label = "" color=black fontcolor=black];
    1 -- 2 [label = "" color=black fontcolor=black];
    2 -- 0 [label = "" color=black fontcolor=black];
    1 -- 3 [label = "" color=black fontcolor=black];
    }

    ```
* 2

[line](bla)



```graph
graph G {

bgcolor="#ffffff00"
node [shape=circle]
rankdir=TB;
ranksep=0.5;
layout=circo;

0 -- 1 [label = "" color=black fontcolor=black];
1 -- 2 [label = "" color=black fontcolor=black];
2 -- 0 [label = "" color=black fontcolor=black];
1 -- 3 [label = "" color=black fontcolor=black];
}
```



```graph
graph G {



0 -- 1 [label = "" color=black fontcolor=black];
1 -- 2 [label = "" color=black fontcolor=black];
2 -- 0 [label = "" color=black fontcolor=black];
1 -- 3 [label = "" color=black fontcolor=black];
}

```
