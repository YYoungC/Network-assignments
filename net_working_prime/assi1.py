# this is assignment 4.1

import asyncio


async def dispatch(reader, writer):
    while True:
        data = await reader.read(2048)

        if data and data != b'exit\r\n':    # if the input data is valid
            writer.write(data)              # write the data back
            await writer.drain()
            print(data)                     # print the data
        else:           # if no data or data is 'exit', break
            break
    
    writer.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 8080, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
