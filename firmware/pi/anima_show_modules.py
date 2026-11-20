"""Create and open FAIR round commitments on the Pi."""
from argparse import ArgumentParser
from hashlib import sha256
from hmac import compare_digest
import json
from pathlib import Path
import secrets
import uuid


CHOICES = ('ROCK', 'PAPER', 'SCISSORS')


def digest(round_id, throw, nonce):
    wire = f'ANIMA-RPS-v1\n{round_id}\n{throw}\n{nonce}\n'.encode('ascii')
    return sha256(wire).hexdigest()


def commit(path):
    private = {'round': uuid.uuid4().hex, 'throw': secrets.choice(CHOICES), 'nonce': secrets.token_hex(24)}
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(private, stream)
    return {'round': private['round'], 'commitment': digest(private['round'], private['throw'], private['nonce'])}


def reveal(path, published_commitment):
    private = json.loads(Path(path).read_text(encoding='utf-8'))
    expected = digest(private['round'], private['throw'], private['nonce'])
    if private['throw'] not in CHOICES or not compare_digest(expected, published_commitment):
        raise ValueError('Round data does not match the published commitment')
    return {**private, 'commitment': expected}


def main():
    parser = ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='operation', required=True)
    seal = commands.add_parser('commit')
    seal.add_argument('private_file')
    open_round = commands.add_parser('reveal')
    open_round.add_argument('private_file')
    open_round.add_argument('published_commitment')
    args = parser.parse_args()
    if args.operation == 'commit':
        result = commit(args.private_file)
    else:
        result = reveal(args.private_file, args.published_commitment)
    print(json.dumps(result, separators=(',', ':')))


if __name__ == '__main__':
    main()
