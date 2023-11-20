import csv


def rewrite_mubench_results(input_path: str, output_path: str):
    """Rewrites mubench results to a usable csv file."""
    with open(output_path, "w+", encoding="utf-8") as output_file:
        csv_writer = csv.writer(output_file)
        headers = [
            "timestamp",
            "latency_ms",
            "status_code",
            "processed_requests",
            "pending_requests",
        ]
        with open(input_path, "r", encoding="utf-8") as input_file:
            for i, line in enumerate(input_file):
                chunks = line.split()
                msg_headers = [ele[1:-1].split(":") for ele in chunks[5:]]
                if i == 0:
                    header_keys = [ele[0][2:] for ele in msg_headers]
                    headers = [*headers, *header_keys]
                    csv_writer.writerow(headers)
                msg_headers = [":".join(ele[1:]) for ele in msg_headers]
                data_point = [*chunks[:5], *msg_headers]
                csv_writer.writerow(data_point)
