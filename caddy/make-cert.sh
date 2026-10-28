#!/bin/sh
# Sinh cert tu ky cho Caddy, voi IP va/hoac hostname nam trong SAN.
#
#   ./caddy/make-cert.sh 10.1.2.3
#   ./caddy/make-cert.sh 10.1.2.3 dmb.dnsvn.local
#
# Browser se canh bao mot lan vi cert tu ky - dieu nay binh thuong voi he thong
# noi bo. Muon het canh bao thi cai cert.pem vao trust store cua may client,
# hoac thay bang cert do CA noi bo cua cong ty phat hanh.

set -e

if [ $# -eq 0 ]; then
	echo "Dung: $0 <ip-hoac-hostname> [them-ten...]" >&2
	echo "Vi du: $0 10.1.2.3 dmb.dnsvn.local" >&2
	exit 1
fi

DIR="$(cd "$(dirname "$0")" && pwd)/certs"
mkdir -p "$DIR"

# Phan loai moi tham so la IP hay DNS name
SAN=""
for host in "$@"; do
	if echo "$host" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
		SAN="${SAN:+$SAN,}IP:$host"
	else
		SAN="${SAN:+$SAN,}DNS:$host"
	fi
done

echo "Sinh cert cho: $SAN"

openssl req -x509 -newkey rsa:2048 -sha256 -days 3650 -nodes \
	-keyout "$DIR/key.pem" -out "$DIR/cert.pem" \
	-subj "/CN=$1" \
	-addext "subjectAltName=$SAN" \
	-addext "basicConstraints=CA:FALSE" \
	-addext "keyUsage=digitalSignature,keyEncipherment" \
	-addext "extendedKeyUsage=serverAuth"

chmod 644 "$DIR/cert.pem"
chmod 600 "$DIR/key.pem"

echo "Da tao:"
echo "  $DIR/cert.pem"
echo "  $DIR/key.pem"
echo
openssl x509 -in "$DIR/cert.pem" -noout -subject -dates -ext subjectAltName
