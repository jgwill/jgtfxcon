

# jgtfxcon

just getting prices from fxconnect


## Installation
```sh
pip install -U jgtfxcon
```

## Example

```py

    >>> import pandas as pd
    >>> import jgtfxcon
    >>> df=jgtfxcon.getPH('EUR/USD','H4')
    >>>
    >>> # retrieve 3000 periods and generate from the DF
    >>> df=jgtfxcon.getPH('EUR/USD','H4',3000,with_index=False)
    >>> dfi=jgtfxcon.createFromDF(df)
    >>>

```

## More


