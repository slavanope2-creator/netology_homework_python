import config
from src.analyzer import OrderAnalyzer


def main() -> None:
    analyzer = OrderAnalyzer(config)
    analyzer.process_all()
    analyzer.summary()


if __name__ == "__main__":
    main()