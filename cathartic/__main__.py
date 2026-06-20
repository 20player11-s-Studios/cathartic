import sys

if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help", "help"):
    print("Cathartic v0.1.0")
    print("A clean system, a clear mind.")
    print()
    print("Usage: cathartic [--help]")
    print()
    print("Just run it — no arguments needed. Navigate with arrow keys.")
    sys.exit(0)

from cathartic.menu import main
main()
