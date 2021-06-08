# shitposts

Asynchronous wrapper for [ShitpostAPI](https://github.com/regulad/ShitpostAPI). 

### Example

```python
import asyncio
from shitposts import AsyncShitpostingSession


async def main():
    with open("input.mp4", "rb") as input_media:
        input_bytes = input_media.read()

    async with AsyncShitpostingSession() as session:
        output_bytes = await session.edit(
            input_bytes,
            "video/mp4",
            [{"name": "frame", "parameters": {"bottom": "funk"}}]
        )

    with open("output.mp4", "xb") as output_media:
        output_media.write(output_bytes)

asyncio.run(main())
```
