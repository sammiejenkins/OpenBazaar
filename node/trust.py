import obelisk

import sys
from twisted.internet import reactor


TESTNET = False

def build_output_info_list(unspent_rows):
    unspent_infos = []
    for row in unspent_rows:
        assert len(row) == 4
        outpoint = obelisk.OutPoint()
        outpoint.hash = row[0]
        outpoint.index = row[1]
        value = row[3]
        unspent_infos.append(
            obelisk.OutputInfo(outpoint, value))
    return unspent_infos


def burnaddr_from_guid(guid_hex):
    # perturbate GUID
    # to ensure unspendability through
    # near-collision resistance of SHA256

    guid_hex = list(guid_hex)

    if guid_hex[14] == '0':
        guid_hex[14] = '1'
    else:
        guid_hex[14] = hex(int(guid_hex[14], 16) - 1)[2:]

    guid_hex = guid_hex[:40]
    guid_hex = ''.join(guid_hex)

    if TESTNET:
        guid_hex = '6f' + guid_hex
    else:
        guid_hex = '00' + guid_hex

    guid = guid_hex.decode('hex')

    return obelisk.bitcoin.EncodeBase58Check(guid)


def get_global(guid, callback):
    pass

def get_unspent(addr, callback):
    print('get_unspent call')
    def history_fetched(ec, history):
        print('history_fetched')
        if ec is not None:
            print >> sys.stderr, "Error fetching history:", ec
            return
        unspent_rows = [row[:4] for row in history if row[4] is None]
        unspent = build_output_info_list(unspent_rows)
        unspent = obelisk.select_outputs(unspent, 10000)

        if unspent is None:
            callback(0)
            return

        points = unspent.points

        if len(points) != 1:
            callback(0)
            return

        point = points[0]
        value = point.value

        callback(value)

    if TESTNET:
        obelisk_addr = "tcp://85.25.198.97:10091"
    else:
        obelisk_addr = "tcp://85.25.198.97:9091"

    print('unspent query to obelisk server at %s' % obelisk_addr)

    client = obelisk.ObeliskOfLightClient(obelisk_addr)

    print('Obelisk client instantiated')

    def get_history():
        print("get_history called from thread")
        client.fetch_history(addr, history_fetched)

    reactor.callFromThread(get_history)
