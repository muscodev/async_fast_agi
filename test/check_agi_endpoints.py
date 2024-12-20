import asyncio
from panoramisk.fast_agi import Application

FAST_AGI_PAYLOAD = b'''agi_network: yes
agi_network_script: book_complaint_old/hello
agi_request: agi://127.0.0.1:4574/book_complaint_old/hello?phone_number=918833&test_args=3&test_args=5&check=3
agi_channel: SIP/xxxxxx-00000000
agi_language: en_US
agi_type: SIP
agi_uniqueid: 1437920906.0
agi_version: asterisk
agi_callerid: 201
agi_calleridname: user 201
agi_callingpres: 0
agi_callingani2: 0
agi_callington: 0
agi_callingtns: 0
agi_dnid: 9011
agi_rdnis: unknown
agi_context: default
agi_extension: 9011
agi_priority: 2
agi_enhanced: 0.0
agi_accountcode: default
agi_threadid: -1260881040
agi_arg_1: answered


'''



async def fake_asterisk_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 4574)
    # send headers
    writer.write(FAST_AGI_PAYLOAD)
    # read it back
    msg_back = await reader.readline()
    writer.write(b'100 Trying...\n')
    writer.write(b'200 result=0\n')
    writer.close()
    return msg_back



async def test_fast_agi_application():


    msg_back = await fake_asterisk_client()
    assert b'ANSWER\n' == msg_back

    await asyncio.sleep(1)  # Wait the end of endpoint


asyncio.run(test_fast_agi_application())