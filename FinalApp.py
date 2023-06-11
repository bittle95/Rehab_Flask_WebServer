
import argparse, sys
from src.Server_Final import NRCServer

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=False, default='0.0.0.0', help="호스트 주소")
    parser.add_argument('--port', required=False, default=9021, help="메인 서버 포트")
    args = parser.parse_args()
    server = NRCServer(args.host, args.port)
    server.Start()