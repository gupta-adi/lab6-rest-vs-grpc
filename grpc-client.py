
import argparse
import base64
import math
import random
import time

import grpc

import lab6_pb2
import lab6_pb2_grpc


IMAGE_FILE = "Flatirons_Winter_Sunrise_edit_2.jpg"


def doAdd(stub, debug=False):
    request = lab6_pb2.AddRequest(a=5, b=10)

    response = stub.Add(request, timeout=30)

    assert response.sum == 15

    if debug:
        print("Sum:", response.sum)


def doRawImage(stub, img, debug=False):
    request = lab6_pb2.RawImageRequest(img=img)

    response = stub.RawImage(request, timeout=60)

    assert response.width > 0
    assert response.height > 0

    if debug:
        print(
            "Width:", response.width,
            "Height:", response.height
        )


def doDotProduct(stub, debug=False):
    a = [random.random() for _ in range(100)]
    b = [random.random() for _ in range(100)]

    request = lab6_pb2.DotProductRequest(
        a=a,
        b=b
    )

    response = stub.DotProduct(
        request,
        timeout=30
    )

    # Account for float32 serialization and
    # float32 response rounding.
    expected = sum(
        x * y for x, y in zip(request.a, request.b)
    )

    assert math.isclose(
        response.dotproduct,
        expected,
        rel_tol=1e-5,
        abs_tol=1e-5
    )

    if debug:
        print("Dot product:", response.dotproduct)


def doJsonImage(stub, encoded, debug=False):
    request = lab6_pb2.JsonImageRequest(
        img=encoded
    )

    response = stub.JsonImage(
        request,
        timeout=60
    )

    assert response.width > 0
    assert response.height > 0

    if debug:
        print(
            "Width:", response.width,
            "Height:", response.height
        )


def main():
    parser = argparse.ArgumentParser(
        description="gRPC client for Lab 6"
    )

    parser.add_argument("host")

    parser.add_argument(
        "cmd",
        choices=[
            "add",
            "rawImage",
            "dotProduct",
            "jsonImage"
        ]
    )

    parser.add_argument("reps", type=int)

    parser.add_argument(
        "-p", "--port",
        type=int,
        default=50051
    )

    parser.add_argument(
        "-d", "--debug",
        action="store_true"
    )

    args = parser.parse_args()

    if args.reps <= 0:
        parser.error("reps must be greater than zero")

    address = f"{args.host}:{args.port}"

    # Preload image input once.
    img = None
    encoded = None

    if args.cmd in ("rawImage", "jsonImage"):
        with open(IMAGE_FILE, "rb") as file:
            img = file.read()

        if args.cmd == "jsonImage":
            encoded = base64.b64encode(
                img
            ).decode("utf-8")

    options = [
        (
            "grpc.max_send_message_length",
            16 * 1024 * 1024
        ),
        (
            "grpc.max_receive_message_length",
            16 * 1024 * 1024
        )
    ]

    with grpc.insecure_channel(
        address,
        options=options
    ) as channel:

        grpc.channel_ready_future(
            channel
        ).result(timeout=10)

        stub = lab6_pb2_grpc.Lab6ServiceStub(
            channel
        )

        print(
            f"Running {args.reps} reps against {address}"
        )

        start = time.perf_counter()

        for _ in range(args.reps):
            if args.cmd == "add":
                doAdd(stub, args.debug)

            elif args.cmd == "rawImage":
                doRawImage(stub, img, args.debug)

            elif args.cmd == "dotProduct":
                doDotProduct(stub, args.debug)

            elif args.cmd == "jsonImage":
                doJsonImage(stub, encoded, args.debug)

        elapsed = time.perf_counter() - start

    avg_ms = (elapsed / args.reps) * 1000

    print(f"Took {avg_ms:.4f} ms per operation")


if __name__ == "__main__":
    main()
