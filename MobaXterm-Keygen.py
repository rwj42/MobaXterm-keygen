# /usr/bin/env python3
"""
Author: Double Sine
License: GPLv3
"""
import os
import sys
import zipfile

VariantBase64Table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
VariantBase64Dict = {i: VariantBase64Table[i] for i in range(len(VariantBase64Table))}
VariantBase64ReverseDict = {VariantBase64Table[i]: i for i in range(len(VariantBase64Table))}


def variant_base64_encode(bs: bytes):
    result = b''
    blocks_count, left_bytes = divmod(len(bs), 3)

    for i in range(blocks_count):
        coding_int = int.from_bytes(bs[3 * i:3 * i + 3], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 18) & 0x3f]
        result += block.encode()

    if left_bytes == 0:
        return result
    elif left_bytes == 1:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        result += block.encode()
        return result
    else:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3f]
        result += block.encode()
        return result


def variant_base64_decode(s: str):
    result = b''
    blocks_count, left_bytes = divmod(len(s), 4)

    for i in range(blocks_count):
        block = VariantBase64ReverseDict[s[4 * i]]
        block += VariantBase64ReverseDict[s[4 * i + 1]] << 6
        block += VariantBase64ReverseDict[s[4 * i + 2]] << 12
        block += VariantBase64ReverseDict[s[4 * i + 3]] << 18
        result += block.to_bytes(3, 'little')

    if left_bytes == 0:
        return result
    elif left_bytes == 2:
        block = VariantBase64ReverseDict[s[4 * blocks_count]]
        block += VariantBase64ReverseDict[s[4 * blocks_count + 1]] << 6
        result += block.to_bytes(1, 'little')
        return result
    elif left_bytes == 3:
        block = VariantBase64ReverseDict[s[4 * blocks_count]]
        block += VariantBase64ReverseDict[s[4 * blocks_count + 1]] << 6
        block += VariantBase64ReverseDict[s[4 * blocks_count + 2]] << 12
        result += block.to_bytes(2, 'little')
        return result
    else:
        raise ValueError('Invalid encoding.')


def encrypt_bytes(key: int, bs: bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xff))
        key = result[-1] & key | 0x482D
    return bytes(result)


def decrypt_bytes(key: int, bs: bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xff))
        key = bs[i] & key | 0x482D
    return bytes(result)


class LicenseType:
    Professional = 1
    Educational = 3
    Personal = 4
    # Persional = 4


def generate_license(license_type: LicenseType, count: int, username: str, major_version: int, minor_version):
    assert (count >= 0)
    license_string = '%d#%s|%d%d#%d#%d3%d6%d#%d#%d#%d#' % (license_type,
                                                           username, MajorVersion, minor_version,
                                                           count,
                                                           major_version, minor_version, minor_version,
                                                           0,  # Unknown
                                                           0,
                                                           # No Games flag. 0 means "NoGames = false". But it does
                                                           # not work.
                                                           0)  # No Plugins flag. 0 means "NoPlugins = false". But it
    # does not work.
    encoded_license_string = variant_base64_encode(encrypt_bytes(0x787, license_string.encode())).decode()
    with zipfile.ZipFile('Custom.mxtpro', 'w') as f:
        f.writestr('Pro.key', data=encoded_license_string)


def help():
    print('Usage:')
    print('    MobaXterm-Keygen.py <UserName> <Version>')
    print()
    print('    <UserName>:      The Name licensed to')
    print('    <Version>:       The Version of MobaXterm')
    print('                     Example:    10.9')
    print()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        help()
        exit(0)
    else:
        MajorVersion, MinorVersion = sys.argv[2].split('.')[0:2]
        MajorVersion = int(MajorVersion)
        MinorVersion = int(MinorVersion)
        generate_license(LicenseType.Professional,
                         1,
                         sys.argv[1],
                         MajorVersion,
                         MinorVersion)
        print('[*] Success!')
        print('[*] File generated: %s' % os.path.join(os.getcwd(), 'Custom.mxtpro'))
        print('[*] Please move or copy the newly-generated file to MobaXterm\'s installation path.')
        print()
else:
    print('[*] ERROR: Please run this script directly')
