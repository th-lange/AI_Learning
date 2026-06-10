import asyncio
import sys
from random import randint


async def do_some_work(identifier: str) -> str:
    """Simulate work for a given identifier.

    Args:
        identifier: The identifier for this work item.

    Returns:
        A completion message string.

    Note:
        Identifiers 'bbb' and 'ddd' use blocking `asyncio.sleep` to demonstrate
        how blocking calls stall the event loop when not used with `gather`.
    """
    await asyncio.sleep(randint(1, 5))

    print("do_some_work for", identifier)
    return "Done with " + identifier


async def main() -> list[str]:
    """Create coroutines for all work items without awaiting them.

    Returns:
        A list of coroutine objects, not yet executed.
    """
    res: list[str] = []

    for itm in ["aaa", "bbb", "ccc", "ddd", "eee"]:
        res.append(do_some_work(itm))

    return res


async def anti_main(itms: list[str]) -> None:
    """Execute items sequentially in reverse order by awaiting each one.

    Args:
        itms: Coroutine objects to execute.
    """
    for itm in reversed(itms):
        res = await itm
        print("Finished work for", res)


async def async_do(itms: list[str]) -> None:
    """Execute all items concurrently using asyncio.gather.

    Args:
        itms: Coroutine objects to execute in parallel.
    """
    res = await asyncio.gather(*itms)
    for itm in res:
        print("Finished work for", itm)


if __name__ == "__main__":
    print("Python Version:", sys.version, "\n")
    items = asyncio.run(main())
    asyncio.run(async_do(items))
