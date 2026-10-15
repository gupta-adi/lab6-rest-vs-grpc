# Lab 6 - REST vs. gRPC

## Setup

Three Google Cloud Compute Engine `e2-standard-2` VMs were used for the experiments. The REST server listened on port `5000`, and the gRPC server listened on port `50051`. All client requests were initiated from VM 1. Remote requests used internal IP addresses.

| VM | Zone | Internal IP | Role |
|---|---|---|---|
| `lab6-vm1` | `us-west1-a` | `10.138.0.23` | Client for all tests; server for local tests |
| `lab6-vm2` | `us-west1-a` | `10.138.0.24` | Server for same-zone tests |
| `lab6-vm3` | `europe-west3-a` | `10.156.0.3` | Server for different-region tests |

The local test used `localhost` on VM 1; same-zone tests connected from VM 1 to VM 2; different-region tests connected from VM 1 to VM 3. The `add` and `dotproduct` operations were run 1,000 times locally and in the same zone; `rawimg` and `jsonimg` were run 100 times. Each different-region operation was run 100 times. Basic network latency was measured using `ping -c 10` for each configuration.

## Results

All RPC values are **average milliseconds per operation**. PING values are **average round-trip times in milliseconds**.

| Method | Local | Same-Zone | Different Region |
|---|---:|---:|---:|
| REST add | 3.958 | 3.746 | 474.966 |
| gRPC add | 0.769 | 1.360 | 161.883 |
| REST rawimg | 9.137 | 10.641 | 1387.669 |
| gRPC rawimg | 11.322 | 9.360 | 195.582 |
| REST dotproduct | 4.193 | 4.223 | 344.934 |
| gRPC dotproduct | 0.873 | 1.550 | 143.550 |
| REST jsonimg | 32.238 | 32.034 | 1614.921 |
| gRPC jsonimg | 20.110 | 14.848 | 226.993 |
| PING | 0.056 | 0.468 | 300.806 |

## Observations

Overall, gRPC had lower average latency than REST for most operations, especially in the different-region tests, although REST was faster for the local raw-image request. Local and same-zone results were relatively close, while cross-region latency increased substantially: average ping rose from 0.056 ms locally and 0.468 ms within the same zone to 300.806 ms between regions. The lightweight `add` operation increased from 3.958 ms to 474.966 ms with REST and from 0.769 ms to 161.883 ms with gRPC. This highlights how network latency becomes more significant when client and server are geographically separated. The REST client makes a new HTTP/TCP connection for each request in this setup, whereas the gRPC client reuses one connection, which likely contributes to gRPC's advantage over longer distances. JSON image requests were also slower than raw-image requests in both implementations, consistent with additional Base64 encoding and processing. Since the REST image client rereads and encodes images per request while the gRPC client preloads them, the image comparisons also include differences in client-side preparation overhead.
