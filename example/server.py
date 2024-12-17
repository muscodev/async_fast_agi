from async_fast_agi import FastAGIApp, Request
import asyncio


# customise the Request to add your own methods
class MyRequest(Request):
    def extension_hi(self):
        print("hi")

#create a fastapi app
fa_app = FastAGIApp(request_class=MyRequest)


# create an endpoint
@fa_app.route('book_complaint_old/hello')
async def book_complaint(request: MyRequest, phone_number:int, test_args='ss'):
    """
    phone_number:int, test_args are the url parameters
    """
    print(request.parsed_url)
    print(request.query_params)
    print(request)
    # argument passed along with from dialplan
    print(request.args)
    # url parameter
    print(phone_number,'phone_number')
    # url parameter
    print(test_args,'test_args')
    # agi action 
    await request.answer()
    # custom action
    request.extension_hi()




async def main():

    server = await asyncio.start_server(fa_app.handler, '0.0.0.0', 4574)

    # Serve requests until CTRL+c is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        await server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # Close the server
        server.close()


if __name__ == '__main__':
    asyncio.run(main())